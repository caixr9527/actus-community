# Connector 应用

每个子目录是一个独立 Python 应用工程，通过公开的 `actus-connector-sdk`
构建 `.connector` 包。不依赖 Actus 平台源码或相邻应用配置。

| 应用 | 目录 | 状态 |
| --- | --- | --- |
| 腾讯文档 | [tencent-docs](tencent-docs/README.md) | 0.1.7 / SDK 0.0.1b9；构建、独立安装及隔离测试通过，未部署 |
| 多字段工单示例 | [form-demo](form-demo/README.md) | 0.1.6 / SDK 0.0.1b9；构建、独立安装及隔离测试通过，UI 与真实厂商另验，未部署 |
| Notion | [notion](notion/README.md) | 0.1.6 / SDK 0.0.1b9；构建、独立安装及隔离测试通过，真实 Notion 与 UI 另验，未部署 |
| 通用文件示例 | [file-demo](file-demo/README.md) | 0.1.3 / SDK 0.0.1b9；固定服务单文件上传下载、独立包及隔离任务链路通过，未部署 |
| 百度网盘 | [baidu-netdisk](baidu-netdisk/README.md) | 0.1.1 / SDK 0.0.1b9；元数据标记解析修复、95 项测试及声明检查通过，构建、上传和升级由用户执行 |

凭据、开发数据库和安装运行材料不得进入仓库。应用的运行和构建步骤见各自 README。

## 本地开发

各应用的默认 `dev` 依赖组包含 SDK 的 `build` 和 `serve` 工具依赖。
在相应应用目录执行 `uv sync` 并激活 `.venv` 后，即可直接使用 `connector check`、
`connector build` 和 `connector serve`，无需额外安装工具依赖。
测试依赖通过 `uv sync --extra test` 安装；`uv sync --no-dev` 适用于不需要开发工具的环境。
