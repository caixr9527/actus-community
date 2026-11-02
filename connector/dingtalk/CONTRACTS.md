# 已核对的接口契约

核对日期：2026-11-02。优先采用钉钉官方授权说明和阿里云官方生成 SDK 的实际请求映射。
官方文档部分页面只有 JavaScript 外壳，未将搜索摘要当成完整接口 Schema。

## 授权与身份

- [钉钉：浏览器内获取用户委托凭证](https://opensource.dingtalk.com/developerpedia/docs/develop/permission/token/browser/get_user_app_token_browser/)
  说明授权码流程、授权端点、prompt=consent、空格分隔的个人权限、authCode/state 回调、
  JSON Token 请求和 corpid 的可选语义。正文未声明 PKCE，本应用不假定支持。
- [官方 OAuth SDK](https://github.com/alibabacloud-go/dingtalk/blob/master/oauth2_1_0/client.go)
  GetUserToken 的 JSON 字段为 clientId/clientSecret/code/grantType/refreshToken；响应
  accessToken/refreshToken/expireIn/corpId。未返回可验证的 scope 快照或 refreshToken TTL。
- [官方通讯录 SDK](https://github.com/alibabacloud-go/dingtalk/blob/master/contact_1_0/client.go)
  GetUser 的路径 /v1.0/contact/users/{unionId}、x-acs-dingtalk-access-token，以及
  unionId/openId/nick 等响应字段；授权教程说明使用当前用户信息接口。
- [钉钉个人身份信息接口](https://open.dingtalk.com/document/orgapp/dingtalk-retrieve-user-information)
  当前用户使用 /v1.0/contact/users/me。本应用只投影 unionId、nick，不输出手机和邮箱。

请求 scopes 固定为 openid、Contact.User.Read、Todo.PersonalTodo.Write。
Contact.User.Read 及显式 scope 机制由官方授权说明确认。
Todo.PersonalTodo.Write 的权限名称/code 映射还核对了
[纷享销客自己发布的钉钉连接器配置指引](https://help.fxiaoke.com/9bfb/c68f/3949/175d)。
该指引只用于此映射，未将其企业代理、其他权限或所有接口适用范围移植进本应用。
钉钉当前后台权限配置、发布和真实用户授权仍需实际环境验收。

不根据 token 响应中可选的 corpId 填造个人待办租户，不把请求的权限视为已授权证明。
Token 缺少刷新材料或有效 expireIn 时拒绝连接/刷新，不沿用缺失字段，不推算 TTL。
允许成功刷新显式返回相同 refreshToken；未知结果不重试旧材料。

## 个人待办

[官方待办 SDK](https://github.com/alibabacloud-go/dingtalk/blob/master/todo_1_0/client.go)
是以下方法、参数位置和回执类型的直接依据。该源码只用于契约核对，不作为应用运行依赖。
SDK 源码版本会变化；本应用测试固定下列已核对请求，不动态发现或调用新增接口。

| 官方方法 | HTTP / 路径 | 请求 | 成功响应 |
| --- | --- | --- | --- |
| CreatePersonalTodoTask | POST /v1.0/todo/users/me/personalTasks | JSON subject、executorIds，可选 description、dueTime | taskId 字符串、createdTime 整数 |
| UpdatePersonalTodoTask | PUT /v1.0/todo/users/me/tasks/{taskId}/update | JSON 修改字段 | success 布尔 |
| UpdatePersonalTodoTaskExecutorStatus | PUT /v1.0/todo/users/me/tasks/{taskId}/updateExecutorStatus | **query done** | success 布尔 |
| DeletePersonalTodoTask | DELETE /v1.0/todo/users/me/tasks/{taskId}/remove | 无 body | success **字符串** |

请求通过固定 HTTPS 域名，HeaderKey 从 SDK 业务访问凭据注入认证头。
UpdatePersonalTodoTask 的官方模型还包含 done/executorIds/participantIds，首版主动不开放。
创建不开放参与者、提醒与通知配置；执行者固定当前已授权用户，不声称能为他人派发任务。
删除方法与 HideUserTodoTask 是不同接口，后者明确仅删除本人视图，不能混用语义。
本应用不保证 remove 的可撤销性或其他参与者视图保持不变。

本应用对标题、描述、ID 和时间采用 README 所列的保守输入子集；不是声称厂商最大值。
描述空字符串表达清空请求，未通过真实账号验证所有客户端展示；截止时间清空未开放。
写入成功仅表示合法回执，不表示已读回核实最终内容或界面状态。

## 尚未纳入的能力

QueryTodoTasks、QueryOrgTodoTasks、QueryOrgTodoByUser、GetTodoTask 等方法存在于官方 SDK，
但仅有路径和参数不足以证明当前个人权限/Token 对应的资源范围。
首版不注册列表/详情工具，不通过 enterprise accessToken 补齐，不制造空列表代替权限失败。
企业应用管理、机器人、日历、审批、工作待办、事件回调均不在首版范围。

## 本地验证边界

测试使用公开 SDK Server/Client、签名平台许可和加密存储，在 HTTPX 公开 transport 边界
模拟已核对的钉钉请求/响应。不修改 SDK 私有方法或厂商域名，不向应用添加测试开关。
这些测试验证本应用如何使用协议，不能证明真实企业配置、用户权限或接口实际可用性。
