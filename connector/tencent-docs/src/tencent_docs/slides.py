"""Generated from reviewed contracts; regenerate with tools/generate.py."""

from typing import Literal

from connector_sdk import operation
from pydantic import Field

from .mcp import call
from .models import Input, Result


class SlideAddSlideInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    index: int = Field(
        default=None,
        description="0-based 插入位置，必须 ∈ [0, 当前页数]（=当前页数即追加到末尾），不支持 -1。不确定时先调 slide_get_info 拿 slide_count。",
    )
    layout_index: int = Field(
        default=None, description="布局序号（0=标题，1=标题+内容 等），默认 0"
    )


class SlideAddSlidesInput(Input):
    count: int = Field(default=None, description="要插入的页数，必须 >= 1")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    index: int = Field(
        default=None,
        description="0-based 插入位置，必须 ∈ [0, 当前页数]（=当前页数即追加到末尾），不支持 -1。不确定时先调 slide_get_info 拿 slide_count。",
    )
    layout_index: int = Field(
        default=None, description="布局序号（0=标题，1=标题+内容 等），默认 0"
    )


class SlideGetInfoInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )


class SlideGetPageInfoInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")


class SlideGetShapeInfoInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="目标形状的 shape_id", max_length=100000)


class SlideGetTextInput(Input):
    col: int = Field(
        default=None, description="表格单元格列索引（0-based）。仅 TABLE 需要，必须与 row 成对出现"
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    row: int = Field(
        default=None, description="表格单元格行索引（0-based）。仅 TABLE 需要，必须与 col 成对出现"
    )
    shape_id: str = Field(default=None, description="shape ID", max_length=100000)


class SlideFindTextInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    search: str = Field(default=None, description="搜索文本", max_length=100000)


class SlideFindReplaceTextInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    replace: str = Field(default=None, description="替换文本", max_length=100000)
    search: str = Field(default=None, description="搜索文本", max_length=100000)


class SlideAddTextInput(Input):
    border_color: str = Field(
        default=None, description="文本框边框色（RRGGBB）；空串表示无边框", max_length=100000
    )
    border_dash: str = Field(
        default=None,
        description="边框线型，如 solid / dash / dot；空串默认 solid",
        max_length=100000,
    )
    border_width: float = Field(default=None, description="边框宽度（pt）；<= 0 取默认 1.0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    fill_color: str = Field(
        default=None,
        description="文本框背景填充色（RRGGBB）；空串表示透明无填充",
        max_length=100000,
    )
    font_color: str = Field(
        default=None, description="字体颜色（RRGGBB，无 # 前缀）；空串使用默认色", max_length=100000
    )
    font_name: str = Field(
        default=None, description="字体名称；空串使用默认字体", max_length=100000
    )
    font_size: int = Field(default=None, description="字号（pt）；<= 0 时使用默认字号")
    h: float = Field(default=None, description="文本框高度（磅 pt，1pt = 12700 EMU），必须 > 0")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    text: str = Field(default=None, description="文本内容；空串表示空文本框", max_length=100000)
    w: float = Field(default=None, description="文本框宽度（磅 pt，1pt = 12700 EMU），必须 > 0")
    x: float = Field(default=None, description="文本框左上角横坐标（磅 pt，1pt = 12700 EMU）")
    y: float = Field(default=None, description="文本框左上角纵坐标（磅 pt，1pt = 12700 EMU）")


class SlideInsertTextInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="插入位置")
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="shape ID", max_length=100000)
    text: str = Field(default=None, description="插入文本", max_length=100000)


class SlideSetTextPropertyInput(Input):
    baseline: int = Field(default=None, description="基线偏移")
    bold: bool = Field(default=None, description="粗体")
    col: int = Field(
        default=None, description="表格单元格列索引（0-based）。仅 TABLE 需要，必须与 row 成对出现"
    )
    color: str = Field(default=None, description="文字颜色", max_length=100000)
    count: int = Field(default=None, description="长度")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    font_name: str = Field(default=None, description="字体名称", max_length=100000)
    font_size: float = Field(default=None, description="字号")
    index: int = Field(default=None, description="起始位置")
    italic: bool = Field(default=None, description="斜体")
    letter_spacing: float = Field(default=None, description="字符间距")
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    row: int = Field(
        default=None, description="表格单元格行索引（0-based）。仅 TABLE 需要，必须与 col 成对出现"
    )
    shape_id: str = Field(default=None, description="shape ID", max_length=100000)
    strikethrough: str = Field(default=None, description="删除线", max_length=100000)
    underline: str = Field(default=None, description="下划线", max_length=100000)


class SlideAddImageInput(Input):
    content: str = Field(
        default=None,
        description="图片的 base64 编码内容（不含 data URI 前缀，兜底方式三，仅适合小图）；与 image_id 二选一。大图请优先使用本工具描述中【方式一】的本地脚本（slide_add_image 工具名），或【方式二】通过 upload_image / 开放平台 OpenAPI 上传后传 image_id",
        max_length=100000,
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    h: float = Field(
        default=None,
        description="图片高度（磅 pt，1pt = 12700 EMU）；仅值为 0 或未传时使用图片自身原始高度，负值不会触发原始高度回退",
    )
    image_id: str = Field(
        default=None,
        description="已上传图片的加密 ID（有效期一天，方式二备选），与 content 二选一。可通过 tencent-docs MCP 的 upload_image 工具上传后获取，或通过腾讯文档开放平台 OpenAPI 获取。详细获取流程参见工具描述。",
        max_length=100000,
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    w: float = Field(
        default=None,
        description="图片宽度（磅 pt，1pt = 12700 EMU）；仅值为 0 或未传时使用图片自身原始宽度，负值不会触发原始宽度回退",
    )
    x: float = Field(default=None, description="图片左上角横坐标（磅 pt，1pt = 12700 EMU）")
    y: float = Field(default=None, description="图片左上角纵坐标（磅 pt，1pt = 12700 EMU）")


class SlideAddShapeInput(Input):
    border_alpha: int = Field(
        default=None,
        description="边框透明度 0~100，0=完全不透明（默认），100=完全透明（去掉边框）；仅 (0, 100) 开区间才显式写入 alpha",
    )
    border_color: str = Field(
        default=None,
        description='边框颜色（RRGGBB）；空串表示无边框；传 "none" 移除边框）',
        max_length=100000,
    )
    border_dash: str = Field(
        default=None,
        description="边框线型，如 solid / dash / dot；空串默认 solid",
        max_length=100000,
    )
    border_width: float = Field(default=None, description="边框宽度（pt）；<= 0 取默认 1.0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    fill_alpha: int = Field(
        default=None,
        description="创建形状时的填充透明度，仅支持 0~50；0=完全不透明（默认）。如需设置 51~100，先创建形状，再调用 slide_set_shape_properties 修改",
    )
    fill_color: str = Field(
        default=None, description="填充颜色（RRGGBB，无 # 前缀）；空串表示无填充", max_length=100000
    )
    h: float = Field(default=None, description="形状高度（磅 pt，1pt = 12700 EMU），必须 > 0")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_type: str = Field(
        default=None,
        description="形状预设类型，如 rect / ellipse / triangle / rightArrow / leftArrow 等；空串默认 rect。注意：rightArrow / leftArrow 是固定方向的图形预设箭头块，不能指定起点终点；如需画两点之间的方向性箭头线条，请改用 slide_add_line_shape",
        max_length=100000,
    )
    w: float = Field(default=None, description="形状宽度（磅 pt，1pt = 12700 EMU），必须 > 0")
    x: float = Field(default=None, description="形状左上角横坐标（磅 pt，1pt = 12700 EMU）")
    y: float = Field(default=None, description="形状左上角纵坐标（磅 pt，1pt = 12700 EMU）")


class SlideAddShapesInputShapesItem(Input):
    border_alpha: int = Field(default=None)
    border_color: str = Field(default=None, max_length=100000)
    border_dash: str = Field(default=None, max_length=100000)
    border_width: float = Field(default=None)
    fill_alpha: int = Field(default=None)
    fill_color: str = Field(default=None, max_length=100000)
    h: float = Field(default=None)
    shape_type: str = Field(default=None, max_length=100000)
    w: float = Field(default=None)
    x: float = Field(default=None)
    y: float = Field(default=None)


class SlideAddShapesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引,从 0 开始")
    shapes: list[SlideAddShapesInputShapesItem] = Field(
        default=None,
        description="待插入的形状列表（对象数组）。单元素字段：x / y / w / h / shape_type / fill_color / fill_alpha / border_color / border_dash / border_width / border_alpha。shape_type 可选 rect / ellipse / triangle / rightArrow / leftArrow 等；方向性箭头线条请改用 slide_add_line_shapes",
        max_length=100,
    )


class SlideRemoveShapesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_ids: list[str] = Field(
        default=None, description="待删除的形状 ID 字符串数组，长度 >= 1", max_length=100
    )


class SlideMoveSlideInput(Input):
    after_section_id: str = Field(
        default=None,
        description='现有幻灯片节的 ID。适用于非空和空的幻灯片节——当目标节还没有幻灯片时，请使用 after_section_id（空节没有 first_slide_index，因此 before_slide_index 无法准确地定位它们）。传递空字符串 "" 可以将幻灯片移动到演示文稿的最开头。与 before_slide_index 互斥',
        max_length=100000,
    )
    before_slide_index: int = Field(
        default=None,
        description="基于 0 的幻灯片索引。被移动的幻灯片将被插入到当前位于该索引位置的幻灯片之前（即被移动的第一张幻灯片最终将占据该索引位置）。若要将幻灯片移动至第 i 个章节的开头，请传入该章节的 first_slide_index（此时被移动的幻灯片将成为该章节新的首张幻灯片，并将原有的首张幻灯片向后顺延）。取值范围：[0, slide_count]；若传入 slide_count，则表示将幻灯片追加至整个演示文稿的末尾。与 after_section_id 互斥",
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_indices: list[int] = Field(
        default=None,
        description="待移动幻灯片的 0-based 页索引列表（整数数组），长度 >= 1",
        max_length=100,
    )


class SlideRemoveSlideInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="待删除幻灯片的 0-based 页索引")


class SlideGetCommentsInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(
        default=None, description="页索引（0-based）；未传或 -1 返回全部页；传 0 仅返回第 1 页"
    )


class SlideDuplicateSlideInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_indexes: list[int] = Field(
        default=None,
        description="待复制幻灯片的 0-based 页索引列表（整数数组），长度 >= 1",
        max_length=100,
    )
    target_page_index: int = Field(
        default=None,
        description="副本插入位置（0-based 索引），不传或 -1 表示默认（紧跟在被复制页后方）",
    )


class SlideSetThemeInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    is_builtin: bool = Field(
        default=None, description="是否使用内置主题（true 时 theme_id 须为内置主题 ID）"
    )
    theme_id: str = Field(default=None, description="目标主题 ID（必填）", max_length=100000)


class SlideSetAnimPropertiesInput(Input):
    anim_subtype: int = Field(default=None, description="新的动画方向整数值，0 表示不需要")
    anim_type: int = Field(default=None, description="新的动画类型整数值")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="要修改的动画索引（0-based）")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="目标形状的 shape_id", max_length=100000)


class SlideAddLineShapeInput(Input):
    color: str = Field(
        default=None, description="颜色（RRGGBB）；空串默认 000000", max_length=100000
    )
    dash: str = Field(
        default=None, description="线型：solid / dash / dot；空串默认 solid", max_length=100000
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    line_type: str = Field(
        default=None,
        description="线形类型：line / arrow / doubleArrow；空串默认 line",
        max_length=100000,
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    width: float = Field(default=None, description="线宽（pt）；<= 0 取默认 1.0")
    x1: float = Field(default=None, description="起点横坐标（磅 pt，1pt = 12700 EMU）")
    x2: float = Field(default=None, description="终点横坐标（磅 pt，1pt = 12700 EMU）")
    y1: float = Field(default=None, description="起点纵坐标（磅 pt，1pt = 12700 EMU）")
    y2: float = Field(default=None, description="终点纵坐标（磅 pt，1pt = 12700 EMU）")


class SlideRemoveSectionsInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    section_ids: list[str] = Field(default=None, description="节 ID 列表", max_length=100)


class SlideGetGroupInfoInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    group_id: str = Field(default=None, description="group shape ID", max_length=100000)
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")


class SlideRemoveSectionWithSlidesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    section_id: str = Field(default=None, description="节 ID", max_length=100000)


class SlideListAnimTypesInput(Input):
    file_id: str = Field(
        default=None,
        description="文档ID，与 file_url 二选一（仅用于 ticket 校验）",
        max_length=100000,
    )
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )


class SlideReplyCommentInput(Input):
    author_name: str = Field(default=None, description="作者名称", max_length=100000)
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    group_id: str = Field(default=None, description="批注分组 ID", max_length=100000)
    page_index: int = Field(default=None, description="页索引")
    text: str = Field(default=None, description="回复文本", max_length=100000)


class SlideModifyCommentInput(Input):
    author_name: str = Field(
        default=None, description="作者名称（覆盖式：传空串会清空原作者名）", max_length=100000
    )
    comment_type: int = Field(default=None, description="批注类型：1=页级，2=元素级，3=文本级")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    group_id: str = Field(default=None, description="批注分组 ID", max_length=100000)
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="shape ID", max_length=100000)
    text: str = Field(
        default=None,
        description="批注文本（覆盖式：传空串会清空原文，不修改请省略此字段）",
        max_length=100000,
    )


class SlideAddAnimInput(Input):
    anim_subtype: int = Field(default=None, description="动画方向/子类型整数值，0 表示不需要")
    anim_type: int = Field(default=None, description="动画类型整数值")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    index: int = Field(
        default=None,
        description="动画在该页动画序列中的插入位置，0-based，必须 >= 0。想追加到末尾时填一个 >= 当前动画数量的值即可（例如 9999），不支持 -1。",
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="目标形状的 shape_id", max_length=100000)


class SlideAddTableInput(Input):
    cols: int = Field(default=None, description="表格列数，必须大于 0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    h: float = Field(default=None, description="表格总高度，单位为磅（pt），会在行之间均分")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始计数")
    rows: int = Field(default=None, description="表格行数，必须大于 0")
    w: float = Field(default=None, description="表格总宽度，单位为磅（pt），会在列之间均分")
    x: float = Field(default=None, description="表格左上角 X 坐标，单位为磅（pt，1pt = 12700 EMU）")
    y: float = Field(default=None, description="表格左上角 Y 坐标，单位为磅（pt，1pt = 12700 EMU）")


class SlideInsertTableRowsInput(Input):
    count: int = Field(default=None, description="插入行数，未传时默认 1，必须大于 0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="插入间隙位置；0 表示表格顶部，N 表示表格底部")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始计数")
    reference_row_index: int = Field(
        default=None,
        description="新行高度参考行索引（0-based）。未传时按 0 处理（=使用第 0 行的高度作为新行高度）；超出已有行数时新行使用默认行高",
    )
    shape_id: str = Field(default=None, description="目标表格 shape id", max_length=100000)


class SlideMoveAnimInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    from_index: int = Field(default=None, description="动画当前索引（0-based）")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="目标形状的 shape_id", max_length=100000)
    to_index: int = Field(default=None, description="动画目标索引（0-based）")


class SlideAddDatetimeInput(Input):
    display_text: str = Field(
        default=None,
        description='可选的显示文本，如 "2026/05/11"；空串时引擎保留空内容',
        max_length=100000,
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片 0-based 页索引")


class SlideDeleteTableRowsInput(Input):
    count: int = Field(default=None, description="删除行数，未传时默认 1，必须大于 0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="起始删除行索引，从 0 开始")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始计数")
    shape_id: str = Field(default=None, description="目标表格 shape id", max_length=100000)


class SlideGetSectionsInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )


class SlideSetNotesTextInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="base version for edit/query, 0 means not specified"
    )
    is_latest: bool = Field(default=None, description="whether to operate on the latest version")


class SlideSetNotesTextInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="待设置备注的幻灯片页索引，从 0 开始计数")
    text: str = Field(
        default=None, description="备注页文本；空字符串表示清空当前备注", max_length=100000
    )
    version_info: SlideSetNotesTextInputVersionInfo = Field(
        default=None, description="版本入参（base_version / is_latest）"
    )


class SlideRenameSectionInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    name: str = Field(default=None, description="节名称", max_length=100000)
    section_id: str = Field(default=None, description="节 ID", max_length=100000)


class SlideAddCommentInput(Input):
    created_time_stamp: int = Field(default=None, description="创建时间戳")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(
        default=None, description="shape ID（元素级/文本级批注必填）", max_length=100000
    )
    text: str = Field(default=None, description="批注文本", max_length=100000)
    text_anchor_cp: int = Field(default=None, description="文本锚点起始位置")
    text_anchor_len: int = Field(default=None, description="文本锚点长度")


class SlideUnmergeTableCellsInput(Input):
    col_span: int = Field(default=None, description="区域列跨度，必须大于 0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始计数")
    row_span: int = Field(default=None, description="区域行跨度，必须大于 0")
    shape_id: str = Field(default=None, description="目标表格 shape id", max_length=100000)
    start_col: int = Field(default=None, description="区域左上角列索引，从 0 开始")
    start_row: int = Field(default=None, description="区域左上角行索引，从 0 开始")


class SlideSetShapePropertiesInputShapesItem(Input):
    border_alpha: int = Field(
        default=None, description="边框透明度 0-100；设置 border_color 时若不传则默认 0"
    )
    border_color: str = Field(
        default=None, description='十六进制边框色；"none" 表示移除边框', max_length=100000
    )
    border_dash: str = Field(
        default=None, description="边框线型：solid/dot/dash/lgDash/dashDot/...", max_length=100000
    )
    border_width: float = Field(default=None, description="边框宽度（pt）")
    fill_alpha: int = Field(
        default=None,
        description="填充透明度 0-100（0=完全不透明）；设置 fill_color 时若不传则默认 0",
    )
    fill_color: str = Field(
        default=None,
        description='十六进制填充色（如 "FF0000"）；"none" 表示移除填充；不传保持不变',
        max_length=100000,
    )
    h: float = Field(default=None, description="新高度（pt）")
    rotation: float = Field(default=None, description="旋转角度（度）")
    shape_id: str = Field(default=None, description="要修改的形状 ID（必填）", max_length=100000)
    w: float = Field(default=None, description="新宽度（pt）")
    x: float = Field(default=None, description="新 X 坐标（pt）")
    y: float = Field(default=None, description="新 Y 坐标（pt）")


