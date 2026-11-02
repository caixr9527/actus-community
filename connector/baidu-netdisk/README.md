# 百度网盘

独立的百度网盘 Connector 应用，版本 `0.1.0`，固定使用公开发布的
`actus-connector-sdk==0.0.1b9`。运行不依赖 Backend、Atlas、SDK 源码或其他应用配置。

## 功能

提供 `list_files`、`search_files`、`get_quota`、`semantic_search`、
`get_file_metadata`、`create_folder`、`copy_file`、`move_file`、`rename_file`、
`delete_file`、`upload_file`、`download_file` 共 12 项操作。

上传通过 SDK `FileInput` 接收单个文件；业务参数只有 `destination_path`（默认 `/`），
不接受 Artifact ID、本地文件路径或任意上传 URL。下载通过 `FileOutput` 交给宿主保存，
不向工具调用者暴露下载地址和 Token。

根目录查询可省略路径或使用 `/`；相对路径以网盘根目录为基准。
拒绝空段、`.`、`..`、反斜线和控制字符。写入操作不允许以根目录作为源对象。
复制和移动显式支持 `fail`、`newcopy`、`overwrite`、`skip`，默认 `fail`；
上传不覆盖同名文件。文件管理采用同步请求，返回的任务标识如实保留，不自行轮询或重试。

容量的到期标记、文件名搜索的更多结果标记或语义搜索的结束标记未返回时，
对应字段为 `null`，表示未知，不推断为未到期或搜索已结束。
目录列表使用起始位置分页，满页时允许继续读取，是否到末尾须结合后续返回确认。

## 授权与配置

在百度开放平台创建应用、开通所需接口权限，并登记宿主提供的回调地址。
Actus 通用回调为 `/api/connector-oauth/callback`，不要使用旧 Provider 专用回调。
实际协议、域名和完整地址以当前部署为准，必须与登记值一致。

安装配置：

- `client_id`：百度 AppKey，普通配置。
- `client_secret`：百度 SecretKey，使用 SDK 标准密钥绑定，不能放入普通配置或仓库。

应用使用机密客户端，申请 `basic,netdisk`，不启用 PKCE。
通过公开 `OAuthProtocol` 定制 GET 令牌交换、刷新和响应解析；业务请求使用公开
`QueryKey` 认证。允许百度省略 `token_type`，要求有效的访问令牌、刷新令牌和过期时间。
state、授权事务、用户隔离、加密保存、刷新并发及取消收尾由 SDK 承担。
刷新接口发生限流、服务异常或结果无法确认时，不能仅凭响应中的错误字符串认定旧刷新令牌
未被使用；交给 SDK 按已尝试刷新处理，阻止继续复用结果未知的刷新凭据。
没有配置远端撤销接口，断开连接是本地断开，结果为 `revocation.not_attempted`，
不表示百度侧授权已经撤销。

语义搜索和下载等能力取决于百度实际授予的应用权限；没有权限会返回失败，
不会改用 Cookie、网页私有接口或借用其他服务凭据。

## 文件传输与运行约束

文件上限为 100 MiB，同时服从宿主更小的限制；空文件上传不支持。
应用先在临时文件中计算 4 MiB 分片 MD5，再预上传、上传缺失分片、以完整摘要列表合并。
单个应用进程仅允许一个上传进入暂存阶段，暂存文件在完成、失败和取消后关闭。
秒传响应没有真实文件 ID 时返回 `external_resource_id: null`，不会制造 ID。

下载逐跳限制 HTTPS 百度下载域名、最多 5 次跳转，并校验文件大小和实际 EOF。
初始链接经域名检查后携带 Token，跨域跳转移除 OAuth Token，后续不重新注入；
响应和客户端由本次 SDK 资源作用域持有，
包括输出流尚未开始消费就被取消的情况。

排队、文件读取、暂存、请求和输出消费使用同一个截止时间。
不会自动重试写入。写入后超时、断连或收到无法确认的响应，可能返回结果未知；
应按原目标路径核实，不直接重新提交。应用不会自动删除可能已经写入的远端文件。

