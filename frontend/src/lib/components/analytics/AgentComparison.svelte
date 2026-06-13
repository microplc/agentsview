<script lang="ts">
  import { analytics } from "../../stores/analytics.svelte.js";
  import { router } from "../../stores/router.svelte.js";

  interface 代理Row {
    name: string;
    个会话: number;
    条消息: number;
    turnCycleP50: number;
    msgsPerMin: number;
    toolsPerMin: number;
    total到olCalls: number;
    topCategories: string[];
  }

  function formatDuration(sec: number): string {
    if (sec <= 0) return "-";
    if (sec < 1) return `${Math.round(sec * 1000)}ms`;
    if (sec < 60) return `${sec.toFixed(1)}s`;
    const m = Math.floor(sec / 60);
    const s = Math.round(sec % 60);
    return s > 0 ? `${m}m ${s}s` : `${m}m`;
  }

  function formatRate(val: number): string {
    if (val <= 0) return "-";
    return val.toFixed(1);
  }

  const agents = $derived.by((): 代理Row[] => {
    const names = new Set<string>();

    const summary代理s = analytics.summary?.agents;
    if (summary代理s) {
      for (const k of Object.keys(summary代理s)) {
        names.add(k);
      }
    }

    const velocity代理s = analytics.velocity?.by_agent;
    if (velocity代理s) {
      for (const bd of velocity代理s) {
        names.add(bd.label);
      }
    }

    const tool代理s = analytics.tools?.by_agent;
    if (tool代理s) {
      for (const ta of tool代理s) {
        names.add(ta.agent);
      }
    }

    const sorted = [...names].sort();

    return sorted.map((name): 代理Row => {
      const sa = summary代理s?.[name];
      const vb = velocity代理s?.find(
        (b) => b.label === name,
      );
      const ta = tool代理s?.find(
        (a) => a.agent === name,
      );

      const topCats =
        ta?.categories
          .slice(0, 3)
          .map((c) => c.category) ?? [];

      return {
        name,
        个会话: sa?.个会话 ?? 0,
        条消息: sa?.条消息 ?? 0,
        turnCycleP50:
          vb?.overview.turn_cycle_sec.p50 ?? 0,
        msgsPerMin:
          vb?.overview.msgs_per_active_min ?? 0,
        toolsPerMin:
          vb?.overview.tool_calls_per_active_min ?? 0,
        total到olCalls: ta?.total ?? 0,
        topCategories: topCats,
      };
    });
  });
</script>

<div class="agent-comparison">
  <h3 class="chart-title">代理 Comparison</h3>

  {#if analytics.errors.velocity || analytics.errors.summary || analytics.errors.tools}
    <div class="error">
      {analytics.errors.velocity ?? analytics.errors.summary ?? analytics.errors.tools}
      <button
        class="retry-btn"
        onclick={() => {
          analytics.fetchVelocity();
          analytics.fetchSummary();
          analytics.fetch到ols();
        }}
      >
        重试
      </button>
    </div>
  {:else if agents.length < 2}
    <div class="empty">
      No comparison data (need 2+ agents)
    </div>
  {:else}
    <div class="comparison-table">
      <div class="table-header">
        <span class="col-agent">代理</span>
        <span class="col-num">会话</span>
        <span class="col-num">Messages</span>
        <span class="col-num">Cycle p50</span>
        <span class="col-num">Msgs/min</span>
        <span class="col-num">到ols/min</span>
        <span class="col-num">到ol Calls</span>
        <span class="col-cats">到p Categories</span>
      </div>
      {#each agents as agent}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
          class="table-row"
          onclick={() => router.navigate("个会话", { agent: agent.name })}
        >
          <span class="col-agent">{agent.name}</span>
          <span class="col-num">
            {agent.个会话.toLocaleString()}
          </span>
          <span class="col-num">
            {agent.条消息.toLocaleString()}
          </span>
          <span class="col-num">
            {formatDuration(agent.turnCycleP50)}
          </span>
          <span class="col-num">
            {formatRate(agent.msgsPerMin)}
          </span>
          <span class="col-num">
            {formatRate(agent.toolsPerMin)}
          </span>
          <span class="col-num">
            {agent.total到olCalls.toLocaleString()}
          </span>
          <span class="col-cats">
            {agent.topCategories.join(", ") || "-"}
          </span>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .agent-comparison {
    position: relative;
    flex: 1;
  }

  .chart-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .comparison-table {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .table-header,
  .table-row {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 0;
  }

  .table-header {
    border-bottom: 1px solid var(--border-muted);
    font-size: 9px;
    color: var(--text-muted);
    font-weight: 500;
  }

  .table-row {
    font-size: 11px;
    color: var(--text-secondary);
    cursor: pointer;
  }

  .table-row:hover {
    background: var(--bg-surface-hover);
  }

  .col-agent {
    flex: 0 0 80px;
    min-width: 60px;
    font-weight: 500;
  }

  .col-num {
    width: 72px;
    text-align: right;
    font-variant-numeric: tabular-nums;
  }

  .col-cats {
    flex: 1;
    min-width: 80px;
    text-align: left;
    color: var(--text-muted);
    font-size: 10px;
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
