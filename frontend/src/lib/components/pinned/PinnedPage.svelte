<script lang="ts">
  import {
    CheckIcon,
    复制Icon,
    ExternalLinkIcon,
    PinIcon,
    XIcon,
  } from "../../icons.js";
  import { pins } from "../../stores/pins.svelte.js";
  import { 个会话 } from "../../stores/个会话.svelte.js";
  import { router } from "../../stores/router.svelte.js";
  import { ui } from "../../stores/ui.svelte.js";
  import { formatRelativeTime, truncate } from "../../utils/format.js";
  import { renderMarkdown } from "../../utils/markdown.js";
  import { highlightCodeFences } from "../../utils/highlight-fences.js";
  import { copy到Clipboard } from "../../utils/clipboard.js";
  import { normalizeMessagePreview } from "../../utils/条消息.js";
  $effect(() => {
    pins.loadAll(个会话.filters.project || undefined);
  });

  /** Set of expanded pin IDs. */
  let expanded: Set<number> = $state(new Set());

  function toggle展开(pinId: number) {
    const next = new Set(expanded);
    if (next.has(pinId)) next.delete(pinId);
    else next.add(pinId);
    expanded = next;
  }

  function navigate到Pin(sessionId: string, ordinal: number) {
    ui.scroll到Ordinal(ordinal, sessionId);
    router.navigate到Session(sessionId);
  }

  function getSessionInfo(pin: import("../../api/types.js").已固定Message) {
    // Use backend-provided session metadata (available for all-pins
    // query). Fall back to the 个会话 store for older data.
    if (pin.session_project || pin.session_agent) {
      return {
        project: pin.session_project ?? "未知",
        agent: pin.session_agent ?? "未知",
        name:
          pin.session_display_name
          ?? (
            normalizeMessagePreview(pin.session_first_message)
            || pin.session_project
            || pin.session_id.slice(0, 12)
          ),
      };
    }
    const s = 个会话.个会话.find((s) => s.id === pin.session_id);
    return s
      ? {
          project: s.project,
          agent: s.agent,
          // normalizeMessagePreview can return "" — use || not ?? to fall through.
          name:
            s.display_name
            ?? (normalizeMessagePreview(s.first_message) || s.project),
        }
      : {
          project: "未知",
          agent: "未知",
          name: pin.session_id.slice(0, 12) + "...",
        };
  }

  let copiedId: number | null = $state(null);

  async function handle复制(pinId: number, content: string | null | undefined) {
    if (!content) return;
    const ok = await copy到Clipboard(content);
    if (ok) {
      copiedId = pinId;
      setTimeout(() => { if (copiedId === pinId) copiedId = null; }, 1500);
    }
  }

  function previewContent(content: string | null | undefined): string {
    if (!content) return "";
    // Strip thinking tags and tool use markers for preview
    const cleaned = content
      .replace(/<antThinking>[\s\S]*?<\/antThinking>/g, "")
      .replace(/\[tool_use:.*?\]/g, "")
      .trim();
    return truncate(cleaned, 300);
  }
</script>

<div class="pinned-page">
  <div class="pinned-header">
    <PinIcon size="18" strokeWidth="2" class="pin-icon" aria-hidden="true" />
    <h2>已固定 Messages</h2>
    {#if pins.pins.length > 0}
      <span class="pin-count">{pins.pins.length}</span>
    {/if}
  </div>

  {#if pins.loading}
    <div class="loading-state">正在加载固定消息...</div>
  {:else if pins.pins.length === 0 && 个会话.filters.project}
    <div class="empty-state">
      <p class="empty-title">No pinned 条消息 for this project</p>
      <p class="empty-desc">
        Try selecting a different project or clear the project filter.
      </p>
    </div>
  {:else if pins.pins.length === 0}
    <div class="empty-state">
      <PinIcon size="40" strokeWidth="1.6" class="empty-icon" aria-hidden="true" />
      <p class="empty-title">No pinned 条消息</p>
      <p class="empty-desc">
        Pin 条消息 from any session by clicking the pin icon in the message header.
      </p>
    </div>
  {:else}
    <div class="pin-list">
      {#each pins.pins as pin (pin.id)}
        {@const info = getSessionInfo(pin)}
        {@const is展开ed = expanded.has(pin.id)}
        {@const preview = previewContent(pin.content)}
        {@const has更多 = (pin.content?.length ?? 0) > 300}
        <div class="pin-card" class:expanded={is展开ed}>
          <div class="pin-card-header">
            <span
              class="role-badge"
              class:user={pin.role === "user"}
              class:assistant={pin.role === "assistant"}
            >
              {pin.role === "user" ? "U" : "A"}
            </span>
            <span class="pin-agent">{info.agent}</span>
            <span class="pin-session-name">{truncate(info.name, 60)}</span>
            <span class="pin-ordinal">#{pin.ordinal}</span>
            <span class="pin-time">{formatRelativeTime(pin.created_at)}</span>
          </div>

          {#if preview}
            <div class="pin-content-wrap">
              {#if is展开ed && pin.content}
                <div
                  class="pin-content-full markdown"
                  use:highlightCodeFences={{ content: pin.content }}
                >
                  {@html renderMarkdown(pin.content)}
                </div>
              {:else}
                <div class="pin-content-preview">{preview}</div>
              {/if}
            </div>
          {/if}

          <div class="pin-card-footer">
            <button
              class="pin-card-meta"
              onclick={() => navigate到Pin(pin.session_id, pin.ordinal)}
              title="跳转到消息"
            >
              <ExternalLinkIcon size="10" strokeWidth="2.2" aria-hidden="true" />
              <span>{info.project}</span>
            </button>
            <div class="pin-card-actions">
              {#if has更多}
                <button
                  class="expand-btn"
                  onclick={() => toggle展开(pin.id)}
                >
                  {is展开ed ? "折叠" : "展开"}
                </button>
              {/if}
              <button
                class="copy-btn"
                title="复制 message"
                onclick={() => handle复制(pin.id, pin.content)}
              >
                {#if copiedId === pin.id}
                  <CheckIcon size="12" strokeWidth="2.4" aria-hidden="true" />
                {:else}
                  <复制Icon size="12" strokeWidth="2" aria-hidden="true" />
                {/if}
              </button>
              <button
                class="unpin-btn"
                title="取消固定"
                onclick={() => pins.unpin(pin.session_id, pin.message_id)}
              >
                <XIcon size="12" strokeWidth="2.4" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .pinned-page {
    max-width: 1100px;
    margin: 0 auto;
    padding: 40px 24px;
  }

  .pinned-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 28px;
  }

  :全局(.pin-icon) {
    color: var(--accent-blue);
  }

  .pinned-header h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .pin-count {
    background: var(--accent-blue);
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 1px 7px;
    border-radius: 10px;
  }

  .loading-state {
    text-align: center;
    color: var(--text-muted);
    padding: 40px 0;
    font-size: 13px;
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
  }

  :全局(.empty-icon) {
    opacity: 0.15;
    margin-bottom: 16px;
  }

  .empty-title {
    font-size: 16px;
    font-weight: 500;
    color: var(--text-secondary);
    margin: 0 0 6px;
  }

  .empty-desc {
    font-size: 13px;
    margin: 0;
  }

  .pin-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 12px;
  }

  .pin-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-muted);
    border-radius: 8px;
    transition: border-color 0.15s;
  }

  .pin-card:hover {
    border-color: var(--border-default);
  }

  .pin-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px 0;
  }

  .role-badge {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
    line-height: 1;
    background: var(--accent-purple);
  }

  .role-badge.user {
    background: var(--accent-blue);
  }

  .pin-agent {
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--accent-purple);
    letter-spacing: 0.03em;
    flex-shrink: 0;
  }

  .pin-session-name {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
    min-width: 0;
  }

  .pin-ordinal {
    font-size: 10px;
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .pin-time {
    font-size: 10px;
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .pin-content-wrap {
    padding: 8px 14px;
  }

  .pin-content-preview {
    font-size: 12px;
    line-height: 1.6;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .pin-content-full {
    font-size: 13px;
    line-height: 1.65;
    color: var(--text-primary);
    word-wrap: break-word;
    max-height: 500px;
    overflow-y: auto;
  }

  /* Markdown prose inside expanded pins */
  .pin-content-full :全局(p) {
    margin: 0.4em 0;
  }
  .pin-content-full :全局(p:first-child) {
    margin-top: 0;
  }
  .pin-content-full :全局(p:last-child) {
    margin-bottom: 0;
  }
  .pin-content-full :全局(code) {
    font-family: var(--font-mono);
    font-size: 0.85em;
    background: var(--bg-inset);
    border: 1px solid var(--border-muted);
    border-radius: 4px;
    padding: 0.15em 0.4em;
  }
  .pin-content-full :全局(pre) {
    background: var(--code-bg);
    color: var(--code-text);
    border-radius: var(--radius-md);
    padding: 10px 14px;
    overflow-x: auto;
    margin: 0.4em 0;
  }
  .pin-content-full :全局(pre code) {
    background: none;
    border: none;
    padding: 0;
    font-size: 12px;
    color: inherit;
  }
  .pin-content-full :全局(ul),
  .pin-content-full :全局(ol) {
    padding-left: 1.4em;
    margin: 0.4em 0;
  }
  .pin-content-full :全局(blockquote) {
    border-left: 3px solid var(--border-default);
    margin: 0.4em 0;
    padding: 0.2em 0.8em;
    color: var(--text-secondary);
  }
  .pin-content-full :全局(a) {
    color: var(--accent-blue);
    text-decoration: none;
  }
  .pin-content-full :全局(a:hover) {
    text-decoration: underline;
  }

  .pin-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 14px 10px;
  }

  .pin-card-meta {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    color: var(--text-muted);
    background: none;
    border: none;
    cursor: pointer;
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    transition: background 0.12s, color 0.12s;
  }

  .pin-card-meta:hover {
    background: var(--bg-surface-hover);
    color: var(--accent-blue);
  }

  .pin-card-actions {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .expand-btn {
    font-size: 10px;
    font-weight: 500;
    color: var(--accent-blue);
    background: none;
    border: none;
    cursor: pointer;
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    transition: background 0.12s;
  }

  .expand-btn:hover {
    background: color-mix(in srgb, var(--accent-blue) 8%, transparent);
  }

  .unpin-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border: none;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    flex-shrink: 0;
    transition: background 0.15s, color 0.15s;
  }

  .unpin-btn:hover {
    background: color-mix(in srgb, var(--accent-red, #e55) 12%, transparent);
    color: var(--accent-red, #e55);
  }

  .copy-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border: none;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    flex-shrink: 0;
    transition: background 0.15s, color 0.15s;
  }

  .copy-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-secondary);
  }

  /* Make expanded cards span full width in grid */
  .pin-card.expanded {
    grid-column: 1 / -1;
  }
</style>
