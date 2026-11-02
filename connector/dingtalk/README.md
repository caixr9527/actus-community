# 钉钉

独立钉钉个人待办 Connector，ID `dingtalk`，包名 `actus-dingtalk`，版本 `0.1.0`。
入口 `dingtalk_connector.app:App`，Python 3.12+，正式依赖 `actus-connector-sdk==0.0.1b9`。

## 配置与授权

部署者在钉钉开放平台创建应用，首版按企业内部应用配置并发布到测试用户可见范围。
开通个人权限中的通讯录个人信息读取权限 `Contact.User.Read`，以及
“以用户的个人身份创建或更新个人待办数据”权限 `Todo.PersonalTodo.Write`。
后台勾选、版本发布和用户实际授权均须完成，具体接口可用性仍由钉钉判断。
第三方企业应用的分发、审核和安装流程未在真实环境验证。

配置安全设置的重定向 URL 为宿主提供的完整 OAuth 回调地址：

- `values.client_id`：应用 ClientId/AppKey。
- `client_secret`：使用 SDK secrets 和 `runtime.secret_bindings`，不放入普通配置。
- `runtime.oauth_redirect_uri`：宿主的完整 HTTPS 回调地址。

用户浏览器访问 `https://login.dingtalk.com/oauth2/auth`，请求
`openid Contact.User.Read Todo.PersonalTodo.Write` 和 `prompt=consent`。
回调使用钉钉的 `authCode`；宿主需要原样转交 callback values，不能只保留 `code`。
应用将其映射为 SDK 标准授权码，拒绝冲突的 code/authCode，state 和事务归属由 SDK 校验。

Token 地址为 `https://api.dingtalk.com/v1.0/oauth2/userAccessToken`。
使用保密客户端、JSON camelCase 请求，显式适配 accessToken、refreshToken、expireIn。
按已核对的官方保密客户端流程关闭 PKCE，不宣称提供未经钉钉确认的 S256 保护。
不使用企业 accessToken、PAT、机器人 Webhook，也不以权限不足为由切换凭证。

SDK 管理授权重放、加密存储、刷新并发与重启恢复。Token 成功响应必须携带有效刷新材料；
不推算未返回的刷新有效期，不要求每次 refreshToken 字符串变化。刷新请求一旦结果未知，
不假设旧材料仍有效，连接要求重新授权。业务上下文只取得 accessToken，不取得 refreshToken。

通过当前用户接口的 unionId 识别用户；昵称只展示，不请求手机号/邮箱权限，业务输出也不包含
这些字段。首版不选择企业、不填写 tenant_id，不将请求 scope 当成已授予的权限快照。
断开只清除 SDK 本地连接，远端撤销未声明，不能据此认定钉钉端授权已撤销。

## 五个静态操作

| 操作 | 效果 | 参数与结果 |
| --- | --- | --- |
| get_current_user | 读 | 无参数；返回 union_id、display_name |
| create_personal_todo | 写 | subject，可选 description、due_at；返回 task_id、created_time_ms |
| update_personal_todo | 写 | task_id，至少一个 subject/description/due_at；返回成功回执 |
| set_my_executor_status | 写 | task_id、done 布尔值；返回本人 executor_done |
| delete_personal_todo | 写 | task_id；返回成功回执 |

创建时先读取并核对当前用户身份，executorIds 固定为本人；不接受其他执行者、参与者、
creatorId、operatorId、企业 ID 或任意 URL。标题最多 50 字符，描述最多 1000 字符，
这是本应用保守输入上限。任务 ID 仅接受 1–256 个字母、数字、下划线和连字符。

`due_at` 必须带明确时区，例如 `2026-11-03T18:00:00+08:00`，精度最多毫秒，
转换为 Unix 毫秒；不接受不带时区的本地时间。省略字段不发送，显式 null 拒绝。
描述 `""` 发送空字符串表达清空请求；不支持清除截止时间，不推断厂商未声明的清空哨兵。
更新不发送 done 或执行者列表，避免隐含改变整个任务状态或人员。

完成接口只更新**本人执行状态**，不能据此声称整个任务完成。删除调用官方个人身份
`.../remove` 接口，不能将其描述为 `.../hide` 的仅隐藏本人视图语义；可能影响其他参与者，
首版不提供多人创建能力。对传入任务的操作权限由钉钉验证，并不额外声称只能修改本应用
创建的任务；本应用未建立本地任务所有权登记表。

首版不包含待办列表、详情、企业工作待办、日历、通讯录搜索、消息或审批。
请保留创建返回的 task_id 供后续操作；需要找回既有任务时在钉钉客户端核实。

## 请求与失败语义

HTTP 服务固定 `https://api.dingtalk.com/`，通过 SDK 公共 ctx.http 请求，使用
`x-acs-dingtalk-access-token`，不跟随重定向，不重试读写，也不做后台刷新任务。
所有请求服从 SDK 的原始截止时间、连接预算和宿主字节预算；应用另限制 JSON 至 1 MiB。
429 直接失败，不睡眠后重发；宿主应控制调用频率。

成功要求 HTTP 200 和符合接口契约的回执。创建验证 taskId/createdTime，两个 PUT
要求 success 为布尔 true，DELETE 按官方 SDK 契约要求字符串 `"true"` 并规范化为布尔输出。
缺失、错误类型、重复 JSON key 和异常业务错误字段均不表示成功。
回执只证明钉钉接口接受操作，未回读验证客户端最终展示或其他参与者状态。

四个写操作声明 effects=write，由宿主管理写入许可。创建身份预检失败时未派发写入，
返回 failed；写请求发出后的异常状态、超时、断连、无效回执均保守返回 SDK uncertain。
不自动重试、补偿或删除。应先在钉钉确认是否生效，不能看到失败便重复提交。
日志仅记录固定诊断码，不回显厂商错误消息、任务正文、授权码或凭证。

## 开发与交付

在本目录使用独立环境：

```sh
uv sync --extra test
.venv/bin/ruff check src tests
.venv/bin/pytest -q
.venv/bin/connector check --project pyproject.toml
```

使用全新源码副本和输出目录构建；镜像须为可访问的正式 PyPI 镜像：

```sh
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  <dev>/bin/connector build --project <build-copy>/pyproject.toml \
  --output-dir <new-delivery> --no-overwrite
```

在全新 consumer 环境安装包中唯一应用 wheel、正式 SDK serve 和测试依赖，执行依赖检查。
仅复制 tests 和 pyproject.toml 到独立目录，不复制 src，运行回归并确认从 site-packages 导入。
通过原版官方 CLI 验证包及 TLS 服务：

```sh
<consumer>/bin/python -I -B <independent>/tests/acceptance.py \
  <delivery>/dingtalk-0.1.0.connector <new-acceptance-output>
```

宿主必须显式设置 http_options、runtime_options、server_options、平台公钥、凭据密钥、
数据目录及 TLS 监听，参考 tests/acceptance.py；测试私钥、密钥和运行数据只存仓库外。
接口依据见 CONTRACTS.md，完成后的验证和限制见 VALIDATION.md。
