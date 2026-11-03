# 飞书 0.1.2 验收与静态复核

更新：2026-11-03。PKCE 令牌接口兼容修复已完成独立检查、构建、安装和隔离模拟运行。
本轮只修改 actus-community；本次交付包含代码与验收记录，
不包含推送、上传或现有安装、容器升级。
真实飞书授权与服务端 PKCE 正反对照尚待验收，不能用模拟结果认定线上问题已解决。

## 问题与实现边界

只读现场记录表明，0.1.1 在 2026-11-03 10:40:37 的令牌交换收到 HTTP 400 / 20049，
尚未进入身份查询。该记录只证明 PKCE 校验失败，没有直接比对该次敏感校验值。
官方授权入口文档说明 PKCE 可暂时搭配 v2，Token v2 文档另推荐迁移 v3；
本次按前者选择固定接口组合，文档差异与依据见 CONTRACTS.md。

应用将交换和刷新统一到 `https://open.feishu.cn/open-apis/authen/v2/oauth/token`，
通过公开 `OAuthProtocol.token_request`、`OAuthRequest(json=...)` 与 `authenticate`
发送 JSON 请求体。SDK 负责 UTF-8 编码、Content-Type、网络预算和资源生命周期；
不手动覆盖其保留头部，不使用私有接口，不新增客户端或依赖，也不更改其他工程。

保留 PKCE S256、state、事务归属、身份与 scope 校验、刷新轮换、凭据模型及错误分类。
旧的 exchange、refresh、token_response、can_refresh、business_credential、resolve_identity
均经 AST 比较保持原实现，其余 8 个模块逐字节未变。
没有跨端点回退、失败重试、授权码复用、tenant Token 回退或权限范围扩大。
诊断事件协议与取消后的上下文复位保持原样；公共文件传输链路没有改动。

## 最终验证

本轮证据、隔离环境和候选包位于外部新目录，不是运行依赖：

`/private/tmp/feishu-pkce-fix-20261103-d1bd52e7`

| 项目 | 结果 |
| --- | --- |
| 先失败回归 | 修复前通过 HTTP transport 模拟现场 20049，支持的接口组合用例失败，regression-before.log |
| 独立依赖环境 | Python 3.12、原锁文件与公开 SDK b9；依赖版本未改变 |
| Ruff / 声明检查 | 全部源码与测试通过；源码与 consumer 的 connector check 均通过，12 项操作 |
| 源码回归 | **119 passed**（32.94 秒），source-tests.log |
| 正式构建 | 独立副本、最终 README、独立输出及 --no-overwrite，通过构建器安装与包校验，final-build.log |
| 全新 consumer | 安装最终包内 wheel、公开 SDK 和约束内测试依赖；36 个安装包依赖检查通过 |
| 独立安装回归 | 只复制 tests 和 pyproject.toml，无 src；**119 passed**（34.00 秒），consumer-tests.log |
| 正式 CLI | 未替换的 connector serve，回环 TLS 健康检查和正常退出通过，consumer-cli.log |
| 产物一致性 | 源码、构建副本、wheel、consumer 的 9 个模块一致；无测试或私有配置，artifact-review.json |
| SDK 独立性 | consumer 的 SDK Python 源文件与已校验哈希的公开 b9 wheel 全部一致 |
| 公开契约 | 与原 0.1.1 包比较，manifest 仅 version 改变，配置、权限、操作与 catalog_revision 相同 |

保留原 114 项业务、授权与诊断测试，新增 5 项接口组合及 PKCE 拒绝测试。
缺失或错误 verifier、缺失或错误 challenge 由严格模拟厂商返回 20049；SDK 链路无连接落库、
无身份查询、无第二端点重试，重复完成不会再调用厂商。
刷新测试确认 JSON 请求、相同 v2 端点及精确参数集合，保留串行刷新、轮换和重启恢复。
原有跨用户隔离、错误 state、权限收窄、未知刷新不重放、取消、日志脱敏及 12 项操作均通过。

提交前复核逐项核对源码、测试、锁文件、consumer 依赖和最终产物，确认未变化，
上述两组 119 项回归与 TLS 启停结果仍适用。检查 JSON 请求的客户端认证、固定端点、
失败不重试、权限收窄、刷新轮换、截止与取消收尾，未发现新增代码问题。
本次复核仅同步交付状态，不追加业务行为变更；真实厂商待验收项继续保留。

最终候选包：`final-delivery/feishu-0.1.2.connector`，不覆盖原交付目录。

```text
SHA-256 3068b2500a4cbf62ce2d9988b713007cd6f6bc22336cca35937a75b4a4b9b535
```

## 真实环境待验收与交付状态

升级和上传由用户执行；本轮没有读取真实凭据、重放授权码、请求真实 Token 接口，
没有写入 Atlas 数据，也没有启停现有容器或宿主服务。
升级后重新发起授权，不沿用旧链接、授权码或 v3 刷新凭据。

v2 文档记载缺少 challenge 时可能接受 verifier。模拟厂商有意执行严格检查，
只能证明应用传递和失败处理正确，不能证明飞书服务端严格执行 PKCE。
在受控租户中用不同的新授权码分别验证：正确 S256 配对成功；保留 challenge 但使用错误
verifier 时被拒绝且没有连接保存；成功连接可刷新且使用轮换后的凭据。
若错误 verifier 被接受，应停止验收并核查厂商行为，不能关闭 PKCE 或用正向成功掩盖该结果。
真实资源权限、飞书控制台回调/权限发布/可用范围和平台 UI 仍需用户验收。
