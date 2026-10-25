"""Pinned Notion endpoints, independent of user input and callback request headers."""

ORIGIN = "https://mcp.notion.com"
RESOURCE = ORIGIN + "/mcp"
METADATA = ORIGIN + "/.well-known/oauth-authorization-server"
PROTECTED = ORIGIN + "/.well-known/oauth-protected-resource/mcp"
PROTOCOL = "2025-06-18"
CLIENT_NAME = "actus-notion"

TOOLS = {
    "search": "notion-search",
    "fetch": "notion-fetch",
    "get_users": "notion-get-users",
    "get_teams": "notion-get-teams",
    "get_comments": "notion-get-comments",
    "query_database_view": "notion-query-data-sources",
    "get_async_task": "notion-get-async-task",
    "create_page": "notion-create-pages",
    "update_page": "notion-update-page",
    "create_comment": "notion-create-comment",
    "move_pages": "notion-move-pages",
    "duplicate_page": "notion-duplicate-page",
}
