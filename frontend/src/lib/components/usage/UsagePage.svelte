<script lang="ts">
  import { onMount, onDestroy, tick, untrack } from "svelte";
  import {
    usage,
    build用量UrlParams,
    merge用量AndSessionUrlParams,
    parseWindowDays,
  } from "../../stores/usage.svelte.js";
  import {
    个会话,
    filters到Params,
    parseFilters从Params,
    splitExclude项目Param,
  } from "../../stores/个会话.svelte.js";
  import { router } from "../../stores/router.svelte.js";
  import { events } from "../../stores/events.svelte.js";
  import 用量SummaryCards from "./用量SummaryCards.svelte";
  import CostTimeSeriesChart from "./CostTimeSeriesChart.svelte";
  import AttributionPanel from "./AttributionPanel.svelte";
  import 到p会话Table from "./到p会话Table.svelte";
  import CacheEfficiencyPanel from "./CacheEfficiencyPanel.svelte";
  import DateRangeSelector from "../shared/DateRangeSelector.svelte";
  import SessionFilterControl from "../filters/SessionFilterControl.svelte";
  import SessionActiveFilters from "../filters/SessionActiveFilters.svelte";
  import FilterDropdown from "./FilterDropdown.svelte";
  import { 刷新CwIcon } from "../../icons.js";

  const REFRESH_MS = 5 * 60 * 1000;
  let refreshTimer: ReturnType<typeof setInterval> | undefined;
  let unsubEvents: (() => void) | undefined;
  let mounted = false;

  const projectItems = $derived(
    个会话.个项目.map((p) => ({
      name: p.name,
      count: p.session_count,
    })),
  );

  // Track every model we've seen in any summary response or
  // model filter — never remove one. This keeps the model
  // dropdown usable when landing on a shared filtered URL.
  let knownModels: string[] = $state([]);

  function mergeIntoKnownModels(names: string[]): void {
    if (names.length === 0) return;
    const set = new Set(knownModels);
    let changed = false;
    for (const m of names) {
      if (m && !set.has(m)) {
        set.add(m);
        changed = true;
      }
    }
    if (changed) {
      knownModels = [...set].sort();
    }
  }

  // Seed from the filtered summary response.
  $effect(() => {
    const fromSummary = (usage.summary?.model到tals ?? [])
      .map((m) => m.model);
    untrack(() => mergeIntoKnownModels(fromSummary));
  });

  // Seed from URL/local model filters before a response arrives.
  $effect(() => {
    const filtered = [
      usage.selectedModels,
    ].filter(Boolean).join(",");
    untrack(() => {
      if (!filtered) return;
      mergeIntoKnownModels(filtered.split(","));
    });
  });

  const modelItems = $derived(
    knownModels.map((m) => ({ name: m })),
  );
  const selectedModels = $derived(
    usage.selectedModels
      ? usage.selectedModels.split(",").filter(Boolean)
      : [],
  );
  const sessionUrlParams = $derived(
    filters到Params(个会话.filters),
  );
  const sessionFilterSignature = $derived(
    JSON.stringify(sessionUrlParams),
  );

  // URL-init: seed store filters from URL params when landing
  // on /usage with a deep-link. A bare /usage preserves the
  // current store state (restored from localStorage). 开ly
  // apply params that are actually present in the URL.
  const USAGE_FILTER_KEYS = new Set([
    "from", "to", "window_days",
    "model", "exclude_model",
  ]);
  const SESSION_FILTER_KEYS = new Set([
    "project", "machine", "agent",
    "date", "date_from", "date_to",
    "active_since", "exclude_project",
    "min_条消息", "max_条消息", "min_user_条消息",
    "include_one_shot", "include_automated",
  ]);
  let urlInitRan = $state(false);
  let urlWritebackReady = $state(false);
  let initialFetchDone = $state(false);
  $effect(() => {
    const route = router.route;
    const params = router.params;
    untrack(() => {
      if (route !== "usage") return;
      const hasDateParam = !!params["from"] || !!params["to"];
      const parsedWindowDays = parseWindowDays(params["window_days"]);
      const hasFilterKeys = Object.keys(params).some(
        (k) =>
          USAGE_FILTER_KEYS.has(k) ||
          SESSION_FILTER_KEYS.has(k),
      );
      const hasSessionFilterKeys = Object.keys(params).some(
        (k) => SESSION_FILTER_KEYS.has(k),
      );

      let changed = false;
      let sessionChanged = false;

      // Sync pin state from URL: dated URL pins, undated URL unpins.
      // 运行s before the !hasFilterKeys early return so a fully bare URL
      // (no exclude_* either) still flips the pin off.
      if (usage.is已固定 !== hasDateParam) {
        usage.is已固定 = hasDateParam;
        changed = true;
      }

      // Apply rolling window from URL when present and the URL is
      // not pinning a specific date range.
      if (!hasDateParam && parsedWindowDays !== null) {
        if (usage.windowDays !== parsedWindowDays) {
          usage.windowDays = parsedWindowDays;
          changed = true;
        }
      }

      if (!hasFilterKeys) {
        if (changed && urlInitRan) {
          usage.fetchAll();
        }
        urlInitRan = true;
        return;
      }
      if (hasSessionFilterKeys) {
        const nextSessionParams = filters到Params(
          parseFilters从Params(params),
        );
        const currentSessionParams = filters到Params(
          个会话.filters,
        );
        if (
          JSON.stringify(nextSessionParams) !==
          JSON.stringify(currentSessionParams)
        ) {
          个会话.init从Params(params);
          sessionChanged = true;
        }
      }
      if (params["from"] && params["from"] !== usage.from) {
        usage.from = params["from"];
        changed = true;
      }
      if (params["to"] && params["to"] !== usage.to) {
        usage.to = params["to"];
        changed = true;
      }
      const newEx项目 = splitExclude项目Param(
        params["exclude_project"],
      ).usageExcluded项目s;
      if (newEx项目 !== usage.excluded项目s) {
        usage.excluded项目s = newEx项目;
        changed = true;
      }
      if (usage.excludedModels) {
        usage.excludedModels = "";
        changed = true;
      }
      const newModel = params["model"] ?? "";
      if (newModel !== usage.selectedModels) {
        usage.selectedModels = newModel;
        if (newModel) usage.excludedModels = "";
        changed = true;
      }
      if ((changed || sessionChanged) && urlInitRan) {
        usage.fetchAll();
      }
      urlInitRan = true;
    });
  });

  // URL write-back: keep URL params in sync with filter state
  // so users can share/bookmark the view.
  $effect(() => {
    const state = {
      from: usage.from,
      to: usage.to,
      is已固定: usage.is已固定,
      windowDays: usage.windowDays,
      excluded项目s: usage.excluded项目s,
      excluded代理s: usage.excluded代理s,
      excludedModels: usage.excludedModels,
      selectedModels: usage.selectedModels,
    };
    const nextParams = merge用量AndSessionUrlParams(
      build用量UrlParams(state),
      sessionUrlParams,
    );
    const ready = urlInitRan && urlWritebackReady;
    untrack(() => {
      if (!ready || router.route !== "usage") return;
      router.replaceParams(nextParams);
    });
  });

  $effect(() => {
    const signature = sessionFilterSignature;
    const ready = urlInitRan && urlWritebackReady;
    untrack(() => {
      if (!ready || !signature || router.route !== "usage" || !mounted) {
        return;
      }
      if (!initialFetchDone) {
        initialFetchDone = true;
      }
      usage.fetchAll();
    });
  });

  onMount(() => {
    mounted = true;
    tick().then(() => {
      urlWritebackReady = true;
    });
    refreshTimer = setInterval(
      () => usage.fetchAll(),
      REFRESH_MS,
    );
    unsubEvents = events.subscribeDebounced(
      () => usage.fetchAll(),
    );
  });

  onDestroy(() => {
    if (refreshTimer !== undefined) {
      clearInterval(refreshTimer);
    }
    unsubEvents?.();
  });
