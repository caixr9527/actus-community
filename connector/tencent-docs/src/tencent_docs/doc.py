"""Generated from reviewed contracts; regenerate with tools/generate.py."""

from connector_sdk import operation
from pydantic import Field

from .mcp import call
from .models import Input, Result


class DocInsertImageInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertImageInput(Input):
    content: str = Field(
        default=None,
        description="base64 编码后的图片内容，与 image_id 二选一；适合图片较小的场景",
        max_length=100000,
    )
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    height: int = Field(default=None, description="图片高度（像素）")
    idx: int = Field(description="插入的文档位置索引")
    image_id: str = Field(
        default=None,
        description="图片的 image_id，与 content 二选一；适合图片较大的场景",
        max_length=100000,
    )
    version_info: DocInsertImageInputVersionInfo = Field(default=None, description="版本参数")
    width: int = Field(default=None, description="图片宽度（像素）")


class DocInsertNormalLinkInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertNormalLinkInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_name: str = Field(default=None, description="文件名", max_length=100000)
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入位置索引")
    independent_render: bool = Field(default=None, description="是否独立渲染")
    layout_type: str = Field(default=None, description="布局类型", max_length=100000)
    link: str = Field(description="链接地址", max_length=100000)
    text: str = Field(default=None, description="显示文本", max_length=100000)
    version_info: DocInsertNormalLinkInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertFootnoteInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertFootnoteInput(Input):
    content: str = Field(description="脚注/尾注文本内容", max_length=100000)
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入位置索引")
    type: int = Field(default=None, description="类型：0=脚注，1=尾注")
    version_info: DocInsertFootnoteInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertRowsInputRowsItem(Input):
    insert_below: bool = Field(default=None, description="true=下方插入")
    row: int = Field(default=None, description="参考行号(0-based)")


class DocInsertRowsInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertRowsInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="表格内任意cell位置")
    rows: list[DocInsertRowsInputRowsItem] = Field(description="要插入的行列表", max_length=100)
    version_info: DocInsertRowsInputVersionInfo = Field(default=None, description="版本参数")


class DocUndoAiEditInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocUndoAiEditInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    target_version: int = Field(
        description="待反向的目标 revision 版本号；必须 > 0 且 <= 当前最新版本"
    )
    version_info: DocUndoAiEditInputVersionInfo = Field(
        default=None, description="版本参数（此处仅用于定位 latest 版本）"
    )


class DocInsertTextInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertTextInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入的文档位置索引")
    text: str = Field(
        description="要插入的文本内容。注意：如果需要插入换行，应该使用插入段落操作，而不是在文本里插入'\\n'符号",
        max_length=100000,
    )
    version_info: DocInsertTextInputVersionInfo = Field(default=None, description="版本参数")


class DocGetLastOperablePosInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocGetLastOperablePosInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    version_info: DocGetLastOperablePosInputVersionInfo = Field(
        default=None, description="版本参数"
    )


class DocInsertBorderInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertBorderInput(Input):
    border_type: str = Field(default=None, description="边框类型", max_length=100000)
    color: str = Field(default=None, description="边框颜色(hex)", max_length=100000)
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="段落位置索引")
    sz: int = Field(default=None, description="边框粗细(1/8磅)")
    version_info: DocInsertBorderInputVersionInfo = Field(default=None, description="版本参数")


class DocUpdateTextPropertyInputProperty(Input):
    background_color: str = Field(
        default=None, description="文字背景颜色，十六进制RRGGBB格式", max_length=100000
    )
    bold: bool = Field(default=None, description="是否加粗")
    color: str = Field(default=None, description="文字颜色，十六进制RRGGBB格式", max_length=100000)
    font_family: str = Field(default=None, description="字体族", max_length=100000)
    font_size: float = Field(default=None, description="字号，单位磅(pt)，例如12表示12pt")
    highlight: str = Field(
        default=None,
        description="高亮文本颜色(Highlight)，与底纹(background_color)不同。值如 yellow/cyan/none 等。传入none可清除高亮",
        max_length=100000,
    )
    italic: bool = Field(default=None, description="是否斜体")
    small_caps: bool = Field(default=None, description="是否小型大写字母")
    strikethrough: bool = Field(default=None, description="是否删除线")
    underline: bool = Field(default=None, description="是否下划线")
    vertical_align: str = Field(
        default=None,
        description="上下标：0=未指定(保持原有)，1=正常基线，2=上标，3=下标",
        max_length=100000,
    )


class DocUpdateTextPropertyInputRangesItem(Input):
    begin: int = Field(default=None, description="范围起始位置索引")
    end: int = Field(default=None, description="范围结束位置索引")


class DocUpdateTextPropertyInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocUpdateTextPropertyInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    property: DocUpdateTextPropertyInputProperty = Field(description="要更新的文本属性")
    ranges: list[DocUpdateTextPropertyInputRangesItem] = Field(
        description="要更新的文档范围列表", max_length=100
    )
    version_info: DocUpdateTextPropertyInputVersionInfo = Field(
        default=None, description="版本参数"
    )


class DocInsertTaskInputTasksItem(Input):
    content: str = Field(default=None, description="任务内容", max_length=100000)
    state: int = Field(default=None, description="任务状态：1=待办(TODO)，2=已完成(DONE)，不可为0")


class DocInsertTaskInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertTaskInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入的文档位置索引")
    tasks: list[DocInsertTaskInputTasksItem] = Field(description="任务信息列表", max_length=100)
    version_info: DocInsertTaskInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertTableInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertTableInput(Input):
    cols: int = Field(description="表格列数")
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入的文档位置索引")
    rows: int = Field(description="表格行数")
    version_info: DocInsertTableInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertNumberingInputPropertyInd(Input):
    end: float = Field(default=None, description="结束缩进")
    end_i: bool = Field(default=None)
    firstLine: float = Field(default=None, description="首行缩进")
    firstLine_i: bool = Field(default=None)
    start: float = Field(default=None, description="起始缩进")
    start_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyParagraphborderBetween(Input):
    color: str = Field(default=None, description="边框颜色(hex)", max_length=100000)
    color_i: bool = Field(default=None)
    space: int = Field(default=None, description="间距")
    space_i: bool = Field(default=None)
    sz: int = Field(default=None, description="边框粗细")
    sz_i: bool = Field(default=None)
    val: str = Field(default=None, description="边框样式", max_length=100000)
    val_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyParagraphborderBottom(Input):
    color: str = Field(default=None, description="边框颜色(hex)", max_length=100000)
    color_i: bool = Field(default=None)
    space: int = Field(default=None, description="间距")
    space_i: bool = Field(default=None)
    sz: int = Field(default=None, description="边框粗细")
    sz_i: bool = Field(default=None)
    val: str = Field(default=None, description="边框样式", max_length=100000)
    val_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyParagraphborderLeft(Input):
    color: str = Field(default=None, description="边框颜色(hex)", max_length=100000)
    color_i: bool = Field(default=None)
    space: int = Field(default=None, description="间距")
    space_i: bool = Field(default=None)
    sz: int = Field(default=None, description="边框粗细")
    sz_i: bool = Field(default=None)
    val: str = Field(default=None, description="边框样式", max_length=100000)
    val_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyParagraphborderRight(Input):
    color: str = Field(default=None, description="边框颜色(hex)", max_length=100000)
    color_i: bool = Field(default=None)
    space: int = Field(default=None, description="间距")
    space_i: bool = Field(default=None)
    sz: int = Field(default=None, description="边框粗细")
    sz_i: bool = Field(default=None)
    val: str = Field(default=None, description="边框样式", max_length=100000)
    val_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyParagraphborderTop(Input):
    color: str = Field(default=None, description="边框颜色(hex)", max_length=100000)
    color_i: bool = Field(default=None)
    space: int = Field(default=None, description="间距")
    space_i: bool = Field(default=None)
    sz: int = Field(default=None, description="边框粗细")
    sz_i: bool = Field(default=None)
    val: str = Field(default=None, description="边框样式", max_length=100000)
    val_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyParagraphborder(Input):
    between: DocInsertNumberingInputPropertyParagraphborderBetween = Field(default=None)
    between_i: bool = Field(default=None)
    bottom: DocInsertNumberingInputPropertyParagraphborderBottom = Field(default=None)
    bottom_i: bool = Field(default=None)
    left: DocInsertNumberingInputPropertyParagraphborderLeft = Field(default=None)
    left_i: bool = Field(default=None)
    right: DocInsertNumberingInputPropertyParagraphborderRight = Field(default=None)
    right_i: bool = Field(default=None)
    top: DocInsertNumberingInputPropertyParagraphborderTop = Field(default=None)
    top_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyShd(Input):
    color: str = Field(default=None, description="底纹颜色(hex)", max_length=100000)
    color_i: bool = Field(default=None)


class DocInsertNumberingInputPropertySpacing(Input):
    after: float = Field(default=None, description="段后间距")
    after_i: bool = Field(default=None)
    before: float = Field(default=None, description="段前间距")
    before_i: bool = Field(default=None)
    line: float = Field(default=None, description="行间距")
    line_i: bool = Field(default=None)
    line_rule: int = Field(default=None, description="行间距规则：1=auto, 2=exact, 3=atLeast")
    line_rule_i: bool = Field(default=None)
    spacing_unit: str = Field(
        default=None, description="间距单位：pt/in/cm/mm/line", max_length=100000
    )


class DocInsertNumberingInputPropertyTabsTabItem(Input):
    pos: float = Field(default=None)
    pos_i: bool = Field(default=None)
    val: str = Field(default=None, description="对齐方式", max_length=100000)
    val_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyTabsTabOp(Input):
    op_index: int = Field(default=None)
    op_type: str = Field(default=None, max_length=100000)


class DocInsertNumberingInputPropertyTabs(Input):
    tab: list[DocInsertNumberingInputPropertyTabsTabItem] = Field(default=None, max_length=100)
    tab_op: DocInsertNumberingInputPropertyTabsTabOp = Field(default=None)


class DocInsertNumberingInputPropertyTextalignment(Input):
    val: str = Field(default=None, max_length=100000)
    val_i: bool = Field(default=None)


class DocInsertNumberingInputPropertyTextdirection(Input):
    val: str = Field(default=None, max_length=100000)
    val_i: bool = Field(default=None)


class DocInsertNumberingInputProperty(Input):
    ind: DocInsertNumberingInputPropertyInd = Field(default=None)
    ind_i: bool = Field(default=None)
    jc: str = Field(default=None, description="段落对齐方式", max_length=100000)
    jc_i: bool = Field(default=None)
    keep_lines: bool = Field(default=None)
    keep_lines_i: bool = Field(default=None)
    keep_next: bool = Field(default=None)
    keep_next_i: bool = Field(default=None)
    pStyle: str = Field(default=None, description="段落样式名称", max_length=100000)
    pStyle_i: bool = Field(default=None)
    paragraphBorder: DocInsertNumberingInputPropertyParagraphborder = Field(default=None)
    paragraphBorder_i: bool = Field(default=None)
    shd: DocInsertNumberingInputPropertyShd = Field(default=None)
    shd_i: bool = Field(default=None)
    spacing: DocInsertNumberingInputPropertySpacing = Field(default=None)
    spacing_i: bool = Field(default=None)
    tabs: DocInsertNumberingInputPropertyTabs = Field(default=None)
    tabs_i: bool = Field(default=None)
    textAlignment: DocInsertNumberingInputPropertyTextalignment = Field(default=None)
    textAlignment_i: bool = Field(default=None)
    textDirection: DocInsertNumberingInputPropertyTextdirection = Field(default=None)
    textDirection_i: bool = Field(default=None)


class DocInsertNumberingInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertNumberingInput(Input):
    abstract_num_id: str = Field(default=None, description="模板id", max_length=100000)
    end_idx: int = Field(default=None, description="替换文本的结束位置")
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    numbering_lvl: str = Field(default=None, description="编号级别", max_length=100000)
    p_idx: int = Field(default=None, description="当前段落的结束位置")
    property: DocInsertNumberingInputProperty = Field(default=None, description="段落属性")
    start_idx: int = Field(default=None, description="替换文本的开始位置")
    type: str = Field(default=None, description="编号类别", max_length=100000)
    version_info: DocInsertNumberingInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertPageBreakInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertPageBreakInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入的文档位置索引")
    version_info: DocInsertPageBreakInputVersionInfo = Field(default=None, description="版本参数")


class DocReplaceImageInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocReplaceImageInput(Input):
    content: str = Field(
        default=None,
        description="base64 编码后的图片内容，与 image_id 二选一；适合图片较小的场景",
        max_length=100000,
    )
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="图片位置索引")
    image_id: str = Field(
        default=None,
        description="图片的 image_id，与 content 二选一；适合图片较大的场景",
        max_length=100000,
    )
    old_attachment_id: str = Field(default=None, description="旧附件图片ID", max_length=100000)
    old_image_url: str = Field(default=None, description="旧图片URL", max_length=100000)
    version_info: DocReplaceImageInputVersionInfo = Field(default=None, description="版本参数")


class DocGetOutlineInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocGetOutlineInput(Input):
    base_version: int = Field(default=None, description="已废弃，改用version_info.base_version")
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    latest: bool = Field(default=None, description="已废弃，改用version_info.is_latest")
    version_info: DocGetOutlineInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertFooterInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertFooterInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    footer_type: str = Field(
        default=None, description="页脚类型：default/first/even", max_length=100000
    )
    section_index: int = Field(default=None, description="节索引(0-based)")
    text: str = Field(description="页脚文本内容", max_length=100000)
    version_info: DocInsertFooterInputVersionInfo = Field(default=None, description="版本参数")


class DocReplaceTextInputRangesItem(Input):
    begin: int = Field(default=None, description="范围起始位置索引")
    end: int = Field(default=None, description="范围结束位置索引")


class DocReplaceTextInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocReplaceTextInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    ranges: list[DocReplaceTextInputRangesItem] = Field(
        description="要替换的文档范围列表", max_length=100
    )
    text: str = Field(description="替换后的新文本内容", max_length=100000)
    version_info: DocReplaceTextInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertHtmlContentInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertHtmlContentInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    html_text: str = Field(description="HTML内容", max_length=100000)
    idx: int = Field(description="插入位置索引")
    version_info: DocInsertHtmlContentInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertParagraphInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertParagraphInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入的文档位置索引")
    indent_count: int = Field(default=None, description="缩进数量")
    level: str = Field(default=None, description="标题级别", max_length=100000)
    numbering_lvl: str = Field(default=None, description="编号级别", max_length=100000)
    numbering_type: str = Field(default=None, description="编号类别", max_length=100000)
    version_info: DocInsertParagraphInputVersionInfo = Field(default=None, description="版本参数")


class DocResolveDocumentStructureInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocResolveDocumentStructureInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    has_idx: bool = Field(default=None, description="idx是否显式传入")
    has_text_preview_length: bool = Field(
        default=None, description="text_preview_length 是否显式传入（区分「未设置」与「设为0」）"
    )
    idx: int = Field(
        default=None, description="可选，传入字符位置索引，只返回包含该位置的块的结构信息"
    )
    include_highlights: bool = Field(
        default=None, description="是否返回 highlight_spans（mode==full 时无论此值都返回）"
    )
    include_table_cells: bool = Field(
        default=None, description="是否返回表格内单元格详情（mode==full 时无论此值都返回）"
    )
    include_textbox_children: bool = Field(
        default=None, description="是否返回文本框子节点（mode==full 时无论此值都返回）"
    )
    limit: int = Field(
        default=None, description="顶层节点数组分页条数；0=不限（has_idx==true 时忽略）；默认150"
    )
    mode: int = Field(
        default=None,
        description="详细程度模式：0=outline（只给标题出preview，骨架级）；1=compact（默认，每节点10字符preview + has_highlights/row_count×col_count/children_count/is_numbering等轻量信号位）；2=full（highlight_spans/table cells/numbering详情全部回填）",
    )
    offset: int = Field(default=None, description="顶层节点数组分页偏移（has_idx==true 时忽略）")
    text_preview_length: int = Field(
        default=None, description="text_preview 字符上限；0=不返回预览；负数或不传=使用 mode 默认值"
    )
    version_info: DocResolveDocumentStructureInputVersionInfo = Field(
        default=None, description="版本参数"
    )


class DocGetTableInfoInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocGetTableInfoInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="表格内任意GCP索引")
    version_info: DocGetTableInfoInputVersionInfo = Field(default=None, description="版本参数")


class DocSetTableLayoutInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocSetTableLayoutInput(Input):
    col_widths_dxa: list[int] = Field(default=None, description="每列列宽(dxa)", max_length=100)
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="表格内任意cell的GCP位置")
    mode: str = Field(description="布局模式：auto/manual", max_length=100000)
    row_heights_dxa: list[int] = Field(default=None, description="每行行高(dxa)", max_length=100)
    version_info: DocSetTableLayoutInputVersionInfo = Field(default=None, description="版本参数")


class DocSetPageNumberInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocSetPageNumberInput(Input):
    continue_from_prev: bool = Field(default=None, description="续前节")
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    format: str = Field(default=None, description="页码格式", max_length=100000)
    position: str = Field(
        default=None, description="页码位置：center/left/right", max_length=100000
    )
    scope: str = Field(default=None, description="应用范围", max_length=100000)
    section_index: int = Field(default=None, description="节索引")
    start: int = Field(default=None, description="起始编号")
    version_info: DocSetPageNumberInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertMarkdownInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertMarkdownInput(Input):
    base64_markdown: str = Field(
        default=None,
        description="base64 编码的 Markdown 内容，与 markdown 二选一；两者同时传入时 markdown 优先，仅当 markdown 为空时使用本字段",
        max_length=100000,
    )
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入位置索引")
    markdown: str = Field(
        default=None, description="Markdown格式内容，与base64_markdown二选一", max_length=100000
    )
    version_info: DocInsertMarkdownInputVersionInfo = Field(default=None, description="版本参数")


class DocModifyParagraphInputHighlightBlock(Input):
    bg_color: str = Field(
        default=None, description="背景颜色（十六进制），如 FEF8E4", max_length=100000
    )
    border_color: str = Field(
        default=None, description="边框颜色（十六进制），如 FBEBAE", max_length=100000
    )


class DocModifyParagraphInputRangesItem(Input):
    begin: int = Field(default=None, description="范围起始位置索引")
    end: int = Field(default=None, description="范围结束位置索引")


class DocModifyParagraphInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocModifyParagraphInput(Input):
    block_quote: bool = Field(default=None, description="设置引用")
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    first_line_indent: float = Field(
        default=None,
        description="首行缩进(磅pt)，传0或负值取消。与first_line_indent_chars二选一，chars优先",
    )
    first_line_indent_chars: int = Field(
        default=None,
        description="首行缩进(字符数)，传0或负值取消。与first_line_indent二选一，本参数优先",
    )
    has_block_quote: bool = Field(default=None, description="是否显式设置引用")
    has_first_line_indent: bool = Field(default=None, description="是否显式设置first_line_indent")
    has_first_line_indent_chars: bool = Field(
        default=None, description="是否显式设置first_line_indent_chars"
    )
    has_line_spacing: bool = Field(default=None, description="是否显式设置行间距")
    has_spacing_after: bool = Field(default=None, description="是否显式设置段后间距")
    has_spacing_before: bool = Field(default=None, description="是否显式设置段前间距")
    highlight_block: DocModifyParagraphInputHighlightBlock = Field(
        default=None, description="高亮块操作"
    )
    indent: str = Field(default=None, description="缩进操作：increase/decrease", max_length=100000)
    jc: str = Field(
        default=None, description="对齐方式：left/center/right/both/distribute", max_length=100000
    )
    line_spacing: float = Field(default=None, description="行间距数值")
    line_spacing_rule: int = Field(default=None, description="行间距规则：1=auto,2=exact,3=atLeast")
    numbering: str = Field(
        default=None, description="编号类型：bullet/decimal/task/none", max_length=100000
    )
    numbering_level: int = Field(default=None, description="编号级别(1-9)")
    p_style: str = Field(default=None, description="段落样式名称", max_length=100000)
    ranges: list[DocModifyParagraphInputRangesItem] = Field(
        description="段落范围列表", max_length=100
    )
    spacing_after: float = Field(default=None, description="段后间距(磅)")
    spacing_before: float = Field(default=None, description="段前间距(磅)")
    version_info: DocModifyParagraphInputVersionInfo = Field(default=None, description="版本参数")


class DocGetCommentsInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocGetCommentsInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    version_info: DocGetCommentsInputVersionInfo = Field(default=None, description="版本参数")


class DocGetTextPropertyInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocGetTextPropertyInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="要查询的字符位置(0-based)")
    version_info: DocGetTextPropertyInputVersionInfo = Field(default=None, description="版本参数")


class DocSetTablePropertiesInputBordersBottom(Input):
    color: str = Field(default=None, description="颜色(hex)", max_length=100000)
    space: int = Field(default=None, description="间距")
    sz: int = Field(default=None, description="粗细(1/8磅)")
    val: str = Field(default=None, description="边框样式", max_length=100000)


class DocSetTablePropertiesInputBordersInsideH(Input):
    color: str = Field(default=None, description="颜色(hex)", max_length=100000)
    space: int = Field(default=None, description="间距")
    sz: int = Field(default=None, description="粗细(1/8磅)")
    val: str = Field(default=None, description="边框样式", max_length=100000)


class DocSetTablePropertiesInputBordersInsideV(Input):
    color: str = Field(default=None, description="颜色(hex)", max_length=100000)
    space: int = Field(default=None, description="间距")
    sz: int = Field(default=None, description="粗细(1/8磅)")
    val: str = Field(default=None, description="边框样式", max_length=100000)


class DocSetTablePropertiesInputBordersLeft(Input):
    color: str = Field(default=None, description="颜色(hex)", max_length=100000)
    space: int = Field(default=None, description="间距")
    sz: int = Field(default=None, description="粗细(1/8磅)")
    val: str = Field(default=None, description="边框样式", max_length=100000)


class DocSetTablePropertiesInputBordersRight(Input):
    color: str = Field(default=None, description="颜色(hex)", max_length=100000)
    space: int = Field(default=None, description="间距")
    sz: int = Field(default=None, description="粗细(1/8磅)")
    val: str = Field(default=None, description="边框样式", max_length=100000)


class DocSetTablePropertiesInputBordersTop(Input):
    color: str = Field(default=None, description="颜色(hex)", max_length=100000)
    space: int = Field(default=None, description="间距")
    sz: int = Field(default=None, description="粗细(1/8磅)")
    val: str = Field(default=None, description="边框样式", max_length=100000)


class DocSetTablePropertiesInputBorders(Input):
    bottom: DocSetTablePropertiesInputBordersBottom = Field(default=None)
    inside_h: DocSetTablePropertiesInputBordersInsideH = Field(default=None)
    inside_v: DocSetTablePropertiesInputBordersInsideV = Field(default=None)
    left: DocSetTablePropertiesInputBordersLeft = Field(default=None)
    right: DocSetTablePropertiesInputBordersRight = Field(default=None)
    top: DocSetTablePropertiesInputBordersTop = Field(default=None)


class DocSetTablePropertiesInputCellFillsItem(Input):
    color: str = Field(default=None, description="颜色(hex)", max_length=100000)
    condition: str = Field(default=None, description="条件", max_length=100000)


class DocSetTablePropertiesInputCellMargin(Input):
    bottom: int = Field(default=None)
    left: int = Field(default=None)
    right: int = Field(default=None)
    top: int = Field(default=None)


class DocSetTablePropertiesInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocSetTablePropertiesInputWidth(Input):
    type: str = Field(default=None, description="宽度类型", max_length=100000)
    value: int = Field(default=None, description="宽度值")


class DocSetTablePropertiesInput(Input):
    alignment: str = Field(default=None, description="对齐方式", max_length=100000)
    borders: DocSetTablePropertiesInputBorders = Field(default=None, description="边框")
    cell_fills: list[DocSetTablePropertiesInputCellFillsItem] = Field(
        default=None, description="单元格填充", max_length=100
    )
    cell_margin: DocSetTablePropertiesInputCellMargin = Field(
        default=None, description="单元格内边距"
    )
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="表格内任意cell的GCP位置")
    version_info: DocSetTablePropertiesInputVersionInfo = Field(
        default=None, description="版本参数"
    )
    width: DocSetTablePropertiesInputWidth = Field(default=None, description="表格宽度")


class DocCompareDocumentsInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocCompareDocumentsInput(Input):
    compare_mode: str = Field(
        default=None, description="对比模式：content/format/all", max_length=100000
    )
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    other_file_id: str = Field(default=None, description="对比文档ID", max_length=100000)
    other_file_url: str = Field(default=None, description="对比文档URL", max_length=100000)
    version_info: DocCompareDocumentsInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertHeaderInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertHeaderInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    header_type: str = Field(
        default=None, description="页眉类型：default/first/even", max_length=100000
    )
    section_index: int = Field(default=None, description="节索引(0-based)")
    text: str = Field(description="页眉文本内容", max_length=100000)
    version_info: DocInsertHeaderInputVersionInfo = Field(default=None, description="版本参数")


class DocCopyFormatInputSourceRange(Input):
    begin: int = Field(default=None, description="起始位置(含)")
    end: int = Field(default=None, description="结束位置(不含)")


class DocCopyFormatInputTargetRangesItem(Input):
    begin: int = Field(default=None, description="起始位置(含)")
    end: int = Field(default=None, description="结束位置(不含)")


class DocCopyFormatInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocCopyFormatInput(Input):
    copy_paragraph_format: bool = Field(default=None, description="是否复制段落格式")
    copy_text_format: bool = Field(default=None, description="是否复制文本格式")
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    source_range: DocCopyFormatInputSourceRange = Field(description="格式来源范围")
    target_ranges: list[DocCopyFormatInputTargetRangesItem] = Field(
        description="目标范围列表", max_length=100
    )
    version_info: DocCopyFormatInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertColsInputColsItem(Input):
    col: int = Field(default=None, description="参考列号(0-based)")
    insert_right: bool = Field(default=None, description="true=右侧插入")


class DocInsertColsInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertColsInput(Input):
    cols: list[DocInsertColsInputColsItem] = Field(description="要插入的列列表", max_length=100)
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="表格内任意cell位置")
    version_info: DocInsertColsInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertCodeBlockInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertCodeBlockInput(Input):
    code: str = Field(description="代码内容", max_length=100000)
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入位置索引")
    language: str = Field(default=None, description="代码语言标签", max_length=100000)
    version_info: DocInsertCodeBlockInputVersionInfo = Field(default=None, description="版本参数")


class DocFindInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocFindInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    text: str = Field(description="要查找的文本内容", max_length=100000)
    version_info: DocFindInputVersionInfo = Field(default=None, description="版本参数")


class DocFindAndReplaceInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocFindAndReplaceInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    new_text: str = Field(description="替换后的新文本", max_length=100000)
    old_text: str = Field(description="要查找的原文本", max_length=100000)
    version_info: DocFindAndReplaceInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertCommentInputRange(Input):
    begin: int = Field(default=None, description="范围起始位置索引")
    end: int = Field(default=None, description="范围结束位置索引")


class DocInsertCommentInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertCommentInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    range: DocInsertCommentInputRange = Field(description="批注关联的文档范围")
    ref_id: str = Field(default=None, description="评论ID（可选）", max_length=100000)
    text: str = Field(description="批注内容", max_length=100000)
    version_info: DocInsertCommentInputVersionInfo = Field(default=None, description="版本参数")


class DocGetImagesInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocGetImagesInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    version_info: DocGetImagesInputVersionInfo = Field(default=None, description="版本参数")


class DocGetParagraphPropertyInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocGetParagraphPropertyInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="要查询的字符位置(0-based)")
    version_info: DocGetParagraphPropertyInputVersionInfo = Field(
        default=None, description="版本参数"
    )


class DocReplaceBookmarksInputSamplesItemImageInfo(Input):
    height: int = Field(default=None, description="图片高度")
    image_url: str = Field(default=None, description="图片URL", max_length=100000)
    width: int = Field(default=None, description="图片宽度")


class DocReplaceBookmarksInputSamplesItem(Input):
    bookmark_name: str = Field(default=None, description="书签名", max_length=100000)
    doc_id: str = Field(default=None, description="适用于Document类型的文档ID", max_length=100000)
    image_info: DocReplaceBookmarksInputSamplesItemImageInfo = Field(
        default=None, description="适用于Image类型的图片信息"
    )
    keyframe: str = Field(
        default=None, description="适用于Document类型的基准关键帧(base64)", max_length=100000
    )
    revisions: list[str] = Field(
        default=None, description="适用于Document类型的增量命令(base64)", max_length=100
    )
    text: str = Field(default=None, description="适用于Text类型的替换文本", max_length=100000)
    type: str = Field(default=None, description="替换类型", max_length=100000)


class DocReplaceBookmarksInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocReplaceBookmarksInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    samples: list[DocReplaceBookmarksInputSamplesItem] = Field(
        description="书签替换样本列表", max_length=100
    )
    version_info: DocReplaceBookmarksInputVersionInfo = Field(default=None, description="版本参数")


class DocPreInsertAttachmentInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocPreInsertAttachmentInput(Input):
    ext: str = Field(default=None, description="附件扩展名", max_length=100000)
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_name: str = Field(default=None, description="文件名", max_length=100000)
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    is_multi_part: bool = Field(default=None, description="是否分片上传")
    size: int = Field(default=None, description="附件大小")
    version_info: DocPreInsertAttachmentInputVersionInfo = Field(
        default=None, description="版本参数"
    )


class DocAcceptAllRevisionsInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocAcceptAllRevisionsInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    version_info: DocAcceptAllRevisionsInputVersionInfo = Field(
        default=None, description="版本参数"
    )


class DocInsertParagraphWithTextInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertParagraphWithTextInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(description="插入位置索引，-1 表示在文档开头插入（即在第一段之前）")
    indent_count: int = Field(default=None, description="编号前缩进空格数")
    level: str = Field(default=None, description="标题级别", max_length=100000)
    numbering_lvl: str = Field(default=None, description="编号级别", max_length=100000)
    text: str = Field(description="段落文本内容", max_length=100000)
    type: str = Field(default=None, description="编号类别", max_length=100000)
    version_info: DocInsertParagraphWithTextInputVersionInfo = Field(
        default=None, description="版本参数"
    )


class DocAiFormatPureTextInput(Input):
    customStyles: str = Field(default=None, description="对文档的自定义样式", max_length=100000)
    scenario: str = Field(default=None, description="模板场景", max_length=100000)
    title: str = Field(description="文档标题", max_length=100000)
    xml: str = Field(description="格式套用后的文档 xml 结构", max_length=100000)


class DocListRecentAiEditsInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocListRecentAiEditsInput(Input):
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_url: str = Field(
        description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    limit: int = Field(default=None, description="返回条数；缺省10，最大50")
    tool_name: str = Field(
        default=None,
        description='可选：按工具名过滤（精确匹配，如 "doc_replace_image"）',
        max_length=100000,
    )
    version_info: DocListRecentAiEditsInputVersionInfo = Field(default=None, description="版本参数")


class DocInsertAttachmentInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="基准版本号，0 表示不指定；仅支持 int32 范围"
    )
    is_latest: bool = Field(default=None, description="是否操作最新版本")


class DocInsertAttachmentInput(Input):
    classify: str = Field(default=None, description="附件分类", max_length=100000)
    file_id: str = Field(
        default=None,
        description="在线文档DOC的文档唯一标识符（与file_url二选一）",
        max_length=100000,
    )
    file_name: str = Field(default=None, description="文件名", max_length=100000)
    file_type: str = Field(default=None, description="文件类型", max_length=100000)
    file_url: str = Field(
        default=None, description="腾讯文档的URL链接（推荐），与file_id二选一", max_length=100000
    )
    idx: int = Field(default=None, description="插入位置索引")
    layout_type: str = Field(default=None, description="布局类型", max_length=100000)
    object_key: str = Field(default=None, description="文件标识key", max_length=100000)
    size: int = Field(default=None, description="文件大小")
    text: str = Field(default=None, description="显示文本", max_length=100000)
    upload_success: bool = Field(default=None, description="是否上传成功")
    version_info: DocInsertAttachmentInputVersionInfo = Field(default=None, description="版本参数")


