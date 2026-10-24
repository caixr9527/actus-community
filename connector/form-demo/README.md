# 多字段工单示例

独立应用 `form-demo`，使用 FormAuth 输入租户、用户名和密码，登录换取 Token，
再核验服务端身份并读取工单。仅保存 Token，不保存登录密码。
示例接口是约定的模拟服务，不代表接入了真实厂商。

## SDK 与开发环境

当前仅用于本地开发验证。包含 FormAuth 的本地 SDK 候选包仍使用 `0.0.1b3`
版本标识；腾讯云镜像中的同版本公开包不包含这项能力，不能仅按版本号判断。
现阶段保持工程依赖声明不变，显式提供经核实的本地 wheel，并记录其提交号和
SHA-256。正式发布后统一更新 SDK 要求，再验证镜像安装及正式构建。

不依赖平台源码、相邻应用或私有配置。以下命令在本工程目录执行，环境、构建
副本和产物目录均使用新目录；不覆盖现有工程环境：

```bash
python3.12 -m venv /absolute/form-env
/absolute/form-env/bin/python -m pip install \
  --index-url https://mirrors.cloud.tencent.com/pypi/simple \
  '/absolute/local-sdk/actus_connector_sdk-0.0.1b3-py3-none-any.whl[build,serve]' \
  '.[test]'
```

SDK 命令入口为环境中的 `connector`：

```bash
/absolute/form-env/bin/connector check --project pyproject.toml
/absolute/form-env/bin/python -m pytest -p no:cacheprovider tests
```

`check` 和测试应导入该环境中已安装的应用。修改源码后重新安装应用；如新环境
误装了镜像旧包，显式以本地 wheel 重新安装 SDK，不修改其他工程依赖文件。
不要通过 PYTHONPATH 加载 SDK 源码或把候选包当作已发布产物。

## 构建与运行

将本工程复制到新的构建目录并重新安装应用，在副本内构建，避免覆盖原目录产物。
工具环境与传入的 SDK wheel 必须匹配：

```bash
/absolute/form-env/bin/connector build --project /absolute/build-copy/pyproject.toml \
  --output-dir /absolute/new-delivery \
  --sdk-wheel /absolute/local-sdk/actus_connector_sdk-0.0.1b3-py3-none-any.whl
```

安装器把 `.connector` 包中的应用 wheel 和 SDK serve extra 安装到新的运行环境。
服务管理员提供 `api_base_url` 配置，例如 `https://tickets.example/api/`，以及 SDK
要求的安装身份、平台公钥、32 字节凭据密钥、数据目录和监听配置；配置和密钥
放在工程目录外。应用运行入口为 `form_demo.app:App`。可使用 SDK 的
`connector dev` 与 `python -m connector_sdk.dev_client` 验证多字段授权；密码从
隐藏输入读取，不放入命令行、环境变量或示例配置。完整配置规则见 SDK README。

## 示例服务契约

| 接口 | 约定 |
| --- | --- |
| `POST login` | 匿名请求，JSON 为 `tenant`、`username`、`password`；成功返回 `{"authenticated": true, "token": "..."}`，明确拒绝返回 `{"authenticated": false}` |
| `GET me` | 使用候选 Token 的 Bearer 请求；返回非空 `account_id`、`tenant_id`，可选 `display_name`、`permissions` |
| `GET tickets` | 使用保存 Token 的 Bearer 请求；参数 `q`、`limit`，返回 `{"items": [{"id": "...", "title": "..."}]}` |

返回租户必须与提交租户一致。权限未知保持未知；明确缺少 `tickets.read` 时 SDK
拒绝业务调用。`list_tickets` 是只读操作，默认 limit 为 20，范围 1–100。
HTTP 非成功、网络失败或无效响应不伪装成授权成功；不自动重试写入。

API 验证顺序为安装、启用、使用资格、多字段授权、连接选择、业务调用、重启、
重授权和断开。跨用户连接拒绝；同账号重授权更新原连接，身份变化创建新连接并
保留原连接，不自动切换当前账号。响应丢失时核实原事务或连接，不依据历史授权
结果判断当前连接状态。

当前 Web 和桌面页面仍需多字段表单适配。候选 SDK 的本地联调通过不代表正式
依赖已升级、真实厂商已验收、页面已验收或应用已部署。
