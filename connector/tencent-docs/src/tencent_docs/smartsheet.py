"""Generated from reviewed contracts; regenerate with tools/generate.py."""

from typing import Literal

from connector_sdk import operation
from pydantic import Field

from .mcp import call
from .models import Input, JsonValue, Result


class SmartsheetListTablesInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)


class SmartsheetGetDashboardComponentInput(Input):
    component_id: str = Field(description="仪表盘组件ID", max_length=100000)
    dashboard_id: str = Field(description="仪表盘子表ID", max_length=100000)
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)


class SmartsheetDeleteFieldsInput(Input):
    field_ids: list[str] = Field(description="字段ID组成的数组", max_length=100)
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="工作表ID", max_length=100000)


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemAutoNumberValue(Input):
    seq: str = Field(default=None, description="序号", max_length=100000)
    text: str = Field(default=None, description="内容", max_length=100000)


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemComputedValue(Input):
    bool_value: bool = Field(
        default=None, description="计算结果为布尔时的值，仅 has_bool 为 true 时有意义"
    )
    has_bool: bool = Field(default=None, description="计算结果是否为布尔类型")
    has_number: bool = Field(default=None, description="计算结果是否为数值类型")
    is_error: bool = Field(default=None, description="公式计算是否出错，为 true 时 text 为错误信息")
    number: float = Field(
        default=None, description="计算结果为数值时的原始数值，仅 has_number 为 true 时有意义"
    )
    text: str = Field(
        default=None,
        description="计算结果的展示文本，与表格中看到的内容一致，优先使用该字段",
        max_length=100000,
    )


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemImageValueItemsItem(Input):
    image_id: str = Field(
        default=None,
        description="图片ID，需要先调用 upload_image 工具上传图片获取",
        max_length=100000,
    )
    image_url: str = Field(default=None, description="图片访问URL", max_length=100000)
    title: str = Field(default=None, description="图片文件名", max_length=100000)


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemImageValue(Input):
    items: list[SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemImageValueItemsItem] = Field(
        default=None, description="图片值数组", max_length=100
    )


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemOptionValueItemsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: str = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
        max_length=100000,
    )
    text: str = Field(default=None, description="内容", max_length=100000)


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemOptionValue(Input):
    items: list[SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemOptionValueItemsItem] = Field(
        default=None, description="选项值数组", max_length=100
    )


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemReferenceValue(Input):
    items: list[str] = Field(default=None, description="字符串值数组", max_length=100)


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemTextValueItemsItem(Input):
    text: str = Field(default=None, description='文本内容，如："待办事项"', max_length=100000)
    type: str = Field(
        default=None,
        description='必填，固定值："text"。缺省或传其他值会报 22015 错误。完整格式：{"text":"内容","type":"text"}',
        max_length=100000,
    )


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemTextValue(Input):
    items: list[SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemTextValueItemsItem] = Field(
        default=None,
        description='文本值数组，每项格式：{"text":"内容","type":"text"}，type 必填且固定为 "text"',
        max_length=100,
    )


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemUrlValueItemsItem(Input):
    link: str = Field(default=None, description="超链接", max_length=100000)
    text: str = Field(default=None, description="内容", max_length=100000)
    type: str = Field(default=None, description="类型: url", max_length=100000)


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemUrlValue(Input):
    items: list[SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemUrlValueItemsItem] = Field(
        default=None, description="超链接值数组", max_length=100
    )


class SmartsheetUpdateRecordsInputRecordsItemFieldValuesItem(Input):
    auto_number_value: SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemAutoNumberValue = (
        Field(default=None, description="自动编号字段的值，自动编号字段无需传值，由服务端自动生成")
    )
    bool_value: bool = Field(
        default=None, description="布尔类型的值，如 true/false。用于复选框字段"
    )
    computed_value: SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemComputedValue = Field(
        default=None,
        description="公式/查找引用/关联记录等计算列的计算结果，只读，仅在 include_computed_values=true 时返回；不可用于写入",
    )
    field: str = Field(default=None, description="字段标题", max_length=100000)
    image_value: SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemImageValue = Field(
        default=None,
        description='图片类型的值列表，用于图片字段。items 每项传 {"image_id":"图片ID"}',
    )
    number_value: float = Field(
        default=None,
        description="数字类型的值，直接传数字，如 60。用于数字、进度、货币、百分数等字段",
    )
    option_value: SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemOptionValue = Field(
        default=None,
        description='选项类型的值列表，用于多选、单选字段。items 每项只需传 {"text":"选项文本"} 即可，id 由服务端解析，也可传 {"id":"选项ID"}',
    )
    reference_value: SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemReferenceValue = Field(
        default=None, description="关联记录ID列表，用于关联字段。items 传关联记录ID字符串数组"
    )
    string_value: str = Field(
        default=None,
        description='字符串类型的值，如 "1785686400000"（日期用毫秒级unix时间戳）。用于日期、电话、邮箱等字段',
        max_length=100000,
    )
    text_value: SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemTextValue = Field(
        default=None,
        description='文本类型的值列表，用于文本字段。items 每项格式：{"text":"内容","type":"text"}，type 必填且固定为 "text"，缺 type 会报 22015 错误',
    )
    url_value: SmartsheetUpdateRecordsInputRecordsItemFieldValuesItemUrlValue = Field(
        default=None,
        description='超链接类型的值列表，用于超链接字段。items 每项格式：{"text":"显示文本","type":"url","link":"https://..."}',
    )


class SmartsheetUpdateRecordsInputRecordsItem(Input):
    field_values: list[SmartsheetUpdateRecordsInputRecordsItemFieldValuesItem] = Field(
        default=None, description="字段值列表，每个元素包含字段标题和对应的值", max_length=100
    )
    record_id: str = Field(default=None, description="记录 ID", max_length=100000)


class SmartsheetUpdateRecordsInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    records: list[SmartsheetUpdateRecordsInputRecordsItem] = Field(
        description="要更新的记录信息列表", max_length=100
    )
    sheet_id: str = Field(description="工作表ID", max_length=100000)


class SmartsheetListRecordsInputSortItem(Input):
    desc: bool = Field(default=None, description="是否进行降序排序，默认值为 false")
    field_title: str = Field(default=None, description="需要排序的字段标题", max_length=100000)


class SmartsheetListRecordsInput(Input):
    field_titles: list[str] = Field(
        default=None, description="由字段标题组成的数组", max_length=100
    )
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    include_computed_values: bool = Field(
        default=None,
        description="可选，默认 false。为 true 时额外返回公式、查找引用、双向关联等计算列的计算结果（见 computed_value.text）。开启会增加请求耗时，建议配合 field_titles 只取需要的列；不需要读取这些列的结果时不要开启",
    )
    limit: int = Field(
        default=None,
        description="分页大小，每页返回多少条数据；当不填写该参数或将该参数设置为0时，如果总数大于100，一次性返回100行记录，当总数小于100时，返回全部记录；limit最大值为100",
    )
    offset: int = Field(default=None, description="偏移量，初始值为0")
    record_ids: list[str] = Field(default=None, description="由记录ID组成的数组", max_length=100)
    sheet_id: str = Field(description="工作表ID", max_length=100000)
    sort: list[SmartsheetListRecordsInputSortItem] = Field(
        default=None, description="对返回记录进行排序", max_length=100
    )
    view_id: str = Field(
        default=None,
        description="视图ID。决定返回记录的行顺序；有用户选区时必须传 selection.viewId。省略时按首个视图排序",
        max_length=100000,
    )


class SmartsheetCreateAutomationFromPlanInput(Input):
    automation_plan: str = Field(
        description="一条完整自动化规划文本。首期仅允许：新增记录、修改记录、到达记录时间触发；查找记录、新增记录、修改记录、发送消息动作。不支持 Webhook、HTTP 请求、运行脚本、创建群、添加群成员、复杂 JSON 引用和仪表盘截图消息。创建默认关闭",
        max_length=100000,
    )
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)


class SmartsheetListViewsInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    limit: int = Field(default=None, description="分页大小 最大为100")
    offset: int = Field(default=None, description="分页查询偏移量")
    sheet_id: str = Field(description="工作表ID", max_length=100000)
    view_ids: list[str] = Field(default=None, description="需要查询的视图 ID 数组", max_length=100)


class SmartsheetGetDashboardInput(Input):
    dashboard_id: str = Field(description="仪表盘子表ID", max_length=100000)
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    limit: int = Field(
        default=None,
        description="分页大小，每页返回多少条数据；当不填写该参数或将该参数设置为0时，默认返回100条；limit最大值为100",
    )
    offset: int = Field(default=None, description="偏移量，初始值为0")


class SmartsheetCommitChangesetInput(Input):
    base_rev: int = Field(description="本次提交的基础修订版本号，即客户端当前持有的最新版本号")
    changeset: str = Field(description="mutation 数据，JSON 格式字符串", max_length=100000)
    pad_id: str = Field(description="智能表文档的唯一标识符", max_length=100000)
    sub_id: str = Field(description="子表 ID", max_length=100000)


class SmartsheetFetchInput(Input):
    calc_version: int = Field(default=None, description="计算版本")
    enable_chunk_rank: bool = Field(default=None, description="是否允许分片下发 rank")
    end_row: int = Field(default=None, description="结束行（不含），用于分页拉取，不填则返回全部行")
    is_perm_calc_by_srv: bool = Field(
        default=None, description="是否服务端判权，为 true 时不返回完整的判权列数据"
    )
    max_cell_per_mutation: int = Field(
        default=None, description="optimized_ver=3 时前端传入的分割单元格设置"
    )
    need_latest: bool = Field(
        default=None, description="是否需要最新的版本，为 true 时忽略 revision_version"
    )
    need_workbook: bool = Field(default=None, description="是否需要返回 workbook 数据")
    not_use_cache: int = Field(default=None, description="后台缓存开关，0 为默认使用缓存")
    optimized_ver: int = Field(default=None, description="优化版本开关，控制数据下发模式")
    pad_id: str = Field(description="智能表文档的唯一标识符", max_length=100000)
    page_ctx: str = Field(
        default=None,
        description="分页上下文，首次请求为空，后续请求传入上次返回的 page_ctx",
        max_length=100000,
    )
    revision_version: int = Field(
        default=None, description="文档修订版本号，为 0 时配合 need_latest 使用"
    )
    start_row: int = Field(
        default=None, description="起始行（从 0 开始），用于分页拉取，不填则从第 0 行开始"
    )
    sub_id: str = Field(description="子表 ID", max_length=100000)
    view_id: str = Field(default=None, description="视图 ID，为空时使用默认视图", max_length=100000)


class SmartsheetListAutomationsInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)


class SmartsheetUpdateAutomationFromPlanInput(Input):
    automation_plan: str = Field(
        description="一条完整自动化规划文本。更新采用完整替换：系统会先读取现有流程，再编译出完整 WorkflowData 后更新；当前会保留原自动化的启停状态。首期支持范围与创建工具相同",
        max_length=100000,
    )
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    workflow_id: str = Field(description="要更新的自动化流程 ID", max_length=100000)


class SmartsheetAddTableInputProperties(Input):
    index: int = Field(default=None, description="工作表下标")
    sheet_id: str = Field(default=None, description="工作表唯一标识符", max_length=100000)
    title: str = Field(default=None, description="工作表标题", max_length=100000)


class SmartsheetAddTableInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    properties: SmartsheetAddTableInputProperties = Field(description="工作表属性配置")


class SmartsheetUpdateViewInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    patch_json: str = Field(
        description="视图局部更新 JSON 字符串。顶层仅支持 title、filter、sort、group、fields、frozen_field_count；sort 使用 items:[{field_id,direction}]，direction 仅支持 asc 或 desc，field_id 必须来自 smartsheet.list_fields 且不可重复；不要直接传入 infos、sortInfos 或 list_views 返回的完整 view.config；仅支持非 query 视图",
        max_length=100000,
    )
    sheet_id: str = Field(description="工作表ID", max_length=100000)
    view_id: str = Field(
        description="要更新的视图ID；调用前必须先通过 list_views 获取当前配置", max_length=100000
    )


class SmartsheetDeleteTableInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="要删除的工作表ID", max_length=100000)


class SmartsheetDeleteAutomationInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    workflow_id: str = Field(
        description="要删除的自动化流程 ID；先调用 list_automations 按名称确认", max_length=100000
    )


class SmartsheetDeleteRecordsInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    record_ids: list[str] = Field(description="要删除的记录ID列表", max_length=100)
    sheet_id: str = Field(description="工作表ID", max_length=100000)


class SmartsheetListFieldsInput(Input):
    field_ids: list[str] = Field(default=None, description="由字段ID组成的数组", max_length=100)
    field_titles: list[str] = Field(
        default=None, description="由字段标题组成的数组", max_length=100
    )
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    limit: int = Field(
        default=None,
        description="分页大小，每页返回多少条数据；当不填写该参数或将该参数设置为0时，如果总数大于100，一次性返回100个字段，当总数小于100时，返回全部字段；limit最大值为100",
    )
    offset: int = Field(default=None, description="偏移量，初始值为0")
    sheet_id: str = Field(description="工作表ID", max_length=100000)
    view_id: str = Field(
        default=None,
        description="视图ID。决定返回字段的列顺序；有用户选区时必须传 selection.viewId。省略时按首个公开视图排序",
        max_length=100000,
    )


class SmartsheetDeleteDashboardComponentInput(Input):
    component_id: str = Field(description="要删除的仪表盘组件ID", max_length=100000)
    dashboard_id: str = Field(description="仪表盘子表ID", max_length=100000)
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)


class SmartsheetGetClientVarInput(Input):
    pad_id: str = Field(description="智能表文档的唯一标识符", max_length=100000)


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemAutoNumberValue(Input):
    seq: str = Field(default=None, description="序号", max_length=100000)
    text: str = Field(default=None, description="内容", max_length=100000)


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemComputedValue(Input):
    bool_value: bool = Field(
        default=None, description="计算结果为布尔时的值，仅 has_bool 为 true 时有意义"
    )
    has_bool: bool = Field(default=None, description="计算结果是否为布尔类型")
    has_number: bool = Field(default=None, description="计算结果是否为数值类型")
    is_error: bool = Field(default=None, description="公式计算是否出错，为 true 时 text 为错误信息")
    number: float = Field(
        default=None, description="计算结果为数值时的原始数值，仅 has_number 为 true 时有意义"
    )
    text: str = Field(
        default=None,
        description="计算结果的展示文本，与表格中看到的内容一致，优先使用该字段",
        max_length=100000,
    )


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemImageValueItemsItem(Input):
    image_id: str = Field(
        default=None,
        description="图片ID，需要先调用 upload_image 工具上传图片获取",
        max_length=100000,
    )
    image_url: str = Field(default=None, description="图片访问URL", max_length=100000)
    title: str = Field(default=None, description="图片文件名", max_length=100000)


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemImageValue(Input):
    items: list[SmartsheetAddRecordsInputRecordsItemFieldValuesItemImageValueItemsItem] = Field(
        default=None, description="图片值数组", max_length=100
    )


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemOptionValueItemsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: str = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
        max_length=100000,
    )
    text: str = Field(default=None, description="内容", max_length=100000)


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemOptionValue(Input):
    items: list[SmartsheetAddRecordsInputRecordsItemFieldValuesItemOptionValueItemsItem] = Field(
        default=None, description="选项值数组", max_length=100
    )


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemReferenceValue(Input):
    items: list[str] = Field(default=None, description="字符串值数组", max_length=100)


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemTextValueItemsItem(Input):
    text: str = Field(default=None, description='文本内容，如："待办事项"', max_length=100000)
    type: str = Field(
        default=None,
        description='必填，固定值："text"。缺省或传其他值会报 22015 错误。完整格式：{"text":"内容","type":"text"}',
        max_length=100000,
    )


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemTextValue(Input):
    items: list[SmartsheetAddRecordsInputRecordsItemFieldValuesItemTextValueItemsItem] = Field(
        default=None,
        description='文本值数组，每项格式：{"text":"内容","type":"text"}，type 必填且固定为 "text"',
        max_length=100,
    )


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemUrlValueItemsItem(Input):
    link: str = Field(default=None, description="超链接", max_length=100000)
    text: str = Field(default=None, description="内容", max_length=100000)
    type: str = Field(default=None, description="类型: url", max_length=100000)


class SmartsheetAddRecordsInputRecordsItemFieldValuesItemUrlValue(Input):
    items: list[SmartsheetAddRecordsInputRecordsItemFieldValuesItemUrlValueItemsItem] = Field(
        default=None, description="超链接值数组", max_length=100
    )


class SmartsheetAddRecordsInputRecordsItemFieldValuesItem(Input):
    auto_number_value: SmartsheetAddRecordsInputRecordsItemFieldValuesItemAutoNumberValue = Field(
        default=None, description="自动编号字段的值，自动编号字段无需传值，由服务端自动生成"
    )
    bool_value: bool = Field(
        default=None, description="布尔类型的值，如 true/false。用于复选框字段"
    )
    computed_value: SmartsheetAddRecordsInputRecordsItemFieldValuesItemComputedValue = Field(
        default=None,
        description="公式/查找引用/关联记录等计算列的计算结果，只读，仅在 include_computed_values=true 时返回；不可用于写入",
    )
    field: str = Field(default=None, description="字段标题", max_length=100000)
    image_value: SmartsheetAddRecordsInputRecordsItemFieldValuesItemImageValue = Field(
        default=None,
        description='图片类型的值列表，用于图片字段。items 每项传 {"image_id":"图片ID"}',
    )
    number_value: float = Field(
        default=None,
        description="数字类型的值，直接传数字，如 60。用于数字、进度、货币、百分数等字段",
    )
    option_value: SmartsheetAddRecordsInputRecordsItemFieldValuesItemOptionValue = Field(
        default=None,
        description='选项类型的值列表，用于多选、单选字段。items 每项只需传 {"text":"选项文本"} 即可，id 由服务端解析，也可传 {"id":"选项ID"}',
    )
    reference_value: SmartsheetAddRecordsInputRecordsItemFieldValuesItemReferenceValue = Field(
        default=None, description="关联记录ID列表，用于关联字段。items 传关联记录ID字符串数组"
    )
    string_value: str = Field(
        default=None,
        description='字符串类型的值，如 "1785686400000"（日期用毫秒级unix时间戳）。用于日期、电话、邮箱等字段',
        max_length=100000,
    )
    text_value: SmartsheetAddRecordsInputRecordsItemFieldValuesItemTextValue = Field(
        default=None,
        description='文本类型的值列表，用于文本字段。items 每项格式：{"text":"内容","type":"text"}，type 必填且固定为 "text"，缺 type 会报 22015 错误',
    )
    url_value: SmartsheetAddRecordsInputRecordsItemFieldValuesItemUrlValue = Field(
        default=None,
        description='超链接类型的值列表，用于超链接字段。items 每项格式：{"text":"显示文本","type":"url","link":"https://..."}',
    )


class SmartsheetAddRecordsInputRecordsItem(Input):
    before_record_id: str = Field(
        default=None,
        description="可选。插入到该 record_id 之前；省略则追加到表格末尾。批量添加时，相同 before_record_id 的多条记录按数组顺序连续插在锚点前。须先通过 list_records 取得目标 record_id。",
        max_length=100000,
    )
    field_values: list[SmartsheetAddRecordsInputRecordsItemFieldValuesItem] = Field(
        default=None, description="字段值列表，每个元素包含字段标题和对应的值", max_length=100
    )


class SmartsheetAddRecordsInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    records: list[SmartsheetAddRecordsInputRecordsItem] = Field(
        description="需要添加的记录的具体内容组成的数组", max_length=100
    )
    sheet_id: str = Field(description="工作表ID", max_length=100000)


class SmartsheetCreateTableFromPlanInputProperties(Input):
    index: int = Field(default=None, description="工作表下标")
    sheet_id: str = Field(default=None, description="工作表唯一标识符", max_length=100000)
    title: str = Field(default=None, description="工作表标题", max_length=100000)


class SmartsheetCreateTableFromPlanInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    properties: SmartsheetCreateTableFromPlanInputProperties = Field(
        default=None, description="工作表插入位置；可空，sheet_id 和 title 留空时由规划文本补齐"
    )
    table_plan: str = Field(
        description="智能表规划文本，描述要创建的工作表结构（含表格标题、字段列表、视图列表等）；一次调用仅创建一张工作表，若规划文本包含多张表格，请将每张表格的规划文本拆分后分别调用本工具",
        max_length=100000,
    )


class SmartsheetAddViewInputViewConfigQueryConditionFieldsItem(Input):
    field_id: str = Field(default=None, description="查询条件字段ID", max_length=100000)
    required: bool = Field(default=None, description="是否必填")
    title: str = Field(
        default=None, description="条件字段展示标题；为空时使用字段标题", max_length=100000
    )
    visible: bool = Field(default=None, description="是否展示该条件字段")


class SmartsheetAddViewInputViewConfigQueryResultFieldsItem(Input):
    editable: bool = Field(default=None, description="是否允许在查询结果中编辑该字段")
    field_id: str = Field(default=None, description="查询结果字段ID", max_length=100000)
    visible: bool = Field(default=None, description="是否展示该结果字段")


class SmartsheetAddViewInputViewConfigQuery(Input):
    condition_fields: list[SmartsheetAddViewInputViewConfigQueryConditionFieldsItem] = Field(
        default=None, description="查询条件字段配置", max_length=100
    )
    query_frequency_limit: int = Field(default=None, description="查询频率限制次数，必须大于等于0")
    query_frequency_unit: int = Field(
        default=None, description="查询频率限制单位：0-不限，1-总次数，2-每月，3-每周，4-每天"
    )
    result_fields: list[SmartsheetAddViewInputViewConfigQueryResultFieldsItem] = Field(
        default=None, description="查询结果字段配置，至少一个字段必须可见", max_length=100
    )
    result_title: str = Field(
        default=None, description="查询结果页标题；为空时使用视图标题", max_length=100000
    )
    sticky_field_id: str = Field(
        default=None,
        description="查询结果置顶字段ID，query 视图必填；须为工作表中已存在的字段ID",
        max_length=100000,
    )
    title: str = Field(
        default=None, description="查询页标题；为空时使用视图标题", max_length=100000
    )


class SmartsheetAddViewInputViewConfig(Input):
    end_date_field_id: str = Field(
        default=None, description="结束日期字段ID，gantt 和 calendar 视图必填", max_length=100000
    )
    query: SmartsheetAddViewInputViewConfigQuery = Field(
        default=None, description="查询页配置，query 视图必填"
    )
    start_date_field_id: str = Field(
        default=None, description="开始日期字段ID，gantt 和 calendar 视图必填", max_length=100000
    )


class SmartsheetAddViewInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="工作表ID", max_length=100000)
    view_config: SmartsheetAddViewInputViewConfig = Field(
        default=None,
        description="视图配置；gantt 和 calendar 必须提供开始、结束日期字段ID；query 必须提供 query 配置",
    )
    view_title: str = Field(description="视图标题", max_length=100000)
    view_type: Literal["grid", "kanban", "gallery", "gantt", "calendar", "form", "query"] = Field(
        default=None,
        description="视图类型：grid-表格，kanban-看板，gallery-画廊，gantt-甘特，calendar-日历，form-表单，query-查询页",
    )


class SmartsheetDeleteViewInput(Input):
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="工作表ID", max_length=100000)
    view_ids: list[str] = Field(description="要删除的视图ID列表", max_length=100)


class SmartsheetUpdateFieldsInputFieldsItemPropertyAutoNumberRulesItem(Input):
    type: int = Field(
        default=None, description="规则类型，枚举值：1-自增ID，2-固定字符，3-创建时间"
    )
    value: str = Field(
        default=None,
        description="规则值，存放创建时间格式或固定字符，自增数字位数",
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyAutoNumber(Input):
    rules: list[SmartsheetUpdateFieldsInputFieldsItemPropertyAutoNumberRulesItem] = Field(
        default=None, description="自定义规则列表，type为2时生效", max_length=100
    )
    type: int = Field(default=None, description="编号类型，枚举值：1-自增数字类型，2-自定义类型")


class SmartsheetUpdateFieldsInputFieldsItemPropertyCheckbox(Input):
    checked: bool = Field(default=None, description="新增时是否默认勾选")


class SmartsheetUpdateFieldsInputFieldsItemPropertyCreatedTime(Input):
    format: str = Field(
        default=None,
        description='创建时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyCurrency(Input):
    currency_type: int = Field(
        default=None,
        description="货币类型，枚举值：1-CNY人民币，2-USD美元，3-EUR欧元，4-GBP英镑，5-JPY日元，6-KRW韩元，7-HKD港元，8-MOP澳门元，9-TWD台币，10-AED迪拉姆，11-AUD澳元，12-BRL巴西雷亚尔，13-CAD加元，14-CHF瑞士法郎，15-IDR印尼盾，16-INR印度卢比，17-MXN墨西哥比索，18-MYR马来西亚林吉特，19-PHP菲律宾比索，20-PLN波兰兹罗提，21-RUB俄罗斯卢布，22-SGD新加坡元，23-THB泰铢，24-TRY土耳其里拉，25-VND越南盾",
    )
    decimal_places: int = Field(default=None, description="小数位数，范围0-4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetUpdateFieldsInputFieldsItemPropertyDateTime(Input):
    auto_fill: bool = Field(default=None, description="新建记录时，是否自动填充时间")
    format: str = Field(
        default=None,
        description='日期时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyAutoNumberRulesItem(
    Input
):
    type: int = Field(
        default=None, description="规则类型，枚举值：1-自增ID，2-固定字符，3-创建时间"
    )
    value: str = Field(
        default=None,
        description="规则值，存放创建时间格式或固定字符，自增数字位数",
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyAutoNumber(Input):
    rules: list[
        SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyAutoNumberRulesItem
    ] = Field(default=None, description="自定义规则列表，type为2时生效", max_length=100)
    type: int = Field(default=None, description="编号类型，枚举值：1-自增数字类型，2-自定义类型")


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyCheckbox(Input):
    checked: bool = Field(default=None, description="新增时是否默认勾选")


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyCreatedTime(Input):
    format: str = Field(
        default=None,
        description='创建时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyCurrency(Input):
    currency_type: int = Field(
        default=None,
        description="货币类型，枚举值：1-CNY人民币，2-USD美元，3-EUR欧元，4-GBP英镑，5-JPY日元，6-KRW韩元，7-HKD港元，8-MOP澳门元，9-TWD台币，10-AED迪拉姆，11-AUD澳元，12-BRL巴西雷亚尔，13-CAD加元，14-CHF瑞士法郎，15-IDR印尼盾，16-INR印度卢比，17-MXN墨西哥比索，18-MYR马来西亚林吉特，19-PHP菲律宾比索，20-PLN波兰兹罗提，21-RUB俄罗斯卢布，22-SGD新加坡元，23-THB泰铢，24-TRY土耳其里拉，25-VND越南盾",
    )
    decimal_places: int = Field(default=None, description="小数位数，范围0-4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyDateTime(Input):
    auto_fill: bool = Field(default=None, description="新建记录时，是否自动填充时间")
    format: str = Field(
        default=None,
        description='日期时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyModifiedTime(Input):
    format: str = Field(
        default=None,
        description='最后编辑时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyNumber(Input):
    decimal_places: int = Field(default=None, description="表示小数点的位数，即数字精度")
    use_separate: bool = Field(
        default=None,
        description="是否使用千位符，设置此属性后数字字段将以英文逗号分隔千分位，如 1,000",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyPercentage(Input):
    decimal_places: int = Field(default=None, description="小数位数，范围-1到4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyProgress(Input):
    decimal_places: int = Field(default=None, description="小数位数")


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyReference(Input):
    field_id: str = Field(default=None, description="关联的字段ID", max_length=100000)
    is_multiple: bool = Field(default=None, description="是否允许多选")
    sub_id: str = Field(
        default=None, description="关联的子表ID，为空时表示关联本子表", max_length=100000
    )
    view_id: str = Field(default=None, description="关联视图ID", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertySelectOptionsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertySelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[
        SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertySelectOptionsItem
    ] = Field(default=None, description="多选选项的格式设置", max_length=100)


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertySingleSelectOptionsItem(
    Input
):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertySingleSelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[
        SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertySingleSelectOptionsItem
    ] = Field(default=None, description="单选选项的格式设置", max_length=100)


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyUrl(Input):
    type: int = Field(default=None, description="超链接展示样式 枚举值：0-未知，1-文字，2-图标文字")


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatter(Input):
    property_auto_number: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyAutoNumber = Field(
        default=None, description="自动编号类型的展示格式属性，包含编号类型和自定义规则配置"
    )
    property_checkbox: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyCheckbox = Field(
        default=None, description="复选框类型的展示格式属性，包含默认勾选状态配置"
    )
    property_created_time: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyCreatedTime = Field(
        default=None, description="创建时间类型的展示格式属性，包含时间格式配置"
    )
    property_created_user: dict[str, JsonValue] = Field(
        default=None, description="创建人类型的展示格式属性，创建人类型不需要额外的配置属性"
    )
    property_currency: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyCurrency = Field(
        default=None, description="货币类型的展示格式属性，包含货币种类和小数位数配置"
    )
    property_date_time: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyDateTime = Field(
        default=None, description="日期时间类型的展示格式属性，包含格式和自动填充配置"
    )
    property_email: dict[str, JsonValue] = Field(
        default=None, description="邮件类型的展示格式属性，邮件类型不需要额外的配置属性"
    )
    property_image: dict[str, JsonValue] = Field(
        default=None, description="图片类型的展示格式属性，图片类型不需要额外的配置属性"
    )
    property_modified_time: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyModifiedTime = Field(
        default=None, description="最后编辑时间类型的展示格式属性，包含时间格式配置"
    )
    property_modified_user: dict[str, JsonValue] = Field(
        default=None, description="最后编辑人类型的展示格式属性，最后编辑人类型不需要额外的配置属性"
    )
    property_number: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyNumber = (
        Field(default=None, description="数字类型的展示格式属性，包含精度和千位符等配置")
    )
    property_percentage: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyPercentage = Field(
        default=None, description="百分比类型的展示格式属性，包含小数位数和千位符配置"
    )
    property_phone_number: dict[str, JsonValue] = Field(
        default=None, description="电话类型的展示格式属性，电话类型不需要额外的配置属性"
    )
    property_progress: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyProgress = Field(
        default=None, description="进度类型的展示格式属性，包含小数位数配置"
    )
    property_reference: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyReference = Field(
        default=None, description="关联类型的展示格式属性，包含关联子表、字段和多选配置"
    )
    property_select: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertySelect = (
        Field(default=None, description="多选类型的展示格式属性，包含选项和选择模式配置")
    )
    property_single_select: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertySingleSelect = Field(
        default=None, description="单选类型的展示格式属性，包含选项和选择模式配置"
    )
    property_text: dict[str, JsonValue] = Field(
        default=None, description="文本类型的展示格式属性，文本类型不需要额外的配置属性"
    )
    property_url: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatterPropertyUrl = Field(
        default=None, description="超链接类型的展示格式属性，包含展示样式配置"
    )
    property_user: dict[str, JsonValue] = Field(
        default=None, description="用户类型的展示格式属性，用户类型不需要额外的配置属性"
    )
    type: int = Field(
        default=None,
        description="展示格式对应的列类型(FieldType)，必填且不能为0，它决定使用下方哪个 property 字段(如 26 对应 property_currency)。枚举值：1-文本，2-数字，3-勾选，4-日期，5-图片，7-用户，8-URL，9-多选，10-创建人，11-最后编辑人，12-创建时间，13-修改时间，14-进度，15-电话，16-邮箱，17-单选，18-引用，25-自动编号，26-货币，28-百分比。注意不能填19(公式)/20(查找引用)，展示格式本身不能再是公式或查找引用",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormulaModelItem(Input):
    field_id: str = Field(
        default=None,
        description="被引用的列ID，type为列引用类型时生效，必须为已存在的列",
        max_length=100000,
    )
    table_id: str = Field(
        default=None, description="被引用列所在的子表ID，为空时表示引用本子表", max_length=100000
    )
    text: str = Field(default=None, description="文本片段内容，type为1时生效", max_length=100000)
    type: int = Field(
        default=None,
        description="公式项类型，枚举值：1-文本片段，2-列引用，5-列引用(.列)，6-表.列引用，9-关联列引用",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyFormula(Input):
    formatter: SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormatter = Field(
        default=None,
        description='展示格式设置，用于设置公式计算结果的展示格式，展示格式的类型不一定与计算结果类型一致。可选，不填则由系统自动推断格式。填写时必须同时设置 formatter.type(字段名就是 type，不是 formatter_type) 和与之匹配的 property_xxx，例如展示为人民币金额：{"type": 26, "property_currency": {"currency_type": 1, "decimal_places": 2, "use_separate": true}}；只填 property_xxx 而漏填 type 会被服务端拒绝',
    )
    formula_model: list[SmartsheetUpdateFieldsInputFieldsItemPropertyFormulaFormulaModelItem] = (
        Field(
            default=None,
            description="公式表达式模型，由文本片段与列引用片段按顺序组成，不能为空",
            max_length=100,
        )
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFilterConditionsItemMatchValueValueDateTime(
    Input
):
    timestamps: list[int] = Field(
        default=None,
        description="毫秒时间戳列表：type=1填1个，type=2(范围)填2个(起止时间)，相对类型(今天/本周等)可不填",
        max_length=100,
    )
    type: int = Field(
        default=None,
        description="日期匹配类型，枚举值：1-具体时间，2-具体时间范围，3-今天，4-明天，5-昨天，6-本周，7-上周，8-本月",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFilterConditionsItemMatchValue(Input):
    computed_key_type: int = Field(
        default=None,
        description="被比较值对应的列类型(FieldType)，与具体值比较时必填。枚举值：1-文本，2-数字，3-勾选，4-日期，8-URL，9-多选，12-创建时间，13-修改时间，14-进度，15-电话，16-邮箱，17-单选，18-引用，24-标题，28-百分比。它决定使用下方哪个 value 字段",
    )
    field_id: str = Field(
        default=None,
        description="与列比较时(value_type=1)生效，为被比较的目标表列ID，必须已存在",
        max_length=100000,
    )
    value_bool: bool = Field(default=None, description="勾选类匹配值，用于勾选(3)")
    value_date_time: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFilterConditionsItemMatchValueValueDateTime = Field(
        default=None, description="日期时间类匹配值，用于日期(4)/创建时间(12)/修改时间(13)"
    )
    value_number: float = Field(
        default=None, description="数字类匹配值，用于数字(2)/进度(14)/百分比(28)"
    )
    value_selects: list[str] = Field(
        default=None,
        description="选项类匹配值，为选项ID列表，用于多选(9)/单选(17)/人员(7)/创建人(10)/修改人(11)等",
        max_length=100,
    )
    value_text: str = Field(
        default=None,
        description="文本类匹配值，用于文本(1)/URL(8)/电话(15)/邮箱(16)/引用(18)/标题(24)",
        max_length=100000,
    )
    value_type: int = Field(
        default=None, description="匹配值类型，枚举值：0-与具体值比较，1-与目标表另一列比较"
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFilterConditionsItem(Input):
    condition_id: str = Field(
        default=None,
        description="条件ID，用于唯一标识一条筛选条件，同一 filter 内不能重复(如 cdt1、cdt2)；不填时由服务端按顺序自动生成",
        max_length=100000,
    )
    field_id: str = Field(
        default=None,
        description="筛选条件作用的列ID，必须为被查找目标表中已存在的列，不能为空",
        max_length=100000,
    )
    field_type: int = Field(
        default=None,
        description="列类型(FieldType)，枚举值：1-文本，2-数字，3-勾选，4-日期，8-URL，9-多选，12-创建时间，13-修改时间，14-进度，15-电话，16-邮箱，17-单选，18-引用，24-标题，28-百分比",
    )
    match_value: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFilterConditionsItemMatchValue = Field(
        default=None,
        description="匹配值。当 operator 为 9(为空)/10(不为空) 时无需设置；其余操作符必须设置，否则条件非法会被拒绝",
    )
    operator: int = Field(
        default=None,
        description="筛选操作符，枚举值：1-等于，2-不等于，3-包含，4-不包含，5-大于，6-大于等于，7-小于，8-小于等于，9-为空，10-不为空。除9(为空)/10(不为空) 外，其余操作符必须同时设置 match_value",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFilter(Input):
    conditions: list[SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFilterConditionsItem] = (
        Field(default=None, description="筛选条件列表", max_length=100)
    )
    conjunction: int = Field(default=None, description="条件组合方式，枚举值：1-and，2-or")


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyAutoNumberRulesItem(
    Input
):
    type: int = Field(
        default=None, description="规则类型，枚举值：1-自增ID，2-固定字符，3-创建时间"
    )
    value: str = Field(
        default=None,
        description="规则值，存放创建时间格式或固定字符，自增数字位数",
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyAutoNumber(Input):
    rules: list[
        SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyAutoNumberRulesItem
    ] = Field(default=None, description="自定义规则列表，type为2时生效", max_length=100)
    type: int = Field(default=None, description="编号类型，枚举值：1-自增数字类型，2-自定义类型")


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyCheckbox(Input):
    checked: bool = Field(default=None, description="新增时是否默认勾选")


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyCreatedTime(Input):
    format: str = Field(
        default=None,
        description='创建时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyCurrency(Input):
    currency_type: int = Field(
        default=None,
        description="货币类型，枚举值：1-CNY人民币，2-USD美元，3-EUR欧元，4-GBP英镑，5-JPY日元，6-KRW韩元，7-HKD港元，8-MOP澳门元，9-TWD台币，10-AED迪拉姆，11-AUD澳元，12-BRL巴西雷亚尔，13-CAD加元，14-CHF瑞士法郎，15-IDR印尼盾，16-INR印度卢比，17-MXN墨西哥比索，18-MYR马来西亚林吉特，19-PHP菲律宾比索，20-PLN波兰兹罗提，21-RUB俄罗斯卢布，22-SGD新加坡元，23-THB泰铢，24-TRY土耳其里拉，25-VND越南盾",
    )
    decimal_places: int = Field(default=None, description="小数位数，范围0-4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyDateTime(Input):
    auto_fill: bool = Field(default=None, description="新建记录时，是否自动填充时间")
    format: str = Field(
        default=None,
        description='日期时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyModifiedTime(Input):
    format: str = Field(
        default=None,
        description='最后编辑时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyNumber(Input):
    decimal_places: int = Field(default=None, description="表示小数点的位数，即数字精度")
    use_separate: bool = Field(
        default=None,
        description="是否使用千位符，设置此属性后数字字段将以英文逗号分隔千分位，如 1,000",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyPercentage(Input):
    decimal_places: int = Field(default=None, description="小数位数，范围-1到4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyProgress(Input):
    decimal_places: int = Field(default=None, description="小数位数")


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyReference(Input):
    field_id: str = Field(default=None, description="关联的字段ID", max_length=100000)
    is_multiple: bool = Field(default=None, description="是否允许多选")
    sub_id: str = Field(
        default=None, description="关联的子表ID，为空时表示关联本子表", max_length=100000
    )
    view_id: str = Field(default=None, description="关联视图ID", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertySelectOptionsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertySelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[
        SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertySelectOptionsItem
    ] = Field(default=None, description="多选选项的格式设置", max_length=100)


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertySingleSelectOptionsItem(
    Input
):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertySingleSelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[
        SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertySingleSelectOptionsItem
    ] = Field(default=None, description="单选选项的格式设置", max_length=100)


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyUrl(Input):
    type: int = Field(default=None, description="超链接展示样式 枚举值：0-未知，1-文字，2-图标文字")


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatter(Input):
    property_auto_number: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyAutoNumber = Field(
        default=None, description="自动编号类型的展示格式属性，包含编号类型和自定义规则配置"
    )
    property_checkbox: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyCheckbox = Field(
        default=None, description="复选框类型的展示格式属性，包含默认勾选状态配置"
    )
    property_created_time: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyCreatedTime = Field(
        default=None, description="创建时间类型的展示格式属性，包含时间格式配置"
    )
    property_created_user: dict[str, JsonValue] = Field(
        default=None, description="创建人类型的展示格式属性，创建人类型不需要额外的配置属性"
    )
    property_currency: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyCurrency = Field(
        default=None, description="货币类型的展示格式属性，包含货币种类和小数位数配置"
    )
    property_date_time: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyDateTime = Field(
        default=None, description="日期时间类型的展示格式属性，包含格式和自动填充配置"
    )
    property_email: dict[str, JsonValue] = Field(
        default=None, description="邮件类型的展示格式属性，邮件类型不需要额外的配置属性"
    )
    property_image: dict[str, JsonValue] = Field(
        default=None, description="图片类型的展示格式属性，图片类型不需要额外的配置属性"
    )
    property_modified_time: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyModifiedTime = Field(
        default=None, description="最后编辑时间类型的展示格式属性，包含时间格式配置"
    )
    property_modified_user: dict[str, JsonValue] = Field(
        default=None, description="最后编辑人类型的展示格式属性，最后编辑人类型不需要额外的配置属性"
    )
    property_number: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyNumber = (
        Field(default=None, description="数字类型的展示格式属性，包含精度和千位符等配置")
    )
    property_percentage: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyPercentage = Field(
        default=None, description="百分比类型的展示格式属性，包含小数位数和千位符配置"
    )
    property_phone_number: dict[str, JsonValue] = Field(
        default=None, description="电话类型的展示格式属性，电话类型不需要额外的配置属性"
    )
    property_progress: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyProgress = Field(
        default=None, description="进度类型的展示格式属性，包含小数位数配置"
    )
    property_reference: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyReference = Field(
        default=None, description="关联类型的展示格式属性，包含关联子表、字段和多选配置"
    )
    property_select: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertySelect = (
        Field(default=None, description="多选类型的展示格式属性，包含选项和选择模式配置")
    )
    property_single_select: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertySingleSelect = Field(
        default=None, description="单选类型的展示格式属性，包含选项和选择模式配置"
    )
    property_text: dict[str, JsonValue] = Field(
        default=None, description="文本类型的展示格式属性，文本类型不需要额外的配置属性"
    )
    property_url: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatterPropertyUrl = Field(
        default=None, description="超链接类型的展示格式属性，包含展示样式配置"
    )
    property_user: dict[str, JsonValue] = Field(
        default=None, description="用户类型的展示格式属性，用户类型不需要额外的配置属性"
    )
    type: int = Field(
        default=None,
        description="展示格式对应的列类型(FieldType)，必填且不能为0，它决定使用下方哪个 property 字段(如 26 对应 property_currency)。枚举值：1-文本，2-数字，3-勾选，4-日期，5-图片，7-用户，8-URL，9-多选，10-创建人，11-最后编辑人，12-创建时间，13-修改时间，14-进度，15-电话，16-邮箱，17-单选，18-引用，25-自动编号，26-货币，28-百分比。注意不能填19(公式)/20(查找引用)，展示格式本身不能再是公式或查找引用",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyLookup(Input):
    filter: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFilter = Field(
        default=None, description="查找引用的筛选条件，仅在按条件查找(upgrade_type=1)时生效"
    )
    formatter: SmartsheetUpdateFieldsInputFieldsItemPropertyLookupFormatter = Field(
        default=None,
        description="统计格式设置，用于设置查找引用结果的展示格式，展示格式的类型不一定与计算结果类型一致。可选，不填则由系统自动推断格式。填写时必须同时设置 formatter.type(字段名就是 type，不是 formatter_type) 和与之匹配的 property_xxx，只填 property_xxx 而漏填 type 会被服务端拒绝",
    )
    link_records_field_id: str = Field(
        default=None,
        description="本表中的关联列ID，必须为已存在的关联列。仅在按关联查找(upgrade_type=0)时必填；按条件查找(upgrade_type=1)时无需填写",
        max_length=100000,
    )
    lookup_field_id: str = Field(
        default=None, description="被查找目标表中的列ID，必须为已存在的列", max_length=100000
    )
    lookup_sub_id: str = Field(
        default=None, description="被查找目标表的子表ID，为空时表示本子表", max_length=100000
    )
    rollup_type: int = Field(
        default=None,
        description="统计类型，枚举值：0-原样引用，1-去重引用，2-求和，3-计数，4-去重计数，5-平均值，6-最大值，7-最小值",
    )
    upgrade_type: int = Field(
        default=None,
        description="查找引用方式，枚举值：0-按关联查找(通过本表关联列做桥梁，需填写link_records_field_id)，1-按条件查找(通过 filter 筛选条件，无需 link_records_field_id)",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyModifiedTime(Input):
    format: str = Field(
        default=None,
        description='最后编辑时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyNumber(Input):
    decimal_places: int = Field(default=None, description="表示小数点的位数，即数字精度")
    use_separate: bool = Field(
        default=None,
        description="是否使用千位符，设置此属性后数字字段将以英文逗号分隔千分位，如 1,000",
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyPercentage(Input):
    decimal_places: int = Field(default=None, description="小数位数，范围-1到4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetUpdateFieldsInputFieldsItemPropertyProgress(Input):
    decimal_places: int = Field(default=None, description="小数位数")


class SmartsheetUpdateFieldsInputFieldsItemPropertyReference(Input):
    field_id: str = Field(default=None, description="关联的字段ID", max_length=100000)
    is_multiple: bool = Field(default=None, description="是否允许多选")
    sub_id: str = Field(
        default=None, description="关联的子表ID，为空时表示关联本子表", max_length=100000
    )
    view_id: str = Field(default=None, description="关联视图ID", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertySelectOptionsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertySelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[SmartsheetUpdateFieldsInputFieldsItemPropertySelectOptionsItem] = Field(
        default=None, description="多选选项的格式设置", max_length=100
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertySingleSelectOptionsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertySingleSelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[SmartsheetUpdateFieldsInputFieldsItemPropertySingleSelectOptionsItem] = Field(
        default=None, description="单选选项的格式设置", max_length=100
    )


class SmartsheetUpdateFieldsInputFieldsItemPropertyTwoWayLinkRecords(Input):
    back_field_id: str = Field(
        default=None,
        description="服务端生成的反向字段ID；请求时不得指定，仅在响应中返回",
        max_length=100000,
    )
    field_id: str = Field(
        default=None, description="目标表展示字段ID；可选，默认主字段", max_length=100000
    )
    is_multiple: bool = Field(default=None, description="是否允许多选")
    sub_id: str = Field(
        default=None, description="目标子表ID；首期仅支持同文档跨子表关联", max_length=100000
    )
    view_id: str = Field(default=None, description="目标视图ID；可选", max_length=100000)


class SmartsheetUpdateFieldsInputFieldsItemPropertyUrl(Input):
    type: int = Field(default=None, description="超链接展示样式 枚举值：0-未知，1-文字，2-图标文字")


class SmartsheetUpdateFieldsInputFieldsItemPropertyUserC(Input):
    is_multiple: bool = Field(default=None, description="是否允许添加多个成员，默认 false")
    is_notified: bool = Field(default=None, description="添加成员时是否通知该成员，默认 true")


class SmartsheetUpdateFieldsInputFieldsItem(Input):
    before_field_id: str = Field(
        default=None,
        description="可选。仅 add_fields 生效：插入到该 field_id 之前；省略则追加到列末尾。批量添加时，相同 before_field_id 的多个字段按数组顺序连续插在锚点前。须先通过 list_fields 取得目标 field_id。update_fields 忽略此字段。",
        max_length=100000,
    )
    field_id: str = Field(
        default=None,
        description="字段 ID，更新字段属性时需要填写该字段，但字段 ID 不能被更新",
        max_length=100000,
    )
    field_title: str = Field(default=None, description="需要更新为的字段标题", max_length=100000)
    field_type: Literal[
        "text",
        "number",
        "checkbox",
        "dateTime",
        "image",
        "attachment",
        "url",
        "select",
        "createdUser",
        "modifiedUser",
        "createdTime",
        "modifiedTime",
        "progress",
        "phoneNumber",
        "email",
        "singleSelect",
        "reference",
        "twoWayLinkRecords",
        "autoNumber",
        "currency",
        "percentage",
        "formula",
        "lookup",
        "user",
    ] = Field(
        default=None,
        description="字段类型，该字段不允许被更新，但更新时必须传入原字段类型值。枚举值：text-文本，number-数字，checkbox-复选框，dateTime-日期，image-图片，attachment-附件，url-超链接，select-多选，createdUser-创建人，modifiedUser-最后编辑人，createdTime-创建时间，modifiedTime-最后编辑时间，progress-进度，phoneNumber-电话，email-邮件，singleSelect-单选，reference-关联，twoWayLinkRecords-双向关联，autoNumber-自动编号，currency-货币，percentage-百分比，formula-公式，lookup-查找引用，user-成员",
    )
    property_attachment: dict[str, JsonValue] = Field(
        default=None, description="附件类型的字段属性，附件类型字段不需要额外的配置属性"
    )
    property_auto_number: SmartsheetUpdateFieldsInputFieldsItemPropertyAutoNumber = Field(
        default=None, description="自动编号类型的字段属性，包含编号类型和自定义规则配置"
    )
    property_checkbox: SmartsheetUpdateFieldsInputFieldsItemPropertyCheckbox = Field(
        default=None, description="复选框类型的字段属性，包含默认勾选状态配置"
    )
    property_created_time: SmartsheetUpdateFieldsInputFieldsItemPropertyCreatedTime = Field(
        default=None, description="创建时间类型的字段属性，包含时间格式配置"
    )
    property_created_user: dict[str, JsonValue] = Field(
        default=None, description="创建人类型的字段属性，创建人类型字段不需要额外的配置属性"
    )
    property_currency: SmartsheetUpdateFieldsInputFieldsItemPropertyCurrency = Field(
        default=None, description="货币类型的字段属性，包含货币种类和小数位数配置"
    )
    property_date_time: SmartsheetUpdateFieldsInputFieldsItemPropertyDateTime = Field(
        default=None, description="日期时间类型的字段属性，包含格式和自动填充配置"
    )
    property_email: dict[str, JsonValue] = Field(
        default=None, description="邮件类型的字段属性，邮件类型字段不需要额外的配置属性"
    )
    property_formula: SmartsheetUpdateFieldsInputFieldsItemPropertyFormula = Field(
        default=None, description="公式类型的字段属性，包含公式表达式模型和展示格式配置"
    )
    property_image: dict[str, JsonValue] = Field(
        default=None, description="图片类型的字段属性，图片类型字段不需要额外的配置属性"
    )
    property_lookup: SmartsheetUpdateFieldsInputFieldsItemPropertyLookup = Field(
        default=None, description="查找引用类型的字段属性，包含关联列、被查找列、统计类型和筛选配置"
    )
    property_modified_time: SmartsheetUpdateFieldsInputFieldsItemPropertyModifiedTime = Field(
        default=None, description="最后编辑时间类型的字段属性，包含时间格式配置"
    )
    property_modified_user: dict[str, JsonValue] = Field(
        default=None, description="最后编辑人类型的字段属性，最后编辑人类型字段不需要额外的配置属性"
    )
    property_number: SmartsheetUpdateFieldsInputFieldsItemPropertyNumber = Field(
        default=None, description="数字类型的字段属性，包含精度和千位符等配置"
    )
    property_percentage: SmartsheetUpdateFieldsInputFieldsItemPropertyPercentage = Field(
        default=None, description="百分比类型的字段属性，包含小数位数和千位符配置"
    )
    property_phone_number: dict[str, JsonValue] = Field(
        default=None, description="电话类型的字段属性，电话类型字段不需要额外的配置属性"
    )
    property_progress: SmartsheetUpdateFieldsInputFieldsItemPropertyProgress = Field(
        default=None, description="进度类型的字段属性，包含小数位数配置"
    )
    property_reference: SmartsheetUpdateFieldsInputFieldsItemPropertyReference = Field(
        default=None, description="关联类型的字段属性，包含关联子表、字段和多选配置"
    )
    property_select: SmartsheetUpdateFieldsInputFieldsItemPropertySelect = Field(
        default=None, description="多选类型的字段属性，包含选项和选择模式配置"
    )
    property_single_select: SmartsheetUpdateFieldsInputFieldsItemPropertySingleSelect = Field(
        default=None, description="单选类型的字段属性，包含选项和选择模式配置"
    )
    property_text: dict[str, JsonValue] = Field(
        default=None, description="文本类型的字段属性，文本类型字段不需要额外的配置属性"
    )
    property_two_way_link_records: SmartsheetUpdateFieldsInputFieldsItemPropertyTwoWayLinkRecords = Field(
        default=None,
        description="双向关联类型字段属性；新增时 sub_id 必填，back_field_id 仅在响应中返回",
    )
    property_url: SmartsheetUpdateFieldsInputFieldsItemPropertyUrl = Field(
        default=None, description="超链接类型的字段属性，包含展示样式配置"
    )
    property_user: dict[str, JsonValue] = Field(
        default=None, description="用户类型的字段属性，用户类型字段不需要额外的配置属性"
    )
    property_user_c: SmartsheetUpdateFieldsInputFieldsItemPropertyUserC = Field(
        default=None, description="成员类型的字段属性，包含多选和通知配置"
    )


class SmartsheetUpdateFieldsInput(Input):
    fields: list[SmartsheetUpdateFieldsInputFieldsItem] = Field(
        description="要更新的字段信息列表", max_length=100
    )
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="工作表ID", max_length=100000)


class SmartsheetUpdateDashboardComponentFromPlanInput(Input):
    component_id: str = Field(description="要更新的仪表盘组件ID", max_length=100000)
    component_plan: str = Field(
        description="完整组件规划，例如：任务总数 | T3\\n- 数据源：tableId\\n- 数值轴：COUNT。组件位置保持不变",
        max_length=100000,
    )
    dashboard_id: str = Field(description="仪表盘子表ID", max_length=100000)
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)


class SmartsheetAddDashboardComponentFromPlanInput(Input):
    component_plan: str = Field(
        description="完整组件规划，例如：任务总数 | T3\\n- 数据源：tableId\\n- 数值轴：COUNT",
        max_length=100000,
    )
    dashboard_id: str = Field(description="仪表盘子表ID", max_length=100000)
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    position: str = Field(
        description='JSON格式的组件布局数组 [offsetX, offsetY, width, height]。规则：宽度2-12，高度≥2（文本除外），offsetX+width≤12，不能与其他组件重叠。示例："[0, 0, 6, 4]"',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyAutoNumberRulesItem(Input):
    type: int = Field(
        default=None, description="规则类型，枚举值：1-自增ID，2-固定字符，3-创建时间"
    )
    value: str = Field(
        default=None,
        description="规则值，存放创建时间格式或固定字符，自增数字位数",
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyAutoNumber(Input):
    rules: list[SmartsheetAddFieldsInputFieldsItemPropertyAutoNumberRulesItem] = Field(
        default=None, description="自定义规则列表，type为2时生效", max_length=100
    )
    type: int = Field(default=None, description="编号类型，枚举值：1-自增数字类型，2-自定义类型")


class SmartsheetAddFieldsInputFieldsItemPropertyCheckbox(Input):
    checked: bool = Field(default=None, description="新增时是否默认勾选")


class SmartsheetAddFieldsInputFieldsItemPropertyCreatedTime(Input):
    format: str = Field(
        default=None,
        description='创建时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyCurrency(Input):
    currency_type: int = Field(
        default=None,
        description="货币类型，枚举值：1-CNY人民币，2-USD美元，3-EUR欧元，4-GBP英镑，5-JPY日元，6-KRW韩元，7-HKD港元，8-MOP澳门元，9-TWD台币，10-AED迪拉姆，11-AUD澳元，12-BRL巴西雷亚尔，13-CAD加元，14-CHF瑞士法郎，15-IDR印尼盾，16-INR印度卢比，17-MXN墨西哥比索，18-MYR马来西亚林吉特，19-PHP菲律宾比索，20-PLN波兰兹罗提，21-RUB俄罗斯卢布，22-SGD新加坡元，23-THB泰铢，24-TRY土耳其里拉，25-VND越南盾",
    )
    decimal_places: int = Field(default=None, description="小数位数，范围0-4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetAddFieldsInputFieldsItemPropertyDateTime(Input):
    auto_fill: bool = Field(default=None, description="新建记录时，是否自动填充时间")
    format: str = Field(
        default=None,
        description='日期时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyAutoNumberRulesItem(Input):
    type: int = Field(
        default=None, description="规则类型，枚举值：1-自增ID，2-固定字符，3-创建时间"
    )
    value: str = Field(
        default=None,
        description="规则值，存放创建时间格式或固定字符，自增数字位数",
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyAutoNumber(Input):
    rules: list[
        SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyAutoNumberRulesItem
    ] = Field(default=None, description="自定义规则列表，type为2时生效", max_length=100)
    type: int = Field(default=None, description="编号类型，枚举值：1-自增数字类型，2-自定义类型")


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyCheckbox(Input):
    checked: bool = Field(default=None, description="新增时是否默认勾选")


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyCreatedTime(Input):
    format: str = Field(
        default=None,
        description='创建时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyCurrency(Input):
    currency_type: int = Field(
        default=None,
        description="货币类型，枚举值：1-CNY人民币，2-USD美元，3-EUR欧元，4-GBP英镑，5-JPY日元，6-KRW韩元，7-HKD港元，8-MOP澳门元，9-TWD台币，10-AED迪拉姆，11-AUD澳元，12-BRL巴西雷亚尔，13-CAD加元，14-CHF瑞士法郎，15-IDR印尼盾，16-INR印度卢比，17-MXN墨西哥比索，18-MYR马来西亚林吉特，19-PHP菲律宾比索，20-PLN波兰兹罗提，21-RUB俄罗斯卢布，22-SGD新加坡元，23-THB泰铢，24-TRY土耳其里拉，25-VND越南盾",
    )
    decimal_places: int = Field(default=None, description="小数位数，范围0-4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyDateTime(Input):
    auto_fill: bool = Field(default=None, description="新建记录时，是否自动填充时间")
    format: str = Field(
        default=None,
        description='日期时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyModifiedTime(Input):
    format: str = Field(
        default=None,
        description='最后编辑时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyNumber(Input):
    decimal_places: int = Field(default=None, description="表示小数点的位数，即数字精度")
    use_separate: bool = Field(
        default=None,
        description="是否使用千位符，设置此属性后数字字段将以英文逗号分隔千分位，如 1,000",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyPercentage(Input):
    decimal_places: int = Field(default=None, description="小数位数，范围-1到4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyProgress(Input):
    decimal_places: int = Field(default=None, description="小数位数")


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyReference(Input):
    field_id: str = Field(default=None, description="关联的字段ID", max_length=100000)
    is_multiple: bool = Field(default=None, description="是否允许多选")
    sub_id: str = Field(
        default=None, description="关联的子表ID，为空时表示关联本子表", max_length=100000
    )
    view_id: str = Field(default=None, description="关联视图ID", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertySelectOptionsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertySelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[
        SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertySelectOptionsItem
    ] = Field(default=None, description="多选选项的格式设置", max_length=100)


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertySingleSelectOptionsItem(
    Input
):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertySingleSelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[
        SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertySingleSelectOptionsItem
    ] = Field(default=None, description="单选选项的格式设置", max_length=100)


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyUrl(Input):
    type: int = Field(default=None, description="超链接展示样式 枚举值：0-未知，1-文字，2-图标文字")


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatter(Input):
    property_auto_number: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyAutoNumber = Field(
        default=None, description="自动编号类型的展示格式属性，包含编号类型和自定义规则配置"
    )
    property_checkbox: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyCheckbox = Field(
        default=None, description="复选框类型的展示格式属性，包含默认勾选状态配置"
    )
    property_created_time: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyCreatedTime = Field(
        default=None, description="创建时间类型的展示格式属性，包含时间格式配置"
    )
    property_created_user: dict[str, JsonValue] = Field(
        default=None, description="创建人类型的展示格式属性，创建人类型不需要额外的配置属性"
    )
    property_currency: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyCurrency = Field(
        default=None, description="货币类型的展示格式属性，包含货币种类和小数位数配置"
    )
    property_date_time: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyDateTime = Field(
        default=None, description="日期时间类型的展示格式属性，包含格式和自动填充配置"
    )
    property_email: dict[str, JsonValue] = Field(
        default=None, description="邮件类型的展示格式属性，邮件类型不需要额外的配置属性"
    )
    property_image: dict[str, JsonValue] = Field(
        default=None, description="图片类型的展示格式属性，图片类型不需要额外的配置属性"
    )
    property_modified_time: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyModifiedTime = Field(
        default=None, description="最后编辑时间类型的展示格式属性，包含时间格式配置"
    )
    property_modified_user: dict[str, JsonValue] = Field(
        default=None, description="最后编辑人类型的展示格式属性，最后编辑人类型不需要额外的配置属性"
    )
    property_number: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyNumber = (
        Field(default=None, description="数字类型的展示格式属性，包含精度和千位符等配置")
    )
    property_percentage: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyPercentage = Field(
        default=None, description="百分比类型的展示格式属性，包含小数位数和千位符配置"
    )
    property_phone_number: dict[str, JsonValue] = Field(
        default=None, description="电话类型的展示格式属性，电话类型不需要额外的配置属性"
    )
    property_progress: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyProgress = Field(
        default=None, description="进度类型的展示格式属性，包含小数位数配置"
    )
    property_reference: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyReference = Field(
        default=None, description="关联类型的展示格式属性，包含关联子表、字段和多选配置"
    )
    property_select: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertySelect = (
        Field(default=None, description="多选类型的展示格式属性，包含选项和选择模式配置")
    )
    property_single_select: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertySingleSelect = Field(
        default=None, description="单选类型的展示格式属性，包含选项和选择模式配置"
    )
    property_text: dict[str, JsonValue] = Field(
        default=None, description="文本类型的展示格式属性，文本类型不需要额外的配置属性"
    )
    property_url: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatterPropertyUrl = Field(
        default=None, description="超链接类型的展示格式属性，包含展示样式配置"
    )
    property_user: dict[str, JsonValue] = Field(
        default=None, description="用户类型的展示格式属性，用户类型不需要额外的配置属性"
    )
    type: int = Field(
        default=None,
        description="展示格式对应的列类型(FieldType)，必填且不能为0，它决定使用下方哪个 property 字段(如 26 对应 property_currency)。枚举值：1-文本，2-数字，3-勾选，4-日期，5-图片，7-用户，8-URL，9-多选，10-创建人，11-最后编辑人，12-创建时间，13-修改时间，14-进度，15-电话，16-邮箱，17-单选，18-引用，25-自动编号，26-货币，28-百分比。注意不能填19(公式)/20(查找引用)，展示格式本身不能再是公式或查找引用",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormulaModelItem(Input):
    field_id: str = Field(
        default=None,
        description="被引用的列ID，type为列引用类型时生效，必须为已存在的列",
        max_length=100000,
    )
    table_id: str = Field(
        default=None, description="被引用列所在的子表ID，为空时表示引用本子表", max_length=100000
    )
    text: str = Field(default=None, description="文本片段内容，type为1时生效", max_length=100000)
    type: int = Field(
        default=None,
        description="公式项类型，枚举值：1-文本片段，2-列引用，5-列引用(.列)，6-表.列引用，9-关联列引用",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyFormula(Input):
    formatter: SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormatter = Field(
        default=None,
        description='展示格式设置，用于设置公式计算结果的展示格式，展示格式的类型不一定与计算结果类型一致。可选，不填则由系统自动推断格式。填写时必须同时设置 formatter.type(字段名就是 type，不是 formatter_type) 和与之匹配的 property_xxx，例如展示为人民币金额：{"type": 26, "property_currency": {"currency_type": 1, "decimal_places": 2, "use_separate": true}}；只填 property_xxx 而漏填 type 会被服务端拒绝',
    )
    formula_model: list[SmartsheetAddFieldsInputFieldsItemPropertyFormulaFormulaModelItem] = Field(
        default=None,
        description="公式表达式模型，由文本片段与列引用片段按顺序组成，不能为空",
        max_length=100,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFilterConditionsItemMatchValueValueDateTime(
    Input
):
    timestamps: list[int] = Field(
        default=None,
        description="毫秒时间戳列表：type=1填1个，type=2(范围)填2个(起止时间)，相对类型(今天/本周等)可不填",
        max_length=100,
    )
    type: int = Field(
        default=None,
        description="日期匹配类型，枚举值：1-具体时间，2-具体时间范围，3-今天，4-明天，5-昨天，6-本周，7-上周，8-本月",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFilterConditionsItemMatchValue(Input):
    computed_key_type: int = Field(
        default=None,
        description="被比较值对应的列类型(FieldType)，与具体值比较时必填。枚举值：1-文本，2-数字，3-勾选，4-日期，8-URL，9-多选，12-创建时间，13-修改时间，14-进度，15-电话，16-邮箱，17-单选，18-引用，24-标题，28-百分比。它决定使用下方哪个 value 字段",
    )
    field_id: str = Field(
        default=None,
        description="与列比较时(value_type=1)生效，为被比较的目标表列ID，必须已存在",
        max_length=100000,
    )
    value_bool: bool = Field(default=None, description="勾选类匹配值，用于勾选(3)")
    value_date_time: SmartsheetAddFieldsInputFieldsItemPropertyLookupFilterConditionsItemMatchValueValueDateTime = Field(
        default=None, description="日期时间类匹配值，用于日期(4)/创建时间(12)/修改时间(13)"
    )
    value_number: float = Field(
        default=None, description="数字类匹配值，用于数字(2)/进度(14)/百分比(28)"
    )
    value_selects: list[str] = Field(
        default=None,
        description="选项类匹配值，为选项ID列表，用于多选(9)/单选(17)/人员(7)/创建人(10)/修改人(11)等",
        max_length=100,
    )
    value_text: str = Field(
        default=None,
        description="文本类匹配值，用于文本(1)/URL(8)/电话(15)/邮箱(16)/引用(18)/标题(24)",
        max_length=100000,
    )
    value_type: int = Field(
        default=None, description="匹配值类型，枚举值：0-与具体值比较，1-与目标表另一列比较"
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFilterConditionsItem(Input):
    condition_id: str = Field(
        default=None,
        description="条件ID，用于唯一标识一条筛选条件，同一 filter 内不能重复(如 cdt1、cdt2)；不填时由服务端按顺序自动生成",
        max_length=100000,
    )
    field_id: str = Field(
        default=None,
        description="筛选条件作用的列ID，必须为被查找目标表中已存在的列，不能为空",
        max_length=100000,
    )
    field_type: int = Field(
        default=None,
        description="列类型(FieldType)，枚举值：1-文本，2-数字，3-勾选，4-日期，8-URL，9-多选，12-创建时间，13-修改时间，14-进度，15-电话，16-邮箱，17-单选，18-引用，24-标题，28-百分比",
    )
    match_value: SmartsheetAddFieldsInputFieldsItemPropertyLookupFilterConditionsItemMatchValue = Field(
        default=None,
        description="匹配值。当 operator 为 9(为空)/10(不为空) 时无需设置；其余操作符必须设置，否则条件非法会被拒绝",
    )
    operator: int = Field(
        default=None,
        description="筛选操作符，枚举值：1-等于，2-不等于，3-包含，4-不包含，5-大于，6-大于等于，7-小于，8-小于等于，9-为空，10-不为空。除9(为空)/10(不为空) 外，其余操作符必须同时设置 match_value",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFilter(Input):
    conditions: list[SmartsheetAddFieldsInputFieldsItemPropertyLookupFilterConditionsItem] = Field(
        default=None, description="筛选条件列表", max_length=100
    )
    conjunction: int = Field(default=None, description="条件组合方式，枚举值：1-and，2-or")


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyAutoNumberRulesItem(Input):
    type: int = Field(
        default=None, description="规则类型，枚举值：1-自增ID，2-固定字符，3-创建时间"
    )
    value: str = Field(
        default=None,
        description="规则值，存放创建时间格式或固定字符，自增数字位数",
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyAutoNumber(Input):
    rules: list[
        SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyAutoNumberRulesItem
    ] = Field(default=None, description="自定义规则列表，type为2时生效", max_length=100)
    type: int = Field(default=None, description="编号类型，枚举值：1-自增数字类型，2-自定义类型")


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyCheckbox(Input):
    checked: bool = Field(default=None, description="新增时是否默认勾选")


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyCreatedTime(Input):
    format: str = Field(
        default=None,
        description='创建时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyCurrency(Input):
    currency_type: int = Field(
        default=None,
        description="货币类型，枚举值：1-CNY人民币，2-USD美元，3-EUR欧元，4-GBP英镑，5-JPY日元，6-KRW韩元，7-HKD港元，8-MOP澳门元，9-TWD台币，10-AED迪拉姆，11-AUD澳元，12-BRL巴西雷亚尔，13-CAD加元，14-CHF瑞士法郎，15-IDR印尼盾，16-INR印度卢比，17-MXN墨西哥比索，18-MYR马来西亚林吉特，19-PHP菲律宾比索，20-PLN波兰兹罗提，21-RUB俄罗斯卢布，22-SGD新加坡元，23-THB泰铢，24-TRY土耳其里拉，25-VND越南盾",
    )
    decimal_places: int = Field(default=None, description="小数位数，范围0-4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyDateTime(Input):
    auto_fill: bool = Field(default=None, description="新建记录时，是否自动填充时间")
    format: str = Field(
        default=None,
        description='日期时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyModifiedTime(Input):
    format: str = Field(
        default=None,
        description='最后编辑时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyNumber(Input):
    decimal_places: int = Field(default=None, description="表示小数点的位数，即数字精度")
    use_separate: bool = Field(
        default=None,
        description="是否使用千位符，设置此属性后数字字段将以英文逗号分隔千分位，如 1,000",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyPercentage(Input):
    decimal_places: int = Field(default=None, description="小数位数，范围-1到4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyProgress(Input):
    decimal_places: int = Field(default=None, description="小数位数")


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyReference(Input):
    field_id: str = Field(default=None, description="关联的字段ID", max_length=100000)
    is_multiple: bool = Field(default=None, description="是否允许多选")
    sub_id: str = Field(
        default=None, description="关联的子表ID，为空时表示关联本子表", max_length=100000
    )
    view_id: str = Field(default=None, description="关联视图ID", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertySelectOptionsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertySelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[
        SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertySelectOptionsItem
    ] = Field(default=None, description="多选选项的格式设置", max_length=100)


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertySingleSelectOptionsItem(
    Input
):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertySingleSelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[
        SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertySingleSelectOptionsItem
    ] = Field(default=None, description="单选选项的格式设置", max_length=100)


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyUrl(Input):
    type: int = Field(default=None, description="超链接展示样式 枚举值：0-未知，1-文字，2-图标文字")


class SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatter(Input):
    property_auto_number: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyAutoNumber = Field(
        default=None, description="自动编号类型的展示格式属性，包含编号类型和自定义规则配置"
    )
    property_checkbox: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyCheckbox = (
        Field(default=None, description="复选框类型的展示格式属性，包含默认勾选状态配置")
    )
    property_created_time: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyCreatedTime = Field(
        default=None, description="创建时间类型的展示格式属性，包含时间格式配置"
    )
    property_created_user: dict[str, JsonValue] = Field(
        default=None, description="创建人类型的展示格式属性，创建人类型不需要额外的配置属性"
    )
    property_currency: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyCurrency = (
        Field(default=None, description="货币类型的展示格式属性，包含货币种类和小数位数配置")
    )
    property_date_time: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyDateTime = Field(
        default=None, description="日期时间类型的展示格式属性，包含格式和自动填充配置"
    )
    property_email: dict[str, JsonValue] = Field(
        default=None, description="邮件类型的展示格式属性，邮件类型不需要额外的配置属性"
    )
    property_image: dict[str, JsonValue] = Field(
        default=None, description="图片类型的展示格式属性，图片类型不需要额外的配置属性"
    )
    property_modified_time: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyModifiedTime = Field(
        default=None, description="最后编辑时间类型的展示格式属性，包含时间格式配置"
    )
    property_modified_user: dict[str, JsonValue] = Field(
        default=None, description="最后编辑人类型的展示格式属性，最后编辑人类型不需要额外的配置属性"
    )
    property_number: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyNumber = (
        Field(default=None, description="数字类型的展示格式属性，包含精度和千位符等配置")
    )
    property_percentage: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyPercentage = Field(
        default=None, description="百分比类型的展示格式属性，包含小数位数和千位符配置"
    )
    property_phone_number: dict[str, JsonValue] = Field(
        default=None, description="电话类型的展示格式属性，电话类型不需要额外的配置属性"
    )
    property_progress: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyProgress = (
        Field(default=None, description="进度类型的展示格式属性，包含小数位数配置")
    )
    property_reference: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyReference = Field(
        default=None, description="关联类型的展示格式属性，包含关联子表、字段和多选配置"
    )
    property_select: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertySelect = (
        Field(default=None, description="多选类型的展示格式属性，包含选项和选择模式配置")
    )
    property_single_select: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertySingleSelect = Field(
        default=None, description="单选类型的展示格式属性，包含选项和选择模式配置"
    )
    property_text: dict[str, JsonValue] = Field(
        default=None, description="文本类型的展示格式属性，文本类型不需要额外的配置属性"
    )
    property_url: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatterPropertyUrl = Field(
        default=None, description="超链接类型的展示格式属性，包含展示样式配置"
    )
    property_user: dict[str, JsonValue] = Field(
        default=None, description="用户类型的展示格式属性，用户类型不需要额外的配置属性"
    )
    type: int = Field(
        default=None,
        description="展示格式对应的列类型(FieldType)，必填且不能为0，它决定使用下方哪个 property 字段(如 26 对应 property_currency)。枚举值：1-文本，2-数字，3-勾选，4-日期，5-图片，7-用户，8-URL，9-多选，10-创建人，11-最后编辑人，12-创建时间，13-修改时间，14-进度，15-电话，16-邮箱，17-单选，18-引用，25-自动编号，26-货币，28-百分比。注意不能填19(公式)/20(查找引用)，展示格式本身不能再是公式或查找引用",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyLookup(Input):
    filter: SmartsheetAddFieldsInputFieldsItemPropertyLookupFilter = Field(
        default=None, description="查找引用的筛选条件，仅在按条件查找(upgrade_type=1)时生效"
    )
    formatter: SmartsheetAddFieldsInputFieldsItemPropertyLookupFormatter = Field(
        default=None,
        description="统计格式设置，用于设置查找引用结果的展示格式，展示格式的类型不一定与计算结果类型一致。可选，不填则由系统自动推断格式。填写时必须同时设置 formatter.type(字段名就是 type，不是 formatter_type) 和与之匹配的 property_xxx，只填 property_xxx 而漏填 type 会被服务端拒绝",
    )
    link_records_field_id: str = Field(
        default=None,
        description="本表中的关联列ID，必须为已存在的关联列。仅在按关联查找(upgrade_type=0)时必填；按条件查找(upgrade_type=1)时无需填写",
        max_length=100000,
    )
    lookup_field_id: str = Field(
        default=None, description="被查找目标表中的列ID，必须为已存在的列", max_length=100000
    )
    lookup_sub_id: str = Field(
        default=None, description="被查找目标表的子表ID，为空时表示本子表", max_length=100000
    )
    rollup_type: int = Field(
        default=None,
        description="统计类型，枚举值：0-原样引用，1-去重引用，2-求和，3-计数，4-去重计数，5-平均值，6-最大值，7-最小值",
    )
    upgrade_type: int = Field(
        default=None,
        description="查找引用方式，枚举值：0-按关联查找(通过本表关联列做桥梁，需填写link_records_field_id)，1-按条件查找(通过 filter 筛选条件，无需 link_records_field_id)",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyModifiedTime(Input):
    format: str = Field(
        default=None,
        description='最后编辑时间格式，支持格式：yyyy"年"m"月"d"日" - 2018 年 4 月 20 日，yyyy-mm-dd - 2018-04-20，yyyy/m/d - 2018/4/20，m"月"d"日" - 4 月 20 日，[$-804]yyyy"年"m"月"d"日" dddd - 2018 年 4 月 20 日 星期五，yyyy"年"m"月"d"日" hh:mm - 2018 年 4 月 20 日 14:00，yyyy-mm-dd hh:mm - 2018-04-20 14:00，m/d/yyyy - 4/20/2018，d/m/yyyy - 20/4/2018',
        max_length=100000,
    )


class SmartsheetAddFieldsInputFieldsItemPropertyNumber(Input):
    decimal_places: int = Field(default=None, description="表示小数点的位数，即数字精度")
    use_separate: bool = Field(
        default=None,
        description="是否使用千位符，设置此属性后数字字段将以英文逗号分隔千分位，如 1,000",
    )


class SmartsheetAddFieldsInputFieldsItemPropertyPercentage(Input):
    decimal_places: int = Field(default=None, description="小数位数，范围-1到4")
    use_separate: bool = Field(default=None, description="是否使用千位符")


class SmartsheetAddFieldsInputFieldsItemPropertyProgress(Input):
    decimal_places: int = Field(default=None, description="小数位数")


class SmartsheetAddFieldsInputFieldsItemPropertyReference(Input):
    field_id: str = Field(default=None, description="关联的字段ID", max_length=100000)
    is_multiple: bool = Field(default=None, description="是否允许多选")
    sub_id: str = Field(
        default=None, description="关联的子表ID，为空时表示关联本子表", max_length=100000
    )
    view_id: str = Field(default=None, description="关联视图ID", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertySelectOptionsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertySelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[SmartsheetAddFieldsInputFieldsItemPropertySelectOptionsItem] = Field(
        default=None, description="多选选项的格式设置", max_length=100
    )


class SmartsheetAddFieldsInputFieldsItemPropertySingleSelectOptionsItem(Input):
    id: str = Field(default=None, description="选项 ID", max_length=100000)
    style: int = Field(
        default=None,
        description="选项颜色，枚举值：1-红色，2-橘黄色，3-蓝色，4-绿色，5-紫色，6-粉色，7-灰色，8-白色",
    )
    text: str = Field(default=None, description="要填写的选项内容", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertySingleSelect(Input):
    is_multiple: bool = Field(default=None, description="是否多选，用户不需要设置该参数")
    is_quick_add: bool = Field(
        default=None, description="是否允许填写时新增选项，用户不需要设置该参数"
    )
    options: list[SmartsheetAddFieldsInputFieldsItemPropertySingleSelectOptionsItem] = Field(
        default=None, description="单选选项的格式设置", max_length=100
    )


class SmartsheetAddFieldsInputFieldsItemPropertyTwoWayLinkRecords(Input):
    back_field_id: str = Field(
        default=None,
        description="服务端生成的反向字段ID；请求时不得指定，仅在响应中返回",
        max_length=100000,
    )
    field_id: str = Field(
        default=None, description="目标表展示字段ID；可选，默认主字段", max_length=100000
    )
    is_multiple: bool = Field(default=None, description="是否允许多选")
    sub_id: str = Field(
        default=None, description="目标子表ID；首期仅支持同文档跨子表关联", max_length=100000
    )
    view_id: str = Field(default=None, description="目标视图ID；可选", max_length=100000)


class SmartsheetAddFieldsInputFieldsItemPropertyUrl(Input):
    type: int = Field(default=None, description="超链接展示样式 枚举值：0-未知，1-文字，2-图标文字")


class SmartsheetAddFieldsInputFieldsItemPropertyUserC(Input):
    is_multiple: bool = Field(default=None, description="是否允许添加多个成员，默认 false")
    is_notified: bool = Field(default=None, description="添加成员时是否通知该成员，默认 true")


class SmartsheetAddFieldsInputFieldsItem(Input):
    before_field_id: str = Field(
        default=None,
        description="可选。仅 add_fields 生效：插入到该 field_id 之前；省略则追加到列末尾。批量添加时，相同 before_field_id 的多个字段按数组顺序连续插在锚点前。须先通过 list_fields 取得目标 field_id。update_fields 忽略此字段。",
        max_length=100000,
    )
    field_id: str = Field(
        default=None,
        description="字段 ID，更新字段属性时需要填写该字段，但字段 ID 不能被更新",
        max_length=100000,
    )
    field_title: str = Field(default=None, description="需要更新为的字段标题", max_length=100000)
    field_type: Literal[
        "text",
        "number",
        "checkbox",
        "dateTime",
        "image",
        "attachment",
        "url",
        "select",
        "createdUser",
        "modifiedUser",
        "createdTime",
        "modifiedTime",
        "progress",
        "phoneNumber",
        "email",
        "singleSelect",
        "reference",
        "twoWayLinkRecords",
        "autoNumber",
        "currency",
        "percentage",
        "formula",
        "lookup",
        "user",
    ] = Field(
        default=None,
        description="字段类型，该字段不允许被更新，但更新时必须传入原字段类型值。枚举值：text-文本，number-数字，checkbox-复选框，dateTime-日期，image-图片，attachment-附件，url-超链接，select-多选，createdUser-创建人，modifiedUser-最后编辑人，createdTime-创建时间，modifiedTime-最后编辑时间，progress-进度，phoneNumber-电话，email-邮件，singleSelect-单选，reference-关联，twoWayLinkRecords-双向关联，autoNumber-自动编号，currency-货币，percentage-百分比，formula-公式，lookup-查找引用，user-成员",
    )
    property_attachment: dict[str, JsonValue] = Field(
        default=None, description="附件类型的字段属性，附件类型字段不需要额外的配置属性"
    )
    property_auto_number: SmartsheetAddFieldsInputFieldsItemPropertyAutoNumber = Field(
        default=None, description="自动编号类型的字段属性，包含编号类型和自定义规则配置"
    )
    property_checkbox: SmartsheetAddFieldsInputFieldsItemPropertyCheckbox = Field(
        default=None, description="复选框类型的字段属性，包含默认勾选状态配置"
    )
    property_created_time: SmartsheetAddFieldsInputFieldsItemPropertyCreatedTime = Field(
        default=None, description="创建时间类型的字段属性，包含时间格式配置"
    )
    property_created_user: dict[str, JsonValue] = Field(
        default=None, description="创建人类型的字段属性，创建人类型字段不需要额外的配置属性"
    )
    property_currency: SmartsheetAddFieldsInputFieldsItemPropertyCurrency = Field(
        default=None, description="货币类型的字段属性，包含货币种类和小数位数配置"
    )
    property_date_time: SmartsheetAddFieldsInputFieldsItemPropertyDateTime = Field(
        default=None, description="日期时间类型的字段属性，包含格式和自动填充配置"
    )
    property_email: dict[str, JsonValue] = Field(
        default=None, description="邮件类型的字段属性，邮件类型字段不需要额外的配置属性"
    )
    property_formula: SmartsheetAddFieldsInputFieldsItemPropertyFormula = Field(
        default=None, description="公式类型的字段属性，包含公式表达式模型和展示格式配置"
    )
    property_image: dict[str, JsonValue] = Field(
        default=None, description="图片类型的字段属性，图片类型字段不需要额外的配置属性"
    )
    property_lookup: SmartsheetAddFieldsInputFieldsItemPropertyLookup = Field(
        default=None, description="查找引用类型的字段属性，包含关联列、被查找列、统计类型和筛选配置"
    )
    property_modified_time: SmartsheetAddFieldsInputFieldsItemPropertyModifiedTime = Field(
        default=None, description="最后编辑时间类型的字段属性，包含时间格式配置"
    )
    property_modified_user: dict[str, JsonValue] = Field(
        default=None, description="最后编辑人类型的字段属性，最后编辑人类型字段不需要额外的配置属性"
    )
    property_number: SmartsheetAddFieldsInputFieldsItemPropertyNumber = Field(
        default=None, description="数字类型的字段属性，包含精度和千位符等配置"
    )
    property_percentage: SmartsheetAddFieldsInputFieldsItemPropertyPercentage = Field(
        default=None, description="百分比类型的字段属性，包含小数位数和千位符配置"
    )
    property_phone_number: dict[str, JsonValue] = Field(
        default=None, description="电话类型的字段属性，电话类型字段不需要额外的配置属性"
    )
    property_progress: SmartsheetAddFieldsInputFieldsItemPropertyProgress = Field(
        default=None, description="进度类型的字段属性，包含小数位数配置"
    )
    property_reference: SmartsheetAddFieldsInputFieldsItemPropertyReference = Field(
        default=None, description="关联类型的字段属性，包含关联子表、字段和多选配置"
    )
    property_select: SmartsheetAddFieldsInputFieldsItemPropertySelect = Field(
        default=None, description="多选类型的字段属性，包含选项和选择模式配置"
    )
    property_single_select: SmartsheetAddFieldsInputFieldsItemPropertySingleSelect = Field(
        default=None, description="单选类型的字段属性，包含选项和选择模式配置"
    )
    property_text: dict[str, JsonValue] = Field(
        default=None, description="文本类型的字段属性，文本类型字段不需要额外的配置属性"
    )
    property_two_way_link_records: SmartsheetAddFieldsInputFieldsItemPropertyTwoWayLinkRecords = (
        Field(
            default=None,
            description="双向关联类型字段属性；新增时 sub_id 必填，back_field_id 仅在响应中返回",
        )
    )
    property_url: SmartsheetAddFieldsInputFieldsItemPropertyUrl = Field(
        default=None, description="超链接类型的字段属性，包含展示样式配置"
    )
    property_user: dict[str, JsonValue] = Field(
        default=None, description="用户类型的字段属性，用户类型字段不需要额外的配置属性"
    )
    property_user_c: SmartsheetAddFieldsInputFieldsItemPropertyUserC = Field(
        default=None, description="成员类型的字段属性，包含多选和通知配置"
    )


class SmartsheetAddFieldsInput(Input):
    fields: list[SmartsheetAddFieldsInputFieldsItem] = Field(
        description="要添加的字段的具体内容组成的数组", max_length=100
    )
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="工作表ID", max_length=100000)


class SmartsheetCreateDashboardFromPlanInputProperties(Input):
    index: int = Field(default=None, description="工作表下标")
    sheet_id: str = Field(default=None, description="工作表唯一标识符", max_length=100000)
    title: str = Field(default=None, description="工作表标题", max_length=100000)


class SmartsheetCreateDashboardFromPlanInput(Input):
    components: list[str] = Field(
        description="组件规划文本数组。每项使用仪表盘规划中的组件格式，例如：任务总数 | T3\\n- 数据源：tableId\\n- 数值轴：COUNT",
        max_length=100,
    )
    dashboard_name: str = Field(description="仪表盘名称", max_length=100000)
    file_id: str = Field(description="智能表格文档的唯一标识符", max_length=100000)
    positions: str = Field(
        description='JSON 格式的组件布局数组，每项为 [offsetX, offsetY, width, height]，项数与顺序必须和 components 一致。width 为 2~12，height 至少为 2（包括文本组件），offsetX/offsetY 不小于 0，且 offsetX+width 不超过 12；组件之间不得重叠，允许留白。示例："[[0,0,6,4],[6,0,6,4]]"',
        max_length=100000,
    )
    properties: SmartsheetCreateDashboardFromPlanInputProperties = Field(
        default=None, description="仪表盘插入位置；可空，sheet_id 留空时由服务生成"
    )


class SmartsheetOperations:
    @operation(
        name="smartsheet_list_tables",
        description="列出文档下的工作表，返回工作表的基本信息列表",
        effects="read",
    )
    async def smartsheet_list_tables(self, ctx, params: SmartsheetListTablesInput) -> Result:
        return await call(
            ctx,
            "smartsheet.list_tables",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_get_dashboard_component",
        description="获取智能表仪表盘中指定组件的类型、标题、位置和数据配置",
        effects="read",
    )
    async def smartsheet_get_dashboard_component(
        self, ctx, params: SmartsheetGetDashboardComponentInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.get_dashboard_component",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_delete_fields",
        description="批量删除字段，支持同时删除多个指定的字段",
        effects="write",
    )
    async def smartsheet_delete_fields(self, ctx, params: SmartsheetDeleteFieldsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.delete_fields",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_update_records",
        description='批量更新记录，支持修改多条记录的字段值。字段值(field_values)格式与 add_records 一致：文本字段 text_value 为 {"items":[{"text":"内容","type":"text"}]}（type 必填且固定为 "text"）；选项字段 option_value 只需传 {"items":[{"text":"选项文本"}]}；数字字段 number_value 直接传数字；日期字段 string_value 传毫秒级时间戳',
        effects="write",
    )
    async def smartsheet_update_records(self, ctx, params: SmartsheetUpdateRecordsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.update_records",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_list_records",
        description="分页列出工作表记录，支持排序和筛选条件",
        effects="read",
    )
    async def smartsheet_list_records(self, ctx, params: SmartsheetListRecordsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.list_records",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_create_automation_from_plan",
        description="根据一条规划文本创建智能表自动化。首期支持新增记录、修改记录、到达记录时间触发，以及查找记录、新增记录、修改记录、发送消息动作；不支持 Webhook、HTTP 请求、运行脚本、创建群、添加群成员、复杂 JSON 引用和仪表盘截图消息。创建默认关闭",
        effects="write",
    )
    async def smartsheet_create_automation_from_plan(
        self, ctx, params: SmartsheetCreateAutomationFromPlanInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.create_automation_from_plan",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_list_views",
        description="列出工作表视图，返回视图的基本信息和配置",
        effects="read",
    )
    async def smartsheet_list_views(self, ctx, params: SmartsheetListViewsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.list_views",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_get_dashboard",
        description="获取智能表仪表盘的标题和组件索引列表（组件ID、类型、标题、位置）。修改、更新或删除仪表盘组件前，先调用本工具获取组件ID和现有布局",
        effects="read",
    )
    async def smartsheet_get_dashboard(self, ctx, params: SmartsheetGetDashboardInput) -> Result:
        return await call(
            ctx,
            "smartsheet.get_dashboard",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_commit_changeset",
        description="提交智能表的编辑变更，将 changeset（mutation 数据）提交到服务器，走离线提交链路。需先调用 smartsheet.fetch 获取当前版本号（base_rev），再构造 changeset 后提交。此工具提供给 MCP App 内部调用，AI 不要直接调用",
        effects="write",
    )
    async def smartsheet_commit_changeset(
        self, ctx, params: SmartsheetCommitChangesetInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.commit_changeset",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_fetch",
        description="打开智能表，获取指定子表的完整关键帧二进制数据（raw_data），供后续解析和编辑使用。需配合 smartsheet.commit_changeset 将编辑结果提交回服务器。此工具提供给 MCP App 内部调用，AI 不要直接调用",
        effects="read",
    )
    async def smartsheet_fetch(self, ctx, params: SmartsheetFetchInput) -> Result:
        return await call(
            ctx,
            "smartsheet.fetch",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_list_automations",
        description="列出智能表格文档内的自动化流程摘要（workflow_id、名称、状态、触发器和动作数量）。修改或删除自动化前，先调用本工具按名称确认 workflow_id",
        effects="read",
    )
    async def smartsheet_list_automations(
        self, ctx, params: SmartsheetListAutomationsInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.list_automations",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_update_automation_from_plan",
        description="根据一条完整规划文本覆盖更新指定智能表自动化。系统先读取现有流程再完整替换，不能发送局部字段；当前保留原自动化的启停状态；支持范围与 create_automation_from_plan 相同；若规划文本包含多条自动化，仅使用第一条更新并在 message 字段提示",
        effects="write",
    )
    async def smartsheet_update_automation_from_plan(
        self, ctx, params: SmartsheetUpdateAutomationFromPlanInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.update_automation_from_plan",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_add_table",
        description="在文档中新增工作表，支持设置工作表名称和初始配置",
        effects="write",
    )
    async def smartsheet_add_table(self, ctx, params: SmartsheetAddTableInput) -> Result:
        return await call(
            ctx,
            "smartsheet.add_table",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_update_view",
        description="更新非查询视图的标题、筛选、排序、分组、字段显隐、列宽和冻结列。patch_json 顶层仅支持 title、filter、sort、group、fields、frozen_field_count；排序请使用 sort.items，每项包含 field_id 和 direction（asc 或 desc），field_id 必须来自 smartsheet.list_fields 且不可重复；不要直接传入 infos、sortInfos 或 list_views 返回的完整 view.config。调用前必须先调用 smartsheet.list_views；涉及字段时必须先调用 smartsheet.list_fields",
        effects="write",
    )
    async def smartsheet_update_view(self, ctx, params: SmartsheetUpdateViewInput) -> Result:
        return await call(
            ctx,
            "smartsheet.update_view",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_delete_table",
        description="删除指定的工作表，支持批量删除多个工作表",
        effects="write",
    )
    async def smartsheet_delete_table(self, ctx, params: SmartsheetDeleteTableInput) -> Result:
        return await call(
            ctx,
            "smartsheet.delete_table",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_delete_automation",
        description="删除智能表格文档中指定 workflow_id 的一条自动化流程；删除前先调用 list_automations 确认目标",
        effects="write",
    )
    async def smartsheet_delete_automation(
        self, ctx, params: SmartsheetDeleteAutomationInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.delete_automation",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_delete_records",
        description="批量删除记录，支持同时删除多条指定的记录",
        effects="write",
    )
    async def smartsheet_delete_records(self, ctx, params: SmartsheetDeleteRecordsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.delete_records",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_list_fields",
        description="列出工作表字段，返回字段的基本信息和类型配置。fields 顺序由 view_id 决定；有用户选区时必须传 selection.viewId，否则列序可能不是用户所见顺序，导致 before_field_id 推算错误。省略 view_id 时按首个公开视图排序",
        effects="read",
    )
    async def smartsheet_list_fields(self, ctx, params: SmartsheetListFieldsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.list_fields",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_delete_dashboard_component",
        description="删除智能表仪表盘中指定组件",
        effects="write",
    )
    async def smartsheet_delete_dashboard_component(
        self, ctx, params: SmartsheetDeleteDashboardComponentInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.delete_dashboard_component",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_get_client_var",
        description="获取智能表文档的 clientVar 配置信息，返回包含文档初始化配置的 JSON 字符串。此工具提供给 MCP App 内部调用，AI 不要直接调用",
        effects="read",
    )
    async def smartsheet_get_client_var(self, ctx, params: SmartsheetGetClientVarInput) -> Result:
        return await call(
            ctx,
            "smartsheet.get_client_var",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_add_records",
        description='批量添加记录，支持同时添加多条记录数据。位置由每条记录的 before_record_id 控制（插到该 record_id 之前；省略则与历史行为相同，追加到末尾），不是数字 index。指定位置前须先调用 list_records 取得目标 record_id；相同 before_record_id 的多条按数组顺序连续插入。字段值(field_values)格式按字段类型选择：文本字段 text_value 格式为 {"items":[{"text":"内容","type":"text"}]}（type 必填且固定为 "text"，缺省会报 22015）；选项字段 option_value 只需传 {"items":[{"text":"选项文本"}]}，id 由服务端解析；数字/进度/货币/百分比字段 number_value 直接传数字如 60；日期字段 string_value 传毫秒级时间戳如 "1785686400000"；自动编号字段无需传值',
        effects="write",
    )
    async def smartsheet_add_records(self, ctx, params: SmartsheetAddRecordsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.add_records",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_create_table_from_plan",
        description="根据规划文本创建一张智能表工作表，保留字段、视图、主键、描述和字段编组；一次调用仅创建一张工作表，若规划文本包含多张表格，请拆分后分别调用",
        effects="write",
    )
    async def smartsheet_create_table_from_plan(
        self, ctx, params: SmartsheetCreateTableFromPlanInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.create_table_from_plan",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_add_view",
        description="新增视图，支持自定义视图名称、筛选条件和显示字段",
        effects="write",
    )
    async def smartsheet_add_view(self, ctx, params: SmartsheetAddViewInput) -> Result:
        return await call(
            ctx,
            "smartsheet.add_view",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_delete_view",
        description="删除指定的视图，支持批量删除多个视图",
        effects="write",
    )
    async def smartsheet_delete_view(self, ctx, params: SmartsheetDeleteViewInput) -> Result:
        return await call(
            ctx,
            "smartsheet.delete_view",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_update_fields",
        description="批量更新字段，支持修改字段名称、类型和配置信息",
        effects="write",
    )
    async def smartsheet_update_fields(self, ctx, params: SmartsheetUpdateFieldsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.update_fields",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_update_dashboard_component_from_plan",
        description="根据完整组件规划更新智能表仪表盘中指定组件，组件位置保持不变",
        effects="write",
    )
    async def smartsheet_update_dashboard_component_from_plan(
        self, ctx, params: SmartsheetUpdateDashboardComponentFromPlanInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.update_dashboard_component_from_plan",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_add_dashboard_component_from_plan",
        description="根据组件规划在智能表仪表盘中新增单个组件，需同时指定组件位置布局",
        effects="write",
    )
    async def smartsheet_add_dashboard_component_from_plan(
        self, ctx, params: SmartsheetAddDashboardComponentFromPlanInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.add_dashboard_component_from_plan",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_add_fields",
        description="批量新增字段，支持同时添加多个不同类型的字段。位置由每个字段的 before_field_id 控制（插到该 field_id 之前；省略则与历史行为相同，追加到列末尾），不是数字 index。指定位置前须先调用 list_fields 取得目标 field_id；相同 before_field_id 的多个字段按数组顺序连续插入",
        effects="write",
    )
    async def smartsheet_add_fields(self, ctx, params: SmartsheetAddFieldsInput) -> Result:
        return await call(
            ctx,
            "smartsheet.add_fields",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="smartsheet_create_dashboard_from_plan",
        description="根据规划文本创建一个智能表仪表盘，包含图表、表格、统计数字、文本、词云、布局和筛选条件；一次调用仅创建一个仪表盘",
        effects="write",
    )
    async def smartsheet_create_dashboard_from_plan(
        self, ctx, params: SmartsheetCreateDashboardFromPlanInput
    ) -> Result:
        return await call(
            ctx,
            "smartsheet.create_dashboard_from_plan",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )
