<script lang="ts">
  import { ui } from "../../stores/ui.svelte.js";
  import { sync } from "../../stores/sync.svelte.js";

  type View = "confirm" | "progress" | "done" | "error";

  let view: View = $state("confirm");
  let errorMessage: string = $state("");

  function startResync() {
    if (sync.read开ly) {
      errorMessage =
        "只读后端不支持完全重新同步。";
      view = "error";
      return;
    }
    const started = sync.triggerResync(
      () => {
        view = "done";
      },
      (err) => {
        errorMessage = err.message;
        view = "error";
      },
    );
    if (started) {
      view = "progress";
    } else if (!errorMessage) {
      errorMessage = "同步已在进行中。";
      view = "error";
    }
  }

  function close() {
    ui.activeModal = null;
  }

  function handleOverlayClick(e: MouseEvent) {
    if (
      view !== "progress" &&
      (e.target as HTMLElement).classList.contains(
        "modal-overlay",
      )
    ) {
      close();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape" && view !== "progress") {
      close();
    }
  }

  const progressPct = $derived(
    sync.progress
      ? sync.progress.个会话_total > 0
        ? (sync.progress.个会话_done /
            sync.progress.个会话_total) *
          100
        : 0
      : 0,
  );
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="modal-overlay"
  onclick={handleOverlayClick}
  onkeydown={handleKeydown}
>
  <div class="modal-panel resync-panel">
    <div class="modal-header">
      <h3 class="modal-title">完全重新同步</h3>
      {#if view !== "progress"}
        <button
          class="modal-close"
          onclick={close}
          title="关闭重新同步对话框"
          aria-label="关闭重新同步对话框"
        >
          &times;
        </button>
      {/if}
    </div>

    <div class="modal-body">
      {#if view === "confirm"}
        <p class="confirm-text">
          Re-parse all session files from scratch. Existing
          个会话 will be updated in place &mdash; no data is
          已删除. Use this after upgrading or when 个会话
          appear incorrect.
        </p>
        <div class="confirm-actions">
          <button class="modal-btn" onclick={close}>
            取消
          </button>
          <button
            class="modal-btn modal-btn-primary"
            onclick={startResync}
          >
            Start 完全重新同步
          </button>
        </div>

      {:else if view === "progress"}
        <div class="progress-view">
          <div class="modal-spinner"></div>
          <p class="progress-label">
            {#if sync.progress}
              同步中 {sync.progress.个会话_done}
              / {sync.progress.个会话_total} 个会话...
            {:else}
              准备中...
            {/if}
          </p>
          <div class="progress-bar-track">
            <div
              class="progress-bar-fill"
              style="width: {progressPct}%"
            ></div>
          </div>
        </div>

      {:else if view === "done"}
        <div class="done-view">
          {#if sync.lastSyncStats}
            <p class="done-summary">
              会话 已同步: {sync.lastSyncStats.已同步}
            </p>
            {#if sync.lastSyncStats.failed > 0}
              <p class="done-warning">
                失败: {sync.lastSyncStats.failed}
              </p>
            {/if}
          {/if}
          <div class="done-actions">
            <button
              class="modal-btn modal-btn-primary"
              onclick={close}
            >
              关闭
            </button>
          </div>
        </div>

      {:else if view === "error"}
        <div class="error-view">
          <p class="modal-error">{errorMessage}</p>
          <div class="error-actions">
            <button
              class="modal-btn modal-btn-primary"
              onclick={startResync}
            >
              重试
            </button>
            <button class="modal-btn" onclick={close}>
              关闭
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .resync-panel {
    width: 400px;
  }

  .confirm-text {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 16px;
  }

  .confirm-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }

  .progress-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 16px 0;
  }

  .progress-label {
    font-size: 12px;
    color: var(--text-secondary);
    font-variant-numeric: tabular-nums;
  }

  .progress-bar-track {
    width: 100%;
    height: 4px;
    background: var(--bg-inset);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-bar-fill {
    height: 100%;
    background: var(--accent-blue);
    border-radius: 2px;
    transition: width 0.3s;
  }

  .done-view {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .done-summary {
    font-size: 12px;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
  }

  .done-warning {
    font-size: 12px;
    color: var(--accent-orange, #e09040);
    font-variant-numeric: tabular-nums;
  }

  .done-actions {
    display: flex;
    justify-content: flex-end;
  }

  .error-view {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .error-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
</style>
