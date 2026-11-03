# 飞书 0.1.1 验收与静态复核

更新：2026-11-03。受控 OAuth 诊断使用公开 SDK `0.0.1b9`，源码、独立构建、安装及模拟运行验收通过。
按授权分别提交本应用与 Runtime，不推送。飞书候选包未上传或切换到现有安装；
真实飞书授权失败的具体原因仍未确认，不能用模拟验收代替新的现场证据。

## 实现与复核边界

只通过公开 `OAuthProtocol.exchange/token_response/refresh` 和 `Auth.resolve_identity`
扩展点添加可选 stderr 事件，不使用 SDK 私有接口，不修改 SDK、Backend、Atlas 或 Web。
原请求方法、参数、PKCE、state、权限、刷新轮换、凭据模型及错误分类保持不变；
诊断不新增请求或自动重试，也不额外读取原本未消费的错误响应正文。

事件只记录固定阶段、结果、数字状态码和布尔检查，不包含授权码、state、Token、Secret、
身份值、厂商消息、原始响应或异常正文。厂商未返回业务码时省略，不把逻辑默认值冒充实际返回值。
交换与刷新各自使用 attempt_id；身份查询仅附带公开上下文提供的合法事务/请求 UUID。
SDK b9 的 OAuthContext 不提供事务 ID，不使用私有字段补齐，也不把标识写入凭据。

逐项复核原异常透传、取消时上下文复位、并发 attempt 隔离、身份与 scope 校验、
刷新串行化/轮换及未知结果规则。本次未发现飞书实现的新阻断问题，未追加业务行为变更。
通用诊断接收协议不参与授权判定，不向 SDK 添加厂商分支。

## 最终验证

证据根目录（本地忽略，不是运行依赖）：

`/Users/caixr/workspace/AI/llm/lingxi-mas-studio/.docs/validation/oauth-diagnostics-review-20261103-0a8101d3`

| 项目 | 结果 |
| --- | --- |
| 独立依赖环境 | Python 3.12、腾讯镜像、锁文件及公开 SDK b9，无相邻源码/宿主环境依赖 |
| Ruff | 全部应用源码与测试通过 |
| 源码回归 | **114 passed**（31.98 秒），feishu-all.log |
| 正式构建 | 独立副本 connector build --no-overwrite，通过构建器的独立安装与包校验，feishu-build.log |
| 全新 consumer | 仅安装最终 wheel、公开 SDK 与约束内测试依赖；uv pip check 通过 |
| 独立安装回归 | 只复制 tests 和 pyproject.toml，无 src；**114 passed**（33.22 秒），consumer-tests.log |
| 声明检查 | connector check 通过，12 项操作；导入来源为 consumer site-packages |
| 正式 CLI | 未替换的 connector serve，TLS 健康检查和正常退出通过，consumer-cli.log |
| 产物一致性 | 9 个模块逐字节核对仓库、wheel、consumer；包内没有测试或私有配置，app-artifact-verification.json |
| 公开契约 | 与 0.1.0 比较 auth、config_schema、operations、catalog_revision、sdk_requirement 均相同 |
| 新镜像启停 | 修正后的独立 Runtime 镜像安装本包，两轮启停及诊断窗口关闭通过，auth-matrix/results.json |
| 真实诊断管道 | consumer 实际应用事件经 fixture 真实 stderr 收集，过滤、UID 隔离、EOF 和生命周期验收通过，lifecycle-smoke/results.json |

候选包位于上述证据根目录的 feishu-delivery/feishu-0.1.1.connector，不覆盖原交付目录。

```text
SHA-256 126d759ad092452e26210d65ed056692de07ccb754110be3d37d2c3e5fe74bfe
```

原有 100 项业务/授权回归和新增 14 项诊断用例均保留，覆盖成功阶段、无效凭据布尔项、
厂商错误码/畸形响应、身份 403 不额外读正文、失败不重试、并发关联、日志写失败、
错误 state、取消及上下文复位、刷新和缺失业务码不冒充 0。
原有测试继续覆盖跨用户拒绝、回放、重启、刷新权限收窄、明确客户端拒绝与结果未知的区别、
轮换失败不重放，以及 12 项操作的权限、字段校验和写后未知结果。

本轮 Runtime 复核发现并修正初始化取消/截止的生命周期问题，先失败回归、再修正，
全量 **184 passed**；飞书本身无需改 SDK 或依赖配合。细节见 Runtime 的 VALIDATION.md。
证据与构建副本保存在本地忽略目录，可按 README 和 tests/acceptance.py 在新目录复现。

## 部署与实际环境待验收

2026-11-03 已另行完成本地 Runtime 上一轮诊断镜像切换，四个原安装及 Atlas 当前引用、
profile 已同步，连接、配置、密钥及历史保留；飞书原安装仍为 **0.1.0**，由用户手动升级。
本次复核没有再切换容器或写 Atlas 数据，新取消修正尚未部署。
新镜像 profile 与旧准备/恢复快照不自动兼容，不能仅改 Atlas profile 绕过核验。

应用与 Runtime 两端均支持协议后才能收集新事件；旧 Runtime 丢弃 stderr。
真实浏览器授权、飞书控制台回调/权限发布/可用范围、刷新、资源权限及平台 UI 仍需测试租户验收。
缺少日志不代表没有调用，succeeded 只表示应用步骤成功，最终连接结果仍以 SDK 事务为准。
原有字段预检与写入间没有厂商事务保障、总预算限制和写后未知结果规则继续适用。
