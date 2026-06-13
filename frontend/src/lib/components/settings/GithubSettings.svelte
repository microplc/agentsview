<script lang="ts">
  import 设置Section from "./设置Section.svelte";
  import { settings } from "../../stores/settings.svelte.js";
  import { ConfigService } from "../../api/generated/index";
  import { configure生成dClient } from "../../api/runtime.js";

  let tokenInput: string = $state("");
  let saving: boolean = $state(false);
  let error: string | null = $state(null);
  let success: string | null = $state(null);

  async function handle保存() {
    if (!tokenInput.trim()) return;
    saving = true;
    error = null;
    success = null;
    try {
      configure生成dClient();
      await ConfigService.postApiV1ConfigGithub({
        requestBody: { token: tokenInput.trim() },
      });
      tokenInput = "";
      success = "GitHub 令牌已保存。";
      await settings.load();
    } catch (e) {
      error = e instanceof 错误 ? e.message : "失败 to save token";
    } finally {
      saving = false;
    }
  }
</script>

<设置Section
  title="GitHub 集成"
  description="到ken used for publishing 个会话 as GitHub Gists."
>
  <div class="status-row">
    <span class="status-label">状态</span>
    <span class="status-value" class:configured={settings.github已配置}>
      {settings.github已配置 ? "已配置" : "未配置"}
    </span>
  </div>

  <div class="token-row">
    <input
      class="setting-input"
      type="password"
      placeholder="ghp_..."
      bind:value={tokenInput}
    />
    <button
      class="save-btn"
      disabled={saving || !tokenInput.trim()}
      onclick={handle保存}
    >
      {saving ? "保存中..." : "保存 token"}
    </button>
  </div>

  {#if error}
    <p class="msg error">{error}</p>
  {/if}
  {#if success}
    <p class="msg success">{success}</p>
  {/if}
</设置Section>

<style>
  .status-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
  }

  .status-value {
    font-size: 12px;
    color: var(--text-muted);
  }

  .status-value.configured {
    color: var(--accent-green);
  }

  .token-row {
    display: flex;
    gap: 8px;
  }

  .setting-input {
    flex: 1;
    height: 30px;
    padding: 0 10px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-family: var(--font-mono, monospace);
    color: var(--text-primary);
    background: var(--bg-inset);
    border: 1px solid var(--border-muted);
    transition: border-color 0.15s;
  }

  .setting-input:focus {
    outline: none;
    border-color: var(--accent-blue);
  }

  .save-btn {
    height: 30px;
    padding: 0 14px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 500;
    color: white;
    background: var(--accent-blue);
    border: none;
    cursor: pointer;
    white-space: nowrap;
    transition: opacity 0.12s;
  }

  .save-btn:hover:not(:disabled) {
    opacity: 0.9;
  }

  .save-btn:disabled {
    opacity: 0.6;
    cursor: default;
  }

  .msg {
    font-size: 11px;
    margin: 0;
  }

  .msg.error {
    color: var(--accent-red, #ef4444);
  }

  .msg.success {
    color: var(--accent-green, #22c55e);
  }
</style>
