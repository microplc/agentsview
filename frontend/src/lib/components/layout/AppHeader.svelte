<script lang="ts">
  import {
    ArrowDownIcon,
    ArrowDownWideNarrowIcon,
    ArrowUpNarrowWideIcon,
    CheckIcon,
    CloudUploadIcon,
    复制Icon,
    DownloadIcon,
    EllipsisIcon,
    FunnelIcon,
    GlobeIcon,
    Grid2x2Icon,
    LayoutGridIcon,
    LayoutListIcon,
    LinkIcon,
    List折叠Icon,
    LockIcon,
    LogsIcon,
    MenuIcon,
    MoonIcon,
    更多HorizontalIcon,
    刷新CwIcon,
    SearchIcon,
    设置Icon,
    SunIcon,
    UploadIcon,
  } from "../../icons.js";
  import {
    ui,
    ALL_BLOCK_TYPES,
    type BlockType,
    type TranscriptMode,
  } from "../../stores/ui.svelte.js";
  import { 个会话 } from "../../stores/个会话.svelte.js";
  import { sync } from "../../stores/sync.svelte.js";
  import { router } from "../../stores/router.svelte.js";
  import {
    downloadExport,
    getMarkdownExportUrl,
  } from "../../api/client.js";
  import { copy到Clipboard } from "../../utils/clipboard.js";
  import 项目Typeahead from "./项目Typeahead.svelte";
  import 导入Modal from "../import/导入Modal.svelte";

  const isMac = navigator.platform.toUpperCase().includes("MAC");
  const modKey = isMac ? "Cmd" : "Ctrl";

  let show导入Modal = $state(false);
  let showBlockFilter = $state(false);
  let showExportMenu = $state(false);
  let showPublishMenu = $state(false);
  let showOverflow = $state(false);
  let copiedMarkdownLink = $state(false);
  let copiedMarkdownLinkTimer:
    | ReturnType<typeof setTimeout>
    | undefined;
  let more打开 = $state(false);
  let filterBtnRef: HTMLButtonElement | undefined =
    $state(undefined);
  let filterDropRef: HTMLDivElement | undefined =
    $state(undefined);
  let exportBtnRef: HTMLButtonElement | undefined =
    $state(undefined);
  let exportDropRef: HTMLDivElement | undefined =
    $state(undefined);
  let publishBtnRef: HTMLButtonElement | undefined =
    $state(undefined);
  let publishDropRef: HTMLDivElement | undefined =
    $state(undefined);
  let overflowBtnRef: HTMLButtonElement | undefined =
    $state(undefined);
  let overflowDropRef: HTMLDivElement | undefined =
    $state(undefined);
  let moreBtnRef: HTMLButtonElement | undefined =
    $state(undefined);
  let moreDropRef: HTMLDivElement | undefined =
    $state(undefined);

  const BLOCK_LABELS: Record<BlockType, string> = {
    user: "User 条消息",
    assistant: "助手文本",
    thinking: "思考块",
    tool: "工具调用",
    code: "代码块",
  };

  const BLOCK_COLORS: Record<BlockType, string> = {
    user: "var(--accent-blue)",
    assistant: "var(--accent-purple)",
    thinking: "var(--accent-purple)",
    tool: "var(--accent-amber)",
    code: "var(--text-muted)",
  };

  async function handleExport() {
    if (个会话.activeSessionId) {
      try {
        await downloadExport(个会话.activeSessionId);
      } catch (e) {
        console.error("Export failed:", e);
      }
    }
  }

  async function handle复制MarkdownExportLink() {
    if (!个会话.activeSessionId) return;
    const url = new URL(
      getMarkdownExportUrl(个会话.activeSessionId),
      window.location.origin,
    ).toString();
    const ok = await copy到Clipboard(url);
    if (!ok) return;
    copiedMarkdownLink = true;
    clearTimeout(copiedMarkdownLinkTimer);
    copiedMarkdownLinkTimer = setTimeout(() => {
      copiedMarkdownLink = false;
    }, 1500);
    showExportMenu = false;
    showOverflow = false;
  }

  async function handle复制SourceFilePath() {
    const filePath = 个会话.activeSession?.file_path;
    if (!filePath) return;
    const ok = await copy到Clipboard(filePath);
    if (!ok) return;
    showExportMenu = false;
    showOverflow = false;
  }

  function openPublish(secret: boolean) {
    ui.publishSecret = secret;
    ui.activeModal = "publish";
    showPublishMenu = false;
    showOverflow = false;
  }

  const hasActiveSession = $derived(
    个会话.activeSessionId !== null,
  );
  const activeSessionFilePath = $derived(
    个会话.activeSession?.file_path ?? "",
  );

  // 关闭 block filter dropdown on outside click
  $effect(() => {
    if (!showBlockFilter) return;
    function onClickOutside(e: MouseEvent) {
      const target = e.target as Node;
      if (
        filterBtnRef?.contains(target) ||
        filterDropRef?.contains(target)
      )
        return;
      showBlockFilter = false;
    }
    document.addEventListener("click", onClickOutside, true);
    return () =>
      document.removeEventListener(
        "click",
        onClickOutside,
        true,
      );
  });

  // 关闭 export menu on outside click
  $effect(() => {
    if (!showExportMenu) return;
    function onClickOutside(e: MouseEvent) {
      const target = e.target as Node;
      if (
        exportBtnRef?.contains(target) ||
        exportDropRef?.contains(target)
      )
        return;
      showExportMenu = false;
    }
    document.addEventListener("click", onClickOutside, true);
    return () =>
      document.removeEventListener(
        "click",
        onClickOutside,
        true,
      );
  });

  // 关闭 publish menu on outside click
  $effect(() => {
    if (!showPublishMenu) return;
    function onClickOutside(e: MouseEvent) {
      const target = e.target as Node;
      if (
        publishBtnRef?.contains(target) ||
        publishDropRef?.contains(target)
      )
        return;
      showPublishMenu = false;
    }
    document.addEventListener("click", onClickOutside, true);
    return () =>
      document.removeEventListener(
        "click",
        onClickOutside,
        true,
      );
  });

  // 关闭 overflow dropdown on outside click
  $effect(() => {
    if (!showOverflow) return;
    function onClickOutside(e: MouseEvent) {
      const target = e.target as Node;
      if (
        overflowBtnRef?.contains(target) ||
        overflowDropRef?.contains(target)
      )
        return;
      showOverflow = false;
    }
    document.addEventListener("click", onClickOutside, true);
    return () =>
      document.removeEventListener(
        "click",
        onClickOutside,
        true,
      );
  });

  // 关闭 更多 dropdown on outside click or Escape
  $effect(() => {
    if (!more打开) return;
    function onClickOutside(e: MouseEvent) {
      const target = e.target as Node;
      if (
        moreBtnRef?.contains(target) ||
        moreDropRef?.contains(target)
      )
        return;
      more打开 = false;
    }
    function onKeydown(e: KeyboardEvent) {
      if (e.key === "Escape") more打开 = false;
    }
    document.addEventListener("click", onClickOutside, true);
    document.addEventListener("keydown", onKeydown);
    return () => {
      document.removeEventListener(
        "click",
        onClickOutside,
        true,
      );
      document.removeEventListener("keydown", onKeydown);
    };
  });
</script>

{#snippet messageLayoutIcon(size: string)}
  {#if ui.messageLayout === "default"}
    <LayoutListIcon {size} strokeWidth="2" aria-hidden="true" />
  {:else if ui.messageLayout === "compact"}
    <List折叠Icon {size} strokeWidth="2" aria-hidden="true" />
  {:else}
    <LogsIcon {size} strokeWidth="2" aria-hidden="true" />
  {/if}
{/snippet}

<header class="header">
  <div class="header-left">
    <button
      class="hamburger"
      onclick={() => {
        if (ui.isMobileViewport && router.route !== "个会话") {
          router.navigate("个会话");
          ui.sidebar打开 = true;
        } else {
          ui.toggleSidebar();
        }
      }}
      title="切换侧边栏 (b)"
      aria-label="切换侧边栏"
    >
      <MenuIcon size="16" strokeWidth="2" aria-hidden="true" />
    </button>
    <button
      class="header-home"
      onclick={() => router.navigate("个会话")}
      title="首页"
    >
      <svg class="header-logo" width="18" height="18" viewBox="0 0 32 32" aria-hidden="true">
        <rect width="32" height="32" rx="6" fill="var(--accent-blue, #3b82f6)"/>
        <rect x="13" y="10" width="6" height="16" rx="2" fill="var(--bg-surface, #fff)"/>
        <rect x="11" y="5" width="10" height="7" rx="2" fill="var(--bg-surface, #fff)"/>
        <circle cx="18" cy="8.5" r="2" fill="var(--accent-blue, #3b82f6)"/>
        <circle cx="18" cy="8.5" r="1" fill="#1d4ed8"/>
      </svg>
      <span class="header-title">代理sView</span>
    </button>

    <项目Typeahead
      个项目={个会话.个项目}
      value={个会话.filters.project}
      onselect={(v) => 个会话.set项目Filter(v)}
    />

    <button
      class="nav-btn"
      class:active={router.route === "个会话"}
      onclick={() => router.navigate("个会话")}
      title="会话"
      aria-label="会话"
    >
      <LayoutGridIcon size="12" strokeWidth="2" aria-hidden="true" />
      <span class="nav-label">会话</span>
    </button>

    <button
      class="nav-btn"
      class:active={router.route === "usage"}
      onclick={() => router.navigate("usage")}
      title="到ken 用量"
      aria-label="用量"
    >
      <Grid2x2Icon size="12" strokeWidth="2" aria-hidden="true" />
      <span class="nav-label">用量</span>
    </button>

    <div class="more-wrap">
      <button
        class="nav-btn"
        class:active={router.route === "trends" || router.route === "pinned" || router.route === "insights" || router.route === "trash" || more打开}
        bind:this={moreBtnRef}
        onclick={() => { more打开 = !more打开; }}
        title="更多导航"
        aria-label="更多导航"
        aria-expanded={more打开}
      >
        <EllipsisIcon size="12" strokeWidth="2.4" aria-hidden="true" />
        <span class="nav-label">更多</span>
      </button>
      {#if more打开}
        <div class="more-dropdown" role="menu" bind:this={moreDropRef}>
          <button class="more-item" role="menuitem"
            class:active={router.route === "trends"}
            onclick={() => { router.navigate("trends"); more打开 = false; }}>
            趋势
          </button>
          <button class="more-item" role="menuitem"
            class:active={router.route === "pinned"}
            onclick={() => { router.navigate("pinned"); more打开 = false; }}>
            已固定
          </button>
          <button class="more-item" role="menuitem"
            class:active={router.route === "insights"}
            onclick={() => { router.navigate("insights"); more打开 = false; }}>
            洞察
          </button>
          <button class="more-item" role="menuitem"
            class:active={router.route === "trash"}
            onclick={() => { router.navigate("trash"); more打开 = false; }}>
            回收站
          </button>
        </div>
      {/if}
    </div>
  </div>

  <button
    class="search-hint"
    onclick={() => (ui.activeModal = "commandPalette")}
    title="Search 个会话 ({modKey}+K)"
  >
    <SearchIcon size="12" strokeWidth="2" aria-hidden="true" />
    <span class="search-hint-text">Search 个会话...</span>
    <kbd class="search-hint-kbd">{modKey}+K</kbd>
  </button>

  <div class="header-right">
    {#if hasActiveSession}
      <!-- Transcript controls: mode pills + filter, grouped visually -->
      <div class="transcript-strip">
        <button
          class="pill"
          class:active={ui.transcriptMode === "normal"}
          onclick={() => ui.setTranscriptMode("normal")}
          title="普通 transcript — show all 条消息"
          aria-label="普通模式"
        >
          <span class="pill-label">普通</span>
        </button>
        <button
          class="pill"
          class:active={ui.transcriptMode === "focused"}
          onclick={() => ui.setTranscriptMode("focused")}
          title="聚焦模式 — 仅显示用户提示和最终回答"
          aria-label="聚焦模式"
        >
          <span class="pill-label">聚焦</span>
        </button>

        <span class="strip-divider"></span>

        <div class="filter-wrap">
          <button
            class="pill pill-icon"
            class:filter-active={ui.hasBlockFilters}
            bind:this={filterBtnRef}
            onclick={() => (showBlockFilter = !showBlockFilter)}
            title="过滤块类型"
            aria-label="过滤块类型"
          >
            <FunnelIcon size="12" strokeWidth="2" aria-hidden="true" />
            {#if ui.hasBlockFilters}
              <span class="filter-badge">{ui.hiddenBlockCount}</span>
            {/if}
          </button>

          {#if showBlockFilter}
            <div class="block-filter-dropdown" bind:this={filterDropRef}>
              <div class="block-filter-title">块可见性</div>
              {#each ALL_BLOCK_TYPES as bt}
                {@const visible = ui.isBlockVisible(bt)}
                <button
                  class="block-filter-item"
                  class:active={visible}
                  onclick={() => ui.toggleBlock(bt)}
                >
                  <span
                    class="block-filter-dot"
                    style:background={visible ? BLOCK_COLORS[bt] : "var(--border-muted)"}
                  ></span>
                  <span class="block-filter-label">{BLOCK_LABELS[bt]}</span>
                  <span class="block-filter-check" class:on={visible}>
                    {#if visible}
                      <CheckIcon size="10" strokeWidth="2.4" aria-hidden="true" />
                    {/if}
                  </span>
                </button>
              {/each}
              {#if ui.hasBlockFilters}
                <button
                  class="block-filter-reset"
                  onclick={() => ui.showAllBlocks()}
                >
                  显示全部
                </button>
              {/if}
            </div>
          {/if}
        </div>
      </div>

      <button
        class="header-btn"
        class:active={ui.followLatest}
        onclick={() => ui.toggleFollowLatest()}
        title="Follow latest 条消息"
        aria-label="Follow latest 条消息"
        aria-pressed={ui.followLatest}
      >
        <ArrowDownIcon size="14" strokeWidth="2" aria-hidden="true" />
      </button>

      <button
        class="header-btn"
        onclick={() => ui.toggleSort()}
        title="切换排序顺序 (o)"
        aria-label="切换排序顺序"
      >
        {#if ui.sortNewestFirst}
          <ArrowDownWideNarrowIcon size="14" strokeWidth="2" aria-hidden="true" />
        {:else}
          <ArrowUpNarrowWideIcon size="14" strokeWidth="2" aria-hidden="true" />
        {/if}
      </button>

      <!-- Layout, export, publish: collapse into overflow at narrow widths -->
      <button
        class="header-btn collapsible"
        onclick={() => ui.cycleLayout()}
        title="Cycle layout: {ui.messageLayout} (l)"
        aria-label="切换消息布局"
      >
        {@render messageLayoutIcon("14")}
      </button>

      <div class="export-wrap collapsible">
        <button
          class="header-btn"
          bind:this={exportBtnRef}
          onclick={() => {
            showExportMenu = !showExportMenu;
            showOverflow = false;
          }}
          disabled={!个会话.activeSessionId}
          title="导出会话选项"
          aria-label="导出会话"
          aria-expanded={showExportMenu}
        >
          <CloudUploadIcon size="14" strokeWidth="2" aria-hidden="true" />
        </button>

        {#if showExportMenu}
          <div class="export-dropdown" bind:this={exportDropRef}>
            <button
              class="overflow-item"
              onclick={() => {
                handleExport();
                showExportMenu = false;
              }}
            >
              <CloudUploadIcon size="13" strokeWidth="2" aria-hidden="true" />
              <span>下载 HTML 导出</span>
            </button>
            <button
              class="overflow-item"
              onclick={handle复制MarkdownExportLink}
            >
              {#if copiedMarkdownLink}
                <CheckIcon size="13" strokeWidth="2.4" aria-hidden="true" />
              {:else}
                <LinkIcon size="13" strokeWidth="2" aria-hidden="true" />
              {/if}
              <span>
                {#if copiedMarkdownLink}
                  已复制 Markdown 链接
                {:else}
                  复制 Markdown 导出链接
                {/if}
              </span>
            </button>
            {#if activeSessionFilePath}
              <button
                class="overflow-item"
                onclick={handle复制SourceFilePath}
              >
                <复制Icon size="13" strokeWidth="2" aria-hidden="true" />
                <span>复制源文件路径</span>
              </button>
            {/if}
          </div>
        {/if}
      </div>

      <div class="export-wrap collapsible">
        <button
          class="header-btn"
          bind:this={publishBtnRef}
          onclick={() => {
            showPublishMenu = !showPublishMenu;
            showExportMenu = false;
            showOverflow = false;
          }}
          disabled={!个会话.activeSessionId}
          title="发布到 Gist (p)"
          aria-label="发布到 Gist"
          aria-expanded={showPublishMenu}
        >
          <UploadIcon size="14" strokeWidth="2" aria-hidden="true" />
        </button>

        {#if showPublishMenu}
          <div class="export-dropdown" bind:this={publishDropRef}>
            <button
              class="overflow-item"
              onclick={() => openPublish(false)}
            >
              <GlobeIcon size="13" strokeWidth="2" aria-hidden="true" />
              <span>发布公开 Gist</span>
            </button>
            <button
              class="overflow-item"
              onclick={() => openPublish(true)}
            >
              <LockIcon size="13" strokeWidth="2" aria-hidden="true" />
              <span>发布私密 Gist</span>
            </button>
          </div>
        {/if}
      </div>

      <!-- Overflow menu (visible only at narrow widths) -->
      <div class="overflow-wrap">
        <button
          class="header-btn overflow-btn"
          bind:this={overflowBtnRef}
          onclick={() => (showOverflow = !showOverflow)}
          title="更多 actions"
          aria-label="更多 actions"
        >
          <更多HorizontalIcon size="14" strokeWidth="2.4" aria-hidden="true" />
        </button>

        {#if showOverflow}
          <div class="overflow-dropdown" bind:this={overflowDropRef}>
            <button
              class="overflow-item"
              onclick={() => { ui.cycleLayout(); showOverflow = false; }}
            >
              {@render messageLayoutIcon("13")}
              <span>Layout: {ui.messageLayout}</span>
            </button>
            <button
              class="overflow-item"
              onclick={() => { handleExport(); showOverflow = false; }}
            >
              <CloudUploadIcon size="13" strokeWidth="2" aria-hidden="true" />
              <span>下载 HTML 导出</span>
            </button>
            <button
              class="overflow-item"
              onclick={handle复制MarkdownExportLink}
            >
              {#if copiedMarkdownLink}
                <CheckIcon size="13" strokeWidth="2.4" aria-hidden="true" />
              {:else}
                <LinkIcon size="13" strokeWidth="2" aria-hidden="true" />
              {/if}
              <span>
                {#if copiedMarkdownLink}
                  已复制 Markdown 链接
                {:else}
                  复制 Markdown 导出链接
                {/if}
              </span>
            </button>
            {#if activeSessionFilePath}
              <button
                class="overflow-item"
                onclick={handle复制SourceFilePath}
              >
                <复制Icon size="13" strokeWidth="2" aria-hidden="true" />
                <span>复制源文件路径</span>
              </button>
            {/if}
            <button
              class="overflow-item"
              onclick={() => openPublish(false)}
            >
              <UploadIcon size="13" strokeWidth="2" aria-hidden="true" />
              <span>发布公开 Gist</span>
            </button>
            <button
              class="overflow-item"
              onclick={() => openPublish(true)}
            >
              <LockIcon size="13" strokeWidth="2" aria-hidden="true" />
              <span>发布私密 Gist</span>
            </button>
          </div>
        {/if}
      </div>
    {/if}

    <button
      class="header-btn"
      class:syncing={sync.syncing}
      onclick={() => sync.triggerSync()}
      disabled={sync.syncing}
      title={sync.read开ly ? "刷新数据 (r)" : "Sync 个会话 (r)"}
      aria-label={sync.read开ly ? "刷新数据" : "Sync 个会话"}
    >
      <刷新CwIcon size="14" strokeWidth="2" aria-hidden="true" />
    </button>

    <button
      class="import-btn"
      onclick={() => {
        if (!sync.read开ly) show导入Modal = true;
      }}
      disabled={sync.read开ly}
      title={sync.read开ly
        ? "只读模式下无法导入"
        : "导入对话"}
      aria-label="导入对话"
    >
      <DownloadIcon size="12" strokeWidth="2" aria-hidden="true" />
      <span class="import-label">导入</span>
    </button>

    <span class="header-divider"></span>

    <button
      class="header-btn"
      onclick={() => ui.toggle主题()}
      title="切换主题"
      aria-label="切换主题"
    >
      {#if ui.theme === "light"}
        <MoonIcon size="14" strokeWidth="2" aria-hidden="true" />
      {:else}
        <SunIcon size="14" strokeWidth="2" aria-hidden="true" />
      {/if}
    </button>

    <button
      class="header-btn"
      class:active={router.route === "settings"}
      onclick={() => router.navigate("settings")}
      title="设置"
      aria-label="设置"
    >
      <设置Icon size="14" strokeWidth="2" aria-hidden="true" />
    </button>

    <button
      class="header-btn"
      onclick={() => (ui.activeModal = "shortcuts")}
      title="键盘快捷键 (?)"
      aria-label="键盘快捷键"
    >
      ?
    </button>
  </div>
</header>

<导入Modal
  bind:open={show导入Modal}
  onclose={() => show导入Modal = false}
  onimported={() => {
    个会话.invalidateFilterCaches();
    个会话.load();
  }}
/>

<style>
  .header {
    height: var(--header-height, 40px);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-default);
    flex-shrink: 0;
    gap: 8px;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
  }

  .header-home {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    border-radius: var(--radius-sm);
    padding: 2px 6px 2px 2px;
    transition: background 0.1s;
  }

  .header-home:hover {
    background: var(--bg-surface-hover);
  }

  .header-logo {
    flex-shrink: 0;
  }

  .header-title {
    font-size: 12px;
    font-weight: 650;
    color: var(--text-primary);
    white-space: nowrap;
    letter-spacing: -0.01em;
  }

  .nav-btn {
    height: 26px;
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 0 10px;
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.12s, color 0.12s;
  }

  .nav-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .nav-btn.active {
    color: var(--accent-blue);
    background: color-mix(
      in srgb,
      var(--accent-blue) 8%,
      transparent
    );
  }

  .more-wrap {
    position: relative;
  }

  .more-dropdown {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    min-width: 140px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    display: flex;
    flex-direction: column;
    padding: 4px;
    z-index: 20;
    animation: dropdown-in 0.12s ease-out;
  }

  .more-item {
    padding: 6px 10px;
    font-size: 12px;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    text-align: left;
    background: transparent;
    border: none;
    cursor: pointer;
    transition: background 0.08s, color 0.08s;
  }

  .more-item:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .more-item.active {
    color: var(--text-primary);
    font-weight: 500;
    background: var(--bg-inset);
  }

  .search-hint {
    height: 26px;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 10px;
    background: var(--bg-inset);
    border: 1px solid var(--border-muted);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    font-size: 11px;
    cursor: pointer;
    white-space: nowrap;
    transition: border-color 0.15s, box-shadow 0.15s;
  }

  .search-hint:hover {
    border-color: var(--border-default);
    box-shadow: var(--shadow-sm);
  }

  .search-hint-text {
    color: var(--text-muted);
  }

  .search-hint-kbd {
    font-size: 10px;
    padding: 0 4px;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    background: var(--bg-surface);
    font-family: var(--font-sans);
    line-height: 16px;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 2px;
    flex-shrink: 0;
  }

  /* ── Transcript strip: mode pills + filter ── */
  .transcript-strip {
    display: flex;
    align-items: stretch;
    height: 26px;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    margin-right: 4px;
    flex-shrink: 0;
  }

  .filter-wrap {
    position: relative;
    display: flex;
  }

  .pill {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 9px;
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    background: transparent;
    transition: background 0.1s, color 0.1s;
    white-space: nowrap;
    cursor: pointer;
    border: none;
    border-radius: 0;
  }

  .pill:hover {
    background: var(--bg-surface-hover);
    color: var(--text-secondary);
  }

  .pill.active {
    background: color-mix(
      in srgb,
      var(--accent-blue) 12%,
      transparent
    );
    color: var(--accent-blue);
    font-weight: 600;
  }

  /* Match parent's border-radius on outer edges */
  .pill:first-child {
    border-radius: var(--radius-sm) 0 0 var(--radius-sm);
  }

  .pill-icon {
    padding: 0 7px;
    position: relative;
  }

  .filter-wrap:last-child .pill {
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  }

  .pill.filter-active {
    color: var(--accent-purple);
  }

  .strip-divider {
    width: 1px;
    height: 14px;
    background: var(--border-default);
    flex-shrink: 0;
    align-self: center;
  }

  .filter-badge {
    position: absolute;
    top: 0px;
    right: 0px;
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background: var(--accent-amber);
    color: white;
    font-size: 7px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    pointer-events: none;
  }

  /* ── Block filter dropdown ── */
  .block-filter-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 4px;
    width: 190px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    padding: 6px 0;
    z-index: 100;
    animation: dropdown-in 0.12s ease-out;
    transform-origin: top right;
  }

  @keyframes dropdown-in {
    from {
      opacity: 0;
      transform: scale(0.95) translateY(-2px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  .block-filter-title {
    padding: 4px 12px 6px;
    font-size: 9px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .block-filter-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 5px 12px;
    font-size: 12px;
    color: var(--text-secondary);
    text-align: left;
    transition: background 0.08s;
  }

  .block-filter-item:hover {
    background: var(--bg-surface-hover);
  }

  .block-filter-item:not(.active) {
    opacity: 0.5;
  }

  .block-filter-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
    transition: background 0.1s;
  }

  .block-filter-label {
    flex: 1;
  }

  .block-filter-check {
    width: 14px;
    height: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent-green);
    flex-shrink: 0;
  }

  .block-filter-reset {
    display: block;
    width: calc(100% - 16px);
    margin: 6px 8px 2px;
    padding: 4px 8px;
    font-size: 10px;
    color: var(--text-muted);
    text-align: center;
    border-top: 1px solid var(--border-muted);
    padding-top: 8px;
    transition: color 0.1s;
  }

  .block-filter-reset:hover {
    color: var(--text-primary);
  }

  /* ── Header icon buttons ── */
  .header-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 600;
    transition: background 0.12s, color 0.12s;
    flex-shrink: 0;
  }

  .header-btn:hover:not(:disabled) {
    background: var(--bg-surface-hover);
    color: var(--text-secondary);
  }

  .header-btn:disabled {
    opacity: 0.55;
    cursor: default;
  }

  .header-btn.active {
    color: var(--accent-purple);
  }

  .header-btn.syncing {
    animation: spin 1s linear infinite;
  }

  /* ── 导入 button (icon + label) ── */
  .import-btn {
    height: 26px;
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 0 10px;
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    white-space: nowrap;
    transition: background 0.12s, color 0.12s;
  }

  .import-btn:hover:not(:disabled) {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .import-btn:disabled {
    opacity: 0.55;
    cursor: default;
  }

  .header-divider {
    width: 1px;
    height: 14px;
    background: var(--border-muted);
    margin: 0 2px;
    flex-shrink: 0;
  }

  .export-wrap {
    position: relative;
    display: flex;
  }

  .export-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 4px;
    width: 220px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    padding: 4px 0;
    z-index: 100;
    animation: dropdown-in 0.12s ease-out;
    transform-origin: top right;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .hamburger {
    display: flex;
    width: 28px;
    height: 28px;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    transition: background 0.12s, color 0.12s;
  }

  .hamburger:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  /* ── Overflow menu (narrow viewports) ── */
  .overflow-wrap {
    position: relative;
    display: none;
  }

  .overflow-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 4px;
    width: 180px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    padding: 4px 0;
    z-index: 100;
    animation: dropdown-in 0.12s ease-out;
    transform-origin: top right;
  }

  .overflow-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 6px 12px;
    font-size: 12px;
    color: var(--text-secondary);
    text-align: left;
    transition: background 0.08s;
    white-space: nowrap;
  }

  .overflow-item:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .overflow-item :全局(svg) {
    flex-shrink: 0;
    color: var(--text-muted);
  }

  /* ── Responsive ── */

  /* 1024px: 隐藏 nav button labels + search text/kbd */
  @media (max-width: 1023px) {
    .nav-label,
    .import-label {
      display: none;
    }

    .search-hint-text {
      display: none;
    }

    .search-hint-kbd {
      display: none;
    }

    .hamburger {
      display: flex;
    }
  }

  /* 767px: 隐藏 nav buttons and typeahead */
  @media (max-width: 767px) {
    .header-left .nav-btn,
    .header-left .more-wrap {
      display: none;
    }

    .header-left :全局(.typeahead) {
      display: none;
    }
  }

  /* 699px: 折叠 layout/export/publish into overflow menu */
  @media (max-width: 699px) {
    .collapsible {
      display: none;
    }

    .overflow-wrap {
      display: block;
    }

    .pill-label {
      font-size: 0;
    }

    /* Show first letter only via data attrs */
    .pill:nth-child(1) .pill-label::after {
      content: "普";
      font-size: 11px;
    }

    .pill:nth-child(2) .pill-label::after {
      content: "聚";
      font-size: 11px;
    }

    .pill {
      padding: 0 7px;
    }
  }

  /* 549px: Minimal mode — collapse further */
  @media (max-width: 549px) {
    .header-title {
      display: none;
    }

    .search-hint {
      padding: 0 8px;
    }

    .header {
      padding: 0 6px;
      gap: 4px;
    }

    .header-left {
      gap: 6px;
    }
  }

  /* 到uch targets for coarse pointers */
  @media (pointer: coarse) {
    .header-btn,
    .nav-btn,
    .hamburger,
    .import-btn {
      min-width: 44px;
      min-height: 44px;
    }

    .transcript-strip {
      min-height: 44px;
    }

    .pill {
      min-height: 44px;
    }
  }
</style>