class SlideSetShapePropertiesInput(Input):
    border_alpha: int = Field(
        default=None,
        description="边框透明度，百分比 0-100（0=完全不透明，100=完全透明）。设置 border_color 时若不传则默认 0。普通形状和图片形状均支持",
    )
    border_color: str = Field(
        default=None,
        description='十六进制边框色（如 "000000"）。传 "none" 移除边框。不传则保持不变。普通形状和图片形状均支持',
        max_length=100000,
    )
    border_dash: str = Field(
        default=None,
        description="边框线型：solid/dot/dash/lgDash/dashDot/lgDashDot/lgDashDotDot/sysDash/sysDot/sysDashDot/sysDashDotDot。不传则保持不变",
        max_length=100000,
    )
    border_width: float = Field(
        default=None, description="边框宽度，单位磅（1pt=12700 EMU）。不传则保持不变"
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    fill_alpha: int = Field(
        default=None,
        description="填充透明度，百分比 0-100（0=完全不透明，100=完全透明）。对普通形状控制 solidFill 透明度；对图片形状控制图片整体透明度（alphaModFix）。设置 fill_color 时若不传则默认 0",
    )
    fill_color: str = Field(
        default=None,
        description='十六进制填充色（如 "FF0000"）。传 "none" 移除填充。不传则保持不变。图片形状不支持此属性',
        max_length=100000,
    )
    h: float = Field(default=None, description="新的高度，单位磅。不传则保持不变")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    rotation: float = Field(
        default=None, description="旋转角度（度），如 90 表示顺时针旋转 90°。不传则保持不变"
    )
    shape_id: str = Field(
        default=None, description="单形状模式 (A)：要修改的形状 ID", max_length=100000
    )
    shape_ids: list[str] = Field(
        default=None,
        description="批量多对一模式 (C)：形状 ID 数组，所有形状统一应用顶层属性。与 shape_id、shapes 互斥",
        max_length=100,
    )
    shapes: list[SlideSetShapePropertiesInputShapesItem] = Field(
        default=None,
        description="批量一对一模式 (B)：对象数组，单元素字段：shape_id / fill_color / fill_alpha / border_color / border_alpha / border_width / border_dash / x / y / w / h / rotation。与 shape_id、shape_ids 互斥",
        max_length=100,
    )
    w: float = Field(default=None, description="新的宽度，单位磅。不传则保持不变")
    x: float = Field(default=None, description="新的 X 坐标，单位磅。不传则保持不变")
    y: float = Field(default=None, description="新的 Y 坐标，单位磅。不传则保持不变")


class SlideSetPagePropertiesInputGradientStopsItem(Input):
    color: str = Field(default=None, description="色标颜色（RRGGBB）", max_length=100000)
    pos: int = Field(default=None, description="色标位置（0~100000）")


class SlideSetPagePropertiesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    fill_alpha: int = Field(
        default=None,
        description="背景透明度 0~100，0=完全不透明（默认），100=完全透明；solid/gradient 路径写入 srgb alpha，image 路径写入 blip.alphaModFix.amt",
    )
    fill_color: str = Field(
        default=None,
        description="fill_type=solid 时的背景色（RRGGBB）；空串清除背景",
        max_length=100000,
    )
    fill_type: str = Field(
        default=None,
        description="背景填充类型：solid / image / gradient；省略不修改背景",
        max_length=100000,
    )
    gradient_angle: int = Field(default=None, description="渐变角度（1/60000 度）")
    gradient_stops: list[SlideSetPagePropertiesInputGradientStopsItem] = Field(
        default=None,
        description="fill_type=gradient 时的色标列表（至少 2 项），每项含 color(RRGGBB) 和 pos(0~100000)",
        max_length=100,
    )
    image: str = Field(
        default=None,
        description="fill_type=image 时的图片（data URI / 本地绝对路径，不接受远程 URL）",
        max_length=100000,
    )
    page_index: int = Field(default=None, description="目标幻灯片 0-based 页索引")
    stretch: bool = Field(
        default=None,
        description="fill_type=image 时是否拉伸铺满整页；默认 true。设为 false 时图片按 tile_* 系列参数平铺（仅此时 tile_alignment / tile_flip / tile_tx / tile_ty / tile_sx / tile_sy 才生效）",
    )
    tile_alignment: str = Field(
        default=None,
        description="平铺对齐锚点（仅 fill_type=image && stretch=false 时生效）；常用取值：tl / t / tr / l / ctr / r / bl / b / br（左上 / 上 / 右上 / 左 / 居中 / 右 / 左下 / 下 / 右下）",
        max_length=100000,
    )
    tile_flip: str = Field(
        default=None,
        description="平铺翻转模式（仅 fill_type=image && stretch=false 时生效）；OOXML 取值：none / x / y / xy",
        max_length=100000,
    )
    tile_sx: int = Field(
        default=None,
        description="平铺水平缩放（1/100000；仅 fill_type=image && stretch=false 时生效）",
    )
    tile_sy: int = Field(
        default=None,
        description="平铺垂直缩放（1/100000；仅 fill_type=image && stretch=false 时生效）",
    )
    tile_tx: int = Field(
        default=None, description="平铺水平偏移（EMU；仅 fill_type=image && stretch=false 时生效）"
    )
    tile_ty: int = Field(
        default=None, description="平铺垂直偏移（EMU；仅 fill_type=image && stretch=false 时生效)"
    )
    visible: bool = Field(default=None, description="可见性：true=显示，false=隐藏；省略不修改")


class SlideUndoAiEditInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="base version for edit/query, 0 means not specified"
    )
    is_latest: bool = Field(default=None, description="whether to operate on the latest version")


class SlideUndoAiEditInput(Input):
    file_id: str = Field(
        default=None, description="文档唯一标识符，与 file_url 二选一", max_length=100000
    )
    file_url: str = Field(
        default=None, description="腾讯文档的文档链接，与 file_id 二选一", max_length=100000
    )
    target_version: int = Field(
        default=None,
        description="待反向的目标 revision 版本号（必填），必须 > 0 且 <= 当前最新版本",
    )
    version_info: SlideUndoAiEditInputVersionInfo = Field(default=None, description="版本入参")


class SlideListRecentAiEditsInputVersionInfo(Input):
    base_version: int = Field(
        default=None, description="base version for edit/query, 0 means not specified"
    )
    is_latest: bool = Field(default=None, description="whether to operate on the latest version")


class SlideListRecentAiEditsInput(Input):
    file_id: str = Field(
        default=None, description="文档唯一标识符，与 file_url 二选一", max_length=100000
    )
    file_url: str = Field(
        default=None, description="腾讯文档的文档链接，与 file_id 二选一", max_length=100000
    )
    limit: int = Field(default=None, description="返回条数；缺省 10，最大 50")
    tool_name: str = Field(
        default=None,
        description='可选：按工具名过滤（精确匹配，如 "slide_add_image"）',
        max_length=100000,
    )
    version_info: SlideListRecentAiEditsInputVersionInfo = Field(
        default=None, description="版本入参（用于权限校验；不影响实际查询数据）"
    )


class SlideSetSlideSizeInput(Input):
    aspect_ratio: float = Field(description="页面宽高比：1=4:3, 2=16:9")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    scale_master_layout: bool = Field(
        default=None, description="是否同步缩放 master / layout 页（默认 false）"
    )
    scale_mode: Literal["default", "no_scale", "enlarge"] = Field(
        default=None,
        description="缩放模式：default（等比缩放）/ no_scale（不缩放，居中）/ enlarge（向放大方向缩放）；未传或空串时 handler 自动填 default",
    )


class SlideAddFooterInput(Input):
    display_text: str = Field(
        default=None,
        description='页脚文本内容，如 "Confidential" 或 "© 2026 Acme Corp"；仅 show=true 时生效',
        max_length=100000,
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片 0-based 页索引")
    show: bool = Field(default=None, description="true（默认）=添加/显示页脚；false=移除/隐藏页脚")


class SlideChangeChartTypeInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    new_chart_type: str = Field(default=None, description="目标图表类型", max_length=100000)
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="图表 shape ID", max_length=100000)


class SlideAddTextsInputTextsItem(Input):
    border_color: str = Field(default=None, max_length=100000)
    border_dash: str = Field(default=None, max_length=100000)
    border_width: float = Field(default=None)
    fill_color: str = Field(default=None, max_length=100000)
    font_color: str = Field(default=None, max_length=100000)
    font_name: str = Field(default=None, max_length=100000)
    font_size: int = Field(default=None)
    h: float = Field(default=None)
    text: str = Field(default=None, max_length=100000)
    w: float = Field(default=None)
    x: float = Field(default=None)
    y: float = Field(default=None)


class SlideAddTextsInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    texts: list[SlideAddTextsInputTextsItem] = Field(
        default=None,
        description="待插入的文本框列表（对象数组）。单元素字段：x / y / w / h / text / font_color / font_name / font_size / fill_color / border_color / border_dash / border_width",
        max_length=100,
    )


class SlideReorderShapesInGroupInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    group_id: str = Field(default=None, description="group shape ID", max_length=100000)
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_ids: list[str] = Field(default=None, description="子 shape ID 列表", max_length=100)
    to_index: int = Field(default=None, description="目标层级序号")


class SlideReorderShapeInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    op: int = Field(default=None, description="z-order 操作类型：0=置底 / 1=下移 / 2=上移 / 3=置顶")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_ids: list[str] = Field(
        default=None, description="待调整 z-order 的形状 ID 字符串数组，长度 >= 1", max_length=100
    )


class SlideGetThemesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )


class SlideRemoveAnimInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="要移除的动画索引（0-based）")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="目标形状的 shape_id", max_length=100000)


