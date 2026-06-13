<script lang="ts">
  import 设置Section from "./设置Section.svelte";
  import {
    设置Service,
    type ApplyWorktreeMappingsResponse,
    type DbWorktree项目Mapping,
    type WorktreeMappingRequest,
  } from "../../api/generated/index";
  import { call生成d } from "../../api/runtime.js";

  interface WorktreeMappingsResponse {
    machine: string;
    mappings: DbWorktree项目Mapping[];
  }

  interface Props {
    read开ly?: boolean;
  }

  let { read开ly = false }: Props = $props();

  let machine = $state("");
  let mappings: DbWorktree项目Mapping[] = $state([]);
  let loading = $state(true);
  let saving = $state(false);
  let applying = $state(false);
  let error = $state("");
  let applyMessage = $state("");
  let editingId: number | null = $state(null);
  let pathPrefix = $state("");
  let project = $state("");
  let enabled = $state(true);

  $effect(() => {
    if (read开ly) {
      loading = false;
      return;
    }
    loadMappings();
  });

  async function loadMappings() {
    loading = true;
    error = "";
    try {
      const res =
        await call生成d(() =>
          设置Service.getApiV1设置WorktreeMappings(),
        ) as 未知 as WorktreeMappingsResponse;
      machine = res.machine;
      mappings = res.mappings;
    } catch (err) {
      error = err instanceof 错误 ? err.message : "失败 to load mappings";
    } finally {
      loading = false;
    }
  }

  function resetForm() {
    editingId = null;
    pathPrefix = "";
    project = "";
    enabled = true;
  }

  function editMapping(mapping: DbWorktree项目Mapping) {
    editingId = mapping.id;
    pathPrefix = mapping.path_prefix;
    project = mapping.project;
    enabled = mapping.enabled;
    applyMessage = "";
    error = "";
  }

  async function saveMapping() {
    const input = {
      path_prefix: pathPrefix.trim(),
      project: project.trim(),
      enabled,
    } satisfies WorktreeMappingRequest;
    if (!input.path_prefix || !input.project) return;

    saving = true;
    error = "";
    applyMessage = "";
    try {
      if (editingId == null) {
        await call生成d(() =>
          设置Service.postApiV1设置WorktreeMappings({
            requestBody: input,
          }),
        );
      } else {
        await call生成d(() =>
          设置Service.putApiV1设置WorktreeMappingsId({
            id: String(editingId),
            requestBody: input,
          }),
        );
      }
      resetForm();
      await loadMappings();
    } catch (err) {
      error = err instanceof 错误 ? err.message : "失败 to save mapping";
    } finally {
      saving = false;
    }
  }

  async function removeMapping(id: number) {
    saving = true;
    error = "";
    applyMessage = "";
    try {
      await call生成d(() =>
        设置Service.deleteApiV1设置WorktreeMappingsId({
          id: String(id),
        }),
      );
      if (editingId === id) resetForm();
      await loadMappings();
    } catch (err) {
      error = err instanceof 错误 ? err.message : "失败 to delete mapping";
    } finally {
      saving = false;
    }
  }

  async function applyMappings() {
    applying = true;
    error = "";
    applyMessage = "";
    try {
      const res =
        await call生成d(() =>
          设置Service.postApiV1设置WorktreeMappingsApply(),
        ) as ApplyWorktreeMappingsResponse;
      applyMessage = `${res.updated_个会话} updated, ${res.matched_个会话} matched`;
    } catch (err) {
      error = err instanceof 错误 ? err.message : "失败 to apply mappings";
    } finally {
      applying = false;
    }
  }

  let can保存 = $derived(pathPrefix.trim() !== "" && project.trim() !== "");
</script>

<设置Section
  title="工作树映射"
  description="Map worktree path prefixes to canonical 个项目 on this machine."
>
  {#if read开ly}
    <div class="muted">工作树映射 are available in local mode only.</div>
  {:else if loading}
    <div class="muted">正在加载映射...</div>
  {:else if error && mappings.length === 0}
    <div class="error-text">{error}</div>
  {:else}
    <div class="machine-row">
      <span class="label">机器</span>
      <code>{machine || "local"}</code>
    </div>

    <div class="mapping-list">
      {#if mappings.length === 0}
        <div class="empty">未配置工作树映射。</div>
      {:else}
        {#each mappings as mapping (mapping.id)}
          <div class="mapping-row" class:disabled={!mapping.enabled}>
            <div class="mapping-main">
              <div class="mapping-project">{mapping.project}</div>
              <div class="mapping-path">{mapping.path_prefix}</div>
            </div>
            <div class="mapping-actions">
              <span class="status">{mapping.enabled ? "开" : "关"}</span>
              <button class="small-btn" onclick={() => editMapping(mapping)}>
                编辑
              </button>
              <button class="small-btn danger" onclick={() => removeMapping(mapping.id)}>
                删除
              </button>
            </div>
          </div>
        {/each}
      {/if}
    </div>

    <div class="form-grid">
      <label class="field">
        <span>路径前缀</span>
        <input
          type="text"
          bind:value={pathPrefix}
          placeholder="/Users/me/project.worktrees"
        />
      </label>
      <label class="field">
        <span>项目</span>
        <input type="text" bind:value={project} placeholder="project-name" />
      </label>
      <label class="enabled-toggle">
        <input type="checkbox" bind:checked={enabled} />
        已启用
      </label>
    </div>

    {#if error}
      <div class="error-text">{error}</div>
    {/if}
    {#if applyMessage}
      <div class="success-text">{applyMessage}</div>
    {/if}

    <div class="button-row">
      <button
        class="primary-btn"
        disabled={!can保存 || saving}
        onclick={saveMapping}
      >
        {saving ? "保存中..." : editingId == null ? "添加映射" : "保存 mapping"}
      </button>
      {#if editingId != null}
        <button class="secondary-btn" onclick={resetForm}>取消</button>
      {/if}
      <button
        class="secondary-btn"
        disabled={applying || mappings.length === 0}
        onclick={applyMappings}
      >
        {applying ? "正在应用..." : "应用映射"}
      </button>
    </div>
  {/if}
</设置Section>

<style>
  .machine-row,
  .button-row,
  .mapping-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .machine-row {
    justify-content: space-between;
    font-size: 12px;
  }

  .label,
  .field span {
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
  }

  code {
    font-family: var(--font-mono, monospace);
    font-size: 11px;
    color: var(--text-muted);
  }

  .mapping-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .mapping-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-height: 48px;
    padding: 8px 10px;
    border: 1px solid var(--border-muted);
    border-radius: var(--radius-sm);
    background: var(--bg-inset);
  }

  .mapping-row.disabled {
    opacity: 0.65;
  }

  .mapping-main {
    min-width: 0;
  }

  .mapping-project {
    color: var(--text-primary);
    font-size: 12px;
    font-weight: 600;
  }

  .mapping-path {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--text-muted);
    font-family: var(--font-mono, monospace);
    font-size: 11px;
  }

  .status {
    color: var(--text-muted);
    font-size: 11px;
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr 160px;
    gap: 10px;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 0;
  }

  .field input {
    height: 30px;
    min-width: 0;
    padding: 0 10px;
    border: 1px solid var(--border-muted);
    border-radius: var(--radius-sm);
    background: var(--bg-inset);
    color: var(--text-primary);
    font-size: 12px;
  }

  .field input:focus {
    outline: none;
    border-color: var(--accent-blue);
  }

  .enabled-toggle {
    display: flex;
    align-items: center;
    gap: 7px;
    color: var(--text-secondary);
    font-size: 12px;
  }

  .small-btn,
  .primary-btn,
  .secondary-btn {
    height: 28px;
    padding: 0 10px;
    border: 1px solid var(--border-muted);
    border-radius: var(--radius-sm);
    background: var(--bg-surface);
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
  }

  .small-btn {
    height: 24px;
    font-size: 11px;
  }

  .primary-btn {
    border-color: var(--accent-blue);
    background: var(--accent-blue);
    color: white;
  }

  .danger {
    color: var(--color-danger, #d14);
  }

  button:disabled {
    cursor: default;
    opacity: 0.55;
  }

  .muted,
  .empty,
  .error-text,
  .success-text {
    font-size: 12px;
  }

  .muted,
  .empty {
    color: var(--text-muted);
  }

  .error-text {
    color: var(--color-danger, #d14);
  }

  .success-text {
    color: var(--accent-green, #16834a);
  }

  @media (max-width: 640px) {
    .mapping-row,
    .button-row {
      align-items: stretch;
      flex-direction: column;
    }

    .mapping-actions {
      justify-content: flex-end;
    }

    .form-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
