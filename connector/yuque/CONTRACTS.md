# 语雀接口契约与验收边界

核对日期：2026-11-02。使用正式 SDK 0.0.1b9，独立实现 REST HTTP 请求。

## 证据来源

- [语雀官方 CLI 说明](https://github.com/yuque/yuque-open-cli/blob/main/README.zh-CN.md)：
  个人/团队 Token 区别、默认主站及空间 Host、知识库/搜索/文档能力。
- [官方仓库 OpenAPI](https://github.com/yuque/yuque-open-cli/blob/main/spec/yuque-openapi.yaml)：
  OpenAPI 3.1.0，info.version=2.0.1；X-Auth-Token、端点、参数、数据模型与错误状态。
- [语雀开发者文档入口](https://www.yuque.com/yuque/developer/api)：本轮浏览工具读取超时，
  实际字段核对以上述官方仓库提供的规格为依据，不声称已读到无法访问的页面正文。
- [Token 设置入口](https://www.yuque.com/settings/tokens)：由用户在自己的浏览器操作。

官方规格只读下载到仓库外；未安装、运行 CLI、Skill 或外部脚本，未读取用户登录材料，
没有使用真实 Token 或对真实知识库执行写入。

本轮取得的完整规格为 128001 字节，SHA-256：

```text
f69afdd53530e6438604731a083e97fc5e6c0ca226ab5b1250ee91a9a148eb59
```

临时副本：`/tmp/actus-yuque-contracts-20261102/spec/yuque-openapi.yaml`。
下载自官方仓库 main 的公开文件；main 会变化，摘要只固定本轮内容，不是版本兼容承诺。
规格不作为运行时依赖，也不打包外部 CLI。

## 首版请求子集

固定服务 `https://www.yuque.com/api/v2/`，X-Auth-Token 由 SDK HeaderKey 注入，
User-Agent=Actus-Yuque/0.1.0。无 OAuth、动态工具派发、Cookie 登录或任意 Host。

| 操作 | 请求 |
| --- | --- |
| get_current_user | GET user |
| list_groups | 先 GET user，再 GET users/{current_user_id}/groups；offset |
| list_repositories | user 模式先 GET user，再 GET users/{current_user_id}/repos；团队走 groups/{group_id}/repos；offset/limit |
| get_repository | GET repos/{repository_id} |
| list_documents | GET repos/{repository_id}/docs；offset/limit/deleted=false |
| get_document | GET repos/{repository_id}/docs/{document_id} |
| search | GET search；q/type/page，可选 scope |
| create_document | 预检知识库后 POST repos/{repository_id}/docs；title/body/format=markdown/public=0 |
| update_document | 预检知识库和文档后 PUT repos/{repository_id}/docs/{document_id}；title/body 子集、format=markdown、原 public |

工具 ID 使用本地正整数字符串，HTTP 路径仅使用已校验数字；响应规格的 int64 ID 用 Python
整数读取后转字符串，避免 JSON 客户端丢失精度。SDK query 参数要求字符串，应用显式转换
内部已验证的整数参数，不透传任意用户字典。

## 分页差异

- 搜索：page 1–100，固定每页 20；meta.total/pageNo/pageSize。
- 用户团队列表：offset，固定每页 100，未声明 limit。
- 知识库列表：offset/limit，limit 最大 100，规格未声明 total。
- 文档列表：offset/limit，limit 最大 100，可返回 meta.total。
- 用户团队列表的 data 在规格中引用单个 V2Group，但端点说明和官方功能语义为列表。
  本应用只支持数组结果，不把对象猜成完整列表；该规格不一致仍须真实账号核实。

不依赖不存在的统一 has_more 字段，不以短页/空页推断末页。缺 total 返回 has_more=null，
下一位置仅为继续查询候选。出现已知 total 与本页数量冲突、空页无法推进、重复 ID、
错误归属、搜索页码/页大小不符时失败。单页调用不保证跨页快照一致。

## 写入语义

规格明确创建时 public 省略会继承知识库，更新时 public 默认 0，因此应用创建显式私密，
更新先读取原值并显式保留。普通知识库 type=Book；普通文档 type=Doc、format=markdown
才可写，分类未知时不推断。创建不会自动加入知识库目录，首版也不补发目录写入。

get_document 读取规格的 body（原始内容），不以 body_draft、body_html 或 body_lake 代替。
status 规格为字符串 0/1；额外兼容整数 0/1 并转为字符串，拒绝布尔值；未声称该兼容分支
是线上抓包结果。正文草稿与原文不同且非空时拒绝更新；已删除标记也拒绝。
缺失草稿字段无法证明没有草稿，且预检和写入之间存在并发窗口。

expected_updated_at 为本地写前比较，不传入未声明的服务端条件参数，也不宣称原子锁。
更新时间按明确时区 ISO 8601 校验，比较原始字符串；不同字符串即便代表同一时刻也拒绝，
调用者应原样使用读取结果。正文替换不合并、不追加，不提供路径、公开性或成员变更参数。

回执须为合法文档对象，匹配 ID/归属、普通 Markdown 类型、标题、正文和可见性，更新还
核对原 slug。拒绝顶层或 data 内的错误标记、success=false、错误 ID 或其他矛盾。
accepted 只表示接口回执接受，content_verified=false 表示没有独立回读；不会据此报告
客户端已发布或维持草稿。真实发布行为、服务端正文规范化及 UI 展示仍待验证。

写前已知失败不派发写请求；写请求发出后错误/超时保守为 uncertain，不自动重试或补偿。
其他 SDK 取消/截止时间路径也可能保守为结果未知，即使取消发生在预检阶段。

## 必须保留的验证边界

tests/vendor.py 是根据公开规格构造的兼容性夹具，**不是真实语雀响应抓包**。
尚未用真实 Token 验证 Token 权益、Scope、可见性、完整分页及权限不足、更新回执、
草稿/发布状态、主站账号范围和宿主上传/审批/UI。遇到未支持格式会失败；写后可能未知。
模拟测试和独立包验收只能证明本地实现及交付机制，不能替代以上真实环境验收。
