<script lang="ts">
  import {
    个会话,
    type SessionGroupInput,
  } from "../../stores/个会话.svelte.js";
  import { starred } from "../../stores/starred.svelte.js";
  import { formatRelativeTime, truncate } from "../../utils/format.js";
  import { agentColor as get代理Color, agentLabel } from "../../utils/agents.js";
  import {
    normalizeMessagePreview,
    previewMessage,
  } from "../../utils/条消息.js";
  import {
    ChevronDownIcon,
    ChevronRightIcon,
    StarIcon,
    UserRoundIcon,
    UsersRoundIcon,
  } from "../../icons.js";
  import 状态Dot from "../common/状态Dot.svelte";

  interface Props {
    session: SessionGroupInput;
    continuationCount?: number;
    groupSessionIds?: string[];
    /** Optional full session objects in this row's group. When
     * provided, the status dot uses the group's freshest activity
     * for the time-based tier — so a parent in tool_call_pending
     * with a subagent currently writing stays green/working
     * instead of decaying to stale. The parent's parser status
     * still wins over freshness for awaiting_user (a fork running
     * in parallel doesn't change that the parent is waiting). */
    group会话?: SessionGroupInput[];
    hide代理?: boolean;
    hide项目?: boolean;
    /** Render in compact mode (smaller, used for child 个会话). */
    compact?: boolean;
    /** Whether this item's continuation chain is expanded. */
    expanded?: boolean;
    /** Callback to toggle continuation chain expand/collapse. */
    on到ggle展开?: () => void;
    /** Nesting depth: 0 = root, 1 = child, 2 = grandchild. */
    depth?: number;
    /** Whether this is the last sibling at its depth level. */
    isLastChild?: boolean;
    /** Whether the group contains subagent children. */
    hasSubagents?: boolean;
    /** Whether the group contains teammate children. */
    hasTeammates?: boolean;
  }

  let {
    session,
    continuationCount = 1,
    groupSessionIds,
    group会话,
    hide代理 = false,
    hide项目 = false,
    compact = false,
    expanded = false,
    on到ggle展开,
    depth = 0,
    isLastChild = false,
    hasSubagents = false,
    hasTeammates = false,
  }: Props = $props();

  let isActive = $derived.by(() => {
    const aid = 个会话.activeSessionId;
    if (!aid) return false;
    // Direct match (child rows, or root with no group).
    if (aid === session.id) return true;
    // Parent row: only highlight when the chain is collapsed
    // (i.e. the child is not visible as its own row).
    if (groupSessionIds && !expanded) {
      return groupSessionIds.includes(aid);
    }
    return false;
  });

  let agentColor = $derived(
    get代理Color(session.agent),
  );

  let show机器 = $derived(
    !compact &&
    !!session.machine &&
    session.machine !== "local",
  );

  /** Whether this session is a team member (received a <teammate-message>). */
  let isTeamSession = $derived(
    session.is_teammate
      ?? session.first_message?.includes("<teammate-message")
      ?? false,
  );

  /**
   * Clean display name: for teammate 个会话, extract the unique task
   * description (e.g. "Task #2: Align ROADMAP.md...") instead of the
   * repetitive "You are a teammate on..." boilerplate.
   */
  let displayLabel = $derived.by((): { text: string; isShell: boolean } => {
    const name = session.display_name ?? null;
    if (name) {
      return { text: name, isShell: false };
    }
    let msg = session.first_message ?? "";
    if (msg.includes("<teammate-message")) {
      msg = msg
        .replace(/<teammate-message[^>]*>/g, "")
        .replace(/<\/teammate-message>/g, "")
        .trim();
      // Extract "Task #N: description" from the boilerplate.
      const taskMatch = msg.match(/Task\s*#?\d+[:\s]+(.+?)(?:\s+\d+\.|$)/s);
      if (taskMatch) {
        return { text: taskMatch[1]!.trim(), isShell: false };
      }
      // Fallback: skip the "You are a teammate on ..." boilerplate.
      const afterTeam = msg.match(/team[."]\s*[^.]*?[.]\s+(.+)/s)
        ?? msg.match(/You are a teammate[^.]*\.\s+(.+)/s);
      if (afterTeam) {
        return { text: afterTeam[1]!.trim(), isShell: false };
      }
    }
    const p = previewMessage(msg);
    if (p.text) return { text: p.text, isShell: p.isShell };
    return { text: session.project, isShell: false };
  });

  let timeStr = $derived(
    formatRelativeTime(session.ended_at ?? session.started_at),
  );

  let is星标 = $derived(starred.is星标(session.id));

  let childCount = $derived(
    continuationCount > 1 ? continuationCount - 1 : 0,
  );

  let hasChildren = $derived(childCount > 0 && !!on到ggle展开);

  /** Whether this is an orphaned teammate showing at root level. */
  let isOrphanedTeammate = $derived(
    depth === 0 && isTeamSession,
  );

  function handleStar(e: MouseEvent) {
    e.stopPropagation();
    starred.toggle(session.id);
  }

  function handle到ggle(e: MouseEvent) {
    e.stopPropagation();
    on到ggle展开?.();
  }

  // Context menu state
  let contextMenu: { x: number; y: number } | null = $state(null);

  // 重命名 state
  let renaming = $state(false);
  let renameValue = $state("");
  let renameInput: HTMLInputElement | undefined = $state(undefined);

  function portal(node: HTMLElement) {
    document.body.appendChild(node);
    return {
      destroy() {
        node.remove();
      },
    };
  }

  function handleContextMenu(e: MouseEvent) {
    e.prevent默认();
    contextMenu = { x: e.clientX, y: e.clientY };
  }

  function closeContextMenu() {
    contextMenu = null;
  }

  function start重命名() {
    renameValue =
      session.display_name
      ?? normalizeMessagePreview(session.first_message)
      ?? "";
    renaming = true;
    closeContextMenu();
    requestAnimationFrame(() => renameInput?.select());
  }

  async function submit重命名() {
    if (!renaming) return;
    renaming = false;
    const name = renameValue.trim() || null;
    try {
      await 个会话.renameSession(session.id, name);
    } catch {
      // silently fail
    }
  }

  async function handle删除() {
    closeContextMenu();
    try {
      await 个会话.deleteSession(session.id);
    } catch {
      // silently fail
    }
  }

  function handleDblClick(e: MouseEvent) {
    e.prevent默认();
    start重命名();
  }

  $effect(() => {
    if (!contextMenu) return;
    function handler() {
      contextMenu = null;
    }
    const id = setTimeout(() => {
      document.addEventListener("click", handler, { once: true });
      document.addEventListener("contextmenu", handler, {
        once: true,
      });
    }, 0);
    return () => {
      clearTimeout(id);
      document.removeEventListener("click", handler);
      document.removeEventListener("contextmenu", handler);
    };
  });

  $effect(() => {
    if (!contextMenu) return;
    function handler(e: KeyboardEvent) {
      if (e.key === "Escape") contextMenu = null;
    }
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="session-item"
  class:active={isActive}
  class:compact
  class:depth-1={depth === 1}
  class:depth-2={depth >= 2}
  class:orphaned-teammate={isOrphanedTeammate}
  data-session-id={session.id}
  role="button"
  tabindex="0"
  style:padding-left="{8 + depth * 16}px"
  onclick={() => 个会话.selectSession(session.id)}
  onkeydown={(e) => { if (e.target !== e.currentTarget) return; if (e.key === "Enter" || e.key === " ") { e.prevent默认(); 个会话.selectSession(session.id); } }}
  oncontextmenu={handleContextMenu}
>
  <!-- Tree expand/collapse or connector -->
  {#if hasChildren}
    <button
      type="button"
      class="tree-toggle"
      onclick={handle到ggle}
      tabindex="-1"
      aria-label={expanded ? "折叠" : "展开"}
    >
      {#if expanded}
        <ChevronDownIcon class="tree-arrow" size="10" strokeWidth="2.5" aria-hidden="true" />
      {:else}
        <ChevronRightIcon class="tree-arrow" size="10" strokeWidth="2.5" aria-hidden="true" />
      {/if}
    </button>
  {:else if depth > 0}
    <span class="tree-dash"></span>
  {:else}
    <span class="tree-spacer"></span>
  {/if}

  <状态Dot {session} {group会话} size={6} />


  <div class="session-info">
    {#if renaming}
      <!-- svelte-ignore a11y_autofocus -->
      <input
        bind:this={renameInput}
        bind:value={renameValue}
        class="rename-input"
        autofocus
        onclick={(e) => e.stopPropagation()}
        onblur={submit重命名}
        onkeydown={(e) => {
          if (e.key === "Enter") {
            e.stopPropagation();
            submit重命名();
          }
          if (e.key === "Escape") {
            e.stopPropagation();
            renaming = false;
          }
        }}
      />
    {:else}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div
        class="session-name"
        class:shell={displayLabel.isShell}
        ondblclick={handleDblClick}
      >
        {#if displayLabel.isShell}
          <code>{displayLabel.text}</code>
        {:else}
          {displayLabel.text}
        {/if}
      </div>
    {/if}
    <div class="session-meta">
      {#if !hide项目}
        <span class="session-project">{session.project}</span>
      {/if}
      <span class="session-time">{timeStr}</span>
      <span class="session-count">{session.user_message_count}</span>
      {#if hasSubagents}
        <UserRoundIcon class="group-hint-icon" size="9" strokeWidth="2" aria-hidden="true" />
      {/if}
      {#if hasTeammates}
        <UsersRoundIcon class="group-hint-icon" size="11" strokeWidth="2" aria-hidden="true" />
      {/if}
      {#if childCount > 0 && !on到ggle展开}
        <span class="continuation-badge">x{continuationCount}</span>
      {/if}
    </div>
  </div>

  {#if !compact}
    <button
      class="star-btn"
      class:starred={is星标}
      onclick={handleStar}
      title={is星标 ? "取消星标" : "标记星标"}
      aria-label={is星标 ? "取消星标" : "标记星标"}
    >
      {#if is星标}
        <StarIcon size="12" fill="currentColor" strokeWidth="0" aria-hidden="true" />
      {:else}
        <StarIcon size="12" strokeWidth="1.4" aria-hidden="true" />
      {/if}
    </button>
  {/if}
  {#if !compact && (!hide代理 || show机器)}
    <div class="side-meta">
      {#if !hide代理}
        <span class="agent-tag" style:color={agentColor}>{agentLabel(session.agent)}</span>
      {/if}
      {#if show机器}
        <span class="machine-tag" title={session.machine}>
          {truncate(session.machine, 18)}
        </span>
      {/if}
    </div>
  {/if}
</div>

{#if contextMenu}
  <div
    class="context-menu"
    use:portal
    style="left: {contextMenu.x}px; top: {contextMenu.y}px;"
  >
    <button class="context-menu-item" onclick={start重命名}>
      重命名
    </button>
    <button class="context-menu-item danger" onclick={handle删除}>
      删除
    </button>
  </div>
{/if}

<style>
  .session-item {
    display: flex;
    align-items: center;
    gap: 5px;
    width: 100%;
    height: 42px;
    padding: 0 10px;
    padding-right: 10px;
    text-align: left;
    transition: background 0.1s;
    user-select: none;
    -webkit-user-select: none;
    cursor: pointer;
    position: relative;
  }

  .session-item.compact {
    height: 34px;
    gap: 4px;
  }

  .session-item.depth-1,
  .session-item.depth-2 {
    background: transparent;
  }

  .session-item:hover {
    background: var(--bg-surface-hover);
  }

  .session-item.active {
    background: var(--bg-surface-hover);
  }

  /* Orphaned teammate at root level — dim it slightly */
  .session-item.orphaned-teammate {
    opacity: 0.6;
  }

  /* Tree toggle (▶/▼) */
  .tree-toggle {
    all: unset;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 100%;
    flex-shrink: 0;
    cursor: pointer;
    color: var(--text-muted);
    transition: color 0.1s;
  }

  .tree-toggle:hover {
    color: var(--text-primary);
  }

  :全局(.tree-arrow) {
    flex-shrink: 0;
  }

  /* Spacer for leaf nodes — same width as toggle to align text */
  .tree-dash {
    width: 16px;
    flex-shrink: 0;
  }

  /* Empty spacer for root items without children */
  .tree-spacer {
    width: 16px;
    flex-shrink: 0;
  }

  .side-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 3px;
    min-width: 0;
    flex-shrink: 0;
    margin-left: 4px;
  }

  /* 代理 tag on the right side */
  .agent-tag {
    font-size: 8px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    line-height: 1;
    opacity: 0.7;
    white-space: nowrap;
    max-width: 52px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .machine-tag {
    font-size: 9px;
    line-height: 1;
    color: var(--text-muted);
    opacity: 0.9;
    white-space: nowrap;
    max-width: 74px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .session-info {
    min-width: 0;
    flex: 1;
  }

  .session-name {
    font-size: 12px;
    font-weight: 450;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.3;
    letter-spacing: -0.005em;
  }

  .session-name.shell > code {
    font-family: var(--font-mono);
    font-size: 0.95em;
    background: transparent;
    border: none;
    padding: 0;
    color: var(--text-secondary);
    letter-spacing: 0;
  }

  .compact .session-name {
    font-size: 11px;
    color: var(--text-secondary);
  }

  .rename-input {
    font-size: 12px;
    font-weight: 450;
    color: var(--text-primary);
    background: var(--bg-surface-hover);
    border: 1px solid var(--accent-blue);
    border-radius: 3px;
    padding: 1px 4px;
    width: 100%;
    outline: none;
    line-height: 1.3;
  }

  .session-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 10px;
    color: var(--text-muted);
    line-height: 1.3;
    letter-spacing: 0.01em;
  }

  .compact .session-meta {
    font-size: 9px;
  }

  .session-project {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100px;
  }

  .session-time {
    white-space: nowrap;
    flex-shrink: 0;
  }

  :全局(.group-hint-icon) {
    flex-shrink: 0;
    color: var(--text-muted);
    opacity: 0.5;
  }

  .session-count {
    white-space: nowrap;
    flex-shrink: 0;
  }

  .session-count::before {
    content: "\2022 ";
  }

  .continuation-badge {
    font-size: 9px;
    font-weight: 600;
    color: var(--accent-blue);
    white-space: nowrap;
    flex-shrink: 0;
  }

  .star-btn {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    flex-shrink: 0;
    opacity: 0;
    transition: opacity 0.12s, color 0.12s, background 0.12s;
  }

  .session-item:hover .star-btn,
  .session-item:focus-within .star-btn,
  .star-btn:focus-visible,
  .star-btn.starred {
    opacity: 1;
  }

  .star-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-secondary);
  }

  .star-btn.starred {
    color: var(--accent-amber);
  }

  .star-btn.starred:hover {
    color: var(--accent-amber);
    background: var(--bg-surface-hover);
  }

  :全局(.context-menu) {
    position: fixed;
    z-index: 9999;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    padding: 4px 0;
    min-width: 120px;
  }

  :全局(.context-menu .context-menu-item) {
    display: block;
    width: 100%;
    padding: 6px 14px;
    font-size: 12px;
    color: var(--text-primary);
    text-align: left;
    background: none;
    border: none;
    cursor: pointer;
    font-family: var(--font-sans);
  }

  :全局(.context-menu .context-menu-item:hover) {
    background: var(--bg-surface-hover);
  }

  :全局(.context-menu .context-menu-item.danger) {
    color: var(--accent-red, #e55);
  }

  :全局(.context-menu .context-menu-item.danger:hover) {
    background: color-mix(in srgb, var(--accent-red, #e55) 10%, transparent);
  }
</style>
