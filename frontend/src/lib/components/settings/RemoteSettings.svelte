<script lang="ts">
  import 设置Section from "./设置Section.svelte";
  import { settings } from "../../stores/settings.svelte.js";
  import {
    get服务器Url,
    set服务器Url,
    getAuth到ken,
    setAuth到ken,
    isRemote连接ion,
  } from "../../api/runtime.js";

  let serverUrl: string = $state(get服务器Url());
  let tokenInput: string = $state(getAuth到ken());
  let testing: boolean = $state(false);
  let testResult: { ok: boolean; message: string } | null = $state(null);
  let saving: boolean = $state(false);
  let saveMsg: string | null = $state(null);
  let remote到ggling: boolean = $state(false);

  let isRemote: boolean = $derived(isRemote连接ion());
  let copied: boolean = $state(false);

  async function handleTest连接ion() {
    if (!serverUrl.trim()) return;
    testing = true;
    testResult = null;
    try {
      const base = serverUrl.replace(/\/+$/, "");
      const headers: Record<string, string> = {};
      if (tokenInput.trim()) {
        headers["作者ization"] = `Bearer ${tokenInput.trim()}`;
      }
      const res = await fetch(`${base}/api/v1/version`, { headers });
      if (res.ok) {
        const data = await res.json();
        testResult = {
          ok: true,
          message: `连接ed (v${data.version || "未知"})`,
        };
      } else {
        testResult = { ok: false, message: `服务器 returned ${res.status}` };
      }
    } catch (e) {
      testResult = {
        ok: false,
        message: e instanceof 错误 ? e.message : "连接ion failed",
      };
    } finally {
      testing = false;
    }
  }

  function handle连接() {
    if (!serverUrl.trim()) return;
    const url = serverUrl.replace(/\/+$/, "");
    set服务器Url(url);
    setAuth到ken(tokenInput.trim());
    saveMsg = "连接ed. Reloading...";
    setTimeout(() => window.location.reload(), 500);
  }

  function handle断开连接() {
    // 清除 the remote token before clearing the URL, so the
    // scoped key resolves to the remote server's token.
    setAuth到ken("");
    set服务器Url("");
    saveMsg = "断开连接ed. Reloading...";
    setTimeout(() => window.location.reload(), 500);
  }

  async function handle到ggleRemote() {
    remote到ggling = true;
    try {
      await settings.save({ require_auth: !settings.requireAuth });
    } finally {
      remote到ggling = false;
    }
  }

  function handle复制到ken() {
    if (!settings.auth到ken) return;
    navigator.clipboard.writeText(settings.auth到ken);
    copied = true;
    setTimeout(() => (copied = false), 2000);
  }
</script>

<设置Section
  title="远程访问"
  description="连接 to a remote agentsview server or enable remote access for this instance."
