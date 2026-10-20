"""Generated from reviewed contracts; regenerate with tools/generate.py."""

from typing import Literal

from connector_sdk import operation
from pydantic import Field

from .mcp import call
from .models import Input, Result


class ManageCreateFileInputLinkNode(Input):
    link_description: str = Field(default=None, description="链接描述", max_length=100000)
    link_url: str = Field(default=None, description="链接地址", max_length=100000)


class ManageCreateFileInput(Input):
    file_type: Literal[
        "doc",
        "sheet",
        "slide",
        "form",
        "mind",
        "flowchart",
        "smartsheet",
        "smartcanvas",
        "folder",
        "wikilink",
    ] = Field(
        description="文件类型，个人首页支持:doc-在线文档，sheet-在线表格，form-收集表，slide-幻灯片，mind-思维导图，flowchart-流程图，smartsheet-智能表格, smartcanvas-智能文档，folder-文件夹。空间内创建文件 支持所有类型，其中wikilink-空间链接"
    )
    link_node: ManageCreateFileInputLinkNode = Field(
        default=None,
        description="空间链接节点配置信息。仅当传入 space_id 且 file_type=wikilink 时必填，且 link_url 不能为空；个人首页不支持 wikilink",
    )
    parent_id: str = Field(
        default=None,
        description="父节点ID。不传space_id时表示个人文件夹唯一标识；传入space_id时表示空间父节点ID；parent_id为空则在个人首页或空间的根路径创建",
        max_length=100000,
    )
    space_id: str = Field(
        default=None,
        description="知识库空间ID，传入时在空间中创建节点，不传时在个人首页中创建文件",
        max_length=100000,
    )
    title: str = Field(description="文件标题,长度不超过36字符", max_length=100000)


class ManageFolderListInput(Input):
    folder_id: str = Field(
        default=None, description="文件夹ID，默认为空，表示查询根目录下的文件", max_length=100000
    )
    start: int = Field(default=None, description="查询记录的起始位置，默认为0")


class ManageQueryFolderMetaInput(Input):
    folder_id: str = Field(description="文件夹ID", max_length=100000)


class ManageQueryFileInfoInput(Input):
    file_id: str = Field(description="文档ID", max_length=100000)


class ManageCopyFileInput(Input):
    file_id: str = Field(description="文档ID", max_length=100000)
    folder_id: str = Field(
        default=None,
        description="新文档所在目录的唯一标识，默认为当前文件所在的文件夹",
        max_length=100000,
    )
    title: str = Field(
        default=None, description="新文档标题，新文档标题长度不能超过36个字符", max_length=100000
    )


class ManageMoveFileInput(Input):
    file_id: str = Field(description="文件ID", max_length=100000)
    target_folder_id: str = Field(
        description='移动的目标文件夹唯一标识，必须显式传入；传 "/" 表示首页根目录，空值会被拒绝',
        max_length=100000,
    )


class ManageRenameFileTitleInput(Input):
    file_id: str = Field(description="文档ID", max_length=100000)
    title: str = Field(description="新文档标题，长度不能超过36个字符", max_length=100000)


class ManageDeleteFileInput(Input):
    delete_type: Literal["origin", "recent"] = Field(
        default=None,
        description="仅对首页文件有效，首页文件所属的列表类型:origin-源文件，recent-浏览记录，默认值是origin",
    )
    file_id: str = Field(description="文件ID", max_length=100000)
    remove_type: Literal["current", "all"] = Field(
        default=None,
        description="仅对空间节点有效, 空间节点删除类型：current（默认）仅删除当前节点，子节点自动挂载到上级节点；all 删除当前节点及其所有子节点，【谨慎使用，会递归删除所有子节点】",
    )


class ManageGetPrivilegeInput(Input):
    file_id: str = Field(description="文档ID 或 空间ID", max_length=100000)


class ManageSetPrivilegeInput(Input):
    file_id: str = Field(description="文档ID 或 空间ID", max_length=100000)
    policy: int = Field(description="权限策略，2-所有人可读，3-所有人可编辑")


class ManageMoveFileToSpaceInput(Input):
    file_id: str = Field(description="文件ID", max_length=100000)
    space_id: str = Field(description="移动的目标空间唯一标识", max_length=100000)
    target_parent_id: str = Field(
        default=None,
        description="移动的目标空间节点唯一标识，默认代表为空间根目录",
        max_length=100000,
    )


class ManageImportProgressInput(Input):
    task_id: str = Field(description="导入任务ID", max_length=100000)


class ManageAsyncImportInput(Input):
    file_key: str = Field(
        description="文件唯一标识，不能为空；应使用 manage.pre_import 返回的 file_key",
        max_length=100000,
    )
    file_md5: str = Field(
        description="文件 MD5 标识，不能为空；当前 MCP 层不校验格式，也不校验其是否与 pre_import 时的 file_md5 一致",
        max_length=100000,
    )
    file_name: str = Field(
        description="文件名称（含后缀），需与pre_import时传入的file_name一致", max_length=100000
    )
    file_size: int = Field(description="文件大小，单位为字节(bytes)，如36752")
    task_id: str = Field(
        description="导入任务 ID；应使用 manage.pre_import 返回的 task_id", max_length=100000
    )


class ManagePreImportInput(Input):
    file_md5: str = Field(
        description="文件的MD5哈希值，hex编码的32位小写字符串，如'd41d8cd98f00b204e9800998ecf8427e'",
        max_length=100000,
    )
    file_name: str = Field(
        description="文件名称（含后缀），不能为空且必须包含文件扩展名", max_length=100000
    )
    file_size: int = Field(description="文件大小，单位为字节（bytes），必须大于 0，例如 36752")


class ManageExportProgressInput(Input):
    task_id: str = Field(description="导出任务ID", max_length=100000)


class ManageExportFileInput(Input):
    file_id: str = Field(description="文档ID", max_length=100000)


