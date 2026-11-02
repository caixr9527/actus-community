"""Twelve explicit operations; SDK owns platform authorization and file handoff."""

import asyncio

from connector_sdk import AppSpec, Connector, FileInput, FileOutput, HttpService, operation

from . import api
from . import models as m
from .auth import Auth
from .download import download
from .upload import upload


class App(Connector):
    spec = AppSpec(id="baidu-netdisk", name="百度网盘",
                   description="百度网盘 OAuth、文件查询管理和单文件上传下载")
    config_model = m.Settings
    auth = Auth()
    services = {"api": HttpService(api.ORIGIN, auth="connection")}

    async def startup(self):
        # One staged upload per application process bounds temporary disk use.
        self.upload_gate = asyncio.Semaphore(1)

    @operation(name="list_files", description="列出指定目录中的文件和文件夹。", effects="read")
    async def list_files(self, ctx, params: m.ListFiles) -> m.ListResult:
        return await api.list_files(ctx, params)

    @operation(name="search_files", description="按文件名搜索网盘文件。", effects="read")
    async def search_files(self, ctx, params: m.Search) -> m.SearchResult:
        return await api.search_files(ctx, params)

    @operation(name="get_quota", description="读取网盘总容量、已用和厂商返回的可用容量。",
               effects="read")
    async def get_quota(self, ctx, params: m.Empty) -> m.Quota:
        return await api.quota(ctx)

    @operation(name="semantic_search", description="使用自然语言检索网盘文件，需百度开通对应权限。",
               effects="read")
    async def semantic_search(self, ctx, params: m.Semantic) -> m.SemanticResult:
        return await api.semantic(ctx, params)

    @operation(name="get_file_metadata", description="按文件标识读取元数据，不返回下载链接。",
               effects="read")
    async def get_file_metadata(self, ctx, params: m.FileID) -> m.FileResult:
        record, _ = await api.metadata(ctx, params.fs_id)
        return m.FileResult(file=record)

    @operation(name="create_folder", description="创建文件夹，默认遇到同名冲突则失败。",
               effects="write")
    async def create_folder(self, ctx, params: m.CreateFolder) -> m.FileResult:
        return await api.folder(ctx, params)

    @operation(name="copy_file", description="复制文件或文件夹到指定目录。", effects="write")
    async def copy_file(self, ctx, params: m.CopyMove) -> m.Managed:
        return await api.manage(ctx, "copy", params)

    @operation(name="move_file", description="移动文件或文件夹到指定目录。", effects="write")
    async def move_file(self, ctx, params: m.CopyMove) -> m.Managed:
        return await api.manage(ctx, "move", params)

    @operation(name="rename_file", description="重命名文件或文件夹。", effects="write")
    async def rename_file(self, ctx, params: m.Rename) -> m.Managed:
        return await api.manage(ctx, "rename", params)

    @operation(name="delete_file", description="删除指定文件或文件夹，禁止删除根目录。",
               effects="write")
    async def delete_file(self, ctx, params: m.NonRoot) -> m.Managed:
        return await api.manage(ctx, "delete", params)

    @operation(name="upload_file", description="将一个平台文件上传到网盘目录，默认不覆盖同名文件。",
               effects="write", transport="file_input", max_file_bytes=m.MAX_FILE_BYTES)
    async def upload_file(self, ctx, params: m.Upload, file: FileInput) -> m.Uploaded:
        return await upload(ctx, params, file, self.upload_gate)

    @operation(name="download_file", description="按文件标识下载一个网盘文件，交由平台保存。",
               effects="read", transport="file_output", max_file_bytes=m.MAX_FILE_BYTES)
    async def download_file(self, ctx, params: m.FileID) -> FileOutput:
        return await download(ctx, params.fs_id)
