"""Generated from reviewed contracts; regenerate with tools/generate.py."""

from typing import Literal

from connector_sdk import operation
from pydantic import Field

from .mcp import call
from .models import Input, Result


class CreateSpaceInput(Input):
    description: str = Field(default=None, description="空间的简短描述", max_length=100000)
    title: str = Field(description="空间名称", max_length=100000)


class CreateSpaceNodeInputLinkNode(Input):
    link_description: str = Field(default=None, description="链接描述", max_length=100000)
    link_url: str = Field(default=None, description="链接地址", max_length=100000)
    title: str = Field(default=None, description="链接标题", max_length=100000)


class CreateSpaceNodeInputWikiFolderNode(Input):
    title: str = Field(default=None, description="文件夹名", max_length=100000)


class CreateSpaceNodeInputWikiTdocNode(Input):
    doc_type: str = Field(
        default=None,
        description="在线文档类型：word是文字处理格式，excel是电子表格，form是收集表，slide是幻灯片，smartcanvas是文档，smartsheet是智能表格，mind是思维导图，flowchart是流程图",
        max_length=100000,
    )
    title: str = Field(default=None, description="文档标题", max_length=100000)


class CreateSpaceNodeInput(Input):
    is_before: bool = Field(
        default=None, description="插入位置：true表示插入到父节点子列表的开头，false表示插入到末尾"
    )
    link_node: CreateSpaceNodeInputLinkNode = Field(
        default=None, description="链接节点配置信息，node_type为link时必填"
    )
    node_type: Literal["wiki_folder", "wiki_tdoc", "link"] = Field(
        description="节点类型：wiki_folder(文件夹)、wiki_tdoc(在线文档)、link(链接)"
    )
    parent_node_id: str = Field(
        default=None, description="父节点ID，为空或在根目录创建时可不传", max_length=100000
    )
    space_id: str = Field(description="空间id", max_length=100000)
    title: str = Field(description="节点标题，即文档或文件夹的显示名称", max_length=100000)
    wiki_folder_node: CreateSpaceNodeInputWikiFolderNode = Field(
        default=None, description="文件夹节点配置信息，node_type为wiki_folder时必填"
    )
    wiki_tdoc_node: CreateSpaceNodeInputWikiTdocNode = Field(
        default=None, description="在线文档节点配置信息，node_type为wiki_tdoc时必填"
    )


class DeleteSpaceNodeInput(Input):
    node_id: str = Field(description="要删除的节点ID", max_length=100000)
    remove_type: Literal["current", "all"] = Field(
        default=None,
        description="删除类型：current（默认）仅删除当前节点，子节点自动挂载到上级节点；all 删除当前节点及其所有子节点，【谨慎使用，会递归删除所有子节点】",
    )
    space_id: str = Field(description="空间ID", max_length=100000)


class GetUserInfoInput(Input):
    pass


class CreateMindByMarkdownInput(Input):
    markdown: str = Field(
        description='内容必须是 UTF-8 格式的 Markdown 文本，特殊字符不需要转义，用于根据Markdown生成层次化的思维导图结构。参数名必须为 "markdown"，不要使用 content、text、body 等其他名称',
        max_length=100000,
    )
    parent_id: str = Field(
        default=None,
        description="父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建",
        max_length=100000,
    )
    title: str = Field(
        description='思维导图标题，用于标识创建的思维导图名称。参数名必须为 "title"，不要使用 doc_title、name、file_name 等其他名称',
        max_length=100000,
    )


class CreateFlowchartByMermaidInput(Input):
    mermaid: str = Field(
        description='内容必须是不包含中文的 UTF-8 格式的 mermaid 文本，特殊字符不需要转义，用于根据Mermaid生成流程图结构和连接关系。参数名必须为 "mermaid"，不要使用 content、text、code、body 等其他名称',
        max_length=100000,
    )
    parent_id: str = Field(
        default=None,
        description="父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建",
        max_length=100000,
    )
    title: str = Field(
        description='流程图标题，用于标识创建的流程图名称。参数名必须为 "title"，不要使用 doc_title、name、file_name 等其他名称',
        max_length=100000,
    )


