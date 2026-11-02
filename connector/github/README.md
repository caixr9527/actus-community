# GitHub

独立 GitHub App 用户 OAuth 应用，ID `github`，包名 `actus-github`，版本 `0.1.0`。
入口 `github_connector.app:App`，固定依赖正式 `actus-connector-sdk==0.0.1b9`。
提供 13 项安装、仓库、Issue 与 PR 操作；独立构建为 `.connector`，不导入平台或相邻应用源码。

## 安装与用户授权

在 GitHub.com 创建 **GitHub App**，配置 Callback URL 为宿主提供的完整
`/api/connector-oauth/callback` 地址。Client ID 与 App ID 不同，安装配置使用 Client ID：

- `values.client_id`：普通配置。
- `client_secret`：通过 SDK secrets 和 `runtime.secret_bindings` 绑定，不能放在普通配置中。

首版仅支持 GitHub.com。配置仓库权限 Metadata: Read、Issues: Read and write、
Pull requests: Read；管理员安装应用并选择仓库，然后由用户完成 OAuth 授权。
首版不使用 App 私钥、installation token、PAT 或 GHES 自定义地址。
不需要应用侧 Webhook 接收服务；如启用了 GitHub App Webhook，需由管理员另行提供
可用的接收端，不能把 SDK 的 OAuth 回调当成 Webhook 接收地址。

授权地址 `https://github.com/login/oauth/authorize`，Token 地址
`https://github.com/login/oauth/access_token`。使用 PKCE S256、client_secret_post、
表单请求和 JSON Token 响应。请求 `offline_access` 取得可刷新的过期用户令牌，
必须返回有效的 expires_in、refresh_token、refresh_token_expires_in。
不接受传统 OAuth App、PAT、无期限用户令牌或缺少刷新材料的响应。

SDK 负责 state、事务归属、加密保存、授权重放、并发刷新和重启恢复。
刷新凭据一次使用，结果未知或缺失新凭据时禁止重用旧凭据；业务上下文只得到访问凭据。
通过 `GET /user` 的稳定数字 id 识别用户，login 只用于展示，不把组织安装作为用户租户。

GitHub App 的 Token scope 应为空；不能照搬传统 OAuth App 的 repo scope，
也不能用空 scope 判断用户没有权限。应用不生成全局能力许可，权限未知保持未知。
实际访问由应用权限、安装范围、用户权限及组织策略决定；公开资源的可读范围按 GitHub
规则处理，不把一次仓库访问成功当作其他资源的权限证明。
组织使用 SAML SSO 时，可能需要用户先建立有效 SAML 会话再重新授权。

断开是 SDK 本地断开，远端撤销未声明，结果为 `revocation.not_attempted`；
不表示 GitHub 端授权或应用安装已移除。

## 静态操作

| 操作 | 效果 | 参数 |
| --- | --- | --- |
| list_installations | 读 | 分页参数 |
| list_repositories | 读 | installation_id、分页参数 |
| get_repository | 读 | owner、repo |
| list_issues | 读 | owner、repo、state、labels、sort、direction、since、分页参数 |
| get_issue | 读 | owner、repo、issue_number |
| create_issue | 写 | owner、repo、title、body、可选 labels |
| update_issue | 写 | owner、repo、issue_number，至少一个 title/body/labels/state/state_reason |
| list_issue_comments | 读 | owner、repo、issue_number、分页参数 |
| create_issue_comment | 写 | owner、repo、issue_number、body |
| list_labels | 读 | owner、repo、分页参数 |
| list_pull_requests | 读 | owner、repo、state、sort、direction、base、head、分页参数 |
| get_pull_request | 读 | owner、repo、pull_number |
| list_pull_request_files | 读 | owner、repo、pull_number、分页参数 |

参数使用显式 Pydantic 模型，拒绝额外字段和任意 URL/HTTP 方法。正文和评论最多
65,536 字符，标题最多 256；分页默认 page=1、per_page=30，单页最多 100。
列表结果为 `data.items`，含 page/per_page/has_more/next_page；安装发现的 total_count
在厂商提供时保留，不推算缺失值。单对象结果为 `data` 下的厂商 JSON。

Issues API 列表含 PR，应用过滤后仍保留原始分页进度，空页也可能有后续页。
get_issue、update_issue 和 Issue 评论操作会拒绝带 pull_request 标记的对象；
本应用中的 Issue 评论不用于 PR 讨论或行内 Review。

