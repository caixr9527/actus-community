"""Thirteen static operations; three Issue mutations and read-only PR inspection."""

from connector_sdk import AppSpec, Connector, HttpService, operation

from . import installations, issues, pulls, repositories
from . import models as m
from .api import ORIGIN, Scheduler, execute
from .auth import Auth


class App(Connector):
    spec = AppSpec(id="github", name="GitHub", description="仓库发现、Issue 管理和 PR 只读分析")
    config_model = m.Settings
    auth = Auth()
    services = {"api": HttpService(ORIGIN, auth="connection")}

    async def startup(self):
        self.scheduler = Scheduler()

    @operation(
        name="list_installations", description="分页列出当前用户可访问的应用安装。", effects="read"
    )
    async def list_installations(self, ctx, params: m.Page) -> m.Result:
        return await execute(self.scheduler, ctx, installations.list_installations, params)

    @operation(
        name="list_repositories", description="按安装分页列出用户可访问的仓库。", effects="read"
    )
    async def list_repositories(self, ctx, params: m.InstallationPage) -> m.Result:
        return await execute(self.scheduler, ctx, repositories.list_repositories, params)

    @operation(name="get_repository", description="读取仓库元数据。", effects="read")
    async def get_repository(self, ctx, params: m.Repository) -> m.Result:
        return await execute(self.scheduler, ctx, repositories.get_repository, params)

    @operation(
        name="list_issues",
        description="分页筛选 Issue；过滤 PR 后空页仍可能有后续页。",
        effects="read",
    )
    async def list_issues(self, ctx, params: m.ListIssues) -> m.Result:
        return await execute(self.scheduler, ctx, issues.listing, params)

    @operation(name="get_issue", description="按仓库内编号读取 Issue，不接受 PR。", effects="read")
    async def get_issue(self, ctx, params: m.Issue) -> m.Result:
        return await execute(self.scheduler, ctx, issues.get, params)

    @operation(name="create_issue", description="创建 Issue，可使用仓库已有标签。", effects="write")
    async def create_issue(self, ctx, params: m.CreateIssue) -> m.Result:
        return await execute(self.scheduler, ctx, issues.create, params)

    @operation(
        name="update_issue", description="更新 Issue；标签完整替换，空数组清空。", effects="write"
    )
    async def update_issue(self, ctx, params: m.UpdateIssue) -> m.Result:
        return await execute(self.scheduler, ctx, issues.update, params)

    @operation(
        name="list_issue_comments",
        description="分页读取 Issue 讨论评论，不接受 PR。",
        effects="read",
    )
    async def list_issue_comments(self, ctx, params: m.IssuePage) -> m.Result:
        return await execute(self.scheduler, ctx, issues.comments, params)

    @operation(
        name="create_issue_comment",
        description="为 Issue 添加讨论评论，可能通知参与者。",
        effects="write",
    )
    async def create_issue_comment(self, ctx, params: m.CreateComment) -> m.Result:
        return await execute(self.scheduler, ctx, issues.comment, params)

    @operation(name="list_labels", description="分页列出仓库已有标签。", effects="read")
    async def list_labels(self, ctx, params: m.RepositoryPage) -> m.Result:
        return await execute(self.scheduler, ctx, issues.labels, params)

    @operation(name="list_pull_requests", description="分页列出 PR。", effects="read")
    async def list_pull_requests(self, ctx, params: m.ListPulls) -> m.Result:
        return await execute(self.scheduler, ctx, pulls.listing, params)

    @operation(
        name="get_pull_request",
        description="读取 PR 详情、head/base SHA 和变更文件数。",
        effects="read",
    )
    async def get_pull_request(self, ctx, params: m.Pull) -> m.Result:
        return await execute(self.scheduler, ctx, pulls.get, params)

    @operation(
        name="list_pull_request_files",
        description="分页读取 PR 文件和可用 patch，返回覆盖范围。",
        effects="read",
    )
    async def list_pull_request_files(self, ctx, params: m.PullFiles) -> m.Result:
        return await execute(self.scheduler, ctx, pulls.files, params)