class ManageOperations:
    @operation(
        name="manage_create_file",
        description="创建在线腾讯文档文件，支持创建doc、sheet、智能文档、收集表、幻灯片、思维导图、流程图、智能表格、文件夹、链接。space_id不为空，在知识库空间中创建节点（文件夹、在线文档或链接）; space_id为空 则在个人首页中创建在线文档、文件夹",
        effects="write",
    )
    async def manage_create_file(self, ctx, params: ManageCreateFileInput) -> Result:
        return await call(
            ctx,
            "manage.create_file",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_folder_list", description="拉取指定目录下的文件与文件夹列表", effects="read"
    )
    async def manage_folder_list(self, ctx, params: ManageFolderListInput) -> Result:
        return await call(
            ctx,
            "manage.folder_list",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_query_folder_meta",
        description="查询指定文件夹的meta信息，支持根据folderID查询",
        effects="read",
    )
    async def manage_query_folder_meta(self, ctx, params: ManageQueryFolderMetaInput) -> Result:
        return await call(
            ctx,
            "manage.query_folder_meta",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_query_file_info",
        description="查询在线腾讯文档基础信息，支持查询文档状态、文档创建人、创建时间、最后修改人、最后修改时间、文档owner、是否为文件夹、是否为空间相关文件等信息",
        effects="read",
    )
    async def manage_query_file_info(self, ctx, params: ManageQueryFileInfoInput) -> Result:
        return await call(
            ctx,
            "manage.query_file_info",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_copy_file",
        description="生成副本，支持为指定文档生成一个副本文档，副本文档的权限为仅我可查看",
        effects="write",
    )
    async def manage_copy_file(self, ctx, params: ManageCopyFileInput) -> Result:
        return await call(
            ctx,
            "manage.copy_file",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_move_file",
        description="移动文件到首页文件夹，支持将文档移动到指定的文件夹下",
        effects="write",
    )
    async def manage_move_file(self, ctx, params: ManageMoveFileInput) -> Result:
        return await call(
            ctx,
            "manage.move_file",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_rename_file_title",
        description="重命名文档标题，新文档标题长度不能超过36个字符",
        effects="write",
    )
    async def manage_rename_file_title(self, ctx, params: ManageRenameFileTitleInput) -> Result:
        return await call(
            ctx,
            "manage.rename_file_title",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_delete_file",
        description="删除首页列表文件到回收站以及删除空间内的节点文件",
        effects="write",
    )
    async def manage_delete_file(self, ctx, params: ManageDeleteFileInput) -> Result:
        return await call(
            ctx,
            "manage.delete_file",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_get_privilege",
        description="根据文件id或空间id查询文件或空间的权限，policy=0表示私密文档,policy=1表示部分成员可见, policy=2表示所有人可读，policy=3表示所有人可编辑",
        effects="read",
    )
    async def manage_get_privilege(self, ctx, params: ManageGetPrivilegeInput) -> Result:
        return await call(
            ctx,
            "manage.get_privilege",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_set_privilege",
        description="根据文件id或空间id设置文件或空间的权限，仅支持设置全员可查看和全员可编辑，policy=2表示所有人可读，policy=3表示所有人可编辑",
        effects="write",
    )
    async def manage_set_privilege(self, ctx, params: ManageSetPrivilegeInput) -> Result:
        return await call(
            ctx,
            "manage.set_privilege",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_move_file_to_space",
        description="移动文件到空间内，支持将文件移动到指定的节点下",
        effects="write",
    )
    async def manage_move_file_to_space(self, ctx, params: ManageMoveFileToSpaceInput) -> Result:
        return await call(
            ctx,
            "manage.move_file_to_space",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_import_progress",
        description="查询导入进度，根据导入任务task_id查询任务进度。每隔5秒轮询一次，当progress=100时表示导入完成，此时返回file_id和file_url",
        effects="read",
    )
    async def manage_import_progress(self, ctx, params: ManageImportProgressInput) -> Result:
        return await call(
            ctx,
            "manage.import_progress",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_async_import",
        description="异步导入文档，传入file_size、task_id、file_key、file_name、file_md5触发异步导入，返回task_id。前置条件：需先调用manage.pre_import获取upload_url和file_key以及task_id，并将文件上传到upload_url后再调用此接口。调用后返回task_id，必须配合manage.import_progress工具轮询查询进度（建议间隔5秒），直到progress=100表示导入完成。",
        effects="write",
    )
    async def manage_async_import(self, ctx, params: ManageAsyncImportInput) -> Result:
        return await call(
            ctx,
            "manage.async_import",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_pre_import",
        description="预导入文档，传入文件名称、文件大小和MD5值，返回COS上传链接和file_key以及task_id。使用流程：1.调用manage.pre_import获取upload_url和file_key以及task_id 2.使用curl将文件PUT上传到upload_url 3.调用manage.async_import传入file_size、task_id、file_key、file_name、file_md5触发导入 4.配合manage.import_progress轮询导入进度。",
        effects="write",
    )
    async def manage_pre_import(self, ctx, params: ManagePreImportInput) -> Result:
        return await call(
            ctx,
            "manage.pre_import",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_export_progress",
        description="查询导出进度，根据导出任务task_id查询任务进度。每隔3-5秒轮询一次，当progress=100时表示导出完成，此时返回file_url（带签名的临时下载链接，有效期约30分钟）",
        effects="read",
    )
    async def manage_export_progress(self, ctx, params: ManageExportProgressInput) -> Result:
        return await call(
            ctx,
            "manage.export_progress",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="manage_export_file",
        description="导出文档，支持根据文档ID将文档导出到本地，然后返回导出任务ID。需配合manage.export_progress工具轮询查询导出进度（建议间隔5秒），导出完成后获取file_url下载链接",
        effects="write",
    )
    async def manage_export_file(self, ctx, params: ManageExportFileInput) -> Result:
        return await call(
            ctx,
            "manage.export_file",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )
