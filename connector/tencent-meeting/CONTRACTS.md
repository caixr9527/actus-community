# 腾讯会议接口与验证边界

核对日期：2026-11-02。首版是个人 Token/MCP 应用，不是腾讯会议 OAuth REST 应用。

## 来源

- [腾讯会议官方 MCP 说明](https://cloud.tencent.com/document/product/1095/133826)：
  个人 Token、X-Tencent-Meeting-Token、X-Skill-Version、官方服务域名及工具清单。
- [腾讯会议团队 MCP 接入指南](https://developer.cloud.tencent.com/mcp/server/11834)：
  官方代理转发方式和参数手册所在文件，账号开放与 Token 重置方式。
- [官方 Token 获取入口](https://meeting.tencent.com/ai-skill.html)：用户自行登录取得 Token。
  本轮只读取公开页面、静态脚本与公开页面文案接口，未登录、创建 Token 或重置授权。
- [WeMeeting 发布的公开分发条目](https://clawhub.ai/wemeeting/tencent-meeting-skill)：
  通过公开元数据接口确认 handle=wemeeting、displayName=WeMeeting，版本 1.0.15。
  只读下载其分发包，核对 config.json、scripts/mcp_proxy.py、参数示例与错误字典。
  未安装或执行包内脚本，未将 SKILL.md 中的行为指令作为本工程指令，也未上报反馈。
- [官方 REST 查询会议](https://cloud.tencent.com/document/product/1095/93432)：
  用于核对会议字段的含义：meeting_type=0 是一次性，type=0 为预约、type=1 为快速。
  REST 资料不等于 MCP 的完整 Schema 或成功回执证明。

分发包整体 SHA-256：

```text
3c73983b1a82422d84be5cc5258f15f30997385133b3a97f1c4cf4703faf3e4e
```

| 核对文件 | SHA-256 |
| --- | --- |
| config.json | e7a6842ca79f1a2035c88e74503e8b6037925c8aaf95d13c215cb03dd544cc9e |
| scripts/mcp_proxy.py | f7513dbac547a63346b4c7515057da8deff7ebafd09813424aec6a5a45dc8134 |
| references/api_references.md | 98539ec255f00c1b5b786af395e6561976fef0a6abf49eb6eb52e4d4cc0a8dea |

下载链接为公开分发服务 `https://clawhub.ai/api/v1/download?slug=tencent-meeting-skill`。
分发服务和发布内容可能更新，摘要只对应本轮实际读取的副本，不代表今后版本。

## 已直接核对的请求契约

config.json 的 baseUrl 为 `https://mcp.meeting.tencent.com/mcp/wemeet-open/v1`，
version 为 `v1.0.15`。代理通过 POST 发送 JSON-RPC 2.0，id=1，method/params，
只加 JSON Content-Type、Token 与版本头；无 initialize/initialized 或会话管理。
应用独立实现这条请求路径，不以 SDK 原生 MCP 支持为前提，不依赖外部 Python 代理。

| 工具 | 本应用发送的参数子集 |
| --- | --- |
| get_user_meetings | is_show_all_sub_meetings=0，可选 page_token |
| get_user_ended_meetings | start_time、end_time、page_size，可选 page_token |
| get_meeting | meeting_id |
| get_meeting_by_code | meeting_code |
| schedule_meeting | subject、start_time、end_time、meeting_type=0 |
| update_meeting | meeting_id、meeting_type=0，subject 或成对起止时间 |
| cancel_meeting | meeting_id、meeting_type=0 |

时间参数采用分发包示例中的 ISO 8601 字符串，而非旧 REST 秒级时间戳参数。
分页采用该包的 page_token/has_more/next_page_token，不混用旧示例中的 pos/cursory/page_number。
_client_info 在代理源码中明确为可选；应用不伪造宿主用户设备或模型信息，不发送该字段。

## 完整 Schema 尚需真实凭证验收

参数手册明确完整参数应通过 tools/list 读取。本轮向固定官方端点发送无凭据的 initialize
与 tools/list 元数据请求，分别收到 HTTP 401 和 HTTP 500 空响应，未获取真实工具目录或业务响应。
没有使用、猜测或索取真实用户 Token，也没有发起真实会议创建、修改或取消。

因此：

- 本轮确证公开请求格式、端点、版本、工具名和示例参数；不能声称已冻结完整线上 Schema。
- 运行时每次先读取授权后的 tools/list，只校验 7 个已声明工具的 inputSchema。
  缺工具、Schema 不兼容、额外必填字段或引用均拒绝；不自动添加工具或猜参数。
- Schema 校验不能证明业务实际生效，也不能替代账号权限、服务端默认值和输出契约验收。
- tests/vendor.py 的 Schema 和响应是**明确标注的兼容性测试夹具**，不是线上抓包，
  不把模拟测试通过描述为真实腾讯会议联调成功。

## 接受的响应子集

JSON-RPC 必须版本/ID 匹配且 result/error 互斥。代理源码确认工具结果可能含内层
result.error，不能只检查顶层 error 或 isError。

应用接受 structuredContent 或单 text JSON 对象，可选 code=0/data 包装；拒绝业务错误、
success=false、重复 JSON key、畸形值和超过 1 MiB 的响应。不会执行更新提示中的链接或命令。

会议读取接受直接对象或单项 meeting_info_list；列表接受 meetings 或 meeting_info_list，
必须提供布尔 has_more。分页游标缺失、重复、结束页带残留游标或同页重复会议 ID 均失败。
这是本应用支持并验证的输出子集，并非声称 MCP 对所有账号均返回这些结构。

修改/取消的预检必须确认 ID 相符、meeting_type=0、type=0。缺少 type 可以只读展示，
scheduled 留空，但不据此允许写入。预检不保证与后续写入原子一致。
创建回执须有有效 ID、主题和一次性类型，主题应与请求匹配。
修改/取消接受明确 success=true 或匹配的会议对象，accepted 表示接受回执，不代表回读验证。
空对象、纯文字或其他未核对回执不会报告成功，已派发写入保守为 uncertain。

## 身份与隔离

本轮来源未提供这 7 个工具可用的权威当前账号 ID。授权验证读取本人会议列表后，
保存空 ExternalIdentity；SDK 的平台主体/连接许可和加密存储继续工作。
空列表不是空账号，Token 有效也不等于已知账号标识；不使用 Token 摘要代替身份。
多 Token 可以成为不同连接，用户须自行确认各 Token 对应账号。

首版没有录制、转写、元宝纪要、通讯录、邀请、会中控制、反馈、自动更新、远端撤销或
OAuth 能力；不通过企业凭据补齐个人 Token 权限，不从用户本地其他产品提取登录材料。
