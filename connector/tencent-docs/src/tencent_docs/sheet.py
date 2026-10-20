"""Generated from reviewed contracts; regenerate with tools/generate.py."""

from connector_sdk import operation
from pydantic import Field

from .mcp import call
from .models import Input, Result


class SheetSetRangeValueInputValuesItem(Input):
    bool_value: bool = Field(default=None, description="布尔值，value_type 为 BOOL 时使用")
    col: int = Field(default=None, description="列索引（0-based）")
    formula: str = Field(
        default=None,
        description='公式，value_type 为 FORMULA 时使用，例如 "=SUM(A1:A10)"',
        max_length=100000,
    )
    number_value: float = Field(default=None, description="数值，value_type 为 NUMBER 时使用")
    row: int = Field(default=None, description="行索引（0-based）")
    string_value: str = Field(
        default=None, description="字符串值，value_type 为 STRING 时使用", max_length=100000
    )
    value_type: str = Field(
        default=None,
        description="值类型，合法值: NUMBER, STRING, BOOL, FORMULA（不区分大小写）",
        max_length=100000,
    )


class SheetSetRangeValueInput(Input):
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    values: list[SheetSetRangeValueInputValuesItem] = Field(
        default=None,
        description="单元格值列表，每个元素包含 row(int), col(int), value_type(string), number_value(number), string_value(string), bool_value(bool), formula(string)",
        max_length=100,
    )


class SheetSetLinkInput(Input):
    col: int = Field(default=None, description="单元格列（0-based）")
    display_text: str = Field(default=None, description="单元格显示文本（可选）", max_length=100000)
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    row: int = Field(default=None, description="单元格行（0-based）")
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    url: str = Field(default=None, description="超链接 URL", max_length=100000)


class SheetInsertImageInput(Input):
    col_index: int = Field(default=None, description="目标列索引（0-based）")
    content: str = Field(
        default=None,
        description="base64 编码后的图片内容，与 image_id 二选一；适合图片较小的场景",
        max_length=100000,
    )
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    image_id: str = Field(
        default=None,
        description="图片的 image_id，与 content 二选一；适合图片较大的场景",
        max_length=100000,
    )
    row_index: int = Field(default=None, description="目标行索引（0-based）")
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetGetSheetInfoInput(Input):
    file_id: str = Field(description="在线表格唯一标识", max_length=100000)


class SheetOperationSheetInput(Input):
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    js_script: str = Field(
        description="在沙箱中执行的JS脚本。行列索引从0开始。通过Spreadsheet对象访问表格数据，进行各种操作",
        max_length=100000,
    )
    sheet_id: str = Field(default=None, description="要操作的子表ID", max_length=100000)


class SheetClearRangeStyleInput(Input):
    end_col: int = Field(default=None, description="结束列索引")
    end_row: int = Field(default=None, description="结束行索引")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="起始列索引（0-based）")
    start_row: int = Field(default=None, description="起始行索引（0-based）")


class SheetUnsetFreezeInput(Input):
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetSetFreezeInput(Input):
    col_count: int = Field(default=None, description="冻结列数（0 = 取消冻结列）")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    row_count: int = Field(default=None, description="冻结行数（0 = 取消冻结行）")
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetClearLinkInput(Input):
    col: int = Field(default=None, description="单元格列（0-based）")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    link_id: str = Field(
        default=None, description="链接 ID（可选，不传则按位置清除）", max_length=100000
    )
    row: int = Field(default=None, description="单元格行（0-based）")
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetSetFilterInput(Input):
    end_col: int = Field(default=None, description="数据区域结束列")
    end_row: int = Field(default=None, description="数据区域结束行")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    filter_id: str = Field(
        default=None, description="筛选 ID（可选，不传则自动生成）", max_length=100000
    )
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="数据区域起始列（0-based）")
    start_row: int = Field(default=None, description="数据区域起始行（0-based）")


class SheetGetCellDataInput(Input):
    end_col: int = Field(default=None, description="结束列索引")
    end_row: int = Field(default=None, description="结束行索引")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    include_formula: bool = Field(
        default=None,
        description="true时同时返回计算值和公式源串（值+公式一次拿回），仅return_csv=false时生效",
    )
    return_csv: bool = Field(
        default=None,
        description="是否以CSV格式返回数据，true返回csv_data，false返回cells结构化数据",
    )
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="起始列索引（0-based）")
    start_row: int = Field(default=None, description="起始行索引（0-based）")


class SheetGetMergedCellsInput(Input):
    end_col: int = Field(default=None, description="查询区域结束列索引")
    end_row: int = Field(default=None, description="查询区域结束行索引")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="查询区域起始列索引（0-based）")
    start_row: int = Field(default=None, description="查询区域起始行索引（0-based）")


class SheetRemoveFilterInput(Input):
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    filter_id: str = Field(
        default=None, description="筛选 ID（可选，不传则移除该子表所有筛选）", max_length=100000
    )
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetSetCellValueInput(Input):
    bool_value: bool = Field(default=None, description="布尔值，value_type 为 BOOL 时使用")
    col: int = Field(default=None, description="列索引（0-based）")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    formula: str = Field(
        default=None,
        description='公式，value_type 为 FORMULA 时使用，例如 "=SUM(A1:A10)"',
        max_length=100000,
    )
    number_value: float = Field(default=None, description="数值，value_type 为 NUMBER 时使用")
    row: int = Field(default=None, description="行索引（0-based）")
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    string_value: str = Field(
        default=None, description="字符串值，value_type 为 STRING 时使用", max_length=100000
    )
    value_type: str = Field(
        default=None,
        description="值类型，合法值: NUMBER, STRING, BOOL, FORMULA（不区分大小写）",
        max_length=100000,
    )


class SheetSetCellStyleInput(Input):
    bg_color: str = Field(
        default=None, description='背景色，ARGB hex，如 "FFFFFFFF"', max_length=100000
    )
    bold: bool = Field(default=None, description="粗体")
    end_col: int = Field(default=None, description="结束列索引")
    end_row: int = Field(default=None, description="结束行索引")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    font_color: str = Field(
        default=None, description='字体颜色，ARGB hex，如 "FF000000"', max_length=100000
    )
    font_family: str = Field(default=None, description="字体名称", max_length=100000)
    font_size: int = Field(default=None, description="字号（pt）")
    horizontal_align: str = Field(
        default=None,
        description="水平对齐：general/left/center/right/fill/justify",
        max_length=100000,
    )
    is_clear: bool = Field(default=None, description="若为 true，则清除格式")
    italic: bool = Field(default=None, description="斜体")
    number_format_pattern: str = Field(
        default=None, description='数字格式，如 "0.00%"', max_length=100000
    )
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="起始列索引（0-based）")
    start_row: int = Field(default=None, description="起始行索引（0-based）")
    strike_through: bool = Field(default=None, description="删除线")
    underline: str = Field(
        default=None,
        description="下划线：none/single/double/single_accounting/double_accounting",
        max_length=100000,
    )
    vertical_align: str = Field(
        default=None, description="垂直对齐：top/center/bottom/justify", max_length=100000
    )
    wrap_text: bool = Field(default=None, description="自动换行")


class SheetMergeCellInput(Input):
    end_col: int = Field(default=None, description="结束列索引")
    end_row: int = Field(default=None, description="结束行索引")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    merge_type: str = Field(
        default=None, description='合并类型: "all"（默认）、"columns"、"rows"', max_length=100000
    )
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="起始列索引（0-based）")
    start_row: int = Field(default=None, description="起始行索引（0-based）")


class SheetUnmergeCellInput(Input):
    end_col: int = Field(default=None, description="结束列索引")
    end_row: int = Field(default=None, description="结束行索引")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="起始列索引（0-based）")
    start_row: int = Field(default=None, description="起始行索引（0-based）")


class SheetAddSheetInput(Input):
    append_index: bool = Field(
        default=None, description="是否追加到末尾，为 true 时 index 字段将被忽略"
    )
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    index: int = Field(default=None, description="子表位置索引（0-based），不传则追加到末尾")
    name: str = Field(default=None, description="子表名称，长度限制为31个字符", max_length=100000)


class SheetRenameSheetInput(Input):
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    name: str = Field(
        default=None, description="新的子表名称，长度限制为31个字符", max_length=100000
    )
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetDeleteDimensionInput(Input):
    count: int = Field(default=None, description="删除数量")
    dimension_type: str = Field(
        default=None, description='行列类型: "row" | "col"', max_length=100000
    )
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    index: int = Field(default=None, description="起始索引（0-based）")
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetDeleteSheetInput(Input):
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="要删除的子表 ID(必填)", max_length=100000)


class SheetInsertDimensionInput(Input):
    count: int = Field(default=None, description="插入数量")
    dimension_type: str = Field(
        default=None, description='行列类型: "row" | "col"', max_length=100000
    )
    direction: str = Field(
        default=None, description='插入方向: "before"（默认）| "after"', max_length=100000
    )
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    index: int = Field(default=None, description="起始索引（0-based）")
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetClearRangeAllInput(Input):
    end_col: int = Field(default=None, description="结束列索引")
    end_row: int = Field(default=None, description="结束行索引")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="起始列索引（0-based）")
    start_row: int = Field(default=None, description="起始行索引（0-based）")


class SheetClearRangeCellsInput(Input):
    end_col: int = Field(default=None, description="结束列索引")
    end_row: int = Field(default=None, description="结束行索引")
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)
    start_col: int = Field(default=None, description="起始列索引（0-based）")
    start_row: int = Field(default=None, description="起始行索引（0-based）")


class SheetSetDimensionSizeInputDimensionsItem(Input):
    dimension_type: str = Field(
        default=None, description='行列类型: "row" | "col"', max_length=100000
    )
    index: int = Field(default=None, description="行或列的索引（0-based）")
    is_clear: bool = Field(
        default=None, description="是否清除自定义行高/列宽并恢复默认值，为true时size字段将被忽略"
    )
    size: float = Field(default=None, description="行高或列宽的值，行高单位为pt，列宽单位为像素")


class SheetSetDimensionSizeInput(Input):
    dimensions: list[SheetSetDimensionSizeInputDimensionsItem] = Field(
        default=None, description="行高/列宽参数列表", max_length=100
    )
    file_id: str = Field(description="在线表格的唯一标识符", max_length=100000)
    sheet_id: str = Field(description="子表 ID(必填)", max_length=100000)


class SheetOperations:
    @operation(
        name="sheet_set_range_value",
        description="批量设置在线表格多个单元格的值（SHEET）",
        effects="write",
    )
    async def sheet_set_range_value(self, ctx, params: SheetSetRangeValueInput) -> Result:
        return await call(
            ctx,
            "sheet.set_range_value",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_set_link",
        description="为在线表格指定单元格设置超链接，可指定链接URL和显示文本（SHEET）",
        effects="write",
    )
    async def sheet_set_link(self, ctx, params: SheetSetLinkInput) -> Result:
        return await call(
            ctx, "sheet.set_link", params.model_dump(mode="json", by_alias=True, exclude_unset=True)
        )

    @operation(
        name="sheet_insert_image",
        description="在在线表格指定单元格插入一张图片，图片内容可通过 base64 或 image_id 传入（SHEET）",
        effects="write",
    )
    async def sheet_insert_image(self, ctx, params: SheetInsertImageInput) -> Result:
        return await call(
            ctx,
            "sheet.insert_image",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_get_sheet_info",
        description="获取在线表格的子表信息，包括子表ID、名称、类型、行列数量、已用区域末行/末列、是否隐藏子表（SHEET）",
        effects="read",
    )
    async def sheet_get_sheet_info(self, ctx, params: SheetGetSheetInfoInput) -> Result:
        return await call(
            ctx,
            "sheet.get_sheet_info",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_operation_sheet",
        description="通过JS脚本精细化操作在线表格，支持读写单元格值、设置公式、设置背景色/字体色、插入删除行列、设置行高列宽、查询子表信息等",
        effects="write",
    )
    async def sheet_operation_sheet(self, ctx, params: SheetOperationSheetInput) -> Result:
        return await call(
            ctx,
            "sheet.operation_sheet",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_clear_range_style",
        description="清除在线表格指定区域内所有单元格的样式（SHEET）",
        effects="write",
    )
    async def sheet_clear_range_style(self, ctx, params: SheetClearRangeStyleInput) -> Result:
        return await call(
            ctx,
            "sheet.clear_range_style",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_unset_freeze",
        description="删除在线表格指定子表的所有冻结行列（SHEET）",
        effects="write",
    )
    async def sheet_unset_freeze(self, ctx, params: SheetUnsetFreezeInput) -> Result:
        return await call(
            ctx,
            "sheet.unset_freeze",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_set_freeze",
        description="设置在线表格的冻结行列数，传0可取消冻结（SHEET）",
        effects="write",
    )
    async def sheet_set_freeze(self, ctx, params: SheetSetFreezeInput) -> Result:
        return await call(
            ctx,
            "sheet.set_freeze",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_clear_link",
        description="清除在线表格指定单元格的超链接，可按链接ID精确清除或清除全部超链接（SHEET）",
        effects="write",
    )
    async def sheet_clear_link(self, ctx, params: SheetClearLinkInput) -> Result:
        return await call(
            ctx,
            "sheet.clear_link",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_set_filter",
        description="为在线表格指定数据区域设置筛选（SHEET）",
        effects="write",
    )
    async def sheet_set_filter(self, ctx, params: SheetSetFilterInput) -> Result:
        return await call(
            ctx,
            "sheet.set_filter",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_get_cell_data",
        description="获取在线表格指定区域的单元格数据，支持返回CSV格式或结构化单元格数据（SHEET）",
        effects="read",
    )
    async def sheet_get_cell_data(self, ctx, params: SheetGetCellDataInput) -> Result:
        return await call(
            ctx,
            "sheet.get_cell_data",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_get_merged_cells",
        description="获取在线表格指定区域内与该区域相交的合并单元格信息，返回合并单元格范围列表，格式如 SheetID$A1:B2（SHEET）",
        effects="read",
    )
    async def sheet_get_merged_cells(self, ctx, params: SheetGetMergedCellsInput) -> Result:
        return await call(
            ctx,
            "sheet.get_merged_cells",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_remove_filter",
        description="移除在线表格的筛选，可按筛选ID精确移除或移除全部（SHEET）",
        effects="write",
    )
    async def sheet_remove_filter(self, ctx, params: SheetRemoveFilterInput) -> Result:
        return await call(
            ctx,
            "sheet.remove_filter",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_set_cell_value",
        description="设置在线表格指定单元格的值，支持文本、数字、布尔等类型（SHEET）",
        effects="write",
    )
    async def sheet_set_cell_value(self, ctx, params: SheetSetCellValueInput) -> Result:
        return await call(
            ctx,
            "sheet.set_cell_value",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_set_cell_style",
        description="设置在线表格指定范围单元格的样式，包括字体、颜色、对齐等（SHEET）",
        effects="write",
    )
    async def sheet_set_cell_style(self, ctx, params: SheetSetCellStyleInput) -> Result:
        return await call(
            ctx,
            "sheet.set_cell_style",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_merge_cell",
        description="合并在线表格指定范围的单元格，支持全部合并、按行合并、按列合并（SHEET）",
        effects="write",
    )
    async def sheet_merge_cell(self, ctx, params: SheetMergeCellInput) -> Result:
        return await call(
            ctx,
            "sheet.merge_cell",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_unmerge_cell",
        description="取消在线表格指定区域的单元格合并（SHEET）",
        effects="write",
    )
    async def sheet_unmerge_cell(self, ctx, params: SheetUnmergeCellInput) -> Result:
        return await call(
            ctx,
            "sheet.unmerge_cell",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_add_sheet",
        description="在在线表格中添加一个新的子表，支持指定子表名称和位置（SHEET）",
        effects="write",
    )
    async def sheet_add_sheet(self, ctx, params: SheetAddSheetInput) -> Result:
        return await call(
            ctx,
            "sheet.add_sheet",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_rename_sheet",
        description="重命名在线表格中指定的子表（SHEET）",
        effects="write",
    )
    async def sheet_rename_sheet(self, ctx, params: SheetRenameSheetInput) -> Result:
        return await call(
            ctx,
            "sheet.rename_sheet",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_delete_dimension",
        description="删除在线表格指定位置的行或列（SHEET）",
        effects="write",
    )
    async def sheet_delete_dimension(self, ctx, params: SheetDeleteDimensionInput) -> Result:
        return await call(
            ctx,
            "sheet.delete_dimension",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_delete_sheet", description="删除在线表格中指定的子表（SHEET）", effects="write"
    )
    async def sheet_delete_sheet(self, ctx, params: SheetDeleteSheetInput) -> Result:
        return await call(
            ctx,
            "sheet.delete_sheet",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_insert_dimension",
        description="在在线表格指定位置插入行或列（SHEET）",
        effects="write",
    )
    async def sheet_insert_dimension(self, ctx, params: SheetInsertDimensionInput) -> Result:
        return await call(
            ctx,
            "sheet.insert_dimension",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_clear_range_all",
        description="清空在线表格指定区域内所有单元格的内容和样式（SHEET）",
        effects="write",
    )
    async def sheet_clear_range_all(self, ctx, params: SheetClearRangeAllInput) -> Result:
        return await call(
            ctx,
            "sheet.clear_range_all",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_clear_range_cells",
        description="清除在线表格指定区域内所有单元格的内容（SHEET）",
        effects="write",
    )
    async def sheet_clear_range_cells(self, ctx, params: SheetClearRangeCellsInput) -> Result:
        return await call(
            ctx,
            "sheet.clear_range_cells",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )

    @operation(
        name="sheet_set_dimension_size",
        description="设置在线表格指定行的行高或指定列的列宽，支持批量设置多个行列的尺寸，也支持清除自定义尺寸恢复默认值（SHEET）",
        effects="write",
    )
    async def sheet_set_dimension_size(self, ctx, params: SheetSetDimensionSizeInput) -> Result:
        return await call(
            ctx,
            "sheet.set_dimension_size",
            params.model_dump(mode="json", by_alias=True, exclude_unset=True),
        )