当前 Actus Runtime 默认总预算 30 秒、共享临时目录 128 MiB。
100 MiB 是大小上限，不是任意网络条件下的完成保证；多个安装共享空间时须预留容量。
应用不自行修改 Runtime 超时、磁盘或容器配置。

## 独立开发与交付

以下命令从本目录执行；构建输出、运行数据和依赖环境使用自己的隔离目录。
依赖安装使用腾讯 PyPI 镜像，不使用其他工程的虚拟环境。

```sh
uv venv /tmp/baidu-dev-venv
uv pip install --python /tmp/baidu-dev-venv/bin/python \
  --index-url https://mirrors.cloud.tencent.com/pypi/simple \
  -e '.[test]' 'actus-connector-sdk[build,serve]==0.0.1b9'
/tmp/baidu-dev-venv/bin/ruff check src tests
/tmp/baidu-dev-venv/bin/pytest
/tmp/baidu-dev-venv/bin/connector check --project pyproject.toml
/tmp/baidu-dev-venv/bin/connector build --project pyproject.toml \
  --output-dir /tmp/baidu-delivery --no-overwrite
```

将 `.connector` 交给支持 SDK b9 的 Runtime 安装；独立宿主也可使用
SDK `connector serve --entrypoint baidu_netdisk.app:App --settings <安装配置文件>`。
安装配置须包含包文件、独立安装 ID、凭据加密密钥、平台验签公钥和通用回调地址，
密钥文件按 SDK 要求设置权限。使用平台签发的许可调用，不能直接绕过用户与连接归属检查。

### 构建包独立验收

使用全新的 consumer 环境，将 `.connector` 中唯一的应用 wheel 提取到独立目录，
安装该 wheel 和发布版 `actus-connector-sdk[serve]==0.0.1b9`，执行 `python -m pip check`。
使用 consumer 的 `connector check --project <本应用 pyproject.toml>` 检查安装后的声明；
此处项目文件仅提供元数据，应用与 SDK 均应从 consumer 的 `site-packages` 导入。

将 `tests/acceptance.py`、`tests/serve_fixture.py`、`tests/vendor.py` 复制到独立测试目录，
用 consumer 解释器运行（输出目录必须尚不存在）：

```sh
<consumer>/bin/python -I -B <独立测试目录>/acceptance.py \
  --package <独立目录>/baidu-netdisk-0.1.0.connector \
  --output <独立目录>/acceptance-run
```

脚本先启动未经替换的正式 `connector serve` 验证包校验、TLS 健康检查及关闭；
随后仅在测试进程的公开 HTTPX 传输边界替换百度响应，通过真实 TLS SDK Server／Client
完成授权、重放、用户归属、重启、并发刷新、12 项操作、8 MiB 以上文件的部分分片复用、
下载和断开连接，核对退出码、模块来源、日志及凭据存储。
不修改 SDK 私有接口或应用实现，不向生产配置增加测试开关；测试辅助文件不进入交付包。
产物报告写入 `acceptance-run/report.json`。每次源码或声明变化后须重新构建并安装验收。

## 契约来源与验收边界

业务参考旧百度 Provider，协议核对参考百度公开资料：

- [百度官方 MCP 能力与权限说明](https://github.com/baidu-netdisk/mcp)。
- [百度官方上传示例](https://github.com/baidu-netdisk/mcp/blob/main/src/baidu-netdisk/fileupload_tool.py)。
- [百度官方 Go SDK 协议实现](https://github.com/baidu-netdisk/baidu-drive-sdk-go/tree/main/baidudriver/api)。
- [百度开放平台](https://yun.baidu.com/open/platform)。

隔离验收使用确定性百度响应和测试凭据，不访问真实账号。
真实百度授权、接口权限、真实上传下载和 UI 仍需专门联调；应用开发不等于部署或旧连接迁移。
本应用不会登记 Atlas 数据、修改现有安装或下线旧 Provider。
