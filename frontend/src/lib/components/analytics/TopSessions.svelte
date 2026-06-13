<script lang="ts">
  import { analytics } from "../../stores/analytics.svelte.js";
  import {
    个会话,
    getSession状态,
  } from "../../stores/个会话.svelte.js";
  import { router } from "../../stores/router.svelte.js";
  import { format到kenCount } from "../../utils/format.js";
  import { normalizeMessagePreview } from "../../utils/条消息.js";
  import 状态Dot from "../common/状态Dot.svelte";

  function truncate(text: string, max: number): string {
    if (text.length <= max) return text;
    return text.slice(0, max - 1) + "\u2026";
  }

  function formatDuration(mins: number): string {
    const total = Math.round(mins);
    if (total < 60) return `${total}m`;
    const h = Math.floor(total / 60);
    const m = total % 60;
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  }

  function handleSessionClick(id: string) {
    let needInvalidate = false;
    if (analytics.include开eShot && !个会话.filters.include开eShot) {
      个会话.filters.include开eShot = true;
      needInvalidate = true;
    }
    if (analytics.includeAutomated && !个会话.filters.includeAutomated) {
      个会话.filters.includeAutomated = true;
      needInvalidate = true;
    }
    if (needInvalidate) {
      个会话.invalidateFilterCaches();
    }
    router.navigate到Session(id);
  }

  const supportsOutput到kens = $derived(
    analytics.summary?.total_output_tokens !== undefined &&
      analytics.summary?.token_reporting_个会话 !== undefined,
  );

  const uncleanCount = $derived(
    (analytics.top会话?.个会话 ?? []).filter(
      (s) => getSession状态(s) === "unclean",
    ).length,
  );
</script>

<div class="top-个会话-container">
  <div class="top-header">
    <h3 class="chart-title">到p 会话</h3>
    <div class="header-controls">
      {#if uncleanCount > 0}
        <button
          class="status-count-pill"
          onclick={() => 个会话.setTerminationFilter("unclean")}
          title="Filter to unclean 个会话"
        >
          {uncleanCount} unclean
        </button>
      {/if}
      <div class="metric-toggle">
        <button
          class="toggle-btn"
          class:active={analytics.topMetric === "条消息"}
          onclick={() => analytics.set到pMetric("条消息")}
        >
          By Messages
        </button>
        <button
          class="toggle-btn"
          class:active={analytics.topMetric === "duration"}
          onclick={() => analytics.set到pMetric("duration")}
        >
          By Duration
        </button>
        {#if supportsOutput到kens}
          <button
            class="toggle-btn"
            class:active={analytics.topMetric === "output_tokens"}
            onclick={() => analytics.set到pMetric("output_tokens")}
          >
            By Output 到kens
          </button>
        {/if}
      </div>
    </div>
  </div>

  {#if analytics.errors.top会话}
    <div class="error">
      {analytics.errors.top会话}
      <button
        class="retry-btn"
        onclick={() => analytics.fetch到p会话()}
      >
        重试
      </button>
    </div>
  {:else if analytics.top会话 && analytics.top会话.个会话.length > 0}
    <div class="session-list">
      {#each analytics.top会话.个会话 as session, i}
        {@const preview = normalizeMessagePreview(session.first_message)}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
          class="session-row"
          onclick={() => handleSessionClick(session.id)}
        >
          <span class="rank">{i + 1}</span>
          <span class="session-status">
            <状态Dot session={session} size={7} />
          </span>
          <div class="session-info">
            <span class="session-label">
              {preview
                ? truncate(preview, 50)
                : session.id.slice(0, 12)}
            </span>
            <span class="session-project">{session.project}</span>
          </div>
          <span class="session-metric">
            {#if analytics.topMetric === "duration"}
              {formatDuration(session.duration_min)}
            {:else if analytics.topMetric === "output_tokens"}
              {format到kenCount(session.output_tokens)}
            {:else}
              {session.message_count}
            {/if}
          </span>
        </div>
      {/each}
    </div>
  {:else}
    <div class="empty">No 个会话 in range</div>
  {/if}
</div>

<style>
  .top-个会话-container {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .top-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .chart-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .header-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status-count-pill {
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 500;
    border-radius: 999px;
    color: var(--accent-amber);
    background: color-mix(
      in srgb,
      var(--accent-amber) 10%,
      transparent
    );
    border: 1px solid color-mix(
      in srgb,
      var(--accent-amber) 35%,
      transparent
    );
    cursor: pointer;
    transition: background 0.1s;
  }

  .status-count-pill:hover {
    background: color-mix(
      in srgb,
      var(--accent-amber) 18%,
      transparent
    );
  }

  .metric-toggle {
    display: flex;
    gap: 2px;
    background: var(--bg-inset);
    border-radius: var(--radius-sm);
    padding: 1px;
  }

  .toggle-btn {
    padding: 2px 8px;
    font-size: 10px;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    cursor: pointer;
    transition: background 0.1s, color 0.1s;
  }

  .toggle-btn.active {
    background: var(--bg-surface);
    color: var(--text-primary);
    font-weight: 500;
  }

  .toggle-btn:hover:not(.active) {
    color: var(--text-secondary);
  }

  .session-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow-y: auto;
    flex: 1;
  }

  .session-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 6px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background 0.1s;
  }

  .session-row:hover {
    background: var(--bg-surface-hover);
  }

  .rank {
    flex-shrink: 0;
    width: 18px;
    text-align: right;
    font-size: 10px;
    font-weight: 600;
    color: var(--text-muted);
    font-family: var(--font-mono);
  }

  .session-status {
    flex-shrink: 0;
    width: 14px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    font-size: 11px;
    line-height: 1;
  }

  .session-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 1px;
  }

  .session-label {
    font-size: 11px;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .session-project {
    font-size: 9px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .session-metric {
    flex-shrink: 0;
    font-size: 11px;
    font-weight: 500;
    font-family: var(--font-mono);
    color: var(--accent-blue);
    min-width: 36px;
    text-align: right;
  }

  .empty {
    color: var(--text-muted);
    font-size: 12px;
    padding: 24px;
    text-align: center;
  }

  .error {
    color: var(--accent-red);
    font-size: 12px;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .retry-btn {
    padding: 2px 8px;
    border: 1px solid currentColor;
    border-radius: var(--radius-sm);
    font-size: 11px;
    color: inherit;
    cursor: pointer;
  }
</style>
