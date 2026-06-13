#!/usr/bin/env python3
"""Chinese localization script for agentsview."""
import os
import glob
import re

REPO = "/Users/mac/agentsview"

# Comprehensive English -> Chinese translation map
# Ordered by specificity (longer strings first) to avoid partial matches
REPLACEMENTS = [
    # App.svelte
    ("Authentication Required", "需要身份验证"),
    ("This server requires an auth token to access. Enter the token shown on the server's console or settings page.", "此服务器需要身份验证令牌才能访问。输入服务器控制台或设置页面上显示的令牌。"),
    ("Paste auth token", "粘贴身份验证令牌"),
    ("Authenticate", "验证"),
    ("Disconnect and reset", "断开并重置"),
    ("Session deleted", "会话已删除"),
    ("Undo", "撤销"),

    # StatusBar
    ("sessions", "个会话"),
    ("messages", "条消息"),
    ("projects", "个项目"),
    ("remote server unreachable", "远程服务器无法连接"),
    ("Can't reach the remote server. Open settings to check the URL, token, or disconnect.", "无法连接远程服务器。打开设置检查 URL、令牌或断开连接。"),
    ("sync not ready", "同步未就绪"),
    ("update available", "有可用更新"),
    ("A new version is available:", "有新版本可用："),
    ("version mismatch - reload", "版本不匹配 - 重新加载"),
    ("Frontend and backend versions differ. Click to reload.", "前端和后端版本不一致。点击重新加载。"),
    ("Syncing", "同步中"),
    ("Scanning", "正在扫描"),
    ("synced", "已同步"),
    ("Zoom out", "缩小"),
    ("Reset zoom", "重置缩放"),
    ("Zoom in", "放大"),

    # AppHeader
    ("Toggle sidebar", "切换侧边栏"),
    ("Home", "首页"),
    ("Sessions", "会话"),
    ("Token Usage", "Token 用量"),
    ("Usage", "用量"),
    ("More navigation", "更多导航"),
    ("More", "更多"),
    ("Trends", "趋势"),
    ("Pinned", "已固定"),
    ("Insights", "洞察"),
    ("Trash", "回收站"),
    ("Search sessions...", "搜索会话..."),
    ("Search sessions", "搜索会话"),
    ("Normal transcript — show all messages", "普通模式 — 显示所有消息"),
    ("Normal transcript mode", "普通模式"),
    ("Normal", "普通"),
    ("Focused transcript — user prompts and final answers only", "聚焦模式 — 仅显示用户提示和最终回答"),
    ("Focused transcript mode", "聚焦模式"),
    ("Focused", "聚焦"),
    ("Filter block types", "过滤块类型"),
    ("Block Visibility", "块可见性"),
    ("User messages", "用户消息"),
    ("Assistant text", "助手文本"),
    ("Thinking blocks", "思考块"),
    ("Tool calls", "工具调用"),
    ("Code blocks", "代码块"),
    ("Show all", "显示全部"),
    ("Follow latest messages", "跟随最新消息"),
    ("Toggle sort order", "切换排序顺序"),
    ("Cycle layout: default", "切换布局：默认"),
    ("Cycle layout: compact", "切换布局：紧凑"),
    ("Cycle layout: stream", "切换布局：流式"),
    ("Cycle message layout", "切换消息布局"),
    ("Export session options", "导出会话选项"),
    ("Export session", "导出会话"),
    ("Download HTML export", "下载 HTML 导出"),
    ("Copied markdown link", "已复制 Markdown 链接"),
    ("Copy markdown export link", "复制 Markdown 导出链接"),
    ("Copy source file path", "复制源文件路径"),
    ("Publish to Gist", "发布到 Gist"),
    ("Publish public Gist", "发布公开 Gist"),
    ("Publish secret Gist", "发布私密 Gist"),
    ("More actions", "更多操作"),
    ("Refresh data", "刷新数据"),
    ("Sync sessions", "同步会话"),
    ("Import unavailable in read-only mode", "只读模式下无法导入"),
    ("Import conversations", "导入对话"),
    ("Import", "导入"),
    ("Toggle theme", "切换主题"),
    ("Settings", "设置"),
    ("Keyboard shortcuts", "键盘快捷键"),
    ("Layout: default", "布局：默认"),
    ("Layout: compact", "布局：紧凑"),
    ("Layout: stream", "布局：流式"),
    ("Publish to Gist (p)", "发布到 Gist (p)"),

    # ThreeColumnLayout
    ("Close sidebar", "关闭侧边栏"),
    ("Resize sidebar", "调整侧边栏宽度"),

    # SessionBreadcrumb
    ("Back to sessions", "返回会话列表"),
    ("Session health", "会话健康度"),
    ("Resume session in terminal", "在终端中恢复会话"),
    ("Session actions", "会话操作"),
    ("Resume session", "恢复会话"),
    ("Resume", "恢复"),
    ("Open", "打开"),
    ("Default terminal", "默认终端"),
    ("Copy command", "复制命令"),
    ("Copy directory path", "复制目录路径"),
    ("Open in", "在...中打开"),
    ("Claude Desktop", "Claude Desktop"),
    ("Rename", "重命名"),
    ("Delete", "删除"),
    ("Copy session ID", "复制会话 ID"),
    ("Copied!", "已复制！"),
    ("Copy link to session", "复制会话链接"),
    ("Hide session analysis", "隐藏会话分析"),
    ("Show session analysis", "显示会话分析"),
    ("Find in session", "在会话中查找"),
    ("Command copied!", "命令已复制！"),
    ("Failed", "失败"),
    ("Not supported", "不支持"),
    ("No path available", "路径不可用"),
    ("Path copied!", "路径已复制！"),
    ("Opened in", "已在...中打开"),
    ("Resumed in", "已在...中恢复"),
    ("Failed to open", "打开失败"),
    ("Estimated session cost", "预估会话费用"),
    ("Failed to save token", "保存令牌失败"),

    # SessionBreadcrumb actions menu
    ("Session actions", "会话操作"),
    ("Copy resume command", "复制恢复命令"),

    # ConfirmDeleteModal
    ("Delete Session", "删除会话"),
    ("Close delete confirmation", "关闭删除确认"),
    ("Move **{name}** to trash?", "将 **{name}** 移到回收站？"),
    ("Move", "移动"),
    ("to trash?", "到回收站？"),
    ("You can restore it later from the Trash page.", "您可以稍后从回收站页面恢复它。"),
    ("Cancel", "取消"),
    ("Deleting...", "删除中..."),
    ("Move to Trash", "移到回收站"),

    # ResyncModal
    ("Full Resync", "完全重新同步"),
    ("Close resync dialog", "关闭重新同步对话框"),
    ("Re-parse all session files from scratch. Existing sessions will be updated in place \u2014 no data is deleted. Use this after upgrading or when sessions appear incorrect.", "从头重新解析所有会话文件。现有会话将原地更新 — 不会删除任何数据。升级后或会话显示异常时使用。"),
    ("Start Full Resync", "开始完全重新同步"),
    ("Preparing...", "准备中..."),
    ("Syncing", "同步中"),
    ("sessions...", "个会话..."),
    ("Sessions synced:", "已同步会话："),
    ("Failed:", "失败："),
    ("Close", "关闭"),
    ("Retry", "重试"),
    ("Full resync is unavailable for read-only backends.", "只读后端不支持完全重新同步。"),
    ("A sync is already in progress.", "同步已在进行中。"),

    # PublishModal
    ("Publish to public GitHub Gist", "发布到公开 GitHub Gist"),
    ("Publish to secret GitHub Gist", "发布到私密 GitHub Gist"),
    ("Close publish dialog", "关闭发布对话框"),
    ("Enter a GitHub personal access token with the", "输入具有"),
    ("scope.", "范围的 GitHub 个人访问令牌。"),
    ("Create token on GitHub", "在 GitHub 上创建令牌"),
    ("Save & Publish", "保存并发布"),
    ("Creating public GitHub Gist...", "正在创建公开 GitHub Gist..."),
    ("Creating secret GitHub Gist...", "正在创建私密 GitHub Gist..."),
    ("View URL", "查看 URL"),
    ("Gist URL", "Gist URL"),
    ("Copy", "复制"),
    ("Open in Browser", "在浏览器中打开"),
    ("No session selected", "未选择会话"),
    ("Publish failed", "发布失败"),

    # UpdateModal
    ("Software Update", "软件更新"),
    ("Close update dialog", "关闭更新对话框"),
    ("You are running", "您正在运行"),
    ("unknown", "未知"),
    ("Run", "运行"),
    ("on the command line to install.", "在命令行上安装。"),
    ("You're running the latest version", "您正在运行最新版本"),
    ("Close", "关闭"),

    # AboutModal
    ("Author", "作者"),
    ("Version", "版本"),
    ("Commit", "提交"),
    ("Build date", "构建日期"),
    ("Close about dialog", "关闭关于对话框"),
    ("Local viewer for AI agent sessions", "AI 代理会话本地查看器"),

    # ShortcutsModal
    ("Keyboard Shortcuts", "键盘快捷键"),
    ("Close shortcuts", "关闭快捷键"),
    ("Open command palette", "打开命令面板"),
    ("Find in session", "在会话中查找"),
    ("Close palette / modal / find", "关闭面板/模态框/查找"),
    ("Next message", "下一条消息"),
    ("Previous message", "上一条消息"),
    ("Next session", "下一个会话"),
    ("Previous session", "上一个会话"),
    ("Toggle sort order", "切换排序顺序"),
    ("Cycle message layout", "切换消息布局"),
    ("Trigger sync", "触发同步"),
    ("Star / unstar session", "标记/取消标记会话"),
    ("Export session", "导出会话"),
    ("Publish to Gist", "发布到 Gist"),
    ("Copy resume command", "复制恢复命令"),
    ("Delete session", "删除会话"),
    ("Show this modal", "显示此模态框"),
    ("Zoom in", "放大"),
    ("Zoom out", "缩小"),
    ("Reset zoom", "重置缩放"),

    # CommandPalette
    ("Search sessions and messages...", "搜索会话和消息..."),
    ("Searching...", "搜索中..."),
    ("No results", "无结果"),
    ("Relevance", "相关度"),
    ("Recency", "时间"),
    ("Recent Sessions", "最近会话"),

    # SessionFilterControl
    ("Filter sessions", "过滤会话"),
    ("Agent", "代理"),
    ("Machine", "机器"),
    ("All agents", "所有代理"),
    ("No match", "无匹配"),
    ("No agents", "无代理"),
    ("No machines", "无机器"),
    ("Search agents...", "搜索代理..."),
    ("Search machines...", "搜索机器..."),
    ("Clear filters", "清除过滤"),
    ("Starred only", "仅星标"),
    ("Min Prompts", "最少提示数"),

    # SessionActiveFilters
    ("Clear", "清除"),

    # MessageContent
    ("Copy message", "复制消息"),
    ("Copied message", "消息已复制"),
    ("Pin message", "固定消息"),
    ("Unpin message", "取消固定消息"),
    ("Unpinned", "已取消固定"),
    ("Pinned", "已固定"),

    # SessionFindBar
    ("Find in session...", "在会话中查找..."),
    ("Previous match", "上一个匹配"),
    ("Next match", "下一个匹配"),
    ("No results", "无结果"),
    ("Search query", "搜索查询"),
    ("Close", "关闭"),

    # CodeBlock
    ("Copy code block", "复制代码块"),
    ("Copied code block", "代码块已复制"),
    ("Copy code", "复制代码"),
    ("Copied!", "已复制！"),

    # ToolCallGroup
    ("Copy tool calls", "复制工具调用"),
    ("Copied tool calls", "工具调用已复制"),

    # SessionVitals
    ("Close session analysis", "关闭会话分析"),
    ("Jump to call", "跳转到调用"),

    # SystemBoundaryCard
    ("Session continuation", "会话继续"),
    ("Session resume", "会话恢复"),
    ("Request interrupted", "请求中断"),
    ("Task notification", "任务通知"),
    ("Stop hook feedback", "停止钩子反馈"),
    ("Show content", "显示内容"),
    ("System boundary", "系统边界"),

    # SettingsPage
    ("Loading settings...", "正在加载设置..."),
    ("Authentication Required", "需要身份验证"),

    # AppearanceSettings
    ("Appearance", "外观"),
    ("Theme, layout, and block visibility preferences.", "主题、布局和块可见性偏好。"),
    ("Theme", "主题"),
    ("Light", "浅色"),
    ("Dark", "深色"),
    ("Message layout", "消息布局"),
    ("Default", "默认"),
    ("Compact", "紧凑"),
    ("Stream", "流式"),
    ("Block visibility", "块可见性"),

    # AgentDirSettings
    ("Agent Directories", "代理目录"),
    ("Directories scanned for session data...", "扫描会话数据的目录..."),
    ("Not configured", "未配置"),

    # TerminalSettings
    ("Terminal", "终端"),
    ("Configure how sessions are resumed in your terminal.", "配置如何在终端中恢复会话。"),
    ("Launch mode", "启动模式"),
    ("Auto-detect", "自动检测"),
    ("Custom", "自定义"),
    ("Clipboard only", "仅剪贴板"),
    ("Terminal binary", "终端二进制文件"),
    ("Arguments", "参数"),
    ("Saving...", "保存中..."),
    ("Save", "保存"),

    # GithubSettings
    ("GitHub Integration", "GitHub 集成"),
    ("Token used for publishing sessions as GitHub Gists.", "用于将会话发布为 GitHub Gist 的令牌。"),
    ("Status", "状态"),
    ("Configured", "已配置"),
    ("Not configured", "未配置"),
    ("Save token", "保存令牌"),
    ("GitHub token saved.", "GitHub 令牌已保存。"),

    # RemoteSettings
    ("Remote Access", "远程访问"),
    ("Enabled", "已启用"),
    ("Disabled", "已禁用"),
    ("Note: Toggling auth requires a server restart...", "注意：切换身份验证需要重启服务器..."),
    ("Auth Token", "身份验证令牌"),
    ("Copied", "已复制"),
    ("Server", "服务器"),
    ("Listening on all interfaces...", "正在监听所有接口..."),
    ("Remote Connection", "远程连接"),
    ("Connect to Remote Server", "连接到远程服务器"),
    ("Connected to", "已连接到"),
    ("Disconnect", "断开连接"),
    ("Server URL", "服务器 URL"),
    ("Test Connection", "测试连接"),
    ("Testing...", "测试中..."),
    ("Connect", "连接"),

    # WorktreeMappingSettings
    ("Worktree mappings", "工作树映射"),
    ("Map worktree path prefixes to canonical projects on this machine.", "将工作树路径前缀映射到此机器上的规范项目。"),
    ("Worktree mappings are available in local mode only.", "工作树映射仅在本地模式下可用。"),
    ("Loading mappings...", "正在加载映射..."),
    ("No worktree mappings configured.", "未配置工作树映射。"),
    ("Path prefix", "路径前缀"),
    ("Project", "项目"),
    ("On", "开"),
    ("Off", "关"),
    ("Edit", "编辑"),
    ("Delete", "删除"),
    ("Add mapping", "添加映射"),
    ("Save mapping", "保存映射"),
    ("Apply mappings", "应用映射"),
    ("Applying...", "正在应用..."),

    # AnalyticsPage
    ("Refresh analytics", "刷新分析"),

    # UsagePage
    ("Refresh", "刷新"),
    ("Refresh usage data", "刷新用量数据"),

    # General / Common
    ("No data for this period", "此期间无数据"),
    ("No data", "无数据"),
    ("No sessions in range", "范围内无会话"),
    ("No sessions found.", "未找到会话。"),
    ("No projects found.", "未找到项目。"),
    ("No activity data", "无活动数据"),
    ("No breakdown data", "无细分数据"),
    ("No tool usage data", "无工具使用数据"),
    ("No trend data", "无趋势数据"),
    ("No project data", "无项目数据"),
    ("No token data", "无令牌数据"),
    ("No pinned messages for this project", "此项目无固定消息"),
    ("Try selecting a different project...", "尝试选择其他项目..."),
    ("No pinned messages", "无固定消息"),
    ("Pin messages from any session...", "从任何会话固定消息..."),
    ("Go to message", "跳转到消息"),
    ("Unpin", "取消固定"),
    ("Collapse", "折叠"),
    ("Expand", "展开"),
    ("Empty Trash", "清空回收站"),
    ("Emptying...", "清空中..."),
    ("Deleted sessions are kept until...", "已删除的会话会保留直到..."),
    ("Loading trash...", "正在加载回收站..."),
    ("Trash is empty", "回收站为空"),
    ("Deleted sessions will appear here.", "已删除的会话将显示在此处。"),
    ("Restore", "恢复"),
    ("Delete Forever", "永久删除"),
    ("Restore session", "恢复会话"),
    ("Permanently delete", "永久删除"),
    ("deleted", "已删除"),
    ("Star session", "标记星标"),
    ("Unstar session", "取消星标"),

    # CopyButton
    ("Copy", "复制"),
    ("Copied", "已复制"),

    # DateRangeSelector
    ("Last 7 days", "最近 7 天"),
    ("Last 30 days", "最近 30 天"),
    ("From", "从"),
    ("To", "到"),

    # InsightsPage
    ("Daily Activity", "每日活动"),
    ("Date Range Activity", "日期范围活动"),
    ("Agent Analysis", "代理分析"),
    ("Prompt", "提示"),
    ("Hide", "隐藏"),
    ("Generate", "生成"),
    ("Hide prompt", "隐藏提示"),
    ("Add custom prompt", "添加自定义提示"),
    ("Steer the insight with additional context...", "用额外上下文引导洞察..."),
    ("Read-only remote mode cannot save generated insights.", "只读远程模式无法保存生成的洞察。"),
    ("Tasks", "任务"),
    ("Stop all", "全部停止"),
    ("Completed", "已完成"),
    ("Error", "错误"),
    ("Generating", "生成中"),
    ("Execution Log", "执行日志"),
    ("lines", "行"),
    ("Waiting for", "正在等待"),
    ("Generating insight...", "正在生成洞察..."),
    ("Select an insight to view", "选择要查看的洞察"),
    ("Generate an insight to get started", "生成一个洞察以开始"),
    ("Delete this insight", "删除此洞察"),
    ("Dismiss", "忽略"),
    ("global", "全局"),
    ("Loading...", "加载中..."),
    ("Unavailable in read-only remote mode", "只读远程模式下不可用"),

    # SessionList groups
    ("Starred", "星标"),

    # PinnedPage
    ("Pinned Messages", "固定消息"),
    ("Loading pins...", "正在加载固定消息..."),

    # TrashPage
    ("ago", "前"),
    ("just now", "刚刚"),

    # dropdown filter
    ("Search...", "搜索..."),

    # Bulk backup button states etc
    ("Filter to unclean sessions", "过滤到未清理的会话"),

    # TopSessionsTable
    ("No sessions in range", "范围内无会话"),

    # Publish modal token
    ("ghp_...", "ghp_..."),

    # SettingsSection
    ("Loading...", "加载中..."),
]

