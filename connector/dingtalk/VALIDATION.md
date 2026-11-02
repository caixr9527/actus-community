# 钉钉个人待办 Connector 验证记录

日期：2026-11-02。SDK 为正式 `actus-connector-sdk==0.0.1b9`，Python 3.12.3。
验证过程中未修改 SDK、平台、现有 Connector 或运行安装，未调用真实用户的钉钉写接口。

## 最终结果

| 检查 | 结果 |
| --- | --- |
| 源码集成测试 | **122 passed**，19.19 秒 |
| 静态检查 | Ruff check、格式检查、SDK connector check 通过；5 项静态操作、0 资源 |
| 独立构建 | 最终源码副本、正式 SDK、隔离构建及安装声明核对通过 |
| consumer | 全新环境仅安装交付 wheel、正式 SDK serve 和测试依赖；uv pip check 通过 |
| consumer 回归 | 仅复制 tests 和 pyproject.toml，未复制 src；**122 passed**，19.20 秒 |
| 来源与一致性 | 应用/SDK 从 consumer site-packages 加载；全部 6 个应用模块与源码、wheel 逐字节一致 |
| 官方 CLI | 原版 connector serve 校验包、TLS /v1/health 和正常退出均通过 |
| 产物内容 | package.json、manifest.json、唯一应用 wheel；无测试、私钥或运行数据 |

最终包：`dist/reviewed/dingtalk-0.1.0.connector`，Git 已忽略，未部署。

SHA-256：

```text
9ee37af12ec3ac73b9ec6cd6f9373de7deda979c4fca8f231daac16d9793f62f
```

`dist/verified` 是较早的构建候选，不作为本轮最终交付。最终包位于 `dist/reviewed`。

## 覆盖范围

测试通过真实 SDK Server/Client、签名平台许可和隔离加密存储执行，仅在 HTTPX 公开
transport 边界模拟钉钉；不替换 SDK 私有方法，不增加应用测试开关。

- OAuth：scope/prompt、authCode 映射、冲突回调、state、拒绝、跨用户事务、授权重放。
- JSON camelCase Token 请求，Token/expireIn 类型校验、不制造 scope 快照。
- 稳定 unionId 身份，昵称可缺失；跨用户连接隔离、本地断开和重启恢复。
- 并发刷新串行化，刷新材料明确重复时可接受；缺失/畸形/丢失/错误刷新结果禁止旧材料重用。
- 5 项操作的 HTTP 方法、路径、认证头、JSON 与查询参数位置。
- 创建前身份核对、固定本人执行者；拒绝操作者、任意 URL、额外字段和路径穿越。
- 更新省略、空描述、显式 null、禁止隐含整体完成或替换执行者。
- 带时区的 RFC3339、非法日期/偏移、毫秒精度、远期时间边界、文本控制字符。
- success 的布尔/字符串区别，异常回执、重复 JSON key、响应大小与业务错误字段。
- 400/401/403/404/429/500、跨域重定向、发送后断连、取消和原始截止时间，不自动重发。
- 日志、公开错误和加密存储不包含测试 Secret、授权码、Token 或厂商错误正文。

## 完成后的静态复核

逐文件复核 6 个应用模块、5 个测试/验收模块、独立配置、锁文件、构建白名单、文档和
交付内容；复核修正后重跑源码测试、独立构建、consumer 回归和正式 CLI 验收。

已修正或明确核准：

1. **认证声明。** HeaderKey 使用 SDK 公开 auth 模块，声明在 OAuth 的 request_auth；
   HttpService 保持 connection 模式，业务请求不手写或泄露 Token。
2. **时间边界。** 去除浮点时间戳计算，改用 UTC timedelta 的整数毫秒；拒绝无时区、
   未知 -00:00、越界时区分钟、低于一毫秒精度及时间范围溢出。
3. **文本与身份。** 拒绝标题控制字符、非法描述控制字符和孤立代理字符；昵称校验避免
   不可编码值进入输出。创建身份读取须匹配连接稳定 ID，失败时不派发待办写入。
4. **回执类型。** 官方个人删除接口 success 为字符串，与两个 PUT 的布尔回执分别验证；
   false、缺失、错误类型不报告成功。对写后异常维持 uncertain，不重发。
5. **OAuth 差异。** 不照搬 GitHub 的 PKCE、Token 前缀、强制字符串轮换、refresh TTL 或
   空 scope 契约；只消费钉钉已声明字段，SDK 业务凭据投影不带 refreshToken。
6. **资源与权限。** 只有个人 me 路由；无企业 Token 回退、其他用户操作者参数、动态工具、
   任意 URL、消息或未验证的查询能力。请求 scope 不代表实际可用权限。

复核范围内没有保留的阻断问题。

## 实际环境待验收与限制

本地模拟验证不能替代钉钉后台配置和真实账户验收：

- 应用创建、个人权限点、可见范围、版本发布、出口 IP 策略和真实浏览器回调。
- 当前钉钉环境对三个 scopes 的授权、真实 Token 刷新/失效及所选接口的实际权限范围。
- 创建本人待办的客户端展示、空描述修改、截止时间、执行状态恢复、删除及通知行为。
- Actus 上传安装、宿主原样转交 authCode、工具许可、审批和平台 Web/桌面 UI。

首版没有任务列表或详情回读能力，应保留 task_id；写成功是接口合法回执，不是最终展示
或多人状态核验。更新/删除接受钉钉允许当前用户操作的任务，并非本地限定“本应用创建”。
远端授权撤销未实现；本地断开不等于钉钉授权撤销。限流不自动等待或重试。

SDK 客户端达到截止时间时也可能抛出 ClientError，outcome=result_unknown，调用者同样
不能重复提交来推断是否生效。必要清理可能越过业务截止时间，迟到结果不能报告成功。

## 仓库外复现材料

- 开发环境：`/tmp/actus-dingtalk-dev-20261102`
- 最终源码日志：`/tmp/actus-dingtalk-final-tests-20261102.log`
- 最终构建副本：`/tmp/actus-dingtalk-reviewed-source-20261102`
- 最终构建日志：`/tmp/actus-dingtalk-reviewed-build-20261102.log`
- consumer：`/tmp/actus-dingtalk-consumer-20261102`
- consumer 测试输入：`/tmp/actus-dingtalk-consumer-tests-20261102`
- consumer 日志：`/tmp/actus-dingtalk-consumer-tests-20261102.log`
- TLS CLI 验收目录：`/tmp/actus-dingtalk-cli-acceptance-20261102`

以上是可被系统清理的验证材料，不是运行依赖。完整开发、构建和验收命令见 README。

## 提交前再次复核

2026-11-02 再次逐文件复核 6 个应用模块、5 个测试/验收模块、配置、锁文件、构建白名单
及文档。重点检查 authCode/state、凭证投影与刷新失败、身份归属、me 路由与路径参数、
本人执行状态、字段省略/清空、时间与文本边界、回执类型、写后未知状态和日志内容。
未发现新的阻断问题，本轮未修改应用源码。

重新运行：**122 passed**（19.05 秒）；Ruff、格式检查和 connector check 均通过。
再次核对交付包 SHA-256、包内文件清单、manifest、README、全部应用 Python 文件和
consumer 安装内容，均与当前源码一致；新增文件的空白检查通过。
复核测试日志：`/tmp/actus-dingtalk-rereview-tests-20261102.log`。
真实账号与平台 UI 验收范围仍按上述记录保留，未自动部署或调用真实业务写接口。
