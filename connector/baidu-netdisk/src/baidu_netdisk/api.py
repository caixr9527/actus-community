"""Bounded fixed-origin JSON calls and explicit business response validation."""

import json

from . import models as m

ORIGIN = "https://pan.baidu.com/"


def decode(content: bytes, status: int, *, require_errno=True):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("baidu_response_invalid")
            result[key] = value
        return result

    try:
        if status != 200 or len(content) > 1024 * 1024:
            raise ValueError
        payload = json.loads(content, object_pairs_hook=pairs)
        if type(payload) is not dict:
            raise ValueError
        code = payload.get("errno", payload.get("error_code", payload.get("error_no")))
        if ((code is None and require_errno)
                or (code is not None and (type(code) not in (int, str) or code not in (0, "0")))):
            raise ValueError
        return payload
    except (ValueError, UnicodeError):
        raise ValueError("baidu_request_failed") from None


async def request(ctx, method, route, params, *, data=None, json_body=None):
    async def consume(response):
        return decode(await response.read(), response.status_code)

    return await ctx.http("api").request(method, route, params=params, data=data,
                                         json=json_body, consume=consume)


def integer(value, *, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise ValueError("baidu_response_invalid")
    return value


def flag(value):
    if type(value) not in (bool, int) or value not in (0, 1):
        raise ValueError("baidu_response_invalid")
    return bool(value)


def file_record(value):
    if type(value) is not dict:
        raise ValueError("baidu_response_invalid")
    identifier = value.get("fs_id", value.get("fsid"))
    if type(identifier) not in (int, str):
        raise ValueError("baidu_response_invalid")
    fields = {"fs_id": str(identifier), "name": value.get("server_filename",
                                                          value.get("filename"))}
    for source, target in (("path", "path"), ("parent_path", "parent_path"), ("size", "size_bytes"),
                           ("category", "category"), ("server_mtime", "modified_at"),
                           ("server_ctime", "created_at"), ("md5", "md5"),
                           ("content", "content"), ("ocr", "ocr")):
        if value.get(source) is not None and not (source == "md5" and value[source] == ""):
            fields[target] = value[source]
    if "isdir" in value:
        fields["is_directory"] = flag(value["isdir"])
    return m.FileRecord.model_validate(fields)


def files(value):
    if type(value) is not list or len(value) > 1000:
        raise ValueError("baidu_response_invalid")
    return [file_record(item) for item in value]


async def list_files(ctx, params):
    data = await request(ctx, "GET", "rest/2.0/xpan/file", {
        "method": "list", "dir": params.path, "start": str(params.start),
        "limit": str(params.limit), "order": "name", "desc": "0"})
    items = files(data.get("list"))
    if len(items) > params.limit:
        raise ValueError("baidu_response_invalid")
    return m.ListResult(files=items, start=params.start, limit=params.limit,
                        next_start=params.start + len(items), has_more=len(items) == params.limit)


async def search_files(ctx, params):
    data = await request(ctx, "GET", "rest/2.0/xpan/file", {
        "method": "search", "key": params.query, "dir": params.path,
        "page": str(params.page), "num": str(params.limit), "recursion": "1"})
    items = files(data.get("list"))
    if len(items) > params.limit:
        raise ValueError("baidu_response_invalid")
    more = flag(data["has_more"]) if "has_more" in data else None
    return m.SearchResult(files=items, page=params.page, limit=params.limit, has_more=more)


async def quota(ctx):
    data = await request(ctx, "GET", "api/quota", {"checkfree": "1", "checkexpire": "1"})
    return m.Quota(total_bytes=integer(data.get("total")), used_bytes=integer(data.get("used")),
                   free_bytes=integer(data.get("free")),
                   expires_within_seven_days=flag(data["expire"]) if "expire" in data else None)


async def semantic(ctx, params):
    user = await request(ctx, "GET", "rest/2.0/xpan/nas", {"method": "uinfo"})
    uk = integer(user.get("uk"), positive=True)
    query = {"query": params.query, "scene": "mcpserver",
             "dirs": json.dumps([{"uk": uk, "path": params.path}], ensure_ascii=False),
             "num": str(params.limit), "stream": "0", "search_type": "1"}
    if params.category is not None:
        query["category"] = json.dumps([params.category])
    data = await request(ctx, "POST", "xpan/unisearch", query, json_body={})
    groups = data.get("data")
    if type(groups) is not list or len(groups) > 100:
        raise ValueError("baidu_response_invalid")
    items = []
    for group in groups:
        if type(group) is not dict:
            raise ValueError("baidu_response_invalid")
        items.extend(files(group.get("list")))
        if len(items) > 1000:
            raise ValueError("baidu_response_invalid")
    more = not flag(data["is_end"]) if "is_end" in data else None
    return m.SemanticResult(files=items, limit=params.limit, has_more=more)


async def metadata(ctx, fs_id, *, download=False):
    data = await request(ctx, "GET", "rest/2.0/xpan/multimedia", {
        "method": "filemetas", "fsids": json.dumps([int(fs_id)]),
        "dlink": "1" if download else "0"})
    items = data.get("list")
    if type(items) is not list or len(items) != 1:
        raise ValueError("baidu_response_invalid")
    record = file_record(items[0])
    if record.fs_id != fs_id:
        raise ValueError("baidu_response_invalid")
    return record, items[0].get("dlink") if download else None


async def folder(ctx, params):
    data = await request(ctx, "POST", "rest/2.0/xpan/file", {"method": "create"}, data={
        "path": params.path, "isdir": "1", "rtype": "1" if params.rename_on_conflict else "0"})
    result_path = m.path(data["path"])
    if result_path == "/" or (not params.rename_on_conflict and result_path != params.path):
        raise ValueError("baidu_response_invalid")
    record = file_record(data | {"server_filename": result_path.rsplit("/", 1)[1]})
    if record.is_directory is not True:
        raise ValueError("baidu_response_invalid")
    return m.FileResult(file=record)


async def manage(ctx, operation, params):
    if operation in ("copy", "move"):
        items = [{"path": params.source_path, "dest": params.destination_directory,
                  "newname": params.new_name}]
        ondup = params.conflict_policy
    elif operation == "rename":
        items, ondup = [{"path": params.path, "newname": params.new_name}], "fail"
    else:
        items, ondup = [params.path], "fail"
    data = await request(ctx, "POST", "rest/2.0/xpan/file", {
        "method": "filemanager", "opera": operation}, data={
        "async": "0", "ondup": ondup, "filelist": json.dumps(items, ensure_ascii=False)})
    info = data.get("info", [])
    if type(info) is not list or len(info) > 1:
        raise ValueError("baidu_response_invalid")
    results = []
    for item in info:
        if (type(item) is not dict or type(item.get("errno", 0)) not in (int, str)
                or item.get("errno", 0) not in (0, "0")):
            raise ValueError("baidu_filemanager_failed")
        item_path = item.get("path")
        results.append(m.ManagedItem(path=m.path(item_path) if item_path is not None else None))
    task = data.get("taskid")
    if task is not None and (type(task) not in (str, int) or not str(task)):
        raise ValueError("baidu_response_invalid")
    return m.Managed(operation=operation, items=results,
                     task_id=str(task) if task not in (None, 0, "0") else None)
