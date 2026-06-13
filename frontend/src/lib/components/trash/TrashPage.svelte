<script lang="ts">
  import { 回收站Icon } from "../../icons.js";
  import { onMount } from "svelte";
  import type { Session } from "../../api/types.js";
  import { 会话Service } from "../../api/generated/index";
  import { configure生成dClient } from "../../api/runtime.js";
  import { 个会话 } from "../../stores/个会话.svelte.js";
  import { formatRelativeTime, truncate } from "../../utils/format.js";
  import { normalizeMessagePreview } from "../../utils/条消息.js";
  let trashed会话: Session[] = $state([]);
  let loading = $state(true);
  let emptying = $state(false);

  interface 回收站Response {
    个会话: Session[];
  }

  onMount(() => {
    load回收站();
  });

  async function load回收站() {
    loading = true;
    try {
      configure生成dClient();
      const res =
        await 会话Service.getApiV1回收站() as 未知 as 回收站Response;
      trashed会话 = res.个会话 ?? [];
    } catch {
      // Silently ignore — page will show empty state.
    } finally {
      loading = false;
    }
  }

  async function restoreSession(id: string) {
    try {
      configure生成dClient();
      await 会话Service.postApiV1会话Id恢复({ id });
      trashed会话 = trashed会话.filter((s) => s.id !== id);
      个会话.clearRecently删除d(id);
      个会话.invalidateFilterCaches();
      个会话.load();
    } catch {
      // silently fail
    }
  }

  async function permanent删除(id: string) {
    try {
      configure生成dClient();
      await 会话Service.deleteApiV1会话IdPermanent({ id });
      trashed会话 = trashed会话.filter((s) => s.id !== id);
      个会话.clearRecently删除d(id);
      个会话.invalidateFilterCaches();
    } catch {
      // silently fail
    }
  }

  async function emptyAll() {
    emptying = true;
    try {
      configure生成dClient();
      await 会话Service.deleteApiV1回收站();
      trashed会话 = [];
      个会话.clearRecently删除d();
      个会话.invalidateFilterCaches();
    } catch {
      // Silently ignore — button resets to allow retry.
    } finally {
      emptying = false;
    }
  }

  function displayName(s: Session): string {
    const raw = s.display_name ?? normalizeMessagePreview(s.first_message);
    return raw ? truncate(raw, 70) : s.project;
  }
</script>

<div class="trash-page">
  <div class="trash-header">
    <回收站Icon size="18" strokeWidth="2" class="trash-icon" aria-hidden="true" />
    <h2>回收站</h2>
    {#if trashed会话.length > 0}
      <span class="trash-count">{trashed会话.length}</span>
      <button
        class="empty-all-btn"
        onclick={emptyAll}
        disabled={emptying}
      >
        {emptying ? "清空中..." : "Empty 回收站"}
      </button>
    {/if}
  </div>

  <p class="trash-desc">
    删除d 个会话 are kept until you permanently delete them or empty the trash.
  </p>

  {#if loading}
    <div class="loading-state">正在加载回收站...</div>
  {:else if trashed会话.length === 0}
    <div class="empty-state">
      <回收站Icon size="40" strokeWidth="1.6" class="empty-icon" aria-hidden="true" />
      <p class="empty-title">回收站 is empty</p>
      <p class="empty-desc-text">删除d 个会话 will appear here.</p>
    </div>
  {:else}
    <div class="trash-list">
      {#each trashed会话 as session (session.id)}
        <div class="trash-card">
          <div class="trash-card-info">
            <div class="trash-card-name">{displayName(session)}</div>
            <div class="trash-card-meta">
              <span class="trash-agent">{session.agent}</span>
              <span class="trash-project">{session.project}</span>
              <span class="trash-msgs">{session.user_message_count} msgs</span>
              {#if session.已删除_at}
                <span class="trash-已删除">已删除 {formatRelativeTime(session.已删除_at)}</span>
              {/if}
            </div>
          </div>
          <div class="trash-card-actions">
            <button
              class="restore-btn"
              onclick={() => restoreSession(session.id)}
              title="恢复 session"
            >
              恢复
            </button>
            <button
              class="perm-delete-btn"
              onclick={() => permanent删除(session.id)}
              title="永久删除"
            >
              删除 Forever
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .trash-page {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 24px;
  }

  .trash-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }

  :全局(.trash-icon) {
    color: var(--text-muted);
  }

  .trash-header h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .trash-count {
    background: var(--text-muted);
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 1px 7px;
    border-radius: 10px;
  }

  .trash-desc {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 24px;
  }

  .empty-all-btn {
    margin-left: auto;
    font-size: 11px;
    font-weight: 500;
    color: var(--accent-red, #e55);
    background: none;
    border: 1px solid var(--accent-red, #e55);
    border-radius: var(--radius-sm);
    padding: 4px 12px;
    cursor: pointer;
    transition: background 0.12s;
  }

  .empty-all-btn:hover:not(:disabled) {
    background: color-mix(in srgb, var(--accent-red, #e55) 8%, transparent);
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

  .empty-desc-text {
    font-size: 13px;
    margin: 0;
  }

  .trash-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .trash-card {
    display: flex;
    align-items: center;
    background: var(--bg-surface);
    border: 1px solid var(--border-muted);
    border-radius: 8px;
    padding: 12px 14px;
    gap: 12px;
    transition: border-color 0.15s;
  }

  .trash-card:hover {
    border-color: var(--border-default);
  }

  .trash-card-info {
    flex: 1;
    min-width: 0;
  }

  .trash-card-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 3px;
  }

  .trash-card-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 10px;
    color: var(--text-muted);
  }

  .trash-agent {
    font-weight: 600;
    text-transform: capitalize;
  }

  .trash-project {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
  }

  .trash-msgs {
    white-space: nowrap;
  }

  .trash-已删除 {
    white-space: nowrap;
    color: var(--accent-red, #e55);
    font-style: italic;
  }

  .trash-card-actions {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
  }

  .restore-btn {
    font-size: 11px;
    font-weight: 500;
    color: var(--accent-green);
    background: none;
    border: 1px solid var(--accent-green);
    border-radius: var(--radius-sm);
    padding: 4px 10px;
    cursor: pointer;
    transition: background 0.12s;
  }

  .restore-btn:hover {
    background: color-mix(in srgb, var(--accent-green) 8%, transparent);
  }

  .perm-delete-btn {
    font-size: 11px;
    font-weight: 500;
    color: var(--accent-red, #e55);
    background: none;
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    padding: 4px 10px;
    cursor: pointer;
    transition: background 0.12s, color 0.12s;
  }

  .perm-delete-btn:hover {
    background: color-mix(in srgb, var(--accent-red, #e55) 8%, transparent);
  }
</style>