# Specific multiline or complex replacements for App.svelte
COMPLEX_REPLACEMENTS = [
    # In ConfirmDeleteModal
    ("this session", "此会话"),
]

def replace_in_file(filepath):
    """Replace English strings with Chinese in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    for eng, chn in REPLACEMENTS:
        content = content.replace(eng, chn)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {os.path.relpath(filepath, REPO)}")
        return True
    return False

def main():
    print("=" * 60)
    print("agentsview 中文汉化")
    print("=" * 60)

    # Frontend Svelte components
    svelte_files = glob.glob(os.path.join(REPO, "frontend/src/**/*.svelte"), recursive=True)
    print(f"\n[前端组件] 共 {len(svelte_files)} 个文件")
    count = 0
    for f in svelte_files:
        if replace_in_file(f):
            count += 1
    print(f"  修改了 {count} 个文件")

    # Frontend utility files
    util_files = [
        "frontend/src/lib/utils/agents.ts",
        "frontend/src/lib/utils/format.ts",
        "frontend/src/lib/utils/duration.ts",
        "frontend/src/lib/utils/toolDisplay.ts",
        "frontend/src/lib/utils/keyboard.ts",
        "frontend/src/lib/utils/grade.ts",
        "frontend/src/lib/utils/resume.ts",
    ]
    print(f"\n[工具文件]")
    for f in util_files:
        fp = os.path.join(REPO, f)
        if os.path.exists(fp):
            replace_in_file(fp)

    # index.html
    print(f"\n[入口文件]")
    idx = os.path.join(REPO, "frontend/index.html")
    with open(idx, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('<html lang="en">', '<html lang="zh-CN">')
    c = c.replace('<title>AgentsView</title>', '<title>AgentsView - AI 代理会话查看器</title>')
    with open(idx, 'w', encoding='utf-8') as f:
        f.write(c)
    print("  ✓ frontend/index.html")

    # App.svelte - brand name stays
    app_svelte = os.path.join(REPO, "frontend/src/App.svelte")
    with open(app_svelte, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace(
        '<html lang="en">' if '<html lang="en">' in c else '',
        ''
    )
    # Also fix the "this session" in delete confirmation
    c = c.replace('return truncate(raw, 60);', 'return truncate(raw, 60);')
    with open(app_svelte, 'w', encoding='utf-8') as f:
        f.write(c)

    # Go CLI files (cmd/agentsview/*.go)
    go_main = os.path.join(REPO, "cmd/agentsview/main.go")
    print(f"\n[Go CLI 文件]")
    go_files = glob.glob(os.path.join(REPO, "cmd/agentsview/*.go"))
    go_count = 0
    for f in go_files:
        # Skip test files
        if f.endswith('_test.go'):
            continue
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
        original = content

        # CLI-specific translations
        content = content.replace('"Running initial sync..."', '"正在运行初始同步..."')
        content = content.replace('"Data version changed, running full resync..."', '"数据版本已更改，正在运行完全重新同步..."')
        content = content.replace('"fatal:"', '"致命错误："')
        content = content.replace('"warning:"', '"警告："')
        content = content.replace('"Auth enabled. Token:..."', '"身份验证已启用。令牌：..."')
        content = content.replace('"Database:"', '"数据库："')
        content = content.replace('"Press Ctrl+C to stop."', '"按 Ctrl+C 停止。"')
        content = content.replace('"(no sessions)"', '（无会话）')
        content = content.replace('"(no matches)"', '（无匹配）')
        content = content.replace('"More results:"', '"更多结果："')
        content = content.replace('"TOTAL"', '"总计"')
        content = content.replace('"today"', '"今天"')
        content = content.replace('"Totals"', '"总计"')
        content = content.replace('"Archetypes"', '"类型"')
        content = content.replace('"Session shape (means)"', '"会话形状（均值）"')
        content = content.replace('"Velocity"', '"速度"')
        content = content.replace('"(no sessions in window)"', '（窗口内无会话）')
        content = content.replace('"Dry run: no changes made."', '"试运行：未做任何更改。"')
        content = content.replace('"Aborted."', '"已中止。"')
        content = content.replace('"By project:"', '"按项目："')
        content = content.replace('"Up to date."', '"已是最新。"')
        content = content.replace('"Update cancelled."', '"更新已取消。"')
        content = content.replace('"No sessions found."', '"未找到会话。"')
        content = content.replace('"Health"', '"健康度"')
        content = content.replace('"Signals"', '"信号"')
        content = content.replace('"No findings"', '"未发现"')
        content = content.replace('"synced:"', '"已同步："')
        content = content.replace('"No projects found."', '"未找到项目。"')
        content = content.replace('"PROJECT"', '"项目"')
        content = content.replace('"SESSIONS"', '"会话数"')
        content = content.replace('"Opening DuckDB mirror..."', '"正在打开 DuckDB 镜像..."')
        content = content.replace('"Preparing DuckDB schema..."', '"正在准备 DuckDB 架构..."')
        content = content.replace('"Starting DuckDB push..."', '"正在启动 DuckDB 推送..."')

        # Stats labels
        content = content.replace('"Application"', '"应用"')
        content = content.replace('"Version"', '"版本"')
        content = content.replace('"Commit"', '"提交"')
        content = content.replace('"Build time"', '"构建时间"')

        # Service management
        content = content.replace('"Service installed and started."', '"服务已安装并启动。"')
        content = content.replace('"Service stopped and removed."', '"服务已停止并移除。"')

        # Import
        content = content.replace('"Usage: "', '"用法："')

        # Usage - ORDINAL HEADER
        content = content.replace('"ORDINAL\\tTIMESTAMP\\tTOOL\\tCATEGORY"', '"序号\\t时间戳\\t工具\\t类别"')

        if content != original:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(content)
            print(f"  ✓ {os.path.relpath(f, REPO)}")
            go_count += 1
    print(f"  修改了 {go_count} 个 Go 文件")

    # Update module (internal/update/update.go)
    update_file = os.path.join(REPO, "internal/update/update.go")
    if os.path.exists(update_file):
        with open(update_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('"Verifying and installing..."', '"正在验证并安装..."')
        content = content.replace('"Update complete."', '"更新完成。"')
        with open(update_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✓ internal/update/update.go")

    # README.md - Translate header
    readme = os.path.join(REPO, "README.md")
    print(f"\n[文档]")
    with open(readme, 'r', encoding='utf-8') as f:
        c = f.read()
    # We'll just translate the title and top section
    c = c.replace(
        "# agentsview\n\nBrowse, search, and track costs across all your AI coding agents. One binary, no accounts, everything local.",
        "# agentsview\n\n浏览、搜索和跟踪所有 AI 编码代理的使用成本。单个二进制文件，无需账户，全部在本地运行。"
    )
    # Translate section headers
    c = c.replace("## Install", "## 安装")
    c = c.replace("## Quick Start", "## 快速开始")
    c = c.replace("## Remote / forwarded access", "## 远程/转发访问")
    c = c.replace("## Docker", "## Docker")
    c = c.replace("## Token Usage and Cost Tracking", "## Token 用量与费用跟踪")
    c = c.replace("## Per-Session Details", "## 按会话详情")
    c = c.replace("## Session Stats", "## 会话统计")
    c = c.replace("## Session Browser", "## 会话浏览器")
    c = c.replace("## Supported Agents", "## 支持的代理")
    c = c.replace("## PostgreSQL Sync", "## PostgreSQL 同步")
    c = c.replace("## DuckDB Mirror and Quack", "## DuckDB 镜像与 Quack")
    c = c.replace("## Privacy", "## 隐私")
    c = c.replace("## Documentation", "## 文档")
    c = c.replace("## Development", "## 开发")
    c = c.replace("## Project Layout", "## 项目结构")
    c = c.replace("## Acknowledgements", "## 致谢")
    c = c.replace("## License", "## 许可证")
    c = c.replace("## Quick Start", "## 快速开始")
    c = c.replace("Full docs at", "完整文档请访问")
    c = c.replace("- **Full-text search** across all message content (FTS5)", "- **全文搜索**所有消息内容（FTS5）")
    c = c.replace("- **Token usage and cost dashboard** -- per-session and per-model cost", "- **Token 用量和费用面板** -- 按会话和按模型的费用")
    c = c.replace("  breakdowns, daily spend charts, all in the web UI", "  细分、每日支出图表，全部在 Web 界面中")
    c = c.replace("- **Analytics dashboard** -- activity heatmaps, tool usage, velocity metrics,", "- **分析面板** -- 活动热力图、工具使用、速度指标、")
    c = c.replace("  project breakdowns", "  项目细分")
    c = c.replace("- **Live updates** via SSE as active sessions receive new messages", "- 通过 SSE **实时更新**活跃会话的新消息")
    c = c.replace("- **Keyboard-first** navigation (`j`/`k`/`[`/`]`, `Cmd+K` search, `?` for all", "- **键盘优先**导航（`j`/`k`/`[`/`]`、`Cmd+K`搜索、`?`查看所有")
    c = c.replace("  shortcuts)", "  快捷键）")
    c = c.replace("- **Export** sessions as HTML or publish to GitHub Gist", "- **导出**会话为 HTML 或发布到 GitHub Gist")
    with open(readme, 'w', encoding='utf-8') as f:
        f.write(c)
    print("  ✓ README.md")

    # Tauri config & Rust files
    print(f"\n[桌面端]")
    tauri_conf = os.path.join(REPO, "desktop/src-tauri/tauri.conf.json")
    if os.path.exists(tauri_conf):
        with open(tauri_conf, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('"productName": "AgentsView"', '"productName": "AgentsView"')
        with open(tauri_conf, 'w', encoding='utf-8') as f:
            f.write(c)
        print("  ✓ tauri.conf.json (已检查)")

    lib_rs = os.path.join(REPO, "desktop/src-tauri/src/lib.rs")
    if os.path.exists(lib_rs):
        with open(lib_rs, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('"Check for Updates..."', '"检查更新..."')
        c = c.replace('"About AgentsView"', '"关于 AgentsView"')
        c = c.replace('"An update check is already in progress."', '"更新检查已在进行中。"')
        c = c.replace('"Could not check for updates..."', '"无法检查更新..."')
        c = c.replace('"You\'re running the latest version."', '"您已在运行最新版本。"')
        c = c.replace('"Update Available"', '"有可用更新"')
        c = c.replace('"Update Failed"', '"更新失败"')
        c = c.replace('"Update Complete"', '"更新完成"')
        c = c.replace('"Update installed. Restart now to apply?"', '"更新已安装。立即重启以应用？"')
        # Menu items
        c = c.replace('"File"', '"文件"')
        c = c.replace('"Edit"', '"编辑"')
        c = c.replace('"Help"', '"帮助"')
        c = c.replace('"Quit"', '"退出"')
        c = c.replace('"Cut"', '"剪切"')
        c = c.replace('"Copy"', '"复制"')
        c = c.replace('"Paste"', '"粘贴"')
        c = c.replace('"Select All"', '"全选"')
        with open(lib_rs, 'w', encoding='utf-8') as f:
            f.write(c)
        print("  ✓ lib.rs")

    # Fix the "N" and "F" letter abbreviations in AppHeader
    app_header = os.path.join(REPO, "frontend/src/lib/components/layout/AppHeader.svelte")
    with open(app_header, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('content: "N";', 'content: "普";')
    c = c.replace('content: "F";', 'content: "聚";')
    with open(app_header, 'w', encoding='utf-8') as f:
        f.write(c)
    print("  ✓ AppHeader.svelte (缩写修复)")

    # Fix "Copied!" in SessionBreadcrumb - it gets overridden
    sb_path = os.path.join(REPO, "frontend/src/lib/components/layout/SessionBreadcrumb.svelte")
    with open(sb_path, 'r', encoding='utf-8') as f:
        c = f.read()
    # The hardcoded "Copied!" is near the copiedSessionId check  
    c = c.replace('? "Copied!"', '? "已复制!"')
    with open(sb_path, 'w', encoding='utf-8') as f:
        f.write(c)

    # Fix "this session" text
    confirm_path = os.path.join(REPO, "frontend/src/lib/components/modals/ConfirmDeleteModal.svelte")
    with open(confirm_path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('"this session"', '"此会话"')
    with open(confirm_path, 'w', encoding='utf-8') as f:
        f.write(c)

    print(f"\n{'=' * 60}")
    print("汉化完成！")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
