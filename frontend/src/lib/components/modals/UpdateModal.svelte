<script lang="ts">
  import { ui } from "../../stores/ui.svelte.js";
  import { sync } from "../../stores/sync.svelte.js";

  function close() {
    ui.activeModal = null;
  }

  function handleOverlayClick(e: MouseEvent) {
    if (
      (e.target as HTMLElement).classList.contains(
        "modal-overlay",
      )
    ) {
      close();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") {
      close();
    }
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="modal-overlay"
  onclick={handleOverlayClick}
  onkeydown={handleKeydown}
>
  <div class="modal-panel update-panel">
    <div class="modal-header">
      <h3 class="modal-title">软件更新</h3>
      <button
        class="modal-close"
        onclick={close}
        title="关闭 update dialog"
        aria-label="关闭 update dialog"
      >
        &times;
      </button>
    </div>

    <div class="modal-body">
      {#if sync.updateAvailable && sync.latest版本}
        <p class="update-text">
          有新版本可用：
          <strong>{sync.latest版本}</strong>
        </p>
        <p class="update-current">
          您正在运行
          {sync.server版本?.version ?? "未知"}.
        </p>
        <p class="update-instructions">
          运行 <code>agentsview update</code> on the command
          line to install.
        </p>
      {:else}
        <p class="update-text">
          您正在运行最新版本
          ({sync.server版本?.version ?? "未知"}).
        </p>
      {/if}
      <div class="update-actions">
        <button
          class="modal-btn modal-btn-primary"
          onclick={close}
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</div>

<style>
  .update-panel {
    width: 400px;
  }

  .update-text {
    font-size: 12px;
    color: var(--text-primary);
    line-height: 1.5;
  }

  .update-current {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-top: 4px;
  }

  .update-instructions {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-top: 8px;
  }

  .update-instructions code {
    font-family: var(--font-mono);
    background: var(--bg-inset);
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 11px;
  }

  .update-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }
</style>
