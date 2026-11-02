# 腾讯会议 Connector 验证记录

日期：2026-11-02。Python 3.12.3，正式 `actus-connector-sdk==0.0.1b9`。
本轮完成应用实现、本地协议/业务验证、独立交付和静态复核；**真实腾讯会议联调未完成**。

## 最终结果

| 检查 | 结果 |
| --- | --- |
| 源码回归 | **137 passed**，19.30 秒 |
| 静态检查 | Ruff check、格式检查、connector check 通过；7 个静态操作、0 资源 |
| 独立构建 | 全新源码副本，正式 SDK，隔离 wheel 构建、安装及声明验证通过 |
| consumer | 全新环境只安装交付 wheel、正式 SDK serve 和测试依赖；uv pip check 通过 |
| consumer 回归 | 只复制 tests/pyproject.toml，未复制 src；**137 passed**，19.31 秒 |
| 来源与一致性 | 应用和 SDK 均来自 consumer site-packages；6 个应用模块、README、manifest 与交付内容一致 |
| 原版 CLI | 包校验、connector serve TLS /v1/health 和正常退出通过 |
| 包内容 | package.json、manifest.json、唯一应用 wheel，无测试、外部 Skill 脚本或凭据 |

最终包：`dist/verified/tencent-meeting-0.1.0.connector`，Git 已忽略，未部署。

SHA-256：

```text
ceb683df5ed83c98cdd6a9f9ccfa32ad1c8aa1622712abe33e0805d70311fa59
```

## 请求契约证据与限制

公开官方文档确认工具范围、Token 及头字段；公开分发包确认固定端点、v1.0.15、无会话
JSON-RPC 代理和 ISO 8601/page_token 参数示例。具体来源和文件摘要见 CONTRACTS.md。
外部包只读检查，没有安装或执行其中脚本，没有调用反馈、升级或其他外部写操作。

完整 tools/list 需要凭据。无凭据 initialize 请求返回 HTTP 401，携带版本头的
tools/list 请求返回 HTTP 500 空响应，本轮未取得授权后的线上 Schema 或真实业务回执。
tests/vendor.py 的 Schema/响应是明确标注的兼容性夹具，**不是线上抓包**。
运行时通过 tools/list 校验本地参数，不能把此机制或模拟测试描述成真实接口验收完成。

## 回归覆盖

测试使用公开 SDK Server/Client、签名平台许可和隔离加密存储，只在 HTTPX 公共 transport
边界模拟厂商。不替换 SDK 私有方法，不向应用加入测试域名、环境变量或测试开关。

- Token 表单校验、无效 Token、已连接 Token 被拒绝、只读业务验证、空列表验证。
- 授权重放、重启恢复、本地断开、跨用户事务/连接拒绝、多个 Token 的连接与认证头隔离。
- 空身份保持空值，不伪造账号 ID 或全局权限；SDK 许可仍绑定平台用户及 connection_id。
- 7 项固定工具及参数位置；未知远端工具不扩展本地 manifest。
- tools/list 分页、缺工具、Schema 变化、额外必填字段、非法 Schema、重复目录、游标异常，
  禁止网络/内部 $ref，失败时不派发写入。
- 普通预约会议写入；快速、周期性、PMI、研讨会、类型缺失/畸形或 ID 不匹配均不派发。
- 明确时区、成对时间、非法日期/时区、会议 ID uint64、9 位会议号、额外字段、显式 null。
- 空业务页继续翻页，游标缺失/重复/结束页残留、重复会议或畸形条目不能报告完整列表。
- JSON-RPC ID/版本/结果互斥、重复 JSON key、大小限制、JSON-only Content-Type。
- 结构化或 text JSON、code/data 包装、内层 error、isError、success=false、回执 ID/类型不匹配。
- 主持人密钥、密码、人员信息和未知原始字段投影过滤；不可信入会链接拒绝且不发起请求。
- 400/401/403/404/429/500、重定向、发送后断连、任务取消、原始截止时间、写后未知状态。
- 日志、公开错误和加密存储不包含测试 Token 或厂商错误正文；没有自动写入重试或补偿。

## 完成后的静态复核

逐文件复核 6 个应用模块、5 个测试/验收模块、pyproject、锁文件、构建白名单、文档及
最终包。复核修正后运行完整源码回归、独立构建、consumer 回归和原版 CLI/TLS 验收。

发现并完成修正/确认：

1. **一次性不等于预约。** meeting_type=0 仍可能是快速会议，修改/取消额外要求 type=0；
   缺失时拒绝，不能从缺失字段推断为预约会议。写请求显式使用 meeting_type=0。
2. **失败回执可能夹带合法对象。** 明确拒绝 success=false/错误类型，不能因为同一对象
   还有合法会议 ID/主题而报告成功。相同规则覆盖内层业务错误、错误 ID 和错误会议类型。
3. **时间修改边界。** 起止时间在输入模型中成对验证，避免先派发读取后才发现不完整；
   时间转换用整数计算，不猜用户时区或服务端缺失值。
4. **协议差异。** 按所读代理采用直接 JSON-RPC，无未经核准的 MCP 会话初始化、SSE、
   SDK 修改或企业凭证回退；动态目录只用于校验，不授权新增工具。
5. **身份与输出。** 当前工具无权威账号资料，保留空身份；跨用户隔离由 SDK 实测。
   输出字段采用白名单，不因嵌套原始字段、更新提示或入会链接扩大数据/执行范围。
6. **副作用与预算。** 明确的预检失败/标准 RPC 派发拒绝可返回 failed；写后异常保持
   uncertain，不自动重试。客户端截止时间也可能返回 ClientError/result_unknown。

本地实现复核范围内没有保留的阻断问题。线上 Schema/响应兼容性仍是独立验收事项，
不能据此保证任意真实账号下的完整功能已经可用。

## 提交前再次复核

2026-11-02 再次逐项复核授权与连接归属、7 项操作及输入模型、JSON-RPC/Schema 校验、
分页、普通预约会议写前预检、输出投影、写入失败语义、依赖与构建范围，未发现新的
阻断问题，无需修改运行代码。

- 完整源码回归再次通过：**137 passed**，19.30 秒。
- Ruff check、Ruff format --check、connector check 再次通过。
- 核对交付包 SHA-256、6 个源码模块与 wheel/consumer 安装模块、README、manifest
  一致；压缩包只包含声明和应用 wheel，锁文件无仓库外源码引用。
- 独立 consumer 的 uv pip check 再次通过，38 个包兼容。

交付内容未变，无需重建；此前独立构建、consumer 回归和 CLI/TLS 记录继续对应当前代码。
本次回归日志：`/tmp/actus-tencent-meeting-rereview-tests-20261102.log`。
真实 Token、线上 Schema/回执及平台 UI 的待验收范围未变。

## 上线前实际环境验收

- 用户在宿主安全表单填写自己的 Token，确认账号范围、可见会议和失效/重置行为。
- 保存授权后的 7 个工具 Schema，并核实实际响应字段、嵌套格式、分页及版本提示。
- 在专用测试会议验证预约、修改、取消、客户端显示和通知；核对成功回执的实际格式。
- 证明不支持的会议类型被预检拒绝；若缺失 type 等字段，先补充证据再调整兼容性。
- 验证宿主上传、连接展示、写操作审批、调用及 Web/桌面 UI。

缺失或不支持的响应会失败，写后可能为 uncertain，不以猜测回执结构补齐成功。
仅在收到合法回执时返回 accepted，未进行写后效果回读；读取预检不是服务端事务。
Token 无自动续期/远端撤销，版本固定；生产宿主应控制调用频率和日志访问。

## 仓库外复现材料

- 开发环境：`/tmp/actus-tencent-meeting-dev-20261102`
- 发布者包与元数据：`/tmp/actus-tencent-meeting-skill-20261102.zip`、`/tmp/actus-tencent-meeting-skill-metadata-20261102.json`
- 参数/代理副本：`/tmp/actus-tencent-meeting-contracts-20261102`
- 最终源码日志：`/tmp/actus-tencent-meeting-reviewed-tests-20261102.log`
- 构建副本/日志：`/tmp/actus-tencent-meeting-build-source-20261102`、`/tmp/actus-tencent-meeting-build-20261102.log`
- consumer：`/tmp/actus-tencent-meeting-consumer-20261102`
- 独立测试输入/日志：`/tmp/actus-tencent-meeting-consumer-tests-20261102`、`/tmp/actus-tencent-meeting-consumer-tests-20261102.log`
- CLI 验收目录：`/tmp/actus-tencent-meeting-cli-acceptance-20261102`

这些是可被系统清理的验证材料，不是运行依赖。复现命令见 README。
