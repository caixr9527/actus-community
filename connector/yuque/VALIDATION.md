# 语雀 Connector 验证记录

日期：2026-11-02。Python 3.12.3，正式 `actus-connector-sdk==0.0.1b9`。
完成 7 读 2 写、本地回归、独立交付验收和静态复核。**真实语雀及平台 UI 尚未联调**。
本轮只实现语雀及更新 Connector 索引，飞书现有改动未处理；未推送、未部署。

## 最终结果

| 检查 | 结果 |
| --- | --- |
| 源码回归 | **178 passed**，27.56 秒 |
| 静态检查 | Ruff check、格式检查、connector check 通过；9 个操作、0 资源 |
| 独立构建 | 全新源码副本，原版正式 SDK build 完成隔离 wheel 构建、安装、依赖与声明校验 |
| consumer | 全新环境只安装交付 wheel、正式 SDK serve 和测试依赖，uv pip check 通过，37 个包兼容 |
| consumer 回归 | 仅复制 tests/pyproject.toml，无 src；**178 passed**，28.00 秒 |
| 来源与一致性 | SDK 与应用来自 consumer site-packages；6 个源码模块与 wheel/consumer 内容一致，README 与 manifest 匹配 |
| 原版 CLI | 包校验、connector serve TLS /v1/health 和正常退出通过 |
| 包内容 | package.json、manifest.json、唯一应用 wheel，无测试、外部 CLI/Skill、Token 或运行密钥 |

最终包：`dist/verified/yuque-0.1.0.connector`，Git 已忽略。

SHA-256：

```text
6882062e7c840a69c263d5eb68d0a383b634ffff0238d66a7cfbb20d62293ad2
```

## 构建依赖处理

首次在线隔离构建在 wheel_install 阶段失败；仓库外独立 pip 复现确认腾讯镜像索引
未返回 `aiosqlite>=0.21,<0.22` 的可安装版本，不能据此跳过隔离安装或降低检查。

随后按 uv.lock 的精确 wheel URL 下载 28 个正式运行依赖，逐个核对 SHA-256，另下载
pyproject 声明范围内的构建后端 setuptools 80.10.2。使用原版 SDK、正式 SDK wheel、
`PIP_NO_INDEX=1 PIP_FIND_LINKS=<wheelhouse>` 重新构建成功，隔离安装和声明校验均完成。
没有修改 SDK，没有用仓库外源码替代正式依赖，也没有把临时依赖目录作为运行依赖。

## 回归覆盖

测试使用 SDK 公共 Server/Client、签名平台许可和隔离加密存储，只在 HTTPX 公共
transport 边界模拟语雀，不修改 SDK 私有方法，不给应用添加测试开关或测试域名。

- Token 表单、无效 Token、真实用户 ID、非法身份、显式 Group 身份拒绝、无全局能力伪造。
- 授权重放、跨用户事务/调用拒绝、重启恢复、本地断开、两个账号的凭据隔离。
- 9 个固定操作、用户/团队知识库分支、正确请求方法/路径/头字段；未知操作不出网。
- int64 ID、布尔/浮点/路径拒绝、额外字段、显式 null、控制字符、非法日期/时区。
- 标题限制、UTF-8 正文字节上限、原始格式、草稿不替代正文、派生正文和人员字段过滤。
- 普通知识库/Markdown 文档预检、错误 ID/归属、类型未知、草稿冲突、已删除标记、旧时间戳。
- 创建显式私密、标题更新不发送正文、正文完整替换、原 public 和 slug 保留。
- 顶层及 data 内失败标记与合法对象并存、错误回执、错误可见性/类型/内容都不能报成功。
- 缺 total 保持未知、空页/短页不猜末页、重复 ID、畸形 total、归属错误、分页上限明确标记。
- 搜索页码/页大小、类型/target ID 校验、去 HTML 标记、不可信 URL 拒绝且不主动访问。
- JSON 类型、重复 key、NaN/Infinity/指数溢出、大小限制、JSON Content-Type、无重定向。
- HTTP 400/401/403/404/422/429/500、写前不派发、写后断连/错误/任务取消/截止时间。
- 写后未知状态不重试/补偿；公开错误、日志和存储没有明文测试 Token 或厂商错误正文。

tests/vendor.py 是由公开契约构造的兼容性夹具，**不是线上抓包**。
完整源码回归、consumer 回归和 TLS 启动均不调用真实语雀业务。

## 完成后的静态复核

逐文件复核 6 个应用模块、5 个测试/验收模块、pyproject、锁文件、构建白名单、文档与
最终包；修正后完成完整源码回归、独立构建、consumer 回归和原版 CLI/TLS 验收。

复核重点与结果：

1. SDK query 参数必须为字符串，内部已验证整数显式转换，JSON body 仍保留数值 public。
2. 失败标记可能与合法文档并存，统一检查顶层和 data 内错误、success=false/非法类型、code。
3. 更新 public 的默认值与创建继承规则不同；创建显式私密，更新显式保留预检值并校验回执。
4. Markdown 写入要求 Book/Doc 明确分类，拒绝草稿冲突、删除标记与不支持格式，不做格式转换。
5. 时间戳校验并逐字比较，不捏造服务端条件写入能力；明确并发窗口和草稿字段缺失的不确定性。
6. 分页信息不充分时保留 null；达到搜索/offset 上限明确标记，不返回不可提交的候选页。
7. 不把 body_draft 或格式转换副本当原始正文；回执接受、独立回读和发布状态严格区分。
8. 固定主站和数字路径、白名单输入/输出、无任意 Host、无附带目录写入、无自动重试。

本地实现复核范围内未保留阻断问题。真实 Token 权益与权限、上游响应差异和发布行为
仍须实际环境验证，不据模拟数据声称完整业务已经在线可用。

## 提交前再次复核

2026-11-02 再次复核全部应用模块、测试、授权与连接隔离、输入/输出、分页、Markdown
写前预检、可见性保留、失败回执、写后未知状态、依赖及打包范围，未发现新的阻断问题，
无需修改运行代码。

- 完整源码回归再次通过：**178 passed**，28.65 秒。
- Ruff check、Ruff format --check、connector check 再次通过。
- 独立 consumer 的 uv pip check 通过，37 个包兼容。
- 构建输入、6 个源码模块与 wheel/consumer 安装模块、README、manifest 和交付包摘要
  均一致；归档白名单与锁文件来源检查通过，无需重建未变的交付内容。
- 本次回归日志：`/tmp/actus-yuque-rereview-tests-20261102.log`。

本次提交范围限定为语雀应用与 Connector 索引，飞书改动保持在工作区。
真实语雀、发布行为和宿主 UI 的待验收范围未变。

## 待实际环境验收

- 用户通过宿主安全表单填写主站个人 Token，核对账号权益、身份与失效/重置行为。
- 使用只读与读写权限，验证授权成功不代表任意资源可写，确认 403/404/限流行为。
- 核实用户团队列表 data 的实际数组结构，官方规格此处引用单对象存在不一致。
- 核实各列表 total、搜索 target/URL、ID 类型、status 字符串/整数和完整分页语义。
- 专用测试知识库中验证私密创建、目录表现、标题/正文更新、草稿冲突和原可见性。
- 核实写入回执是否返回完整原文、服务端是否规范化正文、是否改变发布状态及客户端展示。
- 验证宿主上传、连接显示、写操作审批、工具调用、Web/桌面 UI。

## 仓库外复现材料

- 官方规格：`/tmp/actus-yuque-contracts-20261102/spec/yuque-openapi.yaml`
- 开发环境：`/tmp/actus-yuque-dev-20261102`
- 完整源码日志：`/tmp/actus-yuque-reviewed-tests-20261102.log`
- 构建副本：`/tmp/actus-yuque-build-source-20261102`
- 构建日志：`/tmp/actus-yuque-build-offline-20261102.log`
- 已验摘要的 wheelhouse：`/tmp/actus-yuque-wheelhouse-20261102`
- consumer：`/tmp/actus-yuque-consumer-20261102`
- 独立测试输入/日志：`/tmp/actus-yuque-consumer-tests-20261102`、`/tmp/actus-yuque-consumer-tests-20261102.log`
- CLI/TLS 验收：`/tmp/actus-yuque-cli-acceptance-20261102`

这些临时材料可被系统清理，不是运行依赖；复现步骤见 README。
