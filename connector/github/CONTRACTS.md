# GitHub 0.1.0 契约依据

核对日期 2026-11-02。运行时静态声明，不读取本文件或发现新工具。
官方 REST API 版本固定 2026-03-10；公开 SDK 固定 0.0.1b9。

## OAuth 与权限

- [GitHub App 用户令牌](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app)：
  GET https://github.com/login/oauth/authorize，Client ID、state、redirect_uri、PKCE S256，
  scope=offline_access 只请求过期令牌，不授予业务权限。
- POST https://github.com/login/oauth/access_token：表单 Client ID/Secret、code、
  redirect_uri、code_verifier，Accept: application/json；初始交换不传 grant_type。
  刷新使用 grant_type=refresh_token。响应中 Token 类型为 bearer，scope 为空。
- [刷新](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/refreshing-user-access-tokens)：
  使用 expires_in 和 refresh_token_expires_in；刷新同时轮换用户访问令牌和刷新令牌。
  首版要求返回两类过期字段和刷新凭据，不回退长期令牌。
- OAuth 错误可能位于 HTTP 200 JSON 中。仅明确客户端错误 incorrect_client_credentials
  使用 SDK 的客户端拒绝路径；503/429 即使携带相同字符串也不能证明旧刷新凭据未使用。
  bad_refresh_token、bad_verification_code 等按重新授权处理。不回显 error_description。
- GET https://api.github.com/user：稳定数字 id 为账号，login 为展示，type=User。
- 权限为 Metadata Read、Issues Read and write、Pull requests Read；实际资源权限由
  应用、安装、用户及组织共同决定，不从 scope 或一次读取成功生成全局许可。

## REST 操作

以下路径相对 https://api.github.com/；均使用 GitHub App 用户令牌。
参数采用官方契约的有限子集，新增能力必须明确建模后发版。

| 本地操作 | 方法与路径 |
| --- | --- |
| list_installations | GET /user/installations |
| list_repositories | GET /user/installations/{installation_id}/repositories |
| get_repository | GET /repos/{owner}/{repo} |
| list_issues | GET /repos/{owner}/{repo}/issues |
| get_issue | GET /repos/{owner}/{repo}/issues/{issue_number} |
| create_issue | POST /repos/{owner}/{repo}/issues |
| update_issue | PATCH /repos/{owner}/{repo}/issues/{issue_number} |
| list_issue_comments | GET /repos/{owner}/{repo}/issues/{issue_number}/comments |
| create_issue_comment | POST /repos/{owner}/{repo}/issues/{issue_number}/comments |
| list_labels | GET /repos/{owner}/{repo}/labels |
| list_pull_requests | GET /repos/{owner}/{repo}/pulls |
| get_pull_request | GET /repos/{owner}/{repo}/pulls/{pull_number} |
| list_pull_request_files | GET /repos/{owner}/{repo}/pulls/{pull_number}/files |

主要官方依据：

- [安装及仓库发现](https://docs.github.com/en/rest/apps/installations)：
  这里使用 /user/installations 用户接口，不用只接受安装令牌的 /installation/repositories。
- [Issues](https://docs.github.com/en/rest/issues/issues)：列表同时返回 PR，使用 pull_request 字段区分；
  PATCH 省略不修改，标签数组替换集合。厂商可能按用户权限忽略字段，需核对回执。
- [评论](https://docs.github.com/en/rest/issues/comments)：Issues 接口也可操作 PR 讨论，
  本应用额外预检，首版只开放 Issue 评论。
- [PR](https://docs.github.com/en/rest/pulls/pulls)：文件最多 3000，patch 并非总是存在。
- [分页](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)：
  通过 Link 的 next 判断后续页，允许 canonical /repositories/{id} 路径。
- [最佳实践](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)：
  主/次级限流、Retry-After、重定向和写入间隔。
- [API 版本](https://docs.github.com/en/rest/about-the-rest-api/api-versions)。

另行只读下载 GitHub 官方
[OpenAPI](https://github.com/github/rest-api-description/blob/main/descriptions/api.github.com/api.github.com.json)
核对上述方法、参数和状态；原文件保留在仓库外，不作为依赖或随包分发。
本地文件 /tmp/actus-github-openapi-20261102.json，摘要由本轮验证记录保存。

应用只在 200/201 预期状态和有效回执后成功；404 同时可能表示不可见，不推断资源不存在。
写前失败与写后未知区分。没有通用写重试、隐式创建标签、自动合并、代码或 CI 操作。
