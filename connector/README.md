# Connector 应用

每个子目录是一个独立 Python 应用工程，通过公开的 `actus-connector-sdk`
构建 `.connector` 包。不依赖 Actus 平台源码或相邻应用配置。

| 应用 | 目录 | 状态 |
| --- | --- | --- |
| 腾讯文档 | [tencent-docs](tencent-docs/README.md) | 0.1.1 / SDK 0.0.1b3，隔离构建及安装调用验证完成，未部署 |

凭据、开发数据库和安装运行材料不得进入仓库。应用的运行和构建步骤见各自 README。