class DocOperations:
    @operation(
        name="doc_insert_image",
        description="在 Word 文档指定位置插入图片。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（DOC）",
        effects="write",
    )
    async def doc_insert_image(self, ctx, params: DocInsertImageInput) -> Result:
        return await call(
            ctx,
            "doc.insert_image",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_normal_link",
        description="在 Word 文档指定位置插入普通超链接，可指定链接 URL 和显示文本。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（DOC）",
        effects="write",
    )
    async def doc_insert_normal_link(self, ctx, params: DocInsertNormalLinkInput) -> Result:
        return await call(
            ctx,
            "doc.insert_normal_link",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_footnote",
        description="在指定位置插入脚注或尾注（DOC）。脚注显示在页面底部，尾注显示在文档末尾。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引。⚠️ idx 应该使用目标文本的最后一个字符位置（即段落的 end_index - 1，段落分隔符 ¶ 之前），这样脚注/尾注引用标记会出现在文本末尾而非中间。例如：文本\"你好\"占据索引 5-7（5='你', 6='好', 7=¶），应传 idx=7 使引用标记出现在\"好\"之后。",
        effects="write",
    )
    async def doc_insert_footnote(self, ctx, params: DocInsertFootnoteInput) -> Result:
        return await call(
            ctx,
            "doc.insert_footnote",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_rows",
        description="在指定表格中批量插入多行（DOC）。通过 idx 定位目标表格（表格内任意单元格的 GCP 位置），rows 为要插入的多行描述列表，支持一次插入多行，所有插入相对于原表格行号生效（引擎会自动按降序依次应用，避免索引偏移）",
        effects="write",
    )
    async def doc_insert_rows(self, ctx, params: DocInsertRowsInput) -> Result:
        return await call(
            ctx,
            "doc.insert_rows",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_undo_ai_edit",
        description="撤销指定 version 的 AI 编辑（DOC）。\n\n【前置条件（必须）】\n调用本工具前，必须先调 doc.list_recent_ai_edits 列出最近 AI 编辑，\n根据 tool_name / tool_args 定位用户要撤销的具体操作，再取其 version 作为 target_version。\n禁止凭记忆直接填写 target_version。\n\n【可撤销范围】\n仅可撤销 Redis 中仍保留的 edit（每个文档最近 200 条，7 天 TTL）；超出保留窗口的 edit 无法撤销。\n\n【行为说明】\n采用 git revert 风格：取目标 revision 的反向命令，与之后的 revisions 做 OT 冲突处理后，\n作为新 revision 写入文档；不会删除任何历史 revision。\n成功后会写入一条新 revision（version 递增），行为与一次正常写一致；本次撤销也可被后续撤销。\n\n【失败原因】\n(1) 目标 revision 包含暂不支持反向计算的 mutation 类型；\n(2) 反向命令在当前文档上无法合法执行；\n(3) 目标 revision 的全部改动已被后续编辑覆盖（OT 后全部 noop）；\n(4) target_version 不在当前版本范围内，或对应 edit 已不在保留窗口内。",
        effects="write",
    )
    async def doc_undo_ai_edit(self, ctx, params: DocUndoAiEditInput) -> Result:
        return await call(
            ctx,
            "doc.undo_ai_edit",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_text",
        description="在 Word 文档指定位置插入文本，需要换行时应使用 insert_paragraph 插入段落而非在文本中插入换行符。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（DOC）",
        effects="write",
    )
    async def doc_insert_text(self, ctx, params: DocInsertTextInput) -> Result:
        return await call(
            ctx,
            "doc.insert_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_get_last_operable_pos",
        description="获取 Word 文档正文最后一个可操作位置的索引及前面内容，用于向文档末尾追加内容时定位插入位置（DOC）",
        effects="read",
    )
    async def doc_get_last_operable_pos(self, ctx, params: DocGetLastOperablePosInput) -> Result:
        return await call(
            ctx,
            "doc.get_last_operable_pos",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_border",
        description="在指定位置插入分隔符（DOC）。通过设置段落底部边框来实现水平分隔线效果。⚠️ idx 必须是「分隔线上方那个段落」的 end_index（即该段落的段落分隔符 ¶ 的位置）。例如：想在第 2 段和第 3 段之间插入分隔线，应传第 2 段的 end_index。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引。支持多种边框样式（single/thick/dotted/dashed等）和自定义颜色。",
        effects="write",
    )
    async def doc_insert_border(self, ctx, params: DocInsertBorderInput) -> Result:
        return await call(
            ctx,
            "doc.insert_border",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_update_text_property",
        description="更新 Word 文档指定范围内文本的属性（仅修改样式，不改变文档内容长度）。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的位置索引（DOC）",
        effects="write",
    )
    async def doc_update_text_property(self, ctx, params: DocUpdateTextPropertyInput) -> Result:
        return await call(
            ctx,
            "doc.update_text_property",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_task",
        description="在 Word 文档指定位置插入一个或多个任务（待办事项），支持设置任务状态和内容文本。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（DOC）",
        effects="write",
    )
    async def doc_insert_task(self, ctx, params: DocInsertTaskInput) -> Result:
        return await call(
            ctx,
            "doc.insert_task",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_table",
        description="在 Word 文档指定位置插入表格，需指定行数和列数。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（DOC）",
        effects="write",
    )
    async def doc_insert_table(self, ctx, params: DocInsertTableInput) -> Result:
        return await call(
            ctx,
            "doc.insert_table",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_numbering",
        description="在 Word 文档中插入项目列表（编号/项目符号）（DOC）",
        effects="write",
    )
    async def doc_insert_numbering(self, ctx, params: DocInsertNumberingInput) -> Result:
        return await call(
            ctx,
            "doc.insert_numbering",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_page_break",
        description="在 Word 文档指定位置插入分页符。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（DOC）",
        effects="write",
    )
    async def doc_insert_page_break(self, ctx, params: DocInsertPageBreakInput) -> Result:
        return await call(
            ctx,
            "doc.insert_page_break",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_replace_image",
        description="替换 Word 文档中的图片，必须同时提供三组参数：1) idx（图片位置）2) old_image_url 或 old_attachment_id（定位旧图片）3) 新图片来源（按下方优先级三选一）。建议先用 get_images 获取图片信息，再用返回的 pos 和 image_url/attachment_id 填入对应参数（DOC）",
        effects="write",
    )
    async def doc_replace_image(self, ctx, params: DocReplaceImageInput) -> Result:
        return await call(
            ctx,
            "doc.replace_image",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_get_outline",
        description="获取 Word 文档大纲结构（标题层级树），包含各标题和正文的可操作起止位置，编辑前推荐先调用此工具了解文档结构（DOC）",
        effects="read",
    )
    async def doc_get_outline(self, ctx, params: DocGetOutlineInput) -> Result:
        return await call(
            ctx,
            "doc.get_outline",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_footer",
        description="设置页脚文本内容（DOC）。覆盖式写入：先清空已有页脚内容，再写入新文本。本工具一次只处理一个 section（由 section_index 指定）；如需对多个 section 都写入页脚，请按需多次调用本工具。首次插入时会为目标 section 独立创建页眉页脚 substory，打破该 section 与前一节链接到上一节的关系。⚠️ 重要：本工具与 doc_set_page_number 互斥。调用本工具会清除已有的页码（PAGE 字段）。",
        effects="write",
    )
    async def doc_insert_footer(self, ctx, params: DocInsertFooterInput) -> Result:
        return await call(
            ctx,
            "doc.insert_footer",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_replace_text",
        description="替换 Word 文档中指定范围内的文本为新文本，建议先用 find 查找定位后再调用此工具精确替换。使用前请先调用 resolve_document_structure 获取文档结构，或使用 find 查找文本位置，以确定正确的 begin/end 范围（DOC）",
        effects="write",
    )
    async def doc_replace_text(self, ctx, params: DocReplaceTextInput) -> Result:
        return await call(
            ctx,
            "doc.replace_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_html_content",
        description="在 Word 文档指定 idx 处插入一段 HTML 富文本，引擎会按 HTML 标签/内联样式自动转为段落、标题、列表、表格、链接、加粗/斜体/下划线等富文本元素。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（或使用 get_last_operable_pos 获取文档末尾位置）。已知支持：段落与标题(<p>/<h1>..<h6>)、文本样式(<b>/<i>/<u>/<s>/<sub>/<sup>/<span style>)、链接(<a>)、列表(<ul>/<ol><li>)、表格(<table><tr><td>)、分隔(<br>/<hr>)。已知不支持：<script>/<style>标签、position/float/flex/grid等CSS布局属性。注意：idx 必须是有效的段落起始位置，确保 idx 落在真正的段落起始位置（\\r 之后），而不是 Field 域内部（DOC）",
        effects="write",
    )
    async def doc_insert_html_content(self, ctx, params: DocInsertHtmlContentInput) -> Result:
        return await call(
            ctx,
            "doc.insert_html_content",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_paragraph",
        description='在指定 idx 处插入一个「段落分隔符」（paragraph break），并对「该分隔符之前的文本」应用段落级样式。⚠️ 本接口不写入任何文本内容，仅修饰段落属性。正确工作流：先调 insert_text 写入文本，再调 insert_paragraph 把上述文本所在段落标为指定样式。当 type="1"或"2"时必须同时传 numbering_lvl。相关接口：「插入带文本的标题/编号段落」请使用 insert_paragraph_with_text（一步完成）；「只写入纯文本」请使用 insert_text；「批量插入富文本」请使用 insert_html_content 或 insert_markdown；「改变现有段落样式」请使用 modify_paragraph。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（DOC）',
        effects="write",
    )
    async def doc_insert_paragraph(self, ctx, params: DocInsertParagraphInput) -> Result:
        return await call(
            ctx,
            "doc.insert_paragraph",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_resolve_document_structure",
        description="获取文档结构树（DOC），返回扁平节点列表，用于在调用需要 idx/index/ranges 的写类工具前定位位置。节点 type：Paragraph / Heading（heading_level 1..9）/ Title / Subtitle / Table；文字下划线/删除线/高亮通过 has_highlights 标志位 + highlight_spans 嵌入在 Paragraph 内.paragraph_index（全局 1-based 节点序号）标注第几段（含标题）。三档 mode（默认 compact）：outline=只给标题出 preview，骨架级；compact=每节点 10 字符 preview + has_highlights / row_count×col_count / children_count / is_numbering 等轻量信号位；full=highlight_spans / table cells / numbering 详情全部回填。定位单段传 idx（自动按 full 回包，跳过分页）；超长文档用 offset/limit 分页（默认 limit=150）。",
        effects="read",
    )
    async def doc_resolve_document_structure(
        self, ctx, params: DocResolveDocumentStructureInput
    ) -> Result:
        return await call(
            ctx,
            "doc.resolve_document_structure",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_get_table_info",
        description='获取指定位置 idx 所在表格的整体信息（DOC）。返回行高/列宽/合并情况/各单元格文本+属性，是 set_table_layout / set_table_properties 等表格写类工具的「前置查询」。⚠️ idx 必须落在表格内部；若不确定，先用 resolve_document_structure 找到 type=="Table" 的节点，再用其 cells[].start_index 作为 idx。',
        effects="read",
    )
    async def doc_get_table_info(self, ctx, params: DocGetTableInfoInput) -> Result:
        return await call(
            ctx,
            "doc.get_table_info",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_set_table_layout",
        description="设置表格的行高 / 列宽（DOC）。通过表格内任意 cell 的 GCP 位置 idx 定位表格。【两种模式】✅ mode=auto —— 列宽自适应页面宽度并均分：后端从当前 section 的可用页宽 (pgSz.w - pgMar.left - pgMar.right) 自动算出每列宽度 = 可用页宽 / 列数，所有列等宽铺满页面（即「自适应页宽 + 列宽均分」），用户传的 col_widths_dxa 会被完全忽略；行高在 auto 模式下不改写（沿用原值）。适用：表格越界 / 列宽混乱 / 想一键重置表格、用户说「均分列宽 / 自适应页宽 / 铺满 / 一键整理」时。✅ mode=manual —— 行高、列宽按 dxa 数组逐项指定：row_heights_dxa[i] = 第 i 行行高；col_widths_dxa[j] = 第 j 列列宽；任一项为 0 表示「该行/该列保持原值」（不写 mutation）；数组长度短于行/列数时尾部按 0 处理，长于则静默截断。⚠️【manual 模式强制工作流】传 row_heights_dxa / col_widths_dxa 之前必须先调用 get_table_info 获取当前表格的 row_count / col_count / 各行 height_pt / 各 cell width，再结合用户意图确认目标值。auto 模式无需先查，可直接调用。单位：dxa（OOXML 标准单位，1 inch = 1440 dxa）。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的位置索引。",
        effects="write",
    )
    async def doc_set_table_layout(self, ctx, params: DocSetTableLayoutInput) -> Result:
        return await call(
            ctx,
            "doc.set_table_layout",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_set_page_number",
        description="设置页码（在页脚中插入 PAGE 字段）（DOC）。默认参数组合：页面底部居中 + 1,2,3 格式 + 续前节 + 应用于整篇文档。调用前会自动切换为分页模式，注意：本工具和set_footnote冲突，会清空页脚内容再写入。",
        effects="write",
    )
    async def doc_set_page_number(self, ctx, params: DocSetPageNumberInput) -> Result:
        return await call(
            ctx,
            "doc.set_page_number",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_markdown",
        description="在 Word 文档指定位置插入 Markdown 格式内容，引擎自动转换为富文本格式。推荐使用 base64_markdown 参数避免特殊字符问题。语义说明：按段落导入时，每个块级段落（如 <p>/标题/列表项）都会生成段落分隔符（\\r），因此最后一个段落通常也会以段落分隔符结束。注意：如需精确控制标题级别和列表样式，建议使用 insert_paragraph + insert_text 组合。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引（DOC）",
        effects="write",
    )
    async def doc_insert_markdown(self, ctx, params: DocInsertMarkdownInput) -> Result:
        return await call(
            ctx,
            "doc.insert_markdown",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_modify_paragraph",
        description="修改已有段落的属性（DOC），支持设置对齐方式、行间距、段前段后间距、段落样式、缩进、引用、编号等。本工具用于在原有段落上修改属性，如需添加新的待办事项内容请使用 insert_tasks_with_content，如需添加新的列表项目请使用 insert_paragraph。ranges 为段落范围列表，每项包含 begin 和 end（字符位置索引）。所有属性均为可选，只传入需要修改的字段即可，未传入的字段保持原样。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的位置索引。注意：indent、block_quote、numbering、highlight_block 为独立操作，与其他属性互斥，不可同时传入。",
        effects="write",
    )
    async def doc_modify_paragraph(self, ctx, params: DocModifyParagraphInput) -> Result:
        return await call(
            ctx,
            "doc.modify_paragraph",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_get_comments",
        description="获取 Word 文档中所有批注（DOC）。返回按 range_begin 升序排列的批注数组，每条包含：id（批注 id，与 insert_comment 写入时一致）、range_begin / range_end（批注锚定范围的字符 idx，与 get_last_operable_pos.position 同坐标系；begin == end 表示零长度的「点锚」批注，对应字段 is_point_anchor=true）、text（批注正文文本，已过滤复杂内容）、ref_id（回复链父批注 id，仅回复批注才有；为空时不返回）、author / date（作者展示名与 ISO 时间字符串，未设置时不返回）。主要用于对 insert_comment 的结果做验证、以及在执行批注相关编辑前枚举现有批注",
        effects="read",
    )
    async def doc_get_comments(self, ctx, params: DocGetCommentsInput) -> Result:
        return await call(
            ctx,
            "doc.get_comments",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_get_text_property",
        description="读取 DOC 文档指定位置 index 处生效的文本属性（与 update_text_property 字段对称）：加粗/斜体/下划线/删除线/小型大写/颜色/底纹(background_color)/高亮(highlight)/字号(pt)/字体/上下标等。响应中「字段不存在」表示该属性未在 run 上显式设置，应认为「继承自段落/样式默认值」（DOC）。",
        effects="read",
    )
    async def doc_get_text_property(self, ctx, params: DocGetTextPropertyInput) -> Result:
        return await call(
            ctx,
            "doc.get_text_property",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_set_table_properties",
        description="修改表格属性（DOC）。通过表格内任意 cell 的 GCP 位置 idx 定位表格，可同时设置边框、对齐、宽度、单元格内边距，以及按 9 种 condition 染色单元格。全部字段可选，未提供的属性沿用原表格设置。cell_fills 中 condition 取值：whole_table / first_row / last_row / first_col / last_col / band_row_odd / band_row_even / band_col_odd / band_col_even。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的位置索引。",
        effects="write",
    )
    async def doc_set_table_properties(self, ctx, params: DocSetTablePropertiesInput) -> Result:
        return await call(
            ctx,
            "doc.set_table_properties",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_compare_documents",
        description="对比两个 DOC 文档的内容和格式差异。返回段落级别的差异列表，包括新增/删除/内容修改/格式修改。当前文档作为基准（source），通过 other_file_id 或 other_file_url 指定对比目标（target）。差异类型：added（目标新增）、deleted（源文档删除）、modified_content（内容变化）、modified_format（格式变化，如对齐方式、标题级别、段落样式等）。还支持对比页眉页脚、文本框（textbox/代码块/高亮块）、表格、批注和页面设置的差异。表格以原子单元对比：返回 table_diffs 字段，diff_type 包括 added/deleted/modified（维度不同）/modified_content（维度相同但单元格内容不同，此时 cell_diffs 列出具体差异的单元格坐标（1-based）和文本）。用户可进一步使用返回的 idx/range 调用 resolve_document_structure 获取表格内部详细结构。当一篇文档明显更长时，长文档尾部段落不逐段对比，而是通过 tail_summary 字段汇总。",
        effects="read",
    )
    async def doc_compare_documents(self, ctx, params: DocCompareDocumentsInput) -> Result:
        return await call(
            ctx,
            "doc.compare_documents",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_header",
        description='设置页眉文本内容（DOC）。覆盖式写入：先清空已有页眉内容，再写入新文本。本工具一次只处理一个 section（由 section_index 指定）；如需对多个 section 都写入页眉，请按需多次调用本工具。首次插入时会为目标 section 独立创建页眉页脚 substory，打破该 section 与前一节"链接到上一节"的关系',
        effects="write",
    )
    async def doc_insert_header(self, ctx, params: DocInsertHeaderInput) -> Result:
        return await call(
            ctx,
            "doc.insert_header",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_copy_format",
        description="格式刷（DOC）：将源范围的段落属性和文本属性复制到目标范围。读取 source_range 起始位置处生效的段落格式（对齐、缩进、间距、样式等）和文本格式（加粗、斜体、字号、字体、颜色等），然后应用到 target_ranges 指定的所有范围上。适用于快速统一多个段落/文本的格式。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的位置索引。",
        effects="write",
    )
    async def doc_copy_format(self, ctx, params: DocCopyFormatInput) -> Result:
        return await call(
            ctx,
            "doc.copy_format",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_cols",
        description="在指定表格中批量插入多列（DOC）。通过 idx 定位目标表格（表格内任意单元格的 GCP 位置），cols 为要插入的多列描述列表，支持一次插入多列，所有插入相对于原表格列号生效（引擎会自动按降序依次应用，避免索引偏移）",
        effects="write",
    )
    async def doc_insert_cols(self, ctx, params: DocInsertColsInput) -> Result:
        return await call(
            ctx,
            "doc.insert_cols",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_code_block",
        description="在指定位置直接插入一个代码块（DOC）。代码块会以原生 textbox 形式呈现，支持语法高亮语言标签。适用场景：需要在文档中插入代码片段时使用，无需包裹 markdown 围栏语法，直接传入代码内容即可。自动格式化：会自动去除所有行的公共前导缩进（dedent），无需手动处理缩进对齐。使用前请先调用 resolve_document_structure 或 get_last_operable_pos 获取正确的插入位置",
        effects="write",
    )
    async def doc_insert_code_block(self, ctx, params: DocInsertCodeBlockInput) -> Result:
        return await call(
            ctx,
            "doc.insert_code_block",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_find",
        description="在 Word 文档中查找指定文本，返回所有匹配位置及上下文，建议替换前先用此工具定位再用 replace_text 精确替换（DOC）",
        effects="read",
    )
    async def doc_find(self, ctx, params: DocFindInput) -> Result:
        return await call(
            ctx, "doc.find", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="doc_find_and_replace",
        description="在 Word 文档中查找所有匹配文本并直接替换为新文本，会替换所有匹配项（DOC）",
        effects="write",
    )
    async def doc_find_and_replace(self, ctx, params: DocFindAndReplaceInput) -> Result:
        return await call(
            ctx,
            "doc.find_and_replace",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_comment",
        description="在 Word 文档指定范围内插入批注（评论），插入后文本长度会变化，后续操作需重新获取位置。允许 range_begin == range_end（点锚批注，批注附着在单一位置上、不选中任何范围）。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的位置索引（DOC）",
        effects="write",
    )
    async def doc_insert_comment(self, ctx, params: DocInsertCommentInput) -> Result:
        return await call(
            ctx,
            "doc.insert_comment",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_get_images",
        description="获取 Word 文档中所有图片的信息，包括图片位置、URL 或附件 ID（DOC）",
        effects="read",
    )
    async def doc_get_images(self, ctx, params: DocGetImagesInput) -> Result:
        return await call(
            ctx, "doc.get_images", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="doc_get_paragraph_property",
        description="读取 DOC 文档指定位置 index 所在「段落」的属性（与 insert_paragraph 字段对称）：段落样式名（如 heading 1 / Title / Normal）、大纲级别、heading_level (1..9, 0=非标题)、是否带编号及编号级别 (1..9)、对齐方式、缩进（twips）、段前/后间距 (pt) 与行距。字段不存在表示未显式设置（继承默认值）。主要用于在修改段落属性前先了解当前状态（DOC）",
        effects="read",
    )
    async def doc_get_paragraph_property(self, ctx, params: DocGetParagraphPropertyInput) -> Result:
        return await call(
            ctx,
            "doc.get_paragraph_property",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_replace_bookmarks",
        description="替换 Word 文档中书签标记范围的内容，支持文本和图片类型替换（DOC）",
        effects="write",
    )
    async def doc_replace_bookmarks(self, ctx, params: DocReplaceBookmarksInput) -> Result:
        return await call(
            ctx,
            "doc.replace_bookmarks",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_pre_insert_attachment",
        description="在 Word 文档中预插入附件，获取上传链接和 object_key。客户端需使用 HTTP PUT 方法将文件上传到返回的 upload_url，上传完成后再调用 insert_attachment 完成附件插入（DOC）",
        effects="write",
    )
    async def doc_pre_insert_attachment(self, ctx, params: DocPreInsertAttachmentInput) -> Result:
        return await call(
            ctx,
            "doc.pre_insert_attachment",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_accept_all_revisions",
        description="接受 Word 文档中的所有修订（DOC）",
        effects="write",
    )
    async def doc_accept_all_revisions(self, ctx, params: DocAcceptAllRevisionsInput) -> Result:
        return await call(
            ctx,
            "doc.accept_all_revisions",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_paragraph_with_text",
        description="一步插入「带文本的段落」（DOC）。原子完成「在 idx 处插入 text → 在 idx+len(text) 处插入段落分隔符 → 应用 level/type/numbering_lvl/indent_count」。推荐首选此接口而非「insert_text + insert_paragraph」两步调用，避免两步之间的位置漂移。使用前请先调用 resolve_document_structure 获取文档结构以确定正确的插入位置索引",
        effects="write",
    )
    async def doc_insert_paragraph_with_text(
        self, ctx, params: DocInsertParagraphWithTextInput
    ) -> Result:
        return await call(
            ctx,
            "doc.insert_paragraph_with_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_ai_format_pure_text",
        description="将任意文本转换成格式美化后的腾讯文档，需要Skill配合",
        effects="write",
    )
    async def doc_ai_format_pure_text(self, ctx, params: DocAiFormatPureTextInput) -> Result:
        return await call(
            ctx,
            "doc.ai_format_pure_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_list_recent_ai_edits",
        description='列出文档最近通过 MCP 写工具产生的 AI 编辑记录（DOC）。\n返回每条记录的 version + tool_name + time + tool_args（按时间倒序）。\n撤销某次 AI 操作前，必须先调本工具：在返回列表中按 tool_name / tool_args 与用户描述匹配，\n确认具体操作及其 version，再调 doc.undo_ai_edit(target_version=该 version)。\n禁止跳过本工具直接撤销；禁止凭记忆填写 target_version。\n【典型用法】\n当用户要求「撤销刚才的 X 操作」时：\n1. 调本工具（limit 默认 10），拿到最近若干次 AI 编辑（可用 tool_name 进行过滤）；\n2. 在列表中按 tool_name / tool_args 匹配用户描述，定位 target_version；\n3. 调 doc.undo_ai_edit(file_id, target_version=匹配到的 version) 完成撤销。\n【限制】\n(1) 仅记录通过 MCP 写工具产生的编辑，前端手动编辑 / 程序化 CommitRevision 等其他写不在内；\n(2) Redis 存储，7 天 TTL；每个文档最多保留最近 200 条，只能撤销这 200 条内的 edit；\n(3) 部分工具的 tool_args 会截断，不会完整记录；\n(4) limit 缺省 10，上限 50；tool_name 为可选精确过滤（例如 "doc_replace_image"）。',
        effects="read",
    )
    async def doc_list_recent_ai_edits(self, ctx, params: DocListRecentAiEditsInput) -> Result:
        return await call(
            ctx,
            "doc.list_recent_ai_edits",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="doc_insert_attachment",
        description="在 Word 文档指定位置插入附件（DOC）。本接口是 pre_insert_attachment 的后续步骤：必须先调用 pre_insert_attachment 获取 upload_url 和 object_key，客户端使用 HTTP PUT 上传文件成功后，再调用本接口完成附件插入",
        effects="write",
    )
    async def doc_insert_attachment(self, ctx, params: DocInsertAttachmentInput) -> Result:
        return await call(
            ctx,
            "doc.insert_attachment",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )
