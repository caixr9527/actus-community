# 飞书契约依据

OAuth 核对日期：2026-11-03；业务 API 核对日期：2026-11-02。
运行时不读取本文件，不动态发现接口或 scope。
官方文档页面的正文通过飞书公开 `document_portal/v1/document/get_detail?fullPath=...`
读取核对；以下记录实现所依赖的路径、身份、字段和语义，不复制完整上游文档。

官方 Python SDK 另行只读核对，未作为应用依赖或随包分发：
`larksuite/oapi-sdk-python`，`v2_main`，提交 `0d9749a4728446a0ffa2e8374b37b5e1ce1cfd9c`。

## OAuth

- [获取授权码](https://open.feishu.cn/document/common-capabilities/sso/api/obtain-oauth-code)：
  `https://accounts.feishu.cn/open-apis/authen/v1/authorize`，空格分隔 scope，
  state、S256 code_challenge、redirect_uri；用户拒绝返回 access_denied。
  文档的 code_challenge 说明 PKCE 可暂时搭配 v2 Token，最新端点的支持仍待后续提供。
- [获取 Token v2](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/authentication-management/access-token/get-user-access-token)：
  `POST https://open.feishu.cn/open-apis/authen/v2/oauth/token`，请求头声明
  `application/json; charset=utf-8`，机密客户端在 JSON 体提供 client_id/client_secret；
  交换传 code、redirect_uri、code_verifier。使用公开 OAuthRequest 与 authenticate 适配编码。
  该文档虽推荐 v3，但授权入口的 PKCE 兼容说明仍指定 v2；0.1.1 现场收到 v3 的
  HTTP 400 / 20049，只能确认 PKCE 失败，尚未证明服务端内部原因。
  v2 文档同时指出缺少 challenge 却提交 verifier 时可能不拒绝请求。应用继续强制
  SDK S256 流程；真实厂商的正向与错误 verifier 对照仍需使用全新授权码分别验收，
  不能将 mock 的严格拒绝或 v2 正向成功当作厂商严格执行 PKCE 的证据。
- [刷新 Token v2](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/authentication-management/access-token/refresh-user-access-token)：
  同一 Token 端点，grant_type=refresh_token。刷新凭据只能使用一次。
  与交换一致使用 JSON 请求体，仅刷新 v2 接口下发的凭据，不混用 v3 刷新凭据。
  offline_access 控制 refresh_token 及其有效期返回；不硬编码两类 Token 的到期秒数。
- 成功字段：access_token、token_type=Bearer、expires_in、refresh_token、
  refresh_token_expires_in、scope。实际 scope 可能被裁剪，不能按请求 scope 推断授权。
- 错误分类：仅 HTTP 400 / code 20002 为明确客户端密钥错误；400 的已失效授权/凭据
  按重新授权处理。429/5xx、无效响应和断连不证明旧刷新凭据未使用，不能触发保留旧凭据的路径。
- [身份](https://open.feishu.cn/document/server-docs/authentication-management/login-state-management/get)：
  `GET /open-apis/authen/v1/user_info`，身份字段为 open_id、tenant_key、可选 name。
  不依赖需要额外敏感权限的 user_id、邮箱或手机。

## 操作映射

下表路径相对 `https://open.feishu.cn/open-apis/`，所有业务请求为用户 Bearer 凭据。
表中 `{app}` / `{table}` / `{record}` / `{document}` / `{space}` 为独立校验的路径片段。

| 操作 | 方法与路径 | 官方文档 |
| --- | --- | --- |
| get_document | GET docx/v1/documents/{document} | [元数据](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/get) |
| read_document | GET docx/v1/documents/{document}/raw_content | [纯文本](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/raw_content) |
| list_wiki_spaces | GET wiki/v2/spaces | [知识空间](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space/list) |
| list_wiki_nodes | GET wiki/v2/spaces/{space}/nodes | [子节点](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/list) |
| get_wiki_node | GET wiki/v2/spaces/get_node | [节点解析](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node) |
| list_tables | GET bitable/v1/apps/{app}/tables | [数据表](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/list) |
| list_fields | GET bitable/v1/apps/{app}/tables/{table}/fields | [字段](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/list) |
| list_views | GET bitable/v1/apps/{app}/tables/{table}/views | [视图](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-view/list) |
| search_records | POST bitable/v1/apps/{app}/tables/{table}/records/search | [搜索](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table-record/search) |
| get_record | GET bitable/v1/apps/{app}/tables/{table}/records/{record} | [单条读取](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/get) |
| create_record | POST bitable/v1/apps/{app}/tables/{table}/records | [新增](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create) |
| update_record | PUT bitable/v1/apps/{app}/tables/{table}/records/{record} | [部分更新](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update) |

节点解析查询为 token、obj_type=wiki，结果为 node.node_token / obj_type / obj_token。
列表接口使用 page_size / page_token，结果 data.items / has_more / page_token；
知识库可能出现空页但 has_more=true。原样保留厂商游标，不用列表长度推断末页。
应用对外统一限制每页最多 50；内部字段预检每页 100，符合字段接口上限。

搜索体为 view_id、field_names、sort（field_name / desc）及 filter
（conjunction / conditions，每条为 field_name / operator / value 字符串数组）。
首版只开放已建模的单层条件。飞书可能在显式过滤排序时忽略 view_id 的视图条件，
因此应用直接拒绝此组合。

写入体仅为 fields。更新只修改传入字段，官方明确允许 null 清空。
字段类型 1/2/3/4/5/7/15 分别为文本、数字、单选、多选、日期、复选框、链接；
飞书写入新的单选/多选值会自动创建选项，应用通过读取现有选项并校验来限制该行为。
这是检查时快照，不承诺飞书并发修改下的原子性。

HTTP 200 也可能包含非零业务 code，必须同时校验。没有为任何业务错误设置自动重试。
业务结果保留厂商 JSON，失败仅返回固定诊断，不回显厂商 msg、错误正文或授权材料。