class SmartcanvasEditInput(Input):
    action: str = Field(
        description="操作类型：INSERT_BEFORE（在指定元素前插入）、INSERT_AFTER（在指定元素后插入）、DELETE（删除指定元素）、UPDATE（修改指定元素）",
        max_length=100000,
    )
    content: str = Field(
        default=None,
        description="MDX格式的内容。INSERT_BEFORE/INSERT_AFTER/UPDATE时必填，为要插入或替换的内容；DELETE时不需要填写。内容必须严格符合mdx_references规范",
        max_length=100000,
    )
    file_id: str = Field(description="智能文档的唯一标识符", max_length=100000)
    id: str = Field(
        default=None,
        description="锚点Block ID，即目标元素的唯一标识。INSERT_BEFORE/INSERT_AFTER时为插入位置的参考元素ID（为空则追加到文档末尾）；DELETE/UPDATE时为要操作的元素ID（必填）",
        max_length=100000,
    )


class SmartcanvasReadInput(Input):
    file_id: str = Field(description="智能文档的唯一标识符", max_length=100000)
    next_token: str = Field(
        default=None,
        description="分页游标，首次请求为空，后续请求传入上次返回的next_token",
        max_length=100000,
    )
    page_id: str = Field(
        default=None,
        description="要读取的页面ID，为空时自动获取文档的第一个页面",
        max_length=100000,
    )
    size: int = Field(
        default=None,
        description="每页返回的子节点数量；size 小于等于 0 或大于 20 时，服务端统一按 20 处理",
    )


class SmartcanvasFindInput(Input):
    file_id: str = Field(description="智能文档的唯一标识符", max_length=100000)
    query: str = Field(
        description="搜索文本，系统将在文档所有页面中搜索包含该文本的Block，返回匹配Block的ID和MDX内容",
        max_length=100000,
    )


class SmartcanvasGetTopLevelPagesInput(Input):
    file_id: str = Field(description="智能文档的唯一标识符", max_length=100000)


class CreateSlideInput(Input):
    description: str = Field(
        description="用户的原始输入文本，逐字复制，禁止Agent添加、改写、扩写或润色任何内容",
        max_length=100000,
    )
    reference_context: str = Field(
        default=None,
        description="用户主动提供或上传的参考材料原文，UTF-8文本。用户未提供材料时禁止传此参数，禁止Agent搜索或生成资料填充",
        max_length=100000,
    )
    session_id: str = Field(
        default=None,
        description="会话ID，用于多轮对话编辑PPT，在多轮编辑中长期有效。首次创建时不传，后续编辑时传入上一次create_slide返回的session_id，即可对同一份PPT进行修改。注意：session_id不受单次轮询20分钟超时的限制，Agent不要提示用户session_id可能过期",
        max_length=100000,
    )


class UploadImageInput(Input):
    file_name: str = Field(
        description="图片文件名，用于识别图片类型，例如：image.png、photo.jpg，支持 .png/.jpg/.jpeg/.gif/.bmp/.webp/.svg 后缀",
        max_length=100000,
    )
    image_base64: str = Field(
        description="图片的 base64 编码内容，支持 PNG、JPG、GIF、BMP、WEBP 等常见格式，图片大小不超过 10MB。注意：此处必须传入图片文件的实际 base64 编码数据（如 iVBORw0KGgo...），不要传入文件路径（如 /path/to/image.png）或 URL 地址",
        max_length=100000,
    )


class AicanvasReadPageSourceInput(Input):
    end_line: int = Field(
        default=None,
        description="读取的结束行号（含），默认start_line+499（即一次最多500行）；传-1表示读到文件末尾（完整源码）；超过总行数按总行数处理",
    )
    file_id: str = Field(
        description="已有Page的file_id（从Page在线链接解析，或首次生成时manage.import_progress返回的file_id）",
        max_length=100000,
    )
    start_line: int = Field(
        default=None, description="读取的起始行号，从1开始，默认1；小于1按1处理"
    )


class OcrTowordInputImagesItem(Input):
    image_base64: str = Field(
        default=None,
        description="图片的 base64 编码字符串（仅在图片无公网 URL 时使用）。必须是纯 base64 数据，不接受 URL；单张大小不超过 10MB。与 image_url 二选一，不能同时填写",
        max_length=100000,
    )
    image_url: str = Field(
        default=None,
        description="图片的公网 http(s) URL（首选）。URL 必须可被后端直接下载，不支持内网地址、需要鉴权的地址、已过期的临时签名地址。与 image_base64 二选一，不能同时填写",
        max_length=100000,
    )


