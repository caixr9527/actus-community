# 语雀

独立个人 Token 应用，ID `yuque`，包名 `actus-yuque`，版本 `0.1.0`。
Python 3.12+，正式 SDK `actus-connector-sdk==0.0.1b9`，入口 `yuque_connector.app:App`。

## 连接

在 [语雀 Token 设置](https://www.yuque.com/settings/tokens) 创建个人 Token，
通过宿主安全授权表单提交；账号须具备创建令牌的权益。只支持公网主站
`https://www.yuque.com/api/v2/`，不支持空间绑定的团队 Token、独立域名和私有化部署。
不需要安装官方 CLI，也不读取其他产品的本地登录文件、Cookie 或环境变量。

验证实际调用 `GET /user`，用返回的真实用户 ID 建立连接；登录名/名称仅用于展示，
不伪造租户或 Token 权限。读取身份成功不代表可以读写任意知识库。
SDK 负责表单、连接归属、加密存储、授权重放、重启恢复和本地断开。
Token 失效/重置后重新连接；无自动续期，本地断开不撤销语雀端 Token。

## 操作

| 操作 | 类型 | 参数 |
| --- | --- | --- |
| get_current_user | 读 | 无 |
| list_groups | 读 | offset；当前用户的团队，固定每页 100 条 |
| list_repositories | 读 | owner_kind=user/group；group 时必填 group_id；offset/limit |
| get_repository | 读 | repository_id |
| list_documents | 读 | repository_id、offset/limit |
| get_document | 读 | repository_id、document_id |
| search | 读 | query、type=doc/repo、可选 scope、page |
| create_document | 写 | repository_id、title、body |
| update_document | 写 | repository_id、document_id、expected_updated_at；title/body 至少一项 |

ID 是 int64 范围内的正整数字符串，不接受 URL、路径、浮点数或布尔值。
list_repositories 默认读取当前用户，group_id 只用于团队列表，最终权限由语雀决定。
搜索 scope 是用户/团队路径或 `owner/book`；知识库搜索只接受 owner 路径。
搜索每页固定 20 条，页码 1–100；其他列表用 offset，文档/知识库 limit 默认 20、最多 100。
应用将 offset 限制为 0–1000000；不会自动聚合全部数据。

列表返回 items、请求分页参数、total、has_more 和候选下一页位置。
只有 meta.total 明确时才计算 has_more；缺失时为 null，即使页较短/为空也不伪造末页。
未知状态下 next_offset/next_page 只是按本页结果生成的继续查询候选；无结果时留空。
搜索到达第 100 页仍有结果或状态未知时，page_limit_reached=true，不能视为已读完整结果。
offset 候选超过应用上限时同样返回 offset_limit_reached=true，并停止生成不可用的候选值。

## 正文与写入

get_document 只读取 type=Doc 的原始 body，保留 markdown/lake/html 格式标识和服务端
status；不把原始正文称作 Markdown 转换，不用 body_draft 替代正文。
不返回草稿、HTML/Lake 派生副本、人员详情、未知字段或附件；不渲染或抓取正文链接。
正文最多 256 KiB UTF-8，标题输入最多 256 字符，这是本应用的保守限制。
超限或缺失正文直接失败，不静默截断。空正文可读，首版写入要求非空字符串。
显式 null、额外字段、控制字符和非法 Unicode 拒绝；正文允许换行与制表符。

create_document 先核对知识库为 Book，显式发送 format=markdown、public=0 创建私密文档。
只写一次，不自动添加目录节点。可通过文档列表/返回 ID 再访问。
update_document 预检知识库、文档 ID/归属、type=Doc、format=markdown、可见性及更新时间，
检测到不同于正文的非空草稿时拒绝；不转换 Lake/HTML/表格，不修改路径或公开范围。
返回已删除标记的文档也不允许写入。
预检成功后显式携带原 public，防止接口默认值改变可见性；省略 title/body 就不发送该字段。
body 是**整体替换**，不是追加。expected_updated_at 必须与读取结果完全一致，支持带明确
时区的 ISO 8601 秒或最多 6 位小数。未返回更新时间/可见性时不能更新。

更新时间预检不是服务端原子条件写入；其他客户端仍可能在预检后修改正文、草稿或可见性。
无法消除此窗口，使用者应避免同时编辑。缺失草稿字段不证明没有草稿，实际行为仍需联调。

两个写操作声明 effects=write，审批由宿主处理。成功必须通过响应 ID、归属、格式、
标题、正文和可见性等校验；accepted=true 仅表示接口回执接受，不表示客户端发布完成。
content_verified=false 表示未进行独立写后回读。没有单独的发布操作，不自动重试、回滚或补偿；
文档状态和写入是否触发发布行为仍须真实账号验收，不能据接口成功宣称已发布或保持草稿。
写请求发出后超时、断连或回执异常保持 uncertain；客户端截止时间也可能产生
outcome=result_unknown 的 ClientError，应核实语雀状态后再决定是否再次操作。

首版不开放删除、知识库写入、权限管理、目录调整、附件、表格、画板、评论和小记。

## HTTP 与数据范围

只经 SDK 公共 ctx.http 访问固定服务，Token 由 HeaderKey 注入 X-Auth-Token，
设置 Actus-Yuque/0.1.0 标识。只接受 HTTP 200 JSON 和明确 data 包装；拒绝错误包装、
重复 JSON key、非有限数、畸形结果和超过 2 MiB 的响应，不跟随重定向、不自动重试。
请求同时服从宿主 HttpOptions 的大小、超时和连接预算。
认证、权限、资源不存在和限流返回固定错误，不泄露厂商正文或 Token。
搜索摘要去除 HTML 标记，输出链接只允许主站 HTTPS 地址且不会请求它。

## 开发与交付

```sh
uv sync --extra test
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/pytest -q
.venv/bin/connector check --project pyproject.toml
```

在全新源码副本与全新输出目录构建，保留已有产物：

```sh
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  <dev>/bin/connector build --project <build-copy>/pyproject.toml \
  --output-dir <new-delivery> --no-overwrite
```

若镜像索引暂时缺包，可按锁文件的精确 wheel URL 下载运行依赖并校验摘要，再补齐声明的
构建后端，以 `PIP_NO_INDEX=1 PIP_FIND_LINKS=<wheelhouse>` 使用同一原版构建命令离线验收。
不要通过修改 SDK、跳过依赖安装或降低校验来绕过构建失败。

consumer 只安装交付 wheel、正式 SDK serve 和测试依赖，复制 tests/pyproject.toml 而不复制
src，再回归并核对 site-packages 导入来源。原版 CLI/TLS 验收：

```sh
<consumer>/bin/python -I -B <independent>/tests/acceptance.py \
  <delivery>/yuque-0.1.0.connector <new-acceptance-output>
```

宿主需显式配置 HttpOptions、平台公钥、凭据密钥、安装 ID、数据目录与 TLS。
临时密钥、数据库、构建目录及产物不进入 Git。契约来源见 CONTRACTS.md，验证边界见
VALIDATION.md；本地模拟通过不等于真实语雀或宿主 UI 已验收。
