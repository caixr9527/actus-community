# 腾讯文档

腾讯文档个人 Token 应用，独立运行于 Actus Connector SDK。当前使用
`0.0.1b3.dev1` 候选 SDK，仅供隔离开发验证；尚未完成正式依赖交付。

## 范围与契约

保留旧应用 6 个常用操作名与 213 个扩展操作，共 219 个静态声明。
`contracts/` 保存开发时核对的上游声明，运行时不会发现或自动注册新工具。
扩展操作用上游名称将 `.` 替换为 `_`；参数按冻结 Schema 生成具体 Pydantic
模型。智能表字段使用结构化 `fields`，不再使用旧适配器的 `fields_json`。
运行不依赖平台工程、旧 Provider、私有配置或其他服务的凭据。

常用操作：`list_files`、`search_files`、`list_spaces`、`list_space_nodes`、
`read_document`、`create_document`。最近文档每页限制 1–20 条，搜索按标题匹配。
扩展操作保留上游可选字段的“未提供”语义，不自动填入空值；显式非法 null 拒绝。
模型直接声明的字符串字段最多 100,000 字符，数组字段最多 100 项；开放 JSON 值、
嵌套数组元素及完整请求/响应仍受 Runtime 总体字节和截止时间限制。

所有操作的结果为 `{"data": {...}}`，原样保留厂商 JSON 字段与缺失状态。
上游输出既包含普通对象，也包含开放的 protobuf 数据，因此不把所有输出声明为
固定业务模型，不截断成功结果、不补造成功字段。输出 Schema 快照用于审阅。
导出创建任务、网页剪藏及其进度查询按写操作处理。没有通用自动重试；
写入后断连、工具内部错误或无效响应仍可能已有副作用，结果应核实。

仅使用 SDK 的公开 `ctx.http()`，Token 由 SDK 注入官方固定 HTTPS 地址。
不允许配置任意 MCP 地址。连接身份取真实 `get_user_info.user_id`，不使用 Token
指纹冒充账号；权限未知时不生成能力许可。支持 JSON、SSE 和空 202 通知，
请求继承调用截止时间、字节限制和取消收尾。固定使用实测协商成功的 MCP
`2025-03-26`；SSE 支持 UTF-8 分块、BOM、LF/CRLF/CR 行结束符和多行 data。

协议参考：[MCP Streamable HTTP](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)。

导入/附件等操作仍返回腾讯上传链接和任务参数；应用不代传 Sandbox 文件，
不自动访问返回的上传/下载 URL，不包含文件流、OAuth、Agent 发现或 UI。
大文件与二进制传输仍需后续文件协议。

## 开发验证

在新环境显式安装候选 SDK wheel，再安装本项目。候选 wheel 路径由构建者提供，
不要修改平台正式依赖、锁文件或离线 wheelhouse，不回退官方源：

```bash
uv venv /absolute/new-env --python 3.12
uv pip install --python /absolute/new-env/bin/python \
  --index-url https://mirrors.cloud.tencent.com/pypi/simple \
  '/absolute/actus_connector_sdk-0.0.1b3.dev1-py3-none-any.whl[build,serve]'
uv pip install --python /absolute/new-env/bin/python \
  --index-url https://mirrors.cloud.tencent.com/pypi/simple '.[test]'
/absolute/new-env/bin/connector check --project pyproject.toml
/absolute/new-env/bin/python -m pytest -p no:cacheprovider tests
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  /absolute/new-env/bin/connector build --project pyproject.toml \
  --output-dir /absolute/new-delivery \
  --sdk-wheel /absolute/actus_connector_sdk-0.0.1b3.dev1-py3-none-any.whl
```

`tools/generate.py <group>` 从已审阅契约输出补丁，可用 apply_patch 应用。
生成后执行 Ruff、测试和 `connector check`。上游新增能力需单独审阅、更新静态源码、
重新构建发布；不能运行时替换目录。真实测试需通过外部文件提供专用 Token，
只操作当轮新建测试对象，并记录核实后的清理结果，不把秘密放入本工程。

候选验证通过后仍需独立授权发布 SDK；等腾讯镜像同步且 wheel、sdist 摘要与
正式发布产物一致，才可升级平台正式依赖和交付材料。当前包不代表已上线。
