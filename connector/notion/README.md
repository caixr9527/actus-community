# Notion

独立 Notion Hosted MCP OAuth 应用，应用 ID `notion`、包名 `actus-notion`、入口
`notion_connector.app:App`。只使用 `https://mcp.notion.com/mcp`，不调用 Notion REST API。
与平台旧 Notion provider 分开安装；切换及删除旧实现另行安排。

## 安装前准备

平台 OAuth 接入前置已经完成。Backend 的 `CONNECTOR_BACKEND_PUBLIC_BASE_URL` 使用显式配置的
HTTP/HTTPS 公开源站，回调复用 API 端口；Atlas 的 `CONNECTOR_OAUTH_REDIRECT_URI` 必须与该源站的
`/api/connector-oauth/callback` 完全一致。Runtime 使用平台传入并持久恢复的回调地址，
应用及回调请求不能覆盖它。

当前应用版本为 `0.1.4`，固定依赖正式 SDK `0.0.1b7`，通过通用 `DynamicOAuthClient`
接入动态注册。腾讯镜像的 SDK wheel、sdist 已核对与 PyPI 摘要一致；应用构建和独立安装
使用正式发行依赖，不再使用同版本候选 wheel 覆盖。依赖交付不代表已有实例已切换。
不覆盖旧 `0.1.3` 包、安装配置、注册文件或连接数据。

新版本的普通配置 `values={}`、秘密配置 `secrets={}`，拒绝额外字段，不再手填 `client_id`。
应用使用通用 SDK `DynamicOAuthClient` 声明固定的 `https://mcp.notion.com/register`，
以 public client、`none`、`default` 和 PKCE S256 授权。导入、检查、构建、启动、普通查询
不会发起注册；首次有效且获准的显式连接请求才注册。SDK 按安装加密持久化客户端及绑定，
并发连接、重启、后续授权和刷新复用同一客户端。注册结果未知时保留原记录并阻止重复注册，
取消会等待清理，不能通过删除本地数据或重开页面重试。管理员需核实原注册结果后另行处理。

旧 `0.1.3` 的管理员准备工具仍保留在源码中，旧安装继续使用已保存的 `values.client_id`。
它不随新版本打包，不参与新版本的自动注册。仅维护旧版本时可使用原命令：

```bash
python -m notion_connector.registration \
  --redirect-uri https://backend.example.com/api/connector-oauth/callback \
  --output /private/notion/registration.json
```

`--redirect-uri` 接受 HTTP/HTTPS，例如 `http://backend.example:23140/api/connector-oauth/callback`。
登记、平台配置和实际监听须使用同一精确地址；HTTPS 不要求另开 8446 端口。

旧准备工具的输出以 `0600` 排他创建，仅保存 client_id、回调及必要注册元数据。
文件放在源码、构建输入及 Runtime 包之外，备份后持久复用；`registration_unknown`
禁止删除重试。更换回调、迁移旧连接或切换新版本必须单独安排，不猜测关联已有客户端。

## 授权与身份

SDK 管理 state、PKCE、授权事务、Token 交换/加密存储、刷新轮换、重启恢复和撤销。
应用只通过 SDK HTTP 服务发送 MCP 请求，身份来自 `notion-get-self` 的 `workspace.id`
和 `user.id`，只接受 `user.type=person`；不把 bot 当作授权人，也不依赖 Token 响应中
SDK 不保留的厂商字段。空名称允许保留为空，实际账号与工作区标识不归一化。
浏览器返回时必须携带与声明完全一致的 `iss=https://mcp.notion.com`。

断开先由 SDK 清除本地连接；远端撤销使用当前元数据声明的 `/token`，结果单独返回。
HTTP 200 只代表远端接受请求，不承诺工作区或其他客户端已全局撤销。超时、断连的远端
结果可能未知，不自动重试。真实 Notion 撤销行为仍需实际账号补验。

## 操作范围

| 类型 | 操作 |
| --- | --- |
| 读取 | `search`、`fetch`、`get_users`、`get_teams`、`get_comments`、`query_database_view`、`get_async_task` |
| 写入 | `create_page`、`update_page`、`create_comment`、`move_pages`、`duplicate_page` |

所有操作仅接受显式 Pydantic 参数，拒绝额外字段。视图查询只使用已有 view_url；不接受
SQL、任意 MCP 工具名、文件或附件。复制或显式异步创建/更新前，须核对异步查询权限与参数契约；
创建/更新返回任务时，
后续使用原 task_id 查询，不将“已接受任务”表示为“写入已完成”。

Manifest 固定声明上述操作。每次调用重新读取远端工具清单，检查参数类型、必填字段和
约束，再按白名单映射；工具清单不等于权限。可用时读取 `notion-get-tool-access` 的明确
权限，未知权限保持未知并交由实际调用确认，不跨账号缓存。远端新增未支持的 schema
约束会在派发前拒绝，待明确兼容后再接入，不放宽校验。视图查询仅支持显式的顶层布局
或 `data` 包装布局，其余参数变化不猜测。

支持 JSON 和增量 SSE、会话头、通知和 RPC ID 匹配；SSE 事件必须完整结束。
普通工具结果保留结构化 JSON 或 Markdown，结果上限 256 KiB，HTTP 总上限由 SDK 控制。
不截断成假成功；工具错误、网络失败不伪装成空列表。读取和写入均不自动重试，写入
超时/断连或部分失败需按原对象/请求核实。会话清理失败记录固定错误码，不覆盖已确认的
业务结果，不记录凭据、第三方错误正文或业务内容。

## 隔离开发与交付

在新建环境从腾讯镜像安装 `actus-connector-sdk[build,serve]==0.0.1b7` 及应用测试依赖，
使用应用源码副本和独立输出，不覆盖现有环境，不回退其他源。应用目录中执行
`connector check`；构建可在尚未安装应用时直接执行：

```bash
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  connector build
```

新 `.connector` 先用于隔离平台上传、准备和启动验证，再经可信回调
授权。独立部署只需要产物、SDK 和安装配置，不导入 backend、atlas、Runtime 或其他应用
源码。注册文件、测试、临时 CA 和私有配置不进入发布包。

测试覆盖 SDK 动态注册、未知结果不重发、取消收尾、重启复用、身份、工具参数与权限、
增量协议、异常写入，并保留旧准备工具的回归：

```bash
python -m pytest tests
```

当前隔离联调使用私有网络、临时 CA 与模拟 Notion，仅验证应用和平台协议，不代表真实
Notion 已验收。真实环境需补验：一次性注册及复用、浏览器 consent/iss/PKCE、个人/工作区
身份、实际工具 schema/计划权限、分页/异步任务、刷新轮换、重启及本地断开/远端撤销。
写操作应使用专用测试工作区并核实实际效果及通知。

SDK 后续升级仍需核对正式版本、腾讯镜像可拉取性、wheel hash、依赖及
Runtime wheelhouse/profile，重新构建并验证全新安装、授权、工具审批和执行链路。
OAuth UI 优化、旧应用迁移、发布及生产验收不包含在本应用交付中。