三个写操作声明 effects=write，由宿主签发许可并执行审批。
省略字段不修改；正文 `""` 清空，labels 数组表示**完整替换**，`[]` 清空标签；
写入参数的显式 null 拒绝。state_reason 只支持 completed/not_planned/reopened，
并必须携带匹配的 closed/open 状态。标签只使用当前仓库已有名称，写前最多读取
20 页标签清单；未找到则拒绝，不创建标签。对带逗号标签的列表筛选不支持，避免查询歧义。

写前读取只是检查快照，不是事务。GitHub 可能因权限忽略标签更新，因此应用会核对
写入回执；部分字段未生效也不伪装成成功。写入发出后的断连、超时、错误状态或异常回执
返回 SDK 的 uncertain，不自动重试、回滚或删除已创建的 Issue/评论。
用户需要按目标仓库和原请求核实副作用，不能直接重复提交。

## PR 覆盖范围

PR 只读，不创建、编辑、合并 PR，不提交代码、不发 Review、不操作 CI。
文件读取前后核对 head/base SHA 和 changed_files，检测到变化则失败。
这只检测同次调用期间的变化，不能保证服务端原子快照，也不能将不同 SHA 的分页结果拼接。

GitHub 文件接口最多返回 3,000 个文件，patch 可能缺失。结果 coverage 中保留
head_sha/base_sha/changed_files、api_file_limit、exceeds_api_limit、missing_patch_count，
file_list_complete 只在第一页已覆盖全部文件时为 true。patches_are_partial 始终为 true，
不把这些片段表示为完整 diff。缺失 patch 不补造为空字符串。

## 网络、限流与预算

业务服务固定 `https://api.github.com/`，API 版本固定 `2026-03-10`。
普通请求走 SDK ctx.http；以 Link 头判断分页，不按列表长度猜末页，不自动读取下一页。

SDK b9 在暴露响应头前拒绝 3xx。仅对此情形，应用使用公开凭据与 ctx.resources
重新发起原始 GET，再用自己的 HTTPX 路径最多跟随 3 次同源、同资源路径类型的跳转。
这个只读重定向适配不修改 SDK 私有接口，不重试其他失败，不跟随写请求重定向。
限制目标为 api.github.com 的 HTTPS 地址，禁止用户信息、端口变体、片段和路径穿越。

两条 HTTP 路径都限制单响应最多 1 MiB，超限失败而非截断；原始调用截止时间贯穿
排队、请求、分页预检和清理。SDK 路径另外服从宿主配置的更小 HTTP 字节预算；
重定向路径自行计量 1 MiB，不读取 SDK 私有预算状态。低字节预算宿主应结合此差异验收。

同进程业务调用串行执行，同一连接的写请求至少间隔一秒。收到主/次级限流后根据
Retry-After、X-RateLimit-Reset 或默认等待值建立连接冷却；冷却期间拒绝新业务请求，
不在后台重试。冷却状态仅存在于当前安装进程，重启不会持久恢复；多进程、多安装及用户
在其他客户端产生的流量仍须宿主协调。权限错误与限流使用固定诊断码记录，不回显厂商正文。

## 独立开发与交付

使用 Python 3.12+、腾讯 PyPI 镜像和本应用的独立环境；默认 dev 组包含 SDK 构建及服务工具。
从本目录执行：

```sh
uv sync --extra test
.venv/bin/ruff check src tests
.venv/bin/pytest -q
.venv/bin/connector check --project pyproject.toml
```

构建在全新源码副本和输出目录执行，保留现有产物，不使用候选 SDK 替代正式发行依赖：

```sh
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  <dev>/bin/connector build --project <build-copy>/pyproject.toml \
  --output-dir <new-delivery> --no-overwrite
```

全新 consumer 环境安装包中的唯一应用 wheel 和正式 SDK serve，检查依赖。
将 pyproject.toml 和 tests 复制到独立目录，不复制 src；使用 consumer 运行测试，
确认应用从 consumer 的 site-packages 加载。用未经替换的 CLI 验证包校验与 TLS 启动：

```sh
<consumer>/bin/python -I -B <independent>/tests/acceptance.py \
  <delivery>/github-0.1.0.connector <new-acceptance-output>
```

宿主必须显式配置 SDK http_options、runtime_options、server_options、
平台公钥、凭据密钥、数据目录和 TLS 监听；示例见 tests/acceptance.py。
测试、密钥和运行数据不进入应用 wheel 或 .connector。

官方依据见 [CONTRACTS.md](CONTRACTS.md)，验证和静态复核见 [VALIDATION.md](VALIDATION.md)。
真实 GitHub 授权、组织策略、应用安装及平台 UI 需要测试账号验收；独立模拟测试不等于已部署。
