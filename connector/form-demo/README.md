# 多字段工单示例

独立应用 `form-demo`，使用 FormAuth 输入租户、用户名和密码，登录换取 Token，
再核验服务端身份并读取工单。仅保存 Token，不保存登录密码。
示例接口是约定的模拟服务，不代表接入了真实厂商。

## SDK 与开发环境

应用版本 `0.1.3`，固定依赖正式 SDK `0.0.1b6`。腾讯镜像的 wheel、sdist 已与
PyPI 摘要核对一致；示例仍使用模拟厂商，不代表已部署或完成页面验收。

不依赖平台源码、相邻应用或私有配置。以下命令在本工程目录执行，环境、构建
副本和产物目录均使用新目录；不覆盖现有工程环境：

```bash
python3.12 -m venv /absolute/form-env
/absolute/form-env/bin/python -m pip install \
  --index-url https://mirrors.cloud.tencent.com/pypi/simple \
  'actus-connector-sdk[build,serve]==0.0.1b6' \
  '.[test]'
```

SDK 命令入口为环境中的 `connector`：

```bash
/absolute/form-env/bin/connector check --project pyproject.toml
/absolute/form-env/bin/python -m pytest -p no:cacheprovider tests
```

`check` 和测试应导入该环境中已安装的应用。修改源码后重新安装，或一次
editable 安装；不通过 PYTHONPATH 加载 SDK 源码，不使用候选包覆盖正式依赖。

## 构建与运行

将本工程复制到新的构建目录并重新安装应用，在副本内构建，避免覆盖原目录产物。
构建默认核验当前安装的 SDK；从腾讯镜像安装依赖，不自动回退其他源：

```bash
PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple PIP_EXTRA_INDEX_URL= \
  /absolute/form-env/bin/connector build --project /absolute/build-copy/pyproject.toml \
  --output-dir /absolute/new-delivery
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

Web 和桌面端已补齐通用多字段表单；视觉与原生交互仍需人工验收。SDK 依赖升级
不代表真实厂商、页面或生产部署已经验收。