class OcrTowordInput(Input):
    images: list[OcrTowordInputImagesItem] = Field(
        description="图片输入数组，支持 1-9 张图片，每张必须通过 image_url 或 image_base64 二选一提供。单张不超过 10MB，总大小不超过 50MB",
        max_length=100,
    )
    title: str = Field(
        default=None,
        description="生成文档标题；不传或为空时，服务端按“图片转文档-<当前时间>”自动生成",
        max_length=100000,
    )


class ScrapeUrlInput(Input):
    content_type: Literal["smartcanvas"] = Field(
        default=None, description="期望返回的文档格式，目前仅支持文档（smartcanvas）"
    )
    url: str = Field(
        description="要剪藏的网页URL地址，支持http和https协议，包括视频链接（如B站视频）",
        max_length=100000,
    )


class ReportUnsupportedFeatureInput(Input):
    doc_type: str = Field(
        default=None,
        description="涉及的文档类型，如 doc、sheet、slide、smartcanvas、smartsheet、mind、flowchart 等，不涉及具体文档类型则留空",
        max_length=100000,
    )
    feature: str = Field(
        description="用户请求的功能描述，请用简短的动宾短语概括，如：'添加评论'、'设置文档密码'、'插入视频'、'实时协作编辑'",
        max_length=100000,
    )
    user_prompt: str = Field(
        default=None,
        description="用户的原始请求描述，尽量保留用户的原话，用于辅助分析真实意图",
        max_length=100000,
    )


class CheckSkillUpdateInput(Input):
    version: str = Field(default=None, description="当前版本", max_length=100000)


class AicanvasReimportPageInput(Input):
    file_id: str = Field(
        description="已有Page的file_id（首次生成时manage.import_progress返回的file_id，或从Page在线链接解析）",
        max_length=100000,
    )
    file_key: str = Field(
        description="新制品的文件唯一标识，由manage.pre_import返回，需已将重新打包的.aipage文件PUT上传到对应upload_url",
        max_length=100000,
    )
    file_name: str = Field(
        description="文件名称（含.aipage后缀），需与pre_import时传入的file_name一致",
        max_length=100000,
    )


class ScrapeProgressInput(Input):
    parent_id: str = Field(
        default=None,
        description="父节点ID，为空时在空间根目录创建，不为空时在指定节点下创建",
        max_length=100000,
    )
    task_id: str = Field(description="scrape_url返回的异步任务ID", max_length=100000)


class OcrExtractInput(Input):
    extract_type: Literal["basic", "accurate", "efficient"] = Field(
        default=None, description="文字提取类型，可选值：basic（默认）/accurate/efficient"
    )
    image_base64: str = Field(
        default=None,
        description="单张图片的 base64 编码字符串（仅在图片无公网 URL 时使用）。必须是纯 base64 数据，不接受 URL；单张大小不超过 10MB。与 image_url 二选一，不能同时填写",
        max_length=100000,
    )
    image_url: str = Field(
        default=None,
        description="图片的公网 http(s) URL（首选）。URL 必须可被后端直接下载，不支持内网地址、需要鉴权的地址、已过期的临时签名地址。与 image_base64 二选一，不能同时填写",
        max_length=100000,
    )
    with_positions: bool = Field(
        default=None,
        description="是否返回带坐标的文字识别结果(text_detections字段)，默认 false。仅在需要文字在图片中位置坐标时设置为 true",
    )


class AicanvasBindSmartsheetInput(Input):
    file_id: str = Field(
        description="AIPAGE 页面的唯一标识符（当前 Page 自身的 file_id）", max_length=100000
    )
    pad_id: str = Field(
        description="智能表文档的唯一标识符，一个 Page 只能绑定一个智能表文档（多个 Page 可绑定同一个智能表文档）",
        max_length=100000,
    )


class CreateSmartcanvasByMdxInput(Input):
    content_format: str = Field(
        default=None,
        description="内容格式。仅值为 markdown（不区分大小写）时按 Markdown 处理；其他任意值（包括空值、mdx 和非枚举值）均按 MDX 处理",
        max_length=100000,
    )
    mdx: str = Field(
        description="文档正文内容，不能为空。默认按 MDX 处理；content_format 为 markdown 时传标准 Markdown。图片可使用 upload_image 返回的 image_id，也支持 http/https 外链：服务端会下载并转存，单张外链图片最大 10MB",
        max_length=100000,
    )
    title: str = Field(
        description="文档标题，不能为空，最长 36 个字符（按 rune 计）。参数名必须为 title，不要使用 doc_title、name、file_name 等其他名称",
        max_length=100000,
    )


class OcrToexcelInputImagesItem(Input):
    image_base64: str = Field(
        default=None,
        description="图片的 base64 编码字符串（仅在图片无公网 URL 时使用）。必须是纯 base64 数据，不接受 URL；单张大小不超过 10MB。与 image_url 二选一，不能同时填写",
        max_length=100000,
    )
    image_url: str = Field(
        default=None,
        description="图片的公网 http(s) URL（首选）。URL 必须可被后端直接下载，不支持内网地址、需要鉴权的地址、已过期的临时签名地址。与 image_base64 二选一，不能同时填写",
        max_length=100000,
    )


class OcrToexcelInput(Input):
    images: list[OcrToexcelInputImagesItem] = Field(
        description="图片输入数组，支持 1-9 张图片，每张必须使用 image_url 或 image_base64 二选一。单张不超过 10MB，总大小不超过 50MB",
        max_length=100,
    )
    title: str = Field(
        default=None,
        description="生成表格标题；不传或为空时，服务端按“图片转表格-<当前时间>”自动生成",
        max_length=100000,
    )


class CommonOperations:
    @operation(
        name="create_space",
        description="创建空间，创建腾讯文档空间，创建个人空间，返回空间id",
        effects="write",
    )
    async def create_space(self, ctx, params: CreateSpaceInput) -> Result:
        return await call(
            ctx, "create_space", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="create_space_node",
        description="在空间树中创建新节点，支持创建文件夹、在线文档、链接等多种类型，可指定父节点和插入位置。",
        effects="write",
    )
    async def create_space_node(self, ctx, params: CreateSpaceNodeInput) -> Result:
        return await call(
            ctx,
            "create_space_node",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="delete_space_node",
        description="删除空间中的指定节点，仅删除当前节点，子节点自动挂载到上级节点",
        effects="write",
    )
    async def delete_space_node(self, ctx, params: DeleteSpaceNodeInput) -> Result:
        return await call(
            ctx,
            "delete_space_node",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="get_user_info",
        description="查询当前登录用户的个人信息，返回用户ID、昵称和头像链接",
        effects="read",
    )
    async def get_user_info(self, ctx, params: GetUserInfoInput) -> Result:
        return await call(
            ctx, "get_user_info", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="create_mind_by_markdown",
        description='通过Markdown格式创建在线思维导图，内容必须是 UTF-8 格式的 Markdown 文本，特殊字符不需要转义。支持标题层级和列表的嵌套结构，适用于构建层次化的知识图谱和思维组织场景。重要提示：请严格使用以下参数名："title"（思维导图标题）和 "markdown"（Markdown内容），不要使用 content、text、doc_title 等其他名称',
        effects="write",
    )
    async def create_mind_by_markdown(self, ctx, params: CreateMindByMarkdownInput) -> Result:
        return await call(
            ctx,
            "create_mind_by_markdown",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="create_flowchart_by_mermaid",
        description='通过Mermaid格式创建在线流程图，内容必须是不包含中文的 UTF-8 格式的 Mermaid 文本，特殊字符不需要转义。支持基于Mermaid生成流程图结构和连接关系。重要提示：请严格使用以下参数名："title"（流程图标题）和 "mermaid"（Mermaid内容），不要使用 content、text、doc_title、code 等其他名称',
        effects="write",
    )
    async def create_flowchart_by_mermaid(
        self, ctx, params: CreateFlowchartByMermaidInput
    ) -> Result:
        return await call(
            ctx,
            "create_flowchart_by_mermaid",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartcanvas_edit",
        description='编辑智能文档，支持4种操作类型（通过action参数指定）：\n\n【INSERT_BEFORE】在指定Block前插入内容。参数：file_id（必填）、action=INSERT_BEFORE、id（锚点Block ID，为空则追加到文档末尾）、content（MDX格式内容，必填）。\n【INSERT_AFTER】在指定Block后插入内容。参数：file_id（必填）、action=INSERT_AFTER、id（锚点Block ID，为空则追加到文档末尾）、content（MDX格式内容，必填）。\n【DELETE】删除指定Block。参数：file_id（必填）、action=DELETE、id（要删除的Block ID，必填）。\n【UPDATE】修改指定Block的内容。参数：file_id（必填）、action=UPDATE、id（要修改的Block ID，必填）、content（新的MDX格式内容，必填）。\n\n常见工作流：\n1. 在"XXX"后插入内容：先调用smartcanvas.find(query="XXX")获取锚点ID，再调用本工具INSERT_AFTER(id=锚点ID, content=内容)。\n2. 直接插入内容（不指定位置）：调用INSERT_AFTER(id为空, content=内容)，自动追加到文档末尾。\n3. 修改"XXX"为新内容：先调用smartcanvas.find(query="XXX")获取锚点ID，再调用UPDATE(id=锚点ID, content=新内容)。\n4. 删除"XXX"：先调用smartcanvas.find(query="XXX")获取锚点ID，再调用DELETE(id=锚点ID)。\n\n注意：以下旧工具已废弃，请使用本工具替代：smartcanvas.create_smartcanvas_element（请改用INSERT_BEFORE/INSERT_AFTER）、smartcanvas.delete_element（请改用DELETE）、smartcanvas.update_element（请改用UPDATE）、smartcanvas.append_insert_smartcanvas_by_markdown（请改用INSERT_AFTER，id为空）。',
        effects="write",
    )
    async def smartcanvas_edit(self, ctx, params: SmartcanvasEditInput) -> Result:
        return await call(
            ctx,
            "smartcanvas.edit",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartcanvas_read",
        description="获取智能文档指定页面的MDX格式内容，支持分页读取，用于阅读和理解文档全文。\n\n参数：file_id（必填，智能文档的唯一标识符）、page_id（可选，要读取的页面ID，为空时自动获取文档的第一个页面）、size（可选，每页返回的子节点数量，最大为20，为0或不传时默认为20）、next_token（可选，分页游标，首次请求为空，后续请求传入上次返回的next_token以获取下一页内容）。\n\n返回：content（页面内容的MDX格式文本）、next_token（分页游标，非空表示还有更多内容，客户端可传入此值继续拉取）。\n\n注意：本工具返回的是只读的MDX文本，如需编辑请配合smartcanvas.find和smartcanvas.edit使用。\n\n",
        effects="read",
    )
    async def smartcanvas_read(self, ctx, params: SmartcanvasReadInput) -> Result:
        return await call(
            ctx,
            "smartcanvas.read",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartcanvas_find",
        description="根据文本搜索智能文档中的Block，返回匹配Block的ID和MDX格式内容。搜索结果中的Block ID可作为锚点，用于smartcanvas.edit工具的INSERT_BEFORE/INSERT_AFTER/UPDATE/DELETE操作。\n\n参数：file_id（必填，智能文档的唯一标识符）、query（必填，搜索文本，系统将在文档所有页面中搜索包含该文本的Block）。\n\n返回：匹配的Block列表，每项包含id（Block唯一标识符/锚点ID）和content（Block的MDX格式内容）。\n\n典型使用场景：需要定位文档中某段内容的位置时，先用本工具搜索获取Block ID，再配合smartcanvas.edit进行精准编辑。\n\n注意：以下旧工具已废弃，请使用本工具替代：smartcanvas.get_element_info（请改用本工具搜索Block）。",
        effects="read",
    )
    async def smartcanvas_find(self, ctx, params: SmartcanvasFindInput) -> Result:
        return await call(
            ctx,
            "smartcanvas.find",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartcanvas_get_top_level_pages",
        description="查询文档的顶层页面列表，返回文档中所有顶级页面的基本信息，用于快速浏览文档结构",
        effects="read",
    )
    async def smartcanvas_get_top_level_pages(
        self, ctx, params: SmartcanvasGetTopLevelPagesInput
    ) -> Result:
        return await call(
            ctx,
            "smartcanvas.get_top_level_pages",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="create_slide",
        description="通过AI生成或编辑幻灯片（PPT）。后端内置独立AI，自动生成PPT内容和排版。\n\n## 核心规则（必须遵守）\n1. description = 用户原话。逐字复制用户输入，禁止添加、改写、扩写、润色任何文字\n2. reference_context = 仅用户主动提供的材料。用户未提供材料时禁止传此参数，禁止Agent搜索或生成资料\n\n## 使用方式\n- 首次生成：不传session_id\n- 多轮编辑：传入之前返回的session_id\n- 异步接口，使用generate_slide.js脚本完成创建和轮询：node generate_slide.js --description '用户原话' [--reference_context '用户提供的材料'] [--session_id '会话ID']",
        effects="write",
    )
    async def create_slide(self, ctx, params: CreateSlideInput) -> Result:
        return await call(
            ctx, "create_slide", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="upload_image",
        description="上传图片，将图片的 base64 编码上传至腾讯文档，返回有效期为一天的 imageID，可用于智能表格，智能文档等场景的图片字段。重要：image_base64 参数必须传入图片文件的实际 base64 编码数据，不要传入文件路径（如 /path/to/image.png）或 URL 地址",
        effects="write",
    )
    async def upload_image(self, ctx, params: UploadImageInput) -> Result:
        return await call(
            ctx, "upload_image", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="aicanvas_read_page_source",
        description="按行范围读取已有 Page 的入口 HTML 源码内容，用法类似读取本地文件。适用于用户上传 HTML 文件自动导入成的 Page：拿到在线链接对应的 file_id 后调用，即可取回当前 HTML 源码用于分析或改造。入口 HTML 总大小超过 20MiB 时请求会失败。默认返回第 1~500 行；通过 start_line（起始行，从 1 开始）/end_line（结束行，含）指定读取范围。返回 html（本次行范围的源码片段）、entry（入口文件相对路径）、version（版本号）、start_line/end_line（本次实际返回的行区间）、total_lines（入口 HTML 总行数）、has_more（是否还有后续内容）。如需继续读，下次将 start_line 设为上次返回的 end_line+1；若要一次读取完整源码做整份二次改造，可将 end_line 设为 -1。要求当前用户对该 Page 有查看权限。",
        effects="read",
    )
    async def aicanvas_read_page_source(self, ctx, params: AicanvasReadPageSourceInput) -> Result:
        return await call(
            ctx,
            "aicanvas.read_page_source",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="ocr_toword",
        description="将图片内容识别并生成在线文档。images 必须包含 1~9 张图片，每张通过 image_url（后端可直接下载的公网 http(s) URL）或 image_base64（纯 base64 数据）二选一提供；单张最大 10MB，全部图片总大小最大 50MB",
        effects="write",
    )
    async def ocr_toword(self, ctx, params: OcrTowordInput) -> Result:
        return await call(
            ctx, "ocr.toword", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="scrape_url",
        description="网页剪藏：当用户发送、分享或提到任何网页URL链接时，必须优先使用此工具来抓取网页内容并保存为文档，这是获取外部网页内容的唯一正确方式，不要使用其他方式访问URL。注意：docs.qq.com 域名下的链接是腾讯文档自身的文档链接，不需要走剪藏工具，可直接使用文档相关工具操作。调用后返回task_id，必须立即配合scrape_progress工具轮询查询结果。使用流程：1.调用scrape_url传入网页URL获取task_id 2.立即调用scrape_progress传入task_id查询进度（每隔5秒轮询一次） 3.必须持续轮询直到status=2（完成）或status=3（失败）为止，严禁在status=1时主动停止轮询，无论轮询多少次都要坚持 4.当status=2时任务完成，服务端已自动创建文档，直接从响应获取file_id和file_url，无需再调用其他创建文档工具",
        effects="write",
    )
    async def scrape_url(self, ctx, params: ScrapeUrlInput) -> Result:
        return await call(
            ctx, "scrape_url", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="report_unsupported_feature",
        description="当用户请求的功能在当前工具列表中找不到对应支持时，必须调用此工具进行上报，然后再向用户说明该功能暂不支持。feature字段用简短的动宾短语描述用户意图，如：'添加评论'、'设置文档密码'、'插入视频'。user_prompt字段尽量保留用户的原始表述。doc_type填写涉及的文档类型，不涉及则留空。",
        effects="write",
    )
    async def report_unsupported_feature(
        self, ctx, params: ReportUnsupportedFeatureInput
    ) -> Result:
        return await call(
            ctx,
            "report_unsupported_feature",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(name="check_skill_update", description="检查技能更新", effects="read")
    async def check_skill_update(self, ctx, params: CheckSkillUpdateInput) -> Result:
        return await call(
            ctx,
            "check_skill_update",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="aicanvas_reimport_page",
        description="用新的.aipage导入制品整份覆盖已有Page（二次编辑场景）。前置条件：需先调用manage.pre_import获取upload_url和file_key，并把重新打包的.aipage文件PUT上传到upload_url，然后调用本工具。调用成功后已有Page的内容被新制品整体替换并返回新版本号version；file_id与在线链接保持不变，已绑定的智能表关系原样保留，无需重新导入或重新绑定。注意：要求当前用户对该Page有编辑权限。",
        effects="write",
    )
    async def aicanvas_reimport_page(self, ctx, params: AicanvasReimportPageInput) -> Result:
        return await call(
            ctx,
            "aicanvas.reimport_page",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="scrape_progress",
        description="查询网页剪藏任务进度并自动创建文档，与 scrape_url 配合使用。传入 scrape_url 返回的 task_id，每隔 5 秒轮询。parent_id 为保留参数，当前 C 端不会透传，不能指定文档创建位置。状态说明：status=1 进行中，继续轮询；status=2 已完成，网页内容已自动保存为文档，响应包含 title、file_id 和 file_url；status=3 失败，停止轮询。status=2 时直接输出结果即可，无需再调用创建文档工具",
        effects="write",
    )
    async def scrape_progress(self, ctx, params: ScrapeProgressInput) -> Result:
        return await call(
            ctx,
            "scrape_progress",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="ocr_extract",
        description="识别单张图片中的文字内容。图片输入二选一：image_url（后端可直接下载的公网 http(s) URL）或 image_base64（纯 base64 数据，无 data URI 前缀）；单张图片最大 10MB。extract_type 仅支持 basic（默认）/accurate/efficient",
        effects="read",
    )
    async def ocr_extract(self, ctx, params: OcrExtractInput) -> Result:
        return await call(
            ctx, "ocr.extract", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="aicanvas_bind_smartsheet",
        description="将当前 Page 绑定到智能表文档，一个 Page 只能绑定一个智能表文档（多个 Page 可绑定同一个智能表文档）。绑定后 Page 才能读写该智能表数据。注意：要求当前用户同时是该 Page 与该智能表的创建人，只有查看/编辑权限的他人智能表不能绑定",
        effects="write",
    )
    async def aicanvas_bind_smartsheet(self, ctx, params: AicanvasBindSmartsheetInput) -> Result:
        return await call(
            ctx,
            "aicanvas.bind_smartsheet",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="create_smartcanvas_by_mdx",
        description="【创建文档的首选工具】创建排版丰富的在线智能文档。\n\n【格式选择】通过content_format参数指定内容格式：\n- mdx（默认，强烈推荐）：支持分栏布局ColumnList、高亮块Callout、待办列表Todo、表格Table、带样式文本Mark等丰富排版组件，适用于需要复杂排版和视觉效果的场景。内容必须严格遵循mdx_references规范，生成后须对照规范逐条自校验，确保合规后再提交。\n- markdown：仅当用户明确要求时使用，mdx字段传入标准Markdown格式内容即可。\n\n【图片约束（两种格式通用）】所有图片禁止直接使用http/https外链，必须先调用upload_image工具上传获取image_id，再填入对应位置：\n- MDX格式：封面图 cover: image_id值，正文图片 <Image src='image_id值' alt='描述' />\n- Markdown格式：![描述](image_id值)\n如果图片过大导致上传失败，必须先本地压缩图片再重新上传，严禁回退使用URL。",
        effects="write",
    )
    async def create_smartcanvas_by_mdx(self, ctx, params: CreateSmartcanvasByMdxInput) -> Result:
        return await call(
            ctx,
            "create_smartcanvas_by_mdx",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="ocr_toexcel",
        description="将图片内容识别并生成在线表格。images 必须包含 1~9 张图片，每张通过 image_url（后端可直接下载的公网 http(s) URL）或 image_base64（纯 base64 数据）二选一提供；单张最大 10MB，全部图片总大小最大 50MB",
        effects="write",
    )
    async def ocr_toexcel(self, ctx, params: OcrToexcelInput) -> Result:
        return await call(
            ctx, "ocr.toexcel", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )
