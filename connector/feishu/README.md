# 飞书

独立飞书 Connector，应用 ID `feishu`，包名 `actus-feishu`，入口
`feishu_connector.app:App`。版本 `0.1.0`，使用公开 SDK `0.0.1b9`。
用户 OAuth、文档读取、知识库浏览及多维表格单条记录读写；不依赖平台源码。

## 接入前准备

在飞书开放平台创建企业自建应用，配置应用可用范围并发布生效。管理员提供：

- `values.app_id`：应用 App ID。
- `app_secret`：通过 SDK `secrets` 与 `runtime.secret_bindings` 绑定的 App Secret，
  不得放入普通配置、模型参数或源码。
- 宿主提供的 OAuth 回调地址：Actus 为 `/api/connector-oauth/callback`，完整协议、
  域名与路径必须与飞书安全设置中的重定向 URL 完全一致。应用不接受调用者覆盖回调。

在应用的用户身份权限中开通并发布以下权限；授权链接会请求相同 scope：

| scope | 用途 |
| --- | --- |
| `offline_access` | 获取并轮换刷新凭据 |
| `docx:document:readonly` | 新版文档元数据及纯文本读取 |
| `wiki:wiki:readonly` | 知识空间、节点列表及节点解析 |
| `bitable:app` | 多维表格结构、单条记录读取及新增更新 |

`get_record` 的当前官方声明仍列出整体多维表格权限，因此首版请求 `bitable:app`。
它的厂商权限范围大于本应用的 7 项表格操作；本应用没有删除、建表、改字段等工具。
不申请邮箱、手机、完整通讯录等身份敏感字段权限。

使用用户身份 `user_access_token`，没有 `tenant_access_token` 自动回退。
应用授权不能替代资源权限；用户仍需拥有目标文档、知识库或多维表格的相应访问权限，
多维表格高级权限还可能限制可见的行与列。

## 授权与连接

使用官方推荐的 OAuth v3，替代已标记为历史版本的 v2：

- 授权：`https://accounts.feishu.cn/open-apis/authen/v1/authorize`
- 交换和刷新：`https://accounts.feishu.cn/oauth/v3/token`
- 身份：`GET https://open.feishu.cn/open-apis/authen/v1/user_info`

通过公开 SDK `OAuthProtocol` 适配飞书业务错误和令牌响应，其余使用 SDK 标准流程。
机密客户端使用 `client_secret_post`、表单编码和 PKCE S256。SDK 管理 state、
事务归属、加密保存、重放、重启恢复及刷新串行化。
身份使用服务返回的 `tenant_key` 和应用内 `open_id`，不从 Token 推断账号。

实际授权范围以 Token 响应的 `scope` 为准，允许部分业务权限被裁剪；
缺少 `offline_access` 或有效刷新凭据时连接失败。
每次操作再次检查当前凭据范围，刷新收窄权限后不能沿用旧能力快照继续派发。
刷新必须返回新的有效刷新凭据，旧凭据不可自动重用；刷新结果未知时由 SDK
要求重新授权。凭据会记录厂商返回的刷新到期时间；业务上下文只获得访问凭据与 scope。

未声明远端撤销接口。断开清除本地连接，返回 `revocation.not_attempted`，
不表示已在飞书端全局撤销。管理员更换应用身份或 Secret 后应按 SDK 绑定规则处理连接。

## 12 项操作

所有输入拒绝额外字段，不接收任意 URL、HTTP 方法、Token 或工具名。
资源参数接收原样 token/ID；知识库链接中的 token 必须先用 `get_wiki_node` 解析，
不能直接当作文档 ID 或多维表格 app_token。

| 操作 | 效果 | 参数 |
| --- | --- | --- |
| `get_document` | 读 | `document_id` |
| `read_document` | 读 | `document_id` |
| `list_wiki_spaces` | 读 | 分页参数 |
| `list_wiki_nodes` | 读 | `space_id`、可选 `parent_node_token`、分页参数 |
| `get_wiki_node` | 读 | 知识库节点 `token` |
| `list_tables` | 读 | `app_token`、分页参数 |
| `list_fields` | 读 | `app_token`、`table_id`、分页参数 |
| `list_views` | 读 | `app_token`、`table_id`、分页参数 |
| `search_records` | 读 | `app_token`、`table_id`、可选 `view_id` / `filter` / `sort` / `field_names`、分页参数 |
| `get_record` | 读 | `app_token`、`table_id`、`record_id` |
| `create_record` | 写 | `app_token`、`table_id`、`fields` |
| `update_record` | 写 | `app_token`、`table_id`、`record_id`、`fields` |

分页参数为 `page_size`（默认 20、1–50）、可选 `page_token`；每次只读一页。
返回游标和 `has_more` 按厂商原值保留；知识库可能返回空页但仍有后续页。
查询只支持显式单层 AND/OR 条件，不接受 SQL、公式字符串或任意递归过滤。
为避免飞书忽略视图过滤而扩大查询范围，不允许 `view_id` 与显式 `filter` / `sort` 混用。

所有结果为 `{"data": {...}}`，保留记录内的 JSON 字段与分页状态。
`read_document` 额外标记 `format: "plain_text"`；不声称保留富文本、图片或附件内容。
知识库节点中的 `obj_type` / `obj_token` 保持独立，未支持的资源类型照实返回，不猜测调用。

## 表格写入约束

每次写入先分页读取完整字段定义（最多 20 页，每页 100），不跨连接或调用缓存。
按字段名校验后只派发一次单条新增或 PUT 部分更新：

- 文本：字符串，最多 100,000 字符。
- 数字：有限数字，绝对值小于 `2**53`；拒绝布尔值、数字字符串。
- 单选、多选：只接受当前字段定义中的已有选项；多选最多 100 项，不允许重复。
- 日期：非负整数毫秒时间戳，小于 `2**53`。
- 复选框：严格布尔值。
- 超链接：`{"link": "https://...", "text": "可选显示文本"}`，仅允许 HTTP/HTTPS。

`fields` 必须非空，最多 100 个字段；省略字段表示不修改，显式 `null` 表示请求清空。
公式、自动编号、人员、附件、关联记录和其他未支持字段拒绝写入，包括清空。
不代传文件，也不创建选项。字段检查是调用时快照，不是飞书事务：其他用户并发修改
字段或选项后，最终行为仍由飞书决定；无法保证跨请求的原子性和比较交换。

写操作声明 `effects="write"`，由宿主签发许可并执行其审批策略。
字段预检失败尚未发送记录写入，可明确拒绝；写请求发出后的超时、断连、业务错误或无效
回执可能已有副作用，保留 SDK 的 `uncertain`，不自动重试、回滚或删除远端记录。
确认新增成功后记录 `record_id`；未知新增结果需由用户在目标表中核实，不能假定不存在。

## 开发、构建与验收

Python 3.12+，使用独立环境、腾讯 PyPI 镜像及正式 SDK；不复用相邻工程的环境。
在本应用目录执行：

```sh
UV_CACHE_DIR=/tmp/feishu-uv-cache uv sync --extra test
.venv/bin/ruff check src tests
.venv/bin/pytest -q
.venv/bin/connector check --project pyproject.toml
```

构建使用全新源码副本和独立输出；默认校验已安装的公开 SDK，不使用同版本候选包覆盖：

```sh
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  /absolute/dev-env/bin/connector build --project /absolute/build-copy/pyproject.toml \
  --output-dir /absolute/new-delivery --no-overwrite
```

在全新 consumer 环境安装产物中的应用 wheel 和正式 `actus-connector-sdk[serve]==0.0.1b9`，
执行依赖检查。将 `tests/` 和 `pyproject.toml` 复制到独立目录（不复制 src），
在该目录用 consumer 运行 pytest，确认应用从 consumer 的 site-packages 导入。
此外用未经替换的 CLI 验证包校验、TLS 健康检查及退出：

```sh
<consumer>/bin/python -I -B <独立目录>/tests/acceptance.py \
  <交付目录>/feishu-0.1.0.connector <全新验收输出目录>
```

Runtime 的总截止时间与 HTTP 字节预算由宿主配置，应用解码单响应额外限制 1 MiB；
超限会失败，不截断成成功。文件大小、网络和限流可能使操作无法在预算内完成。
SDK b9 对外使用固定操作错误；权限不足、限流、资源不存在等细分类别以固定诊断码
写入宿主日志，不回显厂商消息、响应正文或凭据。
使用 `connector serve` 时必须显式提供 SDK `http_options`，包含连接池、各阶段超时、
请求和响应字节预算；该应用有 HTTP 服务，不能省略这组配置。完整隔离配置示例见
`tests/acceptance.py`，其中测试密钥与设置仅生成在指定的外部新目录中。

契约依据见 [CONTRACTS.md](CONTRACTS.md)，本轮验证与静态复核见 [VALIDATION.md](VALIDATION.md)。
真实飞书 OAuth、资源权限、表格类型和页面交互需要测试租户补验；模拟测试与独立安装
不代表已部署或通过真实厂商验收。
