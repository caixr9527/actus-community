# Notion

独立 Notion Hosted MCP OAuth 应用，应用 ID `notion`、包名 `actus-notion`、入口
`notion_connector.app:App`。只使用 `https://mcp.notion.com/mcp`，不调用 Notion REST API。
与平台旧 Notion provider 分开安装；切换及删除旧实现另行安排。

## 安装前准备

平台 OAuth 接入前置已经完成。Backend 的 `CONNECTOR_BACKEND_PUBLIC_BASE_URL` 使用显式配置的
HTTP/HTTPS 公开源站，回调复用 API 端口；Atlas 的 `CONNECTOR_OAUTH_REDIRECT_URI` 必须与该源站的
`/api/connector-oauth/callback` 完全一致。Runtime 使用平台传入并持久恢复的回调地址，
应用及回调请求不能覆盖它。

应用版本 `0.1.3`，固定依赖正式 SDK `0.0.1b6`；腾讯镜像的 wheel、sdist 已与
PyPI 摘要核对一致。依赖升级不自动更新旧应用包、运行实例或既有连接。
HTTP/HTTPS 回调使用正式 SDK 0.0.1b6；依赖更新不自动切换已有安装、回调或运行环境。

在安装了正式 SDK 和本应用的独立环境内，由管理员显式执行一次：

```bash
python -m notion_connector.registration \
  --redirect-uri https://backend.example.com/api/connector-oauth/callback \
  --output /private/notion/registration.json
```

`--redirect-uri` 接受 HTTP/HTTPS，例如 `http://backend.example:23140/api/connector-oauth/callback`。
登记、平台配置和实际监听须使用同一精确地址；HTTPS 不要求另开 8446 端口。

准备工具检查固定源站的受保护资源和 OAuth 元数据，以 public client、`none`、`default`
和 PKCE S256 注册客户端。输出文件父目录须预先准备，文件以 `0600` 排他创建；仅保存
client_id、回调及必要注册元数据，不保存用户 Token 或注册管理 Token。使用输出的
`values.client_id` 作为安装配置。文件放在源码、构建输入及 Runtime 包之外，备份后持久复用。
启动、导入、授权开始及服务重启均不会注册客户端；相同文件、回调直接复用。
注册 POST 失败或结果未知时保留 `registration_unknown`，禁止直接删除文件重试；先由管理员
核实远端结果。更换回调或客户端需单独登记，不能覆盖现有记录。开发回调也需独立注册。

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

在新建环境从腾讯镜像安装 `actus-connector-sdk[build,serve]==0.0.1b6` 和
本应用测试依赖，使用应用源码副本和独立输出，不覆盖现有环境。应用目录中执行
`connector check`；构建可在尚未安装应用时直接执行：

```bash
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  connector build
```

将 `.connector` 产物交给平台上传、准备和启动，再经可信回调
授权。独立部署只需要产物、SDK 和安装配置，不导入 backend、atlas、Runtime 或其他应用
源码。注册文件、测试、临时 CA 和私有配置不进入发布包。

测试覆盖身份、工具参数与权限、增量协议、异常写入及注册复用：

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