</script>

<div class="usage-page">
  <div class="usage-toolbar">
    <div class="toolbar-controls">
      <div class="usage-filter-anchor">
        <SessionFilterControl
          showDisplay={false}
          show星标={false}
          align="left"
          extraActive={usage.hasActiveFilters || !!个会话.filters.project}
          on清除Extra={() => {
            个会话.filters.project = "";
            usage.clearFilters();
          }}
        />
      </div>

      <DateRangeSelector
        from={usage.from}
        to={usage.to}
        busy={usage.isQuerying}
        onChange={(from, to) => usage.setDateRange(from, to)}
        onPreset={(days) => usage.setRollingWindow(days)}
      />

      <FilterDropdown
        label="项目"
        items={projectItems}
        excludedCsv={usage.excluded项目s}
        on到ggle={(name) => usage.toggle项目(name)}
        onSelectAll={() => usage.selectAll项目s()}
        onDeselectAll={() =>
          usage.deselectAll项目s(projectItems.map((p) => p.name))}
      />

      <FilterDropdown
        label="Model"
        items={modelItems}
        excludedCsv={usage.selectedModels}
        mode="include"
        on到ggle={(name) => usage.toggleModel(name)}
        onSelectAll={() => usage.selectAllModels()}
        onDeselectAll={() =>
          usage.deselectAllModels(modelItems.map((m) => m.name))}
      />

      <button
        class="refresh-btn"
        class:querying={usage.isQuerying}
        onclick={() => usage.fetchAll()}
        disabled={usage.isQuerying}
        title="刷新"
        aria-label="刷新 usage data"
      >
        <刷新CwIcon size="14" strokeWidth="2" aria-hidden="true" />
      </button>

    </div>
  </div>

  <SessionActiveFilters
    modelFilters={selectedModels}
    on清除项目s={() => usage.selectAll项目s()}
    onRemoveModel={(model) => usage.toggleModel(model)}
    on清除Models={() => usage.selectAllModels()}
  />

  <div
    class="usage-content"
    class:querying={usage.isQuerying}
    aria-busy={usage.isQuerying}
  >
    {#if usage.isQuerying}
      <div class="query-progress" aria-hidden="true"></div>
    {/if}

    <用量SummaryCards />

    <div class="chart-panel wide">
      <CostTimeSeriesChart />
    </div>

    <div class="chart-panel wide">
      <AttributionPanel />
    </div>

    <div class="bottom-grid">
      <div class="chart-panel">
        <到p会话Table />
      </div>
      <div class="chart-panel">
        <CacheEfficiencyPanel />
      </div>
    </div>
  </div>
</div>

<style>
  .usage-page {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .usage-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 16px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-muted);
    flex-shrink: 0;
  }

  .toolbar-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    flex: 1;
  }

  .usage-filter-anchor {
    position: relative;
    display: flex;
    align-items: center;
  }

  .refresh-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    cursor: pointer;
    transition: background 0.1s, color 0.1s, opacity 0.1s;
  }

  .refresh-btn:hover:not(:disabled) {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .refresh-btn:disabled {
    cursor: default;
    opacity: 0.75;
  }

  .refresh-btn.querying :全局(svg) {
    animation: spin 0.8s linear infinite;
  }

  .usage-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: relative;
    transition: opacity 0.12s;
  }

  .usage-content.querying {
    opacity: 0.88;
  }

  .query-progress {
    position: sticky;
    top: 0;
    z-index: 4;
    height: 2px;
    margin: -16px -16px 14px;
    overflow: hidden;
    background: color-mix(
      in srgb,
      var(--accent-blue) 16%,
      transparent
    );
  }

  .query-progress::before {
    content: "";
    display: block;
    width: 38%;
    height: 100%;
    background: var(--accent-blue);
    border-radius: 999px;
    animation: query-progress 1s ease-in-out infinite;
  }

  .chart-panel {
    background: var(--bg-surface);
    border: 1px solid var(--border-muted);
    border-radius: var(--radius-md);
    padding: 12px;
    min-width: 0;
  }

  .chart-panel.wide {
    width: 100%;
  }

  .bottom-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  @media (max-width: 800px) {
    .bottom-grid {
      grid-template-columns: 1fr;
    }
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @keyframes query-progress {
    0% {
      transform: translateX(-105%);
    }
    100% {
      transform: translateX(265%);
    }
  }
</style>
