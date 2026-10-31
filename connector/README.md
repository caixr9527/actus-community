# Connector 应用

每个子目录是一个独立 Python 应用工程，通过公开的 `actus-connector-sdk`
构建 `.connector` 包。不依赖 Actus 平台源码或相邻应用配置。

| 应用 | 目录 | 状态 |
| --- | --- | --- |
| 腾讯文档 | [tencent-docs](tencent-docs/README.md) | 0.1.6 / SDK 0.0.1b8；构建、独立安装及隔离测试通过，未部署 |
| 多字段工单示例 | [form-demo](form-demo/README.md) | 0.1.5 / SDK 0.0.1b8；构建、独立安装及隔离测试通过，UI 与真实厂商另验，未部署 |
| Notion | [notion](notion/README.md) | 0.1.5 / SDK 0.0.1b8；构建、独立安装及隔离测试通过，真实 Notion 与 UI 另验，未部署 |
| 通用文件示例 | [file-demo](file-demo/README.md) | 0.1.2 / SDK 0.0.1b8；固定服务单文件上传下载、独立包及隔离任务链路通过，未部署 |

凭据、开发数据库和安装运行材料不得进入仓库。应用的运行和构建步骤见各自 README。