class SlideUpdateChartDataInputSeriesItem(Input):
    name: str = Field(default=None, max_length=100000)
    values: list[float] = Field(default=None, max_length=100)


class SlideUpdateChartDataInput(Input):
    categories: list[str] = Field(
        default=None, description='分类标签（字符串数组），如 ["Q1","Q2","Q3"]', max_length=100
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    series: list[SlideUpdateChartDataInputSeriesItem] = Field(
        default=None,
        description="数据系列（对象数组）。单元素字段：name（系列名） / values（数值数组）",
        max_length=100,
    )
    shape_id: str = Field(default=None, description="图表 shape ID", max_length=100000)
    sub_chart_index: int = Field(default=None, description="子图表索引")


class SlideMergeTableCellsInput(Input):
    col_span: int = Field(default=None, description="合并区域列跨度，必须大于 0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始计数")
    row_span: int = Field(default=None, description="合并区域行跨度，必须大于 0")
    shape_id: str = Field(default=None, description="目标表格 shape id", max_length=100000)
    start_col: int = Field(default=None, description="合并区域左上角列索引，从 0 开始")
    start_row: int = Field(default=None, description="合并区域左上角行索引，从 0 开始")


class SlideSetAnimTriggerInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="要修改的动画索引（0-based）")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="目标形状的 shape_id", max_length=100000)
    trigger_shape_id: str = Field(
        default=None, description="触发形状 ID，空串表示设为默认触发", max_length=100000
    )


class SlideInsertTableColsInput(Input):
    count: int = Field(default=None, description="插入列数，未传时默认 1，必须大于 0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="插入间隙位置；0 表示最左侧，M 表示最右侧")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始计数")
    shape_id: str = Field(default=None, description="目标表格 shape id", max_length=100000)


class SlideDeleteTextInput(Input):
    count: int = Field(default=None, description="删除长度")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="起始位置")
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="shape ID", max_length=100000)


class SlideAddNotesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片 0-based 页索引")
    text: str = Field(
        default=None, description="备注页文本；空字符串时创建空白备注页", max_length=100000
    )


class SlideAddSectionInput(Input):
    after_section_id: str = Field(
        default=None,
        description="已有节的 ID，新节作为空节插入到该节之后（不接管任何页面）；传空字符串表示在最开头插入空节。与 before_slide_index 互斥。使用 slide_get_sections 获取有效的 section ID",
        max_length=100000,
    )
    before_slide_index: int = Field(
        default=None,
        description="0-based slide 索引，新节插入到该 slide 之前并拥有它（该 slide 成为新节的第一页）。原来包含该 slide 的节将从下一页开始。与 after_section_id 互斥",
    )
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    name: str = Field(default=None, description="节名称", max_length=100000)


class SlideListBuiltinThemesInput(Input):
    file_id: str = Field(default=None, description="可选，仅用于 trace/log", max_length=100000)


class SlideAppendTextInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="shape ID", max_length=100000)
    text: str = Field(default=None, description="追加文本", max_length=100000)


class SlideRemoveCommentInput(Input):
    comment_type: int = Field(default=None, description="批注类型：1=页级，2=元素级，3=文本级")
    file_id: str = Field(default=None, description="文档ID,与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    group_id: str = Field(default=None, description="批注分组 ID", max_length=100000)
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="shape ID", max_length=100000)


class SlideAddLineShapesInputLinesItem(Input):
    color: str = Field(default=None, max_length=100000)
    dash: str = Field(default=None, max_length=100000)
    line_type: str = Field(default=None, max_length=100000)
    width: float = Field(default=None)
    x1: float = Field(default=None)
    x2: float = Field(default=None)
    y1: float = Field(default=None)
    y2: float = Field(default=None)


class SlideAddLineShapesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    lines: list[SlideAddLineShapesInputLinesItem] = Field(
        default=None,
        description="待插入的线形列表（对象数组）。单元素字段：x1 / y1 / x2 / y2 / line_type / color / dash / width",
        max_length=100,
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始")


class SlideDeleteTableColsInput(Input):
    count: int = Field(default=None, description="删除列数，未传时默认 1，必须大于 0")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    index: int = Field(default=None, description="起始删除列索引，从 0 开始")
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始计数")
    shape_id: str = Field(default=None, description="目标表格 shape id", max_length=100000)


class SlideUpdateGroupShapePropertiesInput(Input):
    border_color: str = Field(default=None, description="边框色", max_length=100000)
    border_width: float = Field(default=None, description="边框宽度")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    fill_color: str = Field(default=None, description="填充色", max_length=100000)
    group_id: str = Field(default=None, description="group shape ID", max_length=100000)
    h: float = Field(default=None, description="高度")
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    rotation: float = Field(default=None, description="旋转角度")
    w: float = Field(default=None, description="宽度")
    x: float = Field(default=None, description="X 坐标")
    y: float = Field(default=None, description="Y 坐标")


class SlideAddChartInputSeriesItem(Input):
    name: str = Field(default=None, max_length=100000)
    values: list[float] = Field(default=None, max_length=100)


class SlideAddChartInput(Input):
    bg_color: str = Field(default=None, description="背景色", max_length=100000)
    categories: list[str] = Field(
        default=None, description='分类标签（字符串数组），如 ["Q1","Q2","Q3"]', max_length=100
    )
    chart_type: str = Field(default=None, description="图表类型", max_length=100000)
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    h: float = Field(default=None, description="高度")
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    series: list[SlideAddChartInputSeriesItem] = Field(
        default=None,
        description="数据系列（对象数组）。单元素字段：name（系列名） / values（数值数组）",
        max_length=100,
    )
    title: str = Field(default=None, description="图表标题", max_length=100000)
    transparent: bool = Field(default=None, description="是否透明背景")
    w: float = Field(default=None, description="宽度")
    x: float = Field(default=None, description="X 坐标")
    y: float = Field(default=None, description="Y 坐标")


class SlideUpdateChartStyleInputStyleCategoryAxis(Input):
    hidden: bool = Field(default=None, description="是否隐藏该轴（覆盖式：未传保持原值）")
    number_format: str = Field(
        default=None,
        description='轴标签数字格式（OOXML 格式串，如 "0.00%"）；空串=不修改',
        max_length=100000,
    )
    title: str = Field(default=None, description="轴标题；空串清空标题", max_length=100000)


class SlideUpdateChartStyleInputStyleLegend(Input):
    overlay: bool = Field(default=None, description="图例是否与绘图区重叠（覆盖式：未传保持原值）")
    position: str = Field(
        default=None,
        description="图例位置：top / bottom / left / right / topRight；空串=不修改",
        max_length=100000,
    )


class SlideUpdateChartStyleInputStyleSeriesStylesItem(Input):
    fill_color: str = Field(
        default=None, description="填充色（RRGGBB）；空串=不修改", max_length=100000
    )
    line_color: str = Field(
        default=None, description="线条色（RRGGBB）；空串=不修改", max_length=100000
    )
    line_width_emu: int = Field(default=None, description="线宽（EMU）；0=不修改")
    marker_size: int = Field(default=None, description="标记点大小（点）；0=不修改")
    marker_style: str = Field(
        default=None,
        description="标记点样式：circle / square / diamond / triangle / x / star / dot / dash / picture / none；空串=不修改",
        max_length=100000,
    )


class SlideUpdateChartStyleInputStyleValueAxis(Input):
    hidden: bool = Field(default=None, description="是否隐藏该轴（覆盖式：未传保持原值）")
    number_format: str = Field(
        default=None,
        description='轴标签数字格式（OOXML 格式串，如 "0.00%"）；空串=不修改',
        max_length=100000,
    )
    title: str = Field(default=None, description="轴标题；空串清空标题", max_length=100000)


class SlideUpdateChartStyleInputStyle(Input):
    category_axis: SlideUpdateChartStyleInputStyleCategoryAxis = Field(
        default=None, description="分类轴配置（覆盖式）"
    )
    display_blanks_as: str = Field(
        default=None,
        description="空数据点的显示方式：gap / zero / span；空串=不修改",
        max_length=100000,
    )
    legend: SlideUpdateChartStyleInputStyleLegend = Field(
        default=None, description="图例配置（覆盖式：内部字段未传保持原值）"
    )
    plot_vis_only: bool = Field(
        default=None, description="是否仅绘制可见数据（覆盖式：未传保持原值）"
    )
    series_styles: list[SlideUpdateChartStyleInputStyleSeriesStylesItem] = Field(
        default=None,
        description="数据系列样式列表（按系列顺序传入；省略某项保持原值）",
        max_length=100,
    )
    show_major_gridlines: bool = Field(
        default=None, description="是否显示主网格线（覆盖式：未传保持原值）"
    )
    title: str = Field(default=None, description="图表标题；空串清空标题", max_length=100000)
    value_axis: SlideUpdateChartStyleInputStyleValueAxis = Field(
        default=None, description="数值轴配置（覆盖式）"
    )


class SlideUpdateChartStyleInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="图表 shape ID", max_length=100000)
    style: SlideUpdateChartStyleInputStyle = Field(
        default=None,
        description="图表样式属性集合（覆盖式：仅修改传入字段；嵌套 legend / category_axis / value_axis 同样为覆盖式）",
    )


class SlideProgressInput(Input):
    session_id: str = Field(description="create_slide返回的session_id", max_length=100000)


class SlideSetDefaultFontInput(Input):
    bold: bool = Field(default=None, description="粗体（true/false；未传=不修改）")
    ea_font: str = Field(default=None, description="东亚字体名（空串=不修改）", max_length=100000)
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    font_color: str = Field(
        default=None,
        description='字体颜色，6 位 hex（不含 # 前缀，如 "FF0000"；空串=不修改）',
        max_length=100000,
    )
    font_size: float = Field(default=None, description="默认字号（pt，>0；0 或省略=不修改）")
    italic: bool = Field(default=None, description="斜体（true/false；未传=不修改）")
    latin_font: str = Field(
        default=None, description="西文字体名（空串=不修改）", max_length=100000
    )
    spacing: float = Field(
        default=None, description="字符间距，单位 pt（如 3 表示 3pt；范围 -50~50；省略=不修改）"
    )


class SlideGetMasterInfoInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(
        default=None,
        description="可选：指定幻灯片 0-based 页索引，仅返回该页关联的母版；省略时返回所有母版",
    )


class SlideGetChartInfoInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_id: str = Field(default=None, description="图表 shape ID", max_length=100000)


class SlideMoveSectionInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    section_id: str = Field(default=None, description="节 ID", max_length=100000)
    to_section_index: int = Field(default=None, description="目标节序号")


class SlideAddPageNumberInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片 0-based 页索引")


class SlideGroupShapesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")
    shape_ids: list[str] = Field(default=None, description="shape ID 列表", max_length=100)


class SlideUngroupShapesInput(Input):
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片URL，与 file_id 二选一", max_length=100000
    )
    group_id: str = Field(default=None, description="group shape ID", max_length=100000)
    page_index: int = Field(default=None, description="幻灯片页索引，从 0 开始")


class SlideSetCellTextInput(Input):
    col: int = Field(default=None, description="目标单元格列索引，从 0 开始")
    file_id: str = Field(default=None, description="文档ID，与 file_url 二选一", max_length=100000)
    file_url: str = Field(
        default=None, description="在线幻灯片的URL链接，与 file_id 二选一", max_length=100000
    )
    page_index: int = Field(default=None, description="目标幻灯片页索引，从 0 开始计数")
    row: int = Field(default=None, description="目标单元格行索引，从 0 开始")
    shape_id: str = Field(default=None, description="目标表格 shape id", max_length=100000)
    text: str = Field(default=None, description="写入单元格的纯文本，可为空", max_length=100000)


class SlidesOperations:
    @operation(
        name="slide_add_slide",
        description="在演示文稿中插入一张新幻灯片。index 为 0-based 插入位置，必须落在 [0, 当前页数] 区间（等于当前页数即追加到末尾，不支持 -1，越界会报 page insert index out of range）；不确定当前页数时先调 slide_get_info 拿 slide_count；layout_index 为首个母版下的布局序号（0=标题，1=标题+内容 等），默认 0（SLIDE）",
        effects="write",
    )
    async def slide_add_slide(self, ctx, params: SlideAddSlideInput) -> Result:
        return await call(
            ctx,
            "slide_add_slide",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_slides",
        description="在同一位置批量插入多张幻灯片，所有页共用同一布局模板。index 为 0-based 插入位置，必须落在 [0, 当前页数] 区间（=当前页数即追加到末尾，不支持 -1）；不确定当前页数时先调 slide_get_info 拿 slide_count。count 必须 >= 1（SLIDE）",
        effects="write",
    )
    async def slide_add_slides(self, ctx, params: SlideAddSlidesInput) -> Result:
        return await call(
            ctx,
            "slide_add_slides",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_info",
        description="获取演示文稿元数据：幻灯片总数、有序 slide_ids、幻灯片尺寸（EMU 和磅 pt）。在添加或编辑幻灯片前使用此工具了解结构（SLIDE）",
        effects="read",
    )
    async def slide_get_info(self, ctx, params: SlideGetInfoInput) -> Result:
        return await call(
            ctx, "slide_get_info", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="slide_get_page_info",
        description="获取指定幻灯片上所有形状的摘要信息和动画列表。返回数据包含：shapes: 每个形状的 id / 类型 / 位置 / 尺寸 / 文本 / 填充色 / 边框等 16 个字段；animations: 每页的动画序列，每个动画含 shape_id / index / seq_type / category / preset_id / preset_subtype。如果不需要批量、只需要单页信息，直接传 page_index 调用本工具即可；如果只需要总页数/页列表，先调 slide_get_info 即可。【限制】大演示文稿（100+ 页）建议分页获取（SLIDE）",
        effects="read",
    )
    async def slide_get_page_info(self, ctx, params: SlideGetPageInfoInput) -> Result:
        return await call(
            ctx,
            "slide_get_page_info",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_shape_info",
        description="查询指定幻灯片中某个形状的详细信息（包含 type / preset_geom / bounds / text / fill / border / 字体属性 等 16 个字段）。仅支持 SHAPE / CONNECTOR / PICTURE 三种类型；其他类型（如 GROUP / TABLE / CHART）返回的 type 字段会标识为对应类型，但部分字段（fill / border 等）可能为空（SLIDE）",
        effects="read",
    )
    async def slide_get_shape_info(self, ctx, params: SlideGetShapeInfoInput) -> Result:
        return await call(
            ctx,
            "slide_get_shape_info",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_text",
        description="查询指定 shape 或表格单元格的文本内容与格式属性。表格须传 row/col。返回 UTF-8 文本、UTF-16 长度、run/paragraph 区间；index/count 须以该 UTF-16 长度为准（含末尾 \\r），不要用 slide_get_table_info 的纯文本长度（SLIDE）",
        effects="read",
    )
    async def slide_get_text(self, ctx, params: SlideGetTextInput) -> Result:
        return await call(
            ctx, "slide_get_text", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(name="slide_find_text", description="在演示文稿中查找文本（SLIDE）", effects="read")
    async def slide_find_text(self, ctx, params: SlideFindTextInput) -> Result:
        return await call(
            ctx,
            "slide_find_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_find_replace_text",
        description="在指定页查找并替换文本（SLIDE）",
        effects="write",
    )
    async def slide_find_replace_text(self, ctx, params: SlideFindReplaceTextInput) -> Result:
        return await call(
            ctx,
            "slide_find_replace_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_text",
        description="在指定幻灯片插入一个文本框。x/y/w/h 单位为磅（pt，1pt = 12700 EMU），w/h 必须 > 0；text 为空串表示空文本框；font_color / fill_color / border_color 均为 6 位 hex（无 # 前缀）；font_size 单位为 pt，<= 0 取默认字号；border_width 单位为 pt，<= 0 取默认 1.0（SLIDE）",
        effects="write",
    )
    async def slide_add_text(self, ctx, params: SlideAddTextInput) -> Result:
        return await call(
            ctx, "slide_add_text", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="slide_insert_text",
        description="在指定 shape 文本位置插入文本（SLIDE）",
        effects="write",
    )
    async def slide_insert_text(self, ctx, params: SlideInsertTextInput) -> Result:
        return await call(
            ctx,
            "slide_insert_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_text_property",
        description="在不修改文本内容的前提下，对形状或表格单元格内指定字符范围设置富文本样式。表格须额外传 row/col（0-based，合并单元格用左上角）。index 和 count 以 UTF-16 码元为单位（与 slide_get_text 返回的单位一致）。仅传入的字段会被修改。支持三种模式：(A) 单目标——传 shape_id + index + count + 样式属性（表格再加 row/col）；(B) 批量一对一——传 shapes 数组；(C) 批量多对一——传 shape_ids。批量模式下所有变更合并为一个撤销单元 / 一次 SSE 广播（SLIDE）",
        effects="write",
    )
    async def slide_set_text_property(self, ctx, params: SlideSetTextPropertyInput) -> Result:
        return await call(
            ctx,
            "slide_set_text_property",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_image",
        description="在指定幻灯片插入一张图片。【图片来源选择优先级（按推荐顺序）】方式一（⭐首选）：本地脚本（insert_image.py）通过 HTTP 直接调用 MCP endpoint 插入图片，无需把图片 base64 通过 MCP 通道透传，避免大图触发上下文/传输限制，速度也更快。方式二（备选）：传 image_id —— 当无法在本地执行脚本，但可以先通过 upload_image MCP 工具或腾讯文档开放平台 OpenAPI 把图片上传后获取 image_id 时使用。方式三（兜底）：传 content（图片 base64 字符串，不含 data URI 前缀）—— 仅适合图片体积较小的场景；若 base64 超出 MCP 单次传输限制会失败，此时请回退到方式一脚本调用。【限制】单张图片大小不超过 10MB；支持 PNG / JPG / JPEG / GIF / BMP / WEBP / SVG 格式；【⭐图片等比缩放（强制，禁止违反）】入参 w / h 必须严格保持图片原始宽高比（uniform scale only）：即 w / h == 原图 width / height；绝对禁止只调宽不调高、或只调高不调宽——任何横向单独缩放/纵向单独缩放都会导致图片变形，属于硬性禁令；推荐做法：先取得图片原始尺寸，按目标占位框 (W,H) 计算 s = min(W/origW, H/origH)，最终传入 w = origW * s，h = origH * s；简化：若仅指定 w，则按 h = w * origH / origW 推算 h；仅指定 h 同理；w / h 同时 <= 0 时使用图片自身原始尺寸；如果图片在目标占位框内放不下（按等比缩放后会留大块空白或溢出画布），禁止通过非等比拉伸强行填满——应重新设计该页面布局；画布默认 16:9 = 960 x 540 pt；调用 slide_get_page_info 获取实际尺寸后再决定占位框范围。（SLIDE）",
        effects="write",
    )
    async def slide_add_image(self, ctx, params: SlideAddImageInput) -> Result:
        return await call(
            ctx,
            "slide_add_image",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_shape",
        description='在指定幻灯片插入一个普通形状（rect / ellipse / triangle 等图形预设块）。【重要】必须设置 fill_color 或 border_color 中的至少一个，否则形状对用户不可见，调用会被拒绝。【重要】创建时 fill_alpha 仅支持 0~50；如需 51~100，先创建形状，再调用 slide_set_shape_properties 修改。【重要 — 箭头消歧】本工具不支持画两点之间的方向性箭头线条，仅支持 rightArrow / leftArrow 这两种固定方向的图形预设箭头块；如需画"从起点到终点的箭头线"，请改用 slide_add_line_shape 并设置 line_type=arrow / doubleArrow。当用户说"加箭头"时，请先询问要的是"线条箭头"（带起点终点）还是"图形箭头"（固定方向的图形块）再决定调哪个工具。page_index 从 0 开始；x/y/w/h 单位为磅（pt，1pt = 12700 EMU）；border_alpha 取值 0~100；border_width 单位为 pt（SLIDE）',
        effects="write",
    )
    async def slide_add_shape(self, ctx, params: SlideAddShapeInput) -> Result:
        return await call(
            ctx,
            "slide_add_shape",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_shapes",
        description='批量在同一幻灯片插入多个形状。shapes 为对象数组，单个对象的字段含义同 slide_add_shape（不再接受 file_id 等顶层字段）。长度必须 >= 1。【重要】每个形状必须设置 fill_color 或 border_color 中的至少一个，否则形状对用户不可见，调用会被拒绝；每个形状的 fill_alpha 仅支持 0~50，如需 51~100 请在创建后使用 slide_set_shape_properties 修改。【重要 — 箭头消歧，与 slide_add_shape 完全一致】本工具仅支持 rightArrow / leftArrow 这两种图形预设箭头块；批量画"从起点到终点的箭头线"请改用 slide_add_line_shapes 并设置 line_type=arrow / doubleArrow。用户说"加箭头"时请先确认要"线条箭头"还是"图形箭头"（SLIDE）',
        effects="write",
    )
    async def slide_add_shapes(self, ctx, params: SlideAddShapesInput) -> Result:
        return await call(
            ctx,
            "slide_add_shapes",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_remove_shapes",
        description="从指定幻灯片删除一个或多个形状。shape_ids 为待删除的形状 ID 列表，长度必须 >= 1（SLIDE）",
        effects="write",
    )
    async def slide_remove_shapes(self, ctx, params: SlideRemoveShapesInput) -> Result:
        return await call(
            ctx,
            "slide_remove_shapes",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_move_slide",
        description="将一个或多个幻灯片页面移动至演示文稿中的新位置。请务必首先调用 slide_get_sections 和 slide_get_info，以获取当前的章节列表和幻灯片索引。请在 before_slide_index 和 after_section_id 这两个参数中仅选择其中一个进行提供，以指定被移动幻灯片的最终落点位置。（SLIDE）",
        effects="write",
    )
    async def slide_move_slide(self, ctx, params: SlideMoveSlideInput) -> Result:
        return await call(
            ctx,
            "slide_move_slide",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_remove_slide",
        description="删除指定位置的幻灯片。page_index 为 0-based 页索引（SLIDE）",
        effects="write",
    )
    async def slide_remove_slide(self, ctx, params: SlideRemoveSlideInput) -> Result:
        return await call(
            ctx,
            "slide_remove_slide",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_comments",
        description="获取全部批注或指定页批注。page_index 未传或传 -1 返回全部页批注，传 N 只返回第 N+1 页（SLIDE）",
        effects="read",
    )
    async def slide_get_comments(self, ctx, params: SlideGetCommentsInput) -> Result:
        return await call(
            ctx,
            "slide_get_comments",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_duplicate_slide",
        description="深拷贝一张或多张幻灯片，副本插入在各自原始页的紧后方（或 target_page_index 指定的位置），保留所有形状、文本、动画和样式。page_indexes 和 target_page_index 均为 0-based 索引（SLIDE）",
        effects="write",
    )
    async def slide_duplicate_slide(self, ctx, params: SlideDuplicateSlideInput) -> Result:
        return await call(
            ctx,
            "slide_duplicate_slide",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_theme",
        description="设置演示文稿的主题。支持两种模式：(1) switch：传入已存在于文档中的 theme_id，切换到该主题；(2) builtin：is_builtin=true，传入内置主题 ID（可通过 slide_list_builtin_themes 获取），由服务端自动加载内置 ThemeElements（SLIDE）",
        effects="write",
    )
    async def slide_set_theme(self, ctx, params: SlideSetThemeInput) -> Result:
        return await call(
            ctx,
            "slide_set_theme",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_anim_properties",
        description="修改指定形状某个动画的类型和方向。index 为动画在序列中的索引（0-based）；anim_type 为新动画类型；anim_subtype 为新方向（0 表示不需要）（SLIDE）",
        effects="write",
    )
    async def slide_set_anim_properties(self, ctx, params: SlideSetAnimPropertiesInput) -> Result:
        return await call(
            ctx,
            "slide_set_anim_properties",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_line_shape",
        description='在指定幻灯片插入一根线形 / 方向性箭头线条（从 (x1,y1) 起点到 (x2,y2) 终点）。这是绘制"两点之间的箭头线"的正确工具：line_type=arrow 单端箭头、doubleArrow 双端箭头、line 普通直线。slide_add_shape 不能画这种线条箭头，它只支持 rightArrow / leftArrow 两种固定方向的图形块预设。x1/y1 / x2/y2 单位为磅（pt，1pt = 12700 EMU）；width 单位为 pt（SLIDE）',
        effects="write",
    )
    async def slide_add_line_shape(self, ctx, params: SlideAddLineShapeInput) -> Result:
        return await call(
            ctx,
            "slide_add_line_shape",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_remove_sections",
        description="删除一个或多个节但保留节内幻灯片（SLIDE）",
        effects="write",
    )
    async def slide_remove_sections(self, ctx, params: SlideRemoveSectionsInput) -> Result:
        return await call(
            ctx,
            "slide_remove_sections",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_group_info",
        description="获取指定 group shape 的子 shape 列表（SLIDE）",
        effects="read",
    )
    async def slide_get_group_info(self, ctx, params: SlideGetGroupInfoInput) -> Result:
        return await call(
            ctx,
            "slide_get_group_info",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_remove_section_with_slides",
        description="删除指定节，同时删除节内的所有幻灯片（不可恢复）。⚠️ 与 slide_remove_sections 行为不同：后者仅删除节本身、保留节内 slides；本工具会连带 slides 一起删除（SLIDE）",
        effects="write",
    )
    async def slide_remove_section_with_slides(
        self, ctx, params: SlideRemoveSectionWithSlidesInput
    ) -> Result:
        return await call(
            ctx,
            "slide_remove_section_with_slides",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_list_anim_types",
        description="列出所有支持的动画类型，包含类型名称、分类（entrance / exit / emphasis）以及是否支持方向参数。返回的 type 整数值可直接用于 slide_add_anim 的 anim_type 参数（SLIDE）",
        effects="read",
    )
    async def slide_list_anim_types(self, ctx, params: SlideListAnimTypesInput) -> Result:
        return await call(
            ctx,
            "slide_list_anim_types",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_reply_comment",
        description="向已有批注分组追加一条回复（SLIDE）",
        effects="write",
    )
    async def slide_reply_comment(self, ctx, params: SlideReplyCommentInput) -> Result:
        return await call(
            ctx,
            "slide_reply_comment",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_modify_comment",
        description="修改指定批注分组的文本 / 作者。⚠️ 覆盖式：传入空串会把对应字段清空，未传字段保持不变（SLIDE）",
        effects="write",
    )
    async def slide_modify_comment(self, ctx, params: SlideModifyCommentInput) -> Result:
        return await call(
            ctx,
            "slide_modify_comment",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_anim",
        description="为指定幻灯片中的某个形状添加动画效果。anim_type 为动画类型整数值（通过 slide_list_anim_types 获取可用值）；anim_subtype 为方向/子类型（仅 FLY_IN/FLY_OUT 等需要，0 表示不需要）；index 为动画在该页动画序列中的插入位置（0-based）：-1（默认）追加到末尾，0 插入到最前，正数 N 插入到第 N 位（SLIDE）",
        effects="write",
    )
    async def slide_add_anim(self, ctx, params: SlideAddAnimInput) -> Result:
        return await call(
            ctx, "slide_add_anim", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="slide_add_table",
        description="在指定幻灯片页创建空表格，page_index 从 0 开始计数；坐标与尺寸单位为磅（pt，1pt = 12700 EMU）（SLIDE）",
        effects="write",
    )
    async def slide_add_table(self, ctx, params: SlideAddTableInput) -> Result:
        return await call(
            ctx,
            "slide_add_table",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_insert_table_rows",
        description="在表格 shape 中插入一行或多行。index 是间隙位置：对 N 行表格，有效范围为 [0, N]；count 未传时默认 1；reference_row_index 指定复制高度的已有行（SLIDE）",
        effects="write",
    )
    async def slide_insert_table_rows(self, ctx, params: SlideInsertTableRowsInput) -> Result:
        return await call(
            ctx,
            "slide_insert_table_rows",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_move_anim",
        description="移动指定形状的动画在序列中的位置（从 from_index 移到 to_index）（SLIDE）",
        effects="write",
    )
    async def slide_move_anim(self, ctx, params: SlideMoveAnimInput) -> Result:
        return await call(
            ctx,
            "slide_move_anim",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_datetime",
        description="在指定幻灯片插入日期时间占位符。display_text 为可选的显示文本，如 2026/05/11；为空时引擎保留空内容（SLIDE）",
        effects="write",
    )
    async def slide_add_datetime(self, ctx, params: SlideAddDatetimeInput) -> Result:
        return await call(
            ctx,
            "slide_add_datetime",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_delete_table_rows",
        description="从表格 shape 中删除一行或多行，从 index 指定的行开始；count 未传时默认 1，index + count 不能超过当前行数（SLIDE）",
        effects="write",
    )
    async def slide_delete_table_rows(self, ctx, params: SlideDeleteTableRowsInput) -> Result:
        return await call(
            ctx,
            "slide_delete_table_rows",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_sections", description="获取演示文稿中的全部节（SLIDE）", effects="read"
    )
    async def slide_get_sections(self, ctx, params: SlideGetSectionsInput) -> Result:
        return await call(
            ctx,
            "slide_get_sections",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_notes_text",
        description="设置或覆盖指定幻灯片的备注页（演讲者备注）文本，page_index 从 0 开始计数；text 为空字符串时表示清空备注页文本。【使用场景说明】① 如果需要修改已有备注（局部编辑、重新排版、替换某段文字等），请先调用 slide_get_notes_text 读取当前内容，在本地完成修改后，再调用本工具将完整新文本一次性写回；② 如果只需要在现有备注末尾追加内容，请直接使用 slide_append_notes_text，无需先 get 再 set；③ 本工具会完整覆盖当前备注，调用前未读取原文则原有内容将丢失，请谨慎使用（SLIDE）",
        effects="write",
    )
    async def slide_set_notes_text(self, ctx, params: SlideSetNotesTextInput) -> Result:
        return await call(
            ctx,
            "slide_set_notes_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_rename_section", description="修改指定节的名称（SLIDE）", effects="write"
    )
    async def slide_rename_section(self, ctx, params: SlideRenameSectionInput) -> Result:
        return await call(
            ctx,
            "slide_rename_section",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_comment", description="在指定幻灯片上添加批注锚点（SLIDE）", effects="write"
    )
    async def slide_add_comment(self, ctx, params: SlideAddCommentInput) -> Result:
        return await call(
            ctx,
            "slide_add_comment",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_unmerge_table_cells",
        description="取消表格 shape 中指定矩形区域的单元格合并，区域由 start_row/start_col 和 row_span/col_span 指定（SLIDE）",
        effects="write",
    )
    async def slide_unmerge_table_cells(self, ctx, params: SlideUnmergeTableCellsInput) -> Result:
        return await call(
            ctx,
            "slide_unmerge_table_cells",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_shape_properties",
        description='修改幻灯片中一个或多个形状的属性。支持三种使用模式：(A) 单形状模式：传入 shape_id + 属性字段（位置/尺寸/旋转/填充/边框）。(B) 批量一对一模式：传入 shapes 数组，每项包含 shape_id 及各自的属性（填充/边框/位置/尺寸/旋转）。视觉属性变更合并为一次撤销单元，transform 变更合并为另一次撤销单元。(C) 批量多对一模式：传入 shape_ids 数组 + 顶层属性，所有形状统一应用相同变更。未指定的属性保持不变。形状类型支持说明：- 普通形状(shape/connector)：支持 fill_color / fill_alpha / border_color / border_alpha / border_width / border_dash / 位置尺寸旋转。- 图片形状(picture)：支持 fill_alpha（控制整张图片透明度）/ border_color / border_alpha / border_width / border_dash / 位置尺寸旋转；不支持 fill_color（图片颜色由图片本身决定）。- 其他类型（表格、图表等）：仅支持位置/尺寸/旋转，不支持 fill/border 颜色属性。坐标 / 尺寸单位为磅（pt，1pt = 12700 EMU）；rotation 单位为度；border_width 单位为磅（pt）；border_dash 为 OOXML STPresetLineDashVal 字符串（如 "solid" / "dash" / "dashDot"）（SLIDE）',
        effects="write",
    )
    async def slide_set_shape_properties(self, ctx, params: SlideSetShapePropertiesInput) -> Result:
        return await call(
            ctx,
            "slide_set_shape_properties",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_page_properties",
        description="设置幻灯片页面级属性，包括背景填充（纯色/图片/渐变）和可见性。仅修改传入的属性，未传的保持不变。",
        effects="write",
    )
    async def slide_set_page_properties(self, ctx, params: SlideSetPagePropertiesInput) -> Result:
        return await call(
            ctx,
            "slide_set_page_properties",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_undo_ai_edit",
        description="撤销指定 version 的 AI 编辑（SLIDE）。\n\n【前置条件（必须）】\n调用本工具前，必须先调 slide_list_recent_ai_edits 列出最近 AI 编辑，\n根据 tool_name / tool_args 定位用户要撤销的具体操作，再取其 version 作为 target_version。\n禁止凭记忆直接填写 target_version。\n\n【可撤销范围】\n仅可撤销 Redis 中仍保留的 edit（每个文档最近 200 条，7 天 TTL）；超出保留窗口的 edit 无法撤销。\n\n【行为说明】\n采用 git revert 风格：取目标 revision 的反向命令，与之后的 revisions 做 OT 冲突处理后，\n作为新 revision 写入文档；不会删除任何历史 revision。\n成功后会写入一条新 revision（version 递增），行为与一次正常写一致；本次撤销也可被后续撤销。\n\n【失败原因】\n(1) 目标 revision 包含暂不支持反向计算的 mutation 类型；\n(2) 反向命令在当前文档上无法合法执行；\n(3) 目标 revision 的全部改动已被后续编辑覆盖（OT 后全部 noop）；\n(4) target_version 不在当前版本范围内，或对应 edit 已不在保留窗口内。",
        effects="write",
    )
    async def slide_undo_ai_edit(self, ctx, params: SlideUndoAiEditInput) -> Result:
        return await call(
            ctx,
            "slide_undo_ai_edit",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_list_recent_ai_edits",
        description='列出文档最近通过 MCP 写工具产生的 AI 编辑记录（SLIDE）。\n返回每条记录的 version + tool_name + time + tool_args（按时间倒序）。\n撤销某次 AI 操作前，必须先调本工具：在返回列表中按 tool_name / tool_args 与用户描述匹配，\n确认具体操作及其 version，再调 slide_undo_ai_edit(target_version=该 version)。\n禁止跳过本工具直接撤销；禁止凭记忆填写 target_version。\n【典型用法】\n当用户要求「撤销刚才的 X 操作」时：\n1. 调本工具（limit 默认 10），拿到最近若干次 AI 编辑（可用 tool_name 进行过滤）；\n2. 在列表中按 tool_name / tool_args 匹配用户描述，定位 target_version；\n3. 调 slide_undo_ai_edit(file_id, target_version=匹配到的 version) 完成撤销。\n【限制】\n(1) 仅记录通过 MCP 写工具产生的编辑，前端手动编辑 / 程序化 CommitRevision 等其他写不在内；\n(2) Redis 存储，7 天 TTL；每个文档最多保留最近 200 条，只能撤销这 200 条内的 edit；\n(3) 部分工具的 tool_args 会截断，不会完整记录；\n(4) limit 缺省 10，上限 50；tool_name 为可选精确过滤（例如 "slide_add_image"）。',
        effects="read",
    )
    async def slide_list_recent_ai_edits(self, ctx, params: SlideListRecentAiEditsInput) -> Result:
        return await call(
            ctx,
            "slide_list_recent_ai_edits",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_slide_size",
        description="设置演示文稿页面尺寸，仅支持 16:9 和 4:3 两种比例（SLIDE）",
        effects="write",
    )
    async def slide_set_slide_size(self, ctx, params: SlideSetSlideSizeInput) -> Result:
        return await call(
            ctx,
            "slide_set_slide_size",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_footer",
        description="在指定幻灯片添加或移除页脚占位符。show=true（默认）时插入页脚占位符并写入 display_text；show=false 时移除已有页脚占位符。位置和样式从布局/母版继承（SLIDE）",
        effects="write",
    )
    async def slide_add_footer(self, ctx, params: SlideAddFooterInput) -> Result:
        return await call(
            ctx,
            "slide_add_footer",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_change_chart_type", description="更改指定图表类型（SLIDE）", effects="write"
    )
    async def slide_change_chart_type(self, ctx, params: SlideChangeChartTypeInput) -> Result:
        return await call(
            ctx,
            "slide_change_chart_type",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_texts",
        description="批量在同一张幻灯片插入多个文本框，单次产生一个 SlideCommand（一次广播），比循环调用 slide_add_text 更高效。texts 为对象数组，单元素字段含义同 slide_add_text（不再接受 file_id 等顶层字段）。长度必须 >= 1（SLIDE）",
        effects="write",
    )
    async def slide_add_texts(self, ctx, params: SlideAddTextsInput) -> Result:
        return await call(
            ctx,
            "slide_add_texts",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_reorder_shapes_in_group",
        description="调整分组内子 shape 层级（SLIDE）",
        effects="write",
    )
    async def slide_reorder_shapes_in_group(
        self, ctx, params: SlideReorderShapesInGroupInput
    ) -> Result:
        return await call(
            ctx,
            "slide_reorder_shapes_in_group",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_reorder_shape",
        description="调整指定形状的 z-order 层级。op 取值：0=置于底层 / 1=下移一层 / 2=上移一层 / 3=置于顶层。shape_ids 为待调整顺序的形状 ID 列表，长度必须 >= 1（SLIDE）",
        effects="write",
    )
    async def slide_reorder_shape(self, ctx, params: SlideReorderShapeInput) -> Result:
        return await call(
            ctx,
            "slide_reorder_shape",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_themes",
        description="获取当前演示文稿中嵌入的所有主题列表，返回每个主题的 theme_id 和 theme_name（SLIDE）",
        effects="read",
    )
    async def slide_get_themes(self, ctx, params: SlideGetThemesInput) -> Result:
        return await call(
            ctx,
            "slide_get_themes",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_remove_anim",
        description="移除指定形状的某个动画。index 为动画在形状动画序列中的位置（0-based）（SLIDE）",
        effects="write",
    )
    async def slide_remove_anim(self, ctx, params: SlideRemoveAnimInput) -> Result:
        return await call(
            ctx,
            "slide_remove_anim",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_update_chart_data",
        description="替换指定图表的内嵌数据（SLIDE）",
        effects="write",
    )
    async def slide_update_chart_data(self, ctx, params: SlideUpdateChartDataInput) -> Result:
        return await call(
            ctx,
            "slide_update_chart_data",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_merge_table_cells",
        description="合并表格 shape 中的矩形单元格区域，区域由 start_row/start_col 和 row_span/col_span 指定；合并后内容来自左上角单元格（SLIDE）",
        effects="write",
    )
    async def slide_merge_table_cells(self, ctx, params: SlideMergeTableCellsInput) -> Result:
        return await call(
            ctx,
            "slide_merge_table_cells",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_anim_trigger",
        description='修改指定形状某个动画的触发方式。trigger_shape_id 为触发形状 ID，空串表示设为默认触发（即"单击"播放，跟随默认序列）（SLIDE）',
        effects="write",
    )
    async def slide_set_anim_trigger(self, ctx, params: SlideSetAnimTriggerInput) -> Result:
        return await call(
            ctx,
            "slide_set_anim_trigger",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_insert_table_cols",
        description="在表格 shape 中插入一列或多列。index 是间隙位置：对 M 列表格，有效范围为 [0, M]；count 未传时默认 1；插入后表格总宽度保持不变并重新均分列宽（SLIDE）",
        effects="write",
    )
    async def slide_insert_table_cols(self, ctx, params: SlideInsertTableColsInput) -> Result:
        return await call(
            ctx,
            "slide_insert_table_cols",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_delete_text", description="删除指定 shape 文本区间（SLIDE）", effects="write"
    )
    async def slide_delete_text(self, ctx, params: SlideDeleteTextInput) -> Result:
        return await call(
            ctx,
            "slide_delete_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_notes",
        description="为指定幻灯片创建演讲者备注页并写入文本内容。text 为空串时创建空白备注页（SLIDE）",
        effects="write",
    )
    async def slide_add_notes(self, ctx, params: SlideAddNotesInput) -> Result:
        return await call(
            ctx,
            "slide_add_notes",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_section",
        description="在指定位置添加新节。提供 before_slide_index 或 after_section_id 之一来指定插入位置。\\n- before_slide_index: 新节将拥有目标页及其后续页面（直到下一个节边界）。原来拥有该页的节将从下一页开始。\\n- after_section_id: 新节作为空节插入到指定节之后，不会接管任何页面。",
        effects="write",
    )
    async def slide_add_section(self, ctx, params: SlideAddSectionInput) -> Result:
        return await call(
            ctx,
            "slide_add_section",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_list_builtin_themes",
        description="列出服务端所有内置（预置）主题，返回每个主题的 theme_id 和 theme_name；不依赖文档状态，可在调用 slide_set_theme 前用于查询可用的内置主题 ID（SLIDE）",
        effects="read",
    )
    async def slide_list_builtin_themes(self, ctx, params: SlideListBuiltinThemesInput) -> Result:
        return await call(
            ctx,
            "slide_list_builtin_themes",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_append_text",
        description="向指定 shape 文本末尾追加文本（SLIDE）",
        effects="write",
    )
    async def slide_append_text(self, ctx, params: SlideAppendTextInput) -> Result:
        return await call(
            ctx,
            "slide_append_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_remove_comment", description="删除指定批注分组（SLIDE）", effects="write"
    )
    async def slide_remove_comment(self, ctx, params: SlideRemoveCommentInput) -> Result:
        return await call(
            ctx,
            "slide_remove_comment",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_line_shapes",
        description='批量在同一幻灯片插入多根线形 / 方向性箭头线条。lines 为对象数组，单元素字段含义同 slide_add_line_shape。长度必须 >= 1。这是批量绘制"两点之间的方向性箭头线"的正确工具（line_type=arrow / doubleArrow）；slide_add_shapes 不能批量画线条箭头，它只支持 rightArrow / leftArrow 两种图形预设块（SLIDE）',
        effects="write",
    )
    async def slide_add_line_shapes(self, ctx, params: SlideAddLineShapesInput) -> Result:
        return await call(
            ctx,
            "slide_add_line_shapes",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_delete_table_cols",
        description="从表格 shape 中删除一列或多列，从 index 指定的列开始；count 未传时默认 1，index + count 不能超过当前列数（SLIDE）",
        effects="write",
    )
    async def slide_delete_table_cols(self, ctx, params: SlideDeleteTableColsInput) -> Result:
        return await call(
            ctx,
            "slide_delete_table_cols",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_update_group_shape_properties",
        description="更新分组视觉或变换属性（SLIDE）",
        effects="write",
    )
    async def slide_update_group_shape_properties(
        self, ctx, params: SlideUpdateGroupShapePropertiesInput
    ) -> Result:
        return await call(
            ctx,
            "slide_update_group_shape_properties",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_chart", description="在指定幻灯片上添加图表（SLIDE）", effects="write"
    )
    async def slide_add_chart(self, ctx, params: SlideAddChartInput) -> Result:
        return await call(
            ctx,
            "slide_add_chart",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_update_chart_style",
        description="增量更新指定图表样式（SLIDE）",
        effects="write",
    )
    async def slide_update_chart_style(self, ctx, params: SlideUpdateChartStyleInput) -> Result:
        return await call(
            ctx,
            "slide_update_chart_style",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_progress",
        description="查询AI幻灯片生成进度，与create_slide配合使用。通常由create_slide.js脚本自动调用，无需手动轮询。状态说明：status=in_progress进行中；status=completed已完成，幻灯片已生成，响应file_url；status=failed失败；status=not_found未找到(session_id不正确)。当status=completed时，直接将file_url结果输出给用户即可，不要再继续调用其他任何工具",
        effects="read",
    )
    async def slide_progress(self, ctx, params: SlideProgressInput) -> Result:
        return await call(
            ctx, "slide_progress", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="slide_set_default_font",
        description='设置演示文稿默认字体（SLIDE）。仅修改显式传入的字段，未传或空串/0 视为「不修改」；font_color 必须 6 位 hex（不含 # 前缀，如 "FF0000"）；font_size 单位 pt（>0）；spacing 单位 pt（如 3 表示 3pt，范围 -50~50）；bold / italic / spacing 直接传即可（内部自动映射到 options 子结构）',
        effects="write",
    )
    async def slide_set_default_font(self, ctx, params: SlideSetDefaultFontInput) -> Result:
        return await call(
            ctx,
            "slide_set_default_font",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_master_info",
        description="获取演示文稿中母版页的详细信息，包含母版 ID、页眉页脚状态、布局列表及母版上的形状。可选传 page_index 仅返回该页关联的母版（SLIDE）",
        effects="read",
    )
    async def slide_get_master_info(self, ctx, params: SlideGetMasterInfoInput) -> Result:
        return await call(
            ctx,
            "slide_get_master_info",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_get_chart_info", description="获取指定图表结构信息（SLIDE）", effects="read"
    )
    async def slide_get_chart_info(self, ctx, params: SlideGetChartInfoInput) -> Result:
        return await call(
            ctx,
            "slide_get_chart_info",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_move_section",
        description="移动指定节到新的节序号位置（SLIDE）",
        effects="write",
    )
    async def slide_move_section(self, ctx, params: SlideMoveSectionInput) -> Result:
        return await call(
            ctx,
            "slide_move_section",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_add_page_number",
        description="在指定幻灯片插入页码占位符，位置和样式从布局/母版继承（SLIDE）",
        effects="write",
    )
    async def slide_add_page_number(self, ctx, params: SlideAddPageNumberInput) -> Result:
        return await call(
            ctx,
            "slide_add_page_number",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_group_shapes",
        description="将同一页多个 shape 组合成 group shape（SLIDE）",
        effects="write",
    )
    async def slide_group_shapes(self, ctx, params: SlideGroupShapesInput) -> Result:
        return await call(
            ctx,
            "slide_group_shapes",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_ungroup_shapes", description="解散指定 group shape（SLIDE）", effects="write"
    )
    async def slide_ungroup_shapes(self, ctx, params: SlideUngroupShapesInput) -> Result:
        return await call(
            ctx,
            "slide_ungroup_shapes",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="slide_set_cell_text",
        description="向表格 shape 的单个单元格写入纯文本。row 和 col 从 0 开始计数；文本可为空，不需要传入段落结束符（SLIDE）",
        effects="write",
    )
    async def slide_set_cell_text(self, ctx, params: SlideSetCellTextInput) -> Result:
        return await call(
            ctx,
            "slide_set_cell_text",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )
