<script lang="ts">
  import { ui } from "../../stores/ui.svelte.js";
  import { sync } from "../../stores/sync.svelte.js";

  const isMac = navigator.platform.toUpperCase().includes("MAC");
  const mod = isMac ? "Cmd" : "Ctrl";

  const baseShortcuts = [
    { key: `${mod}+K`, action: "打开 command palette" },
    { key: `${mod}+F / /`, action: "在会话中查找" },
    { key: "Esc", action: "关闭 palette / modal / find" },
    { key: "j / \u2193", action: "下一条消息" },
    { key: "k / \u2191", action: "上一条消息" },
    { key: "]", action: "下一个会话" },
    { key: "[", action: "上一个会话" },
    { key: "o", action: "切换排序顺序" },
    { key: "l", action: "切换消息布局" },
    { key: "r", action: "触发同步" },
    { key: "s", action: "标记/取消标记会话" },
    { key: "e", action: "导出会话" },
    { key: "p", action: "发布到 Gist" },
    { key: "c", action: "复制恢复命令" },
    { key: "Del", action: "删除 session" },
    { key: "?", action: "显示此模态框" },
  ];

  const zoomShortcuts = [
    { key: `${mod}++`, action: "放大" },
    { key: `${mod}+-`, action: "缩小" },
    { key: `${mod}+0`, action: "重置缩放" },
  ];

  const shortcuts = sync.isDesktop
    ? [...baseShortcuts, ...zoomShortcuts]
    : baseShortcuts;

  function handleOverlayClick(e: MouseEvent) {
    if (
      (e.target as HTMLElement).classList.contains(
        "shortcuts-overlay",
      )
    ) {
      ui.activeModal = null;
    }
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="shortcuts-overlay"
  onclick={handleOverlayClick}
  onkeydown={(e) => {
    if (e.key === "Escape") ui.activeModal = null;
  }}
>
  <div class="shortcuts-modal">
    <div class="shortcuts-header">
      <h3 class="shortcuts-title">键盘快捷键</h3>
      <button
        class="close-btn"
        onclick={() => ui.activeModal = null}
        title="关闭 shortcuts"
        aria-label="关闭 shortcuts"
      >
        &times;
      </button>
    </div>

    <div class="shortcuts-list">
      {#each shortcuts as shortcut}
        <div class="shortcut-row">
          <kbd class="shortcut-key">{shortcut.key}</kbd>
          <span class="shortcut-action">{shortcut.action}</span>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .shortcuts-overlay {
    position: fixed;
    inset: 0;
    background: var(--overlay-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .shortcuts-modal {
    width: 360px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    overflow: hidden;
  }

  .shortcuts-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-default);
  }

  .shortcuts-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .close-btn {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: var(--text-muted);
    border-radius: var(--radius-sm);
  }

  .close-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .shortcuts-list {
    padding: 8px 0;
  }

  .shortcut-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 5px 16px;
  }

  .shortcut-key {
    font-family: var(--font-mono);
    font-size: 11px;
    padding: 1px 6px;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    background: var(--bg-inset);
    color: var(--text-secondary);
    min-width: 60px;
    text-align: center;
  }

  .shortcut-action {
    font-size: 12px;
    color: var(--text-secondary);
  }
</style>
