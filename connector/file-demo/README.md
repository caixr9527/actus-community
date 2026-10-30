# 通用文件示例

独立应用 `file-demo`，版本 `0.1.0`，通过固定服务下载一个文件并由平台导入 Artifact。
适用于任意文件类型；不包含网盘、工单、文档或图片专属协议。服务是明确约定的模拟 API，
不代表已接入真实厂商。SDK 候选为 `0.0.1b8.dev4`，尚未正式发布。

## 配置、授权与操作

管理员提供 `values.api_base_url`，例如 `https://files.example/api/`。该地址不会出现在
模型参数中；用户连接时提交文件服务 Token，由 SDK 按 Bearer 注入请求、验证身份并加密保存。
账号、租户及权限来自服务响应，不从 Token 推断。权限未知保留未知，服务仍须逐文件鉴权。

唯一业务操作 `download_file` 接收 `{file_id: 原样标识}`，只读、单文件输出，声明上限
100 MiB。标识仅作为查询参数，不拼接路径，不接受 URL、目的路径或存储凭据字段。
应用先获取并校验元信息，再用公开 `ctx.http("api").get_file(...)` 返回受管 `FileOutput`。
不按扩展名猜 MIME，不把未知大小当作零，不在应用或 Gateway 拼接整个文件。

SDK 按当前调用的截止和文件上限读取，关闭成功后才能完成输出；平台还会取自己的较小上限。
超限、长度不符、截断、超时或取消不能登记成功文件。必要关闭可超过截止，迟到结果不能成功。
服务元信息读取与内容读取不是内容快照；本例不提供 Range、断点续传或自动重试。

平台成功结果是实际登记摘要 `data.artifact`，包含 artifact_id、file_name、可空 mime_type、
实测 size_bytes 和 kind。SDK 应用本身不生成平台引用，也不接收 Sandbox 地址或凭据。
Backend 已登记但随后响应丢失或关闭失败时，保留产物、返回未知，不自动重复下载或导入。

## 示例服务契约

三个接口相对 api_base_url，均使用 `Authorization: Bearer <Token>`：

| 接口 | 成功响应 |
| --- | --- |
| `GET me` | `{"account_id":"account-1","tenant_id":null,"display_name":null,"permissions":["files.read"]}`；permissions 可省略或为 null |
| `GET files/metadata?file_id=...` | `{"file_id":"sample","file_name":"样例.bin","mime_type":null,"size_bytes":null}` |
| `GET files/content?file_id=...` | HTTP 200 原始字节；Content-Length 可未知，不压缩、不重定向 |

元信息的 file_id 必须与请求一致，文件名遵循 SDK 单文件名称契约，大小为严格非负整数或 null。
零字节合法，MIME 可未知。身份无效返回 401/403，不可见文件返回 404；服务故障不能用 HTTP 200
错误 JSON 冒充文件。JSON 文件本身可以合法下载，SDK 不按内容类型猜测业务错误。

本地服务在 `tests/file_service.py`，只用于演示和验证，不进入应用 wheel 或 `.connector`：

```bash
python tests/file_service.py --token-file /absolute/private/demo-token --host 127.0.0.1 --port 24019
```

token-file 在源码和交付目录外准备；示例 api_base_url 为 `http://127.0.0.1:24019/api/`。
容器内运行应用时，该地址必须改为容器实际可达的隔离服务地址。默认文件标识有 sample、
empty、binary、unknown；它们分别展示文本、零字节、二进制和未知大小，不限制生产服务的类型。
故障控制仅存在于测试服务，应用参数不含测试开关。

## 独立开发与交付

仅依赖公开 SDK 与 Pydantic，不导入平台、Runtime 或相邻应用源码。当前候选未发布，使用
本轮构建的真实 SDK wheel 在新环境安装，不能用候选覆盖现有正式环境：

```bash
python3.12 -m venv /absolute/new-file-env
/absolute/new-file-env/bin/python -m pip install --index-url https://mirrors.cloud.tencent.com/pypi/simple \
  '/absolute/actus_connector_sdk-0.0.1b8.dev4-py3-none-any.whl[build,serve]'
/absolute/new-file-env/bin/python -m pip install --index-url https://mirrors.cloud.tencent.com/pypi/simple '.[test]'
/absolute/new-file-env/bin/connector check --project pyproject.toml
/absolute/new-file-env/bin/python -m pytest -p no:cacheprovider tests --basetemp /absolute/new-test-output
```

构建使用本工程的全新副本和新输出目录，避免覆盖既有产物：

```bash
/absolute/new-file-env/bin/connector build --project /absolute/build-copy/pyproject.toml \
  --sdk-wheel /absolute/actus_connector_sdk-0.0.1b8.dev4-py3-none-any.whl \
  --output-dir /absolute/new-delivery
```

安装运行还需提供 SDK 要求的安装身份、平台公钥、凭据密钥、数据目录及 HTTP 选项。
测试服务、测试数据、私钥和授权材料不进入发布包。

平台正式依赖继续固定 b7。候选隔离验证、SDK 正式发布、平台消费升级、Atlas Web 的 null
输出声明适配和现有安装切换分别验收；不能用示例通过证明生产文件能力已开放。
本项只实现下载，上传及页面展示单独推进。