>
  {#if !isRemote}
    <div class="subsection">
      <div class="toggle-row">
        <span class="toggle-label">Require auth token</span>
        <button
          class="toggle-btn"
          class:active={settings.requireAuth}
          disabled={remote到ggling}
          onclick={handle到ggleRemote}
        >
          {settings.requireAuth ? "已启用" : "已禁用"}
        </button>
      </div>

      <p class="restart-note">
        Note: 到ggling auth requires a server restart to take effect.
      </p>

      {#if settings.requireAuth && settings.auth到ken}
        <div class="security-warning">
          Warning: Remote connections use unencrypted HTTP. Use a secure
          tunnel (Tailscale, SSH tunnel, or a reverse proxy with TLS) to
          protect your data in transit.
        </div>

        <div class="token-display">
          <span class="field-label">身份验证令牌</span>
          <div class="token-row">
            <code class="token-value">{settings.auth到ken}</code>
            <button class="copy-btn" onclick={handle复制到ken}>
              {copied ? "已复制" : "复制"}
            </button>
          </div>
        </div>

        <div class="server-info">
          <span class="field-label">服务器</span>
          {#if settings.host === "0.0.0.0" || settings.host === "::"}
            <span class="info-value">
              Listening on all interfaces (port {settings.port}).
              连接 using your machine's IP address or hostname.
            </span>
          {:else}
            <code class="info-value"
              >http://{settings.host}:{settings.port}</code
            >
          {/if}
        </div>
      {/if}
    </div>

    <div class="divider"></div>
  {/if}

  <div class="subsection">
    <span class="subsection-title">
      {isRemote ? "远程连接" : "连接 to Remote 服务器"}
    </span>

    {#if isRemote}
      <div class="connected-info">
        <span class="field-label">已连接到</span>
        <code class="info-value">{get服务器Url()}</code>
      </div>
      <button class="disconnect-btn" onclick={handle断开连接}>
        断开连接
      </button>
    {:else}
      <div class="field">
        <label class="field-label" for="remote-url">服务器 URL</label>
        <input
          id="remote-url"
          class="setting-input"
          type="url"
          placeholder="http://192.168.1.100:8080"
          bind:value={serverUrl}
        />
      </div>

      <div class="field">
        <label class="field-label" for="remote-token">身份验证令牌</label>
        <input
          id="remote-token"
          class="setting-input"
          type="password"
          placeholder="粘贴身份验证令牌 from server"
          bind:value={tokenInput}
        />
      </div>

      <div class="actions">
        <button
          class="test-btn"
          disabled={testing || !serverUrl.trim()}
          onclick={handleTest连接ion}
        >
          {testing ? "测试中..." : "测试连接"}
        </button>
        <button
          class="connect-btn"
          disabled={saving || !serverUrl.trim()}
          onclick={handle连接}
        >
          连接
        </button>
      </div>

      {#if testResult}
        <p class="msg" class:success={testResult.ok} class:error={!testResult.ok}>
          {testResult.message}
        </p>
      {/if}

      {#if saveMsg}
        <p class="msg success">{saveMsg}</p>
      {/if}
    {/if}
  </div>
</设置Section>

<style>
  .subsection {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .subsection-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .divider {
    border-top: 1px solid var(--border-muted);
    margin: 2px 0;
  }

  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }

  .toggle-label {
    font-size: 12px;
    color: var(--text-primary);
  }

  .toggle-btn {
    height: 26px;
    padding: 0 12px;
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-weight: 500;
    border: 1px solid var(--border-muted);
    cursor: pointer;
    background: var(--bg-inset);
    color: var(--text-secondary);
    transition:
      background 0.12s,
      color 0.12s;
  }

  .toggle-btn.active {
    background: var(--accent-green, #22c55e);
    color: white;
    border-color: transparent;
  }

  .toggle-btn:disabled {
    opacity: 0.6;
    cursor: default;
  }

  .token-display,
  .server-info,
  .connected-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .field-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
  }

  .token-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .token-value {
    font-size: 11px;
    font-family: var(--font-mono, monospace);
    color: var(--text-primary);
    background: var(--bg-inset);
    padding: 4px 8px;
    border-radius: var(--radius-sm);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
    min-width: 0;
  }

  .copy-btn {
    height: 24px;
    padding: 0 10px;
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary);
    background: var(--bg-inset);
    border: 1px solid var(--border-muted);
    cursor: pointer;
    white-space: nowrap;
    transition: opacity 0.12s;
  }

  .copy-btn:hover {
    opacity: 0.8;
  }

  .info-value {
    font-size: 12px;
    font-family: var(--font-mono, monospace);
    color: var(--text-primary);
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .setting-input {
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

  .actions {
    display: flex;
    gap: 8px;
  }

  .test-btn,
  .connect-btn,
  .disconnect-btn {
    height: 30px;
    padding: 0 14px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 500;
    border: none;
    cursor: pointer;
    white-space: nowrap;
    transition: opacity 0.12s;
  }

  .test-btn {
    color: var(--text-primary);
    background: var(--bg-inset);
    border: 1px solid var(--border-muted);
  }

  .connect-btn {
    color: white;
    background: var(--accent-blue);
  }

  .disconnect-btn {
    color: white;
    background: var(--accent-red, #ef4444);
  }

  .test-btn:hover:not(:disabled),
  .connect-btn:hover:not(:disabled),
  .disconnect-btn:hover:not(:disabled) {
    opacity: 0.9;
  }

  .test-btn:disabled,
  .connect-btn:disabled {
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

  .restart-note {
    font-size: 11px;
    color: var(--text-muted);
    margin: 0;
    font-style: italic;
  }

  .security-warning {
    font-size: 11px;
    color: var(--accent-amber, #f59e0b);
    background: color-mix(in srgb, var(--accent-amber, #f59e0b) 8%, transparent);
    border: 1px solid color-mix(in srgb, var(--accent-amber, #f59e0b) 25%, transparent);
    border-radius: var(--radius-sm);
    padding: 8px 10px;
    line-height: 1.5;
  }
</style>
