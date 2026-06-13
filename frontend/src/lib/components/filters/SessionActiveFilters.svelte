<script lang="ts">
  import { 个会话 } from "../../stores/个会话.svelte.js";
  import {
    agentColor,
    agentLabel,
  } from "../../utils/agents.js";

  interface Props {
    projectFilters?: string[];
    modelFilters?: string[];
    onRemove项目?: (project: string) => void;
    on清除项目s?: () => void;
    onRemoveModel?: (model: string) => void;
    on清除Models?: () => void;
  }

  let {
    projectFilters = [],
    modelFilters = [],
    onRemove项目,
    on清除项目s,
    onRemoveModel,
    on清除Models,
  }: Props = $props();

  const selected代理s = $derived(
    个会话.filters.agent
      ? 个会话.filters.agent.split(",")
      : [],
  );
  const selected机器s = $derived(
    个会话.filters.machine
      ? 个会话.filters.machine.split(",")
      : [],
  );

  const hasFilters = $derived(
    !!个会话.filters.project ||
      个会话.hasActiveFilters ||
      projectFilters.length > 0 ||
      modelFilters.length > 0,
  );

  function clear项目() {
    个会话.filters.project = "";
    个会话.activeSessionId = null;
    个会话.load();
  }

  function remove机器(machine: string) {
    个会话.toggle机器Filter(machine);
  }

  function remove代理(agent: string) {
    个会话.toggle代理Filter(agent);
  }

  function clearAll() {
    个会话.filters.project = "";
    个会话.clearSessionFilters();
    on清除项目s?.();
    on清除Models?.();
  }
</script>

{#if hasFilters}
  <div class="active-filters">
    <span class="filters-label">Filters:</span>

    {#if 个会话.filters.project}
      <button
        class="filter-chip"
        onclick={clear项目}
        title="清除 project filter"
      >
        {个会话.filters.project}
        <span class="chip-x">&times;</span>
      </button>
    {/if}

    {#each selected机器s as machine (machine)}
      <button
        class="filter-chip"
        onclick={() => remove机器(machine)}
        title="Remove {machine} filter"
      >
        {machine}
        <span class="chip-x">&times;</span>
      </button>
    {/each}

    {#each selected代理s as agent (agent)}
      <button
        class="filter-chip"
        onclick={() => remove代理(agent)}
        title="Remove {agentLabel(agent)} filter"
      >
        <span
          class="agent-chip-dot"
          style:background={agentColor(agent)}
        ></span>
        {agentLabel(agent)}
        <span class="chip-x">&times;</span>
      </button>
    {/each}

    {#if 个会话.filters.minUserMessages > 0}
      <button
        class="filter-chip"
        onclick={() => 个会话.setMinUserMessagesFilter(0)}
        title="清除 min prompts filter"
      >
        &ge;{个会话.filters.minUserMessages} prompts
        <span class="chip-x">&times;</span>
      </button>
    {/if}

    {#if 个会话.filters.recentlyActive}
      <button
        class="filter-chip"
        onclick={() => 个会话.setRecentlyActiveFilter(false)}
        title="清除 recently active filter"
      >
        Active 24h
        <span class="chip-x">&times;</span>
      </button>
    {/if}

    {#if 个会话.filters.hideUnknown项目}
      <button
        class="filter-chip"
        onclick={() => 个会话.set隐藏Unknown项目Filter(false)}
        title="清除 hidden 未知 project filter"
      >
        Unknown hidden
        <span class="chip-x">&times;</span>
      </button>
    {/if}

    {#each projectFilters as project (project)}
      <button
        class="filter-chip"
        onclick={() => onRemove项目?.(project)}
        title="Remove {project} project filter"
      >
        {project}
        <span class="chip-x">&times;</span>
      </button>
    {/each}

    {#if !个会话.filters.include开eShot}
      <button
        class="filter-chip"
        onclick={() => 个会话.setInclude开eShotFilter(true)}
        title="清除 single-turn filter"
      >
        Single-turn hidden
        <span class="chip-x">&times;</span>
      </button>
    {/if}

    {#if 个会话.filters.includeAutomated}
      <button
        class="filter-chip"
        onclick={() => 个会话.setIncludeAutomatedFilter(false)}
        title="清除 automated filter"
      >
        Automated included
        <span class="chip-x">&times;</span>
      </button>
    {/if}

    {#each modelFilters as model (model)}
      <button
        class="filter-chip"
        onclick={() => onRemoveModel?.(model)}
        title="Remove {model} model filter"
      >
        {model}
        <span class="chip-x">&times;</span>
      </button>
    {/each}

    <button
      class="clear-all"
      onclick={clearAll}
      title="清除 all filters"
    >
      清除 all
    </button>
  </div>
{/if}

<style>
  .active-filters {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 16px 6px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-muted);
    flex-shrink: 0;
    flex-wrap: wrap;
  }

  .filters-label {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .filter-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    height: 22px;
    padding: 0 6px;
    font-size: 11px;
    font-weight: 500;
    color: var(--accent-blue);
    background: color-mix(
      in srgb, var(--accent-blue) 10%, transparent
    );
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background 0.1s;
  }

  .filter-chip:hover {
    background: color-mix(
      in srgb, var(--accent-blue) 18%, transparent
    );
  }

  .agent-chip-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .chip-x {
    opacity: 0.65;
    font-size: 12px;
    line-height: 1;
  }

  .clear-all {
    font-size: 11px;
    color: var(--text-muted);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    cursor: pointer;
  }

  .clear-all:hover {
    color: var(--text-primary);
    background: var(--bg-surface-hover);
  }
</style>
