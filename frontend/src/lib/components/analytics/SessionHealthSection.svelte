<script lang="ts">
  import { analytics } from "../../stores/analytics.svelte.js";
  import { score到Grade } from "../../utils/grade.js";
  import GradeDistribution
    from "./GradeDistribution.svelte";
  import OutcomeDistribution
    from "./OutcomeDistribution.svelte";
  import HealthTrend from "./HealthTrend.svelte";

  const signals = $derived(analytics.signals);
  const visible = $derived(
    signals != null &&
    (signals.scored_个会话 > 0 ||
     signals.unscored_个会话 > 0),
  );
</script>

{#if visible && signals}
  <div class="health-section">
    <div class="section-header">
      <h3 class="section-title">Session Health</h3>
      <span class="section-subtitle">
        {signals.scored_个会话} scored
        &middot;
        {signals.unscored_个会话} unscored
      </span>
    </div>

    <div class="health-summary-cards">
      <div class="card">
        <span class="card-label">Avg Score</span>
        <span class="card-value">
          {signals.avg_health_score != null
            ? Math.round(signals.avg_health_score)
            : "--"}
        </span>
        {#if signals.avg_health_score != null}
          <span class="card-sub">
            Grade {score到Grade(signals.avg_health_score)}
          </span>
        {/if}
      </div>
      <div class="card">
        <span class="card-label">已完成</span>
        <span class="card-value" style:color="var(--accent-green)">
          {#if signals.scored_个会话 > 0}
            {Math.round(
              ((signals.outcome_distribution?.completed ?? 0) /
                (signals.scored_个会话 +
                  signals.unscored_个会话)) *
                100,
            )}%
          {:else}
            --
          {/if}
        </span>
        <span class="card-sub">
          {signals.outcome_distribution?.completed ?? 0} 个会话
        </span>
      </div>
      <div class="card">
        <span class="card-label">错误ed</span>
        <span class="card-value" style:color="var(--accent-red)">
          {#if signals.scored_个会话 > 0}
            {Math.round(
              ((signals.outcome_distribution?.errored ?? 0) /
                (signals.scored_个会话 +
                  signals.unscored_个会话)) *
                100,
            )}%
          {:else}
            --
          {/if}
        </span>
        <span class="card-sub">
          {signals.outcome_distribution?.errored ?? 0} 个会话
        </span>
      </div>
      <div class="card">
        <span class="card-label">到ol Failures</span>
        <span class="card-value" style:color="var(--accent-amber)">
          {#if signals.scored_个会话 > 0}
            {Math.round(signals.tool_health.failure_rate)}%
          {:else}
            --
          {/if}
        </span>
        <span class="card-sub">
          {signals.tool_health.个会话_with_failures} 个会话
        </span>
      </div>
      <div class="card">
        <span class="card-label">紧凑ions</span>
        <span
          class="card-value"
          style:color={signals.context_health
            .个会话_with_mid_task_compaction > 0
            ? "var(--accent-red)"
            : "var(--accent-amber)"}
        >
          {signals.context_health.个会话_with_compaction}
        </span>
        <span class="card-sub">
          {#if signals.context_health.个会话_with_mid_task_compaction > 0}
            {signals.context_health.个会话_with_mid_task_compaction}
            mid-task &middot;
          {/if}
          avg {signals.context_health.avg_compaction_count.toFixed(1)}/session
        </span>
      </div>
    </div>

    <div class="chart-grid">
      <div class="chart-panel">
        <GradeDistribution
          distribution={signals.grade_distribution}
        />
      </div>
      <div class="chart-panel">
        <OutcomeDistribution
          distribution={signals.outcome_distribution}
        />
      </div>
      <div class="chart-panel wide">
        <HealthTrend trend={signals.trend} />
      </div>
      <div class="chart-panel">
        <div class="mini-table">
          <div class="table-title">By 代理</div>
          <table>
            <thead>
              <tr>
                <th>代理</th>
                <th class="num">会话</th>
                <th class="num">Avg Score</th>
                <th class="num">已完成</th>
              </tr>
            </thead>
            <tbody>
              {#each [...signals.by_agent].sort(
                (a, b) => b.session_count - a.session_count,
              ) as row}
                <tr>
                  <td>{row.agent}</td>
                  <td class="num">{row.session_count}</td>
                  <td class="num">
                    {row.avg_health_score != null
                      ? Math.round(row.avg_health_score)
                      : "--"}
                  </td>
                  <td class="num">
                    {Math.round(row.completed_rate)}%
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
      <div class="chart-panel">
        <div class="mini-table">
          <div class="table-title">By 项目</div>
          <table>
            <thead>
              <tr>
                <th>项目</th>
                <th class="num">会话</th>
                <th class="num">Avg Score</th>
                <th class="num">已完成</th>
              </tr>
            </thead>
            <tbody>
              {#each [...signals.by_project].sort(
                (a, b) => b.session_count - a.session_count,
              ) as row}
                <tr>
                  <td>{row.project}</td>
                  <td class="num">{row.session_count}</td>
                  <td class="num">
                    {row.avg_health_score != null
                      ? Math.round(row.avg_health_score)
                      : "--"}
                  </td>
                  <td class="num">
                    {Math.round(row.completed_rate)}%
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .health-section {
    margin-top: 16px;
  }
  .section-header {
    margin-bottom: 12px;
  }
  .section-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 2px;
  }
  .section-subtitle {
    font-size: 12px;
    color: var(--text-muted);
  }
  .health-summary-cards {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 12px;
  }
  .card {
    background: var(--bg-surface);
    border: 1px solid var(--border-muted);
    border-radius: var(--radius-md);
    padding: 12px;
  }
  .card-label {
    display: block;
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  .card-value {
    display: block;
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
  }
  .card-sub {
    display: block;
    font-size: 12px;
    color: var(--text-secondary);
  }
  .chart-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .chart-panel {
    background: var(--bg-surface);
    border: 1px solid var(--border-muted);
    border-radius: var(--radius-md);
    padding: 12px;
  }
  .chart-panel.wide {
    grid-column: 1 / -1;
  }
  .mini-table {
    font-size: 12px;
  }
  .table-title {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th {
    text-align: left;
    padding: 4px 0;
    color: var(--text-muted);
    font-weight: 500;
    border-bottom: 1px solid var(--border-muted);
  }
  th.num, td.num {
    text-align: right;
  }
  td {
    padding: 6px 0;
    color: var(--text-primary);
    border-bottom: 1px solid var(--bg-inset);
  }
  @media (max-width: 767px) {
    .health-summary-cards {
      grid-template-columns: repeat(2, 1fr);
    }
    .chart-grid {
      grid-template-columns: 1fr;
    }
    .chart-panel.wide {
      grid-column: 1;
    }
  }
</style>
