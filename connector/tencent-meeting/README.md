# 腾讯会议

独立个人 Token/MCP 应用，ID `tencent-meeting`，包名 `actus-tencent-meeting`，版本 `0.1.0`。
Python 3.12+，正式 SDK `actus-connector-sdk==0.0.1b9`，入口 `tencent_meeting_connector.app:App`。
首版提供 7 个静态操作，写操作只允许一次性普通会议。

## 连接

在 [腾讯会议官方入口](https://meeting.tencent.com/ai-skill.html) 登录并取得个人 Token，
在宿主连接表单中填写。只通过 SDK 的授权表单提交，不把 Token 放入聊天、源码或普通配置。
不需要企业 AppKey/Secret、OAuth 回调或安装级凭证，不读取用户本地 CLI/Skill 登录文件。
账号是否在官方开放范围内、Token 的有效性及会议权限由腾讯会议决定。

SDK 负责表单、连接归属、加密存储、授权重放、重启恢复和本地断开。
验证时读取 tools/list 后调用 get_user_meetings，合法的空业务列表也可以验证成功。
版本信息或工具目录成功本身不能证明业务凭证有效。

这 7 个工具没有经核对的当前账号资料接口，因此 account_id/tenant_id 留空，capabilities
保持未知；不以 Token 摘要、会议创建人或用户输入伪造身份。连接按平台主体和 connection_id
隔离，不能靠空身份判断两个连接属于同一腾讯会议账号。Token 重置后由用户重新连接；
本地断开不表示腾讯会议端 Token 已被撤销，不实现自动续期。

## 工具

| 操作 | 效果 | 参数 |
| --- | --- | --- |
| list_meetings | 读 | 可选 page_token；即将开始/进行中 |
| list_ended_meetings | 读 | start_time、end_time、可选 page_size/page_token |
| get_meeting | 读 | meeting_id |
| get_meeting_by_code | 读 | 9 位 meeting_code |
| create_meeting | 写 | subject、start_time、end_time |
| update_meeting | 写 | meeting_id，subject 或同时提供 start_time/end_time |
| cancel_meeting | 写 | meeting_id |

meeting_id 为 uint64 范围内的正整数字符串，区别于 9 位会议号。
时间使用含秒和明确时区的 RFC3339，例如 `2026-11-03T18:00:00+08:00`；不猜相对日期，
不接受无时区、-00:00、非法日期或亚秒时间。结束必须晚于开始；历史查询单次窗口最多
31 天，每页最多 20 条。标题最多 128 字符，这些是本应用保守输入限制。
省略字段不修改，显式 null、额外字段、操作者 ID、受邀人及任意 URL 均拒绝。

三个写操作均声明 effects=write，许可与审批由宿主处理。修改/取消前读取会议并核对
ID、meeting_type=0 和 type=0（预约会议）；快速/周期性/个人会议号/研讨会等类型不开放写入。
预检返回缺少预约/快速分类时也拒绝写入，不猜测缺失值。
所有写请求显式指定 meeting_type=0，修改时间要求成对输入，不替用户推算另一端时间。
写前读取不是事务，不能消除其他客户端并发修改带来的变化。

会议输出只包含 ID、主题、类型、scheduled 预约标记、会议号、起止时间、状态和入会链接，不透传主持人密钥、
密码、通讯录、厂商提示或其他原始字段。入会链接只允许官方 HTTPS 域名，应用不会请求它。
列表保留 has_more/next_page_token，每次只读取一页；不猜末页、不自动聚合所有会议。
读返回可展示其他会议类型，但重复 ID 或不可信分页结构会失败。

写成功输出是合法接口回执，不能据此声称客户端展示已回读核实。缺失或不支持的回执
保守为 uncertain；修改、取消返回 accepted，只表示接口回执被接受，不是额外的效果校验。
写请求发出后的超时、断连、错误回执不重试、不自动回滚。SDK 客户端超时也可能抛出
outcome=result_unknown 的 ClientError，调用者应先核实实际会议状态，避免重复预约。

首版不开放录制、纪要、参会报告、邀请成员、会议中控制、反馈上报、动态工具或周期会议写入。

## 协议与兼容性

固定服务 `https://mcp.meeting.tencent.com/mcp/wemeet-open/v1`，通过 SDK 公共 ctx.http 请求，
Token 由 HeaderKey 注入 X-Tencent-Meeting-Token；X-Skill-Version 固定为分发包的 v1.0.15。
按所核对代理直接使用无会话的 JSON-RPC POST；不添加未经确认的 initialize/SSE 会话流程。
只接受 application/json，不跟随重定向，不执行服务端返回的命令、升级链接或任意工具。
请求服从 SDK 截止时间和 HTTP 预算，应用另限制每响应 1 MiB，429 失败而不重发。

官方公开手册的部分完整 Schema 需要凭证读取。因此在每次操作前分页读取 tools/list，
检查允许工具的 inputSchema，实际派发前验证参数；缺工具、必填字段变化或不支持的
Schema 会在写入前拒绝。目录最多 10 页，Schema 不允许外部/内部引用，不解析网络 $ref。
远端目录只用于兼容性校验，不会扩展本地 manifest 或审批范围。

结果兼容的严格子集：MCP structuredContent 或单个 text JSON 对象，可选 code=0/data
包装；会议对象或单个 meeting_info_list，列表为 meetings/meeting_info_list 与
has_more/next_page_token。写回执须为匹配会议对象或明确 success=true；不把任意文字、
空对象或字段缺失当成功。真实 MCP 未提供的格式不补造，详见 CONTRACTS.md 的验收边界。

## 开发与交付

使用本目录的独立环境：

```sh
uv sync --extra test
.venv/bin/ruff check src tests
.venv/bin/pytest -q
.venv/bin/connector check --project pyproject.toml
```

在全新源码副本与输出目录独立构建，保留现有产物：

```sh
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  <dev>/bin/connector build --project <build-copy>/pyproject.toml \
  --output-dir <new-delivery> --no-overwrite
```

全新 consumer 仅安装交付 wheel、正式 SDK serve 和测试依赖；复制 tests 与 pyproject.toml，
不复制 src，执行回归并确认从 consumer site-packages 导入。
使用原版 connector serve 验证包及 TLS：

```sh
<consumer>/bin/python -I -B <independent>/tests/acceptance.py \
  <delivery>/tencent-meeting-0.1.0.connector <new-acceptance-output>
```

宿主需要显式配置 HttpOptions、平台公钥、凭据密钥、安装 ID、数据目录与 TLS。
测试临时材料放在仓库外，不打包真实凭据、外部 Skill 脚本或运行数据。
真实账号可用性、完整 Schema/响应结构和平台 UI 仍须实际验收，详见 VALIDATION.md。
