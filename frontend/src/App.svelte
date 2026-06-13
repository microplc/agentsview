<script lang="ts">
  import { onMount, untrack } from "svelte";
  import AppHeader from "./lib/components/layout/AppHeader.svelte";
  import ThreeColumnLayout from "./lib/components/layout/ThreeColumnLayout.svelte";
  import SessionBreadcrumb from "./lib/components/layout/SessionBreadcrumb.svelte";
  import 状态Bar from "./lib/components/layout/状态Bar.svelte";
  import SessionList from "./lib/components/sidebar/SessionList.svelte";
  import MessageList from "./lib/components/content/MessageList.svelte";
  import SessionVitals from "./lib/components/content/SessionVitals.svelte";
  import { sessionActivity } from "./lib/stores/sessionActivity.svelte.js";
  import { sessionTiming } from "./lib/stores/sessionTiming.svelte.js";
  import CommandPalette from "./lib/components/command-palette/CommandPalette.svelte";
  import AboutModal from "./lib/components/modals/AboutModal.svelte";
  import ShortcutsModal from "./lib/components/modals/ShortcutsModal.svelte";
  import PublishModal from "./lib/components/modals/PublishModal.svelte";
  import ResyncModal from "./lib/components/modals/ResyncModal.svelte";
  import UpdateModal from "./lib/components/modals/UpdateModal.svelte";
  import Confirm删除Modal from "./lib/components/modals/Confirm删除Modal.svelte";
  import AnalyticsPage from "./lib/components/analytics/AnalyticsPage.svelte";
  import 用量Page from "./lib/components/usage/用量Page.svelte";
  import 趋势Page from "./lib/components/trends/趋势Page.svelte";
  import 洞察Page from "./lib/components/insights/洞察Page.svelte";
  import 已固定Page from "./lib/components/pinned/已固定Page.svelte";
  import 回收站Page from "./lib/components/trash/回收站Page.svelte";
  import 设置Page from "./lib/components/settings/设置Page.svelte";
  import { 个会话, filters到Params } from "./lib/stores/个会话.svelte.js";
  import { 条消息 } from "./lib/stores/条消息.svelte.js";
  import { sync } from "./lib/stores/sync.svelte.js";
  import { ui } from "./lib/stores/ui.svelte.js";
  import { router } from "./lib/stores/router.svelte.js";
  import { starred } from "./lib/stores/starred.svelte.js";
  import { pins } from "./lib/stores/pins.svelte.js";
  import { settings } from "./lib/stores/settings.svelte.js";
  import { setAuth到ken, getAuth到ken, set服务器Url, getBase } from "./lib/api/runtime.js";
  import { setupVisibilityHealthCheck } from "./lib/utils/health.js";
  import { registerShortcuts } from "./lib/utils/keyboard.js";
  import { shouldAutoSwitchTranscriptMode到普通 } from "./lib/utils/transcript-mode.js";

  let 全局Auth到ken: string = $state("");

  function handleGlobalAuth() {
    const token = 全局Auth到ken.trim();
    if (!token) return;
    setAuth到ken(token);
    // Full reload ensures all stores (settings, 个会话, starred,
    // sync, pins, etc.) reinitialize with the new credentials.
    window.location.reload();
  }
  import type { DisplayItem } from "./lib/utils/display-items.js";
  import {
    parseContent,
    enrichSegments,
  } from "./lib/utils/content-parser.js";

  let messageListRef:
    | {
        scroll到Ordinal: (o: number) => void;
        getDisplayItems: () => DisplayItem[];
        get普通DisplayItems: () => DisplayItem[];
      }
    | undefined = $state(undefined);

  // Load active session's 条消息 when selection changes.
  // 开ly track activeSessionId — untrack the rest to prevent
  // reactive loops from 条消息.loading / 条消息.条消息.
  $effect(() => {
    const id = 个会话.activeSessionId;
    untrack(() => {
      // Preserve selection when a pending scroll is queued
      // for this specific session (e.g. search result
      // navigation sets session + ordinal before this effect
      // fires). 清除 if the pending scroll targets a
      // different session or there is no pending scroll.
      const pendingMatchesSession =
        ui.pendingScrollOrdinal !== null &&
        (ui.pendingScrollSession === null ||
          ui.pendingScrollSession === id);
      if (!pendingMatchesSession) {
        ui.clearSelection();
        ui.pendingScrollOrdinal = null;
        ui.pendingScrollSession = null;
      }
      if (id) {
        if (ui.isMobileViewport) {
          ui.closeSidebar();
        }
        条消息.loadSession(id);
        个会话.loadChild会话(id);
        sessionTiming.load(id);
        sync.watchSession(
          id,
          () => {
            条消息.reload();
            个会话.refreshActiveSession();
            个会话.loadChild会话(id);
            if (ui.vitals打开) {
              sessionActivity.reload(id);
            } else {
              sessionActivity.invalidate();
            }
          },
          (t) => {
            sessionTiming.applyEvent(t);
          },
        );
        pins.loadForSession(id);
      } else {
        sessionActivity.clear();
        sessionTiming.reset();
        条消息.clear();
        个会话.child会话 = new Map();
        sync.unwatchSession();
        pins.clearSession();
      }
    });
  });

  // Scroll to pending ordinal once 条消息 finish loading.
  // If the target message is hidden specifically because thinking
  // is disabled, auto-enable thinking so the message becomes visible.
  // Messages hidden by other block filters (tool/code/user/assistant)
  // are left alone — auto-changing unrelated filters is unexpected.
  $effect(() => {
    const ordinal = ui.pendingScrollOrdinal;
    const loading = 条消息.loading;
    const thinkingVisible = ui.isBlockVisible("thinking");
    untrack(() => {
      if (ordinal === null || loading || !messageListRef) return;

      const items = messageListRef.getDisplayItems();
      const normalItems =
        messageListRef.get普通DisplayItems();
      const found = items.some((item) =>
        item.ordinals.includes(ordinal),
      );

      if (!found) {
        if (
          shouldAutoSwitchTranscriptMode到普通(
            ui.transcriptMode,
            ordinal,
            items,
            normalItems,
          )
        ) {
          ui.setTranscriptMode("normal");
          return; // effect re-runs with normal transcript mode
        }

        // 开ly auto-enable thinking if the ordinal is loaded
        // but filtered out *specifically* due to hidden thinking.
        // If it's outside the loaded window, don't change filters.
        // Auto-enable thinking filter when navigating to a message
        // that contains a thinking block.
        const msg = 条消息.条消息.find(
          (m) => m.ordinal === ordinal,
        );
        if (msg && !thinkingVisible) {
          const segs = enrichSegments(
            parseContent(
              msg.content,
              msg.has_tool_use,
              msg.id,
              msg.content_length,
            ),
            msg.tool_calls,
          );
          const hasThinkingSegment = segs.some(
            (s) => s.type === "thinking",
          );
          if (hasThinkingSegment) {
            ui.setBlockVisible("thinking", true);
            return; // effect re-runs with thinking visible
          }
        }
      }

      messageListRef.scroll到Ordinal(ordinal);
      // Ensure highlight is set (the session-change effect
      // may have cleared it before this effect ran).
      ui.selectedOrdinal = ordinal;
      ui.pendingScrollOrdinal = null;
      ui.pendingScrollSession = null;
    });
  });

  function navigateMessage(delta: number) {
    const items = messageListRef?.getDisplayItems();
    if (!items || items.length === 0) return;

    const sorted = ui.sortNewestFirst
      ? [...items].reverse()
      : items;

    const selected = ui.selectedOrdinal;
    if (selected === null) {
      const first = sorted[0]!;
      navigate到MessageOrdinal(first.ordinals[0]!);
      return;
    }

    const curIdx = sorted.findIndex((item) =>
      item.ordinals.includes(selected),
    );
    const nextIdx = Math.max(
      0,
      Math.min(sorted.length - 1, curIdx + delta),
    );
    if (nextIdx === curIdx) return;

    const next = sorted[nextIdx]!;
    navigate到MessageOrdinal(next.ordinals[0]!);
  }

  function navigate到MessageOrdinal(ordinal: number) {
    if (ui.followLatest) {
      ui.setFollowLatest(false);
    }
    ui.selectOrdinal(ordinal);
    messageListRef?.scroll到Ordinal(ordinal);
  }

  /** True when URL params contain session filter keys (deep-link). */
  const SESSION_FILTER_KEYS = new Set([
    "project", "machine", "agent", "date", "date_from", "date_to",
    "active_since", "exclude_project", "min_条消息", "max_条消息",
    "min_user_条消息", "include_one_shot", "include_automated",
  ]);
  function hasFilterParams(params: Record<string, string>): boolean {
    return Object.keys(params).some((k) => SESSION_FILTER_KEYS.has(k));
  }

  // React to route changes: reload 个会话 and apply URL params.
  // 开ly apply URL deep-link params (init从Params) when the URL
  // actually contains filter keys — a bare /个会话 preserves the
  // current store state (restored from localStorage).
  // 开ly track route and params — NOT sessionId.
  $effect(() => {
    const route = router.route;
    const params = router.params;
    untrack(() => {
      const sid = router.sessionId;
      if (!sid && route === "个会话" && hasFilterParams(params)) {
        个会话.init从Params(params);
      }
      个会话.load();
      个会话.load项目s();
      个会话.load代理s();
    });
  });

  // Deep-link: select session from URL and handle ?msg param.
  $effect(() => {
    const sid = router.sessionId;
    const msgParam = router.params["msg"] ?? null;
    untrack(() => {
      if (sid) {
        if (sid !== 个会话.activeSessionId) {
          个会话.navigate到Session(sid);
        }
        if (msgParam) {
          if (msgParam === "last") {
            ui.pendingScrollOrdinal = -1;
            ui.pendingScrollSession = sid;
          } else {
            const ordinal = parseInt(msgParam, 10);
            if (Number.isFinite(ordinal)) {
              ui.scroll到Ordinal(ordinal, sid);
            }
          }
        }
      } else if (router.route === "个会话") {
        if (个会话.activeSessionId !== null) {
          个会话.deselectSession();
        }
      }
    });
  });

  // Resolve msg=last once 条消息 are loaded.
  $effect(() => {
    const pending = ui.pendingScrollOrdinal;
    const loading = 条消息.loading;
    const msgs = 条消息.条消息;
    untrack(() => {
      if (pending !== -1 || loading || msgs.length === 0) return;
      const target = ui.pendingScrollSession;
      if (target !== null && target !== 条消息.sessionId) return;
      const lastOrdinal = msgs[msgs.length - 1]!.ordinal;
      ui.scroll到Ordinal(lastOrdinal, target ?? undefined);
    });
  });

  // Sync active session to URL.
  $effect(() => {
    const activeId = 个会话.activeSessionId;
    const currentUrlSessionId = router.sessionId;
    untrack(() => {
      if (router.route !== "个会话") return;
      if (activeId === currentUrlSessionId) return;
      if (activeId) {
        router.navigate到Session(activeId);
      } else {
        router.navigate从Session(filters到Params(个会话.filters));
      }
    });
  });

  // Compare only filter keys so sticky params (e.g. desktop)
  // don't cause spurious replaceParams calls.
  function filterParamsEqual(
    a: Record<string, string>,
    b: Record<string, string>,
  ): boolean {
    for (const k of SESSION_FILTER_KEYS) {
      if ((a[k] ?? "") !== (b[k] ?? "")) return false;
    }
    return true;
  }

  // URL write-back: keep query string in sync with filter state
  // when on /个会话 with no session selected, so users can
  // share/bookmark the view and the URL reflects what's shown.
  // Tracks route so a tab switch back to /个会话 also syncs
  // the URL with localStorage-restored filters.
  $effect(() => {
    const route = router.route;
    const newParams = filters到Params(个会话.filters);
    untrack(() => {
      if (route !== "个会话") return;
      if (router.sessionId) return;
      if (filterParamsEqual(router.params, newParams)) return;
      router.replaceParams(newParams);
    });
  });

  function showAbout() {
    if (ui.activeModal === "resync" && sync.syncing) return;
    ui.activeModal = "about";
  }

  onMount(() => {
    全局Auth到ken = getAuth到ken();
    settings.load();
    starred.load();
    sync.load状态();
    sync.loadStats();
    sync.load版本();
    sync.checkForUpdate();
    sync.startPolling();

    const healthCleanup = setupVisibilityHealthCheck(getBase, {
      onBackendDegraded: () => sync.markBackendDegraded(),
    });

    window.addEventListener("show-about", showAbout);
    const cleanup = registerShortcuts({ navigateMessage });
    return () => {
      healthCleanup();
      cleanup();
      window.removeEventListener("show-about", showAbout);
      sync.stopPolling();
      sync.unwatchSession();
    };
  });

</script>

{#if settings.needsAuth && router.route !== "settings"}
  <div class="auth-overlay">
    <div class="auth-card">
      <h2 class="auth-card-title">需要身份验证</h2>
      <p class="auth-card-desc">
        This server requires an auth token to access. Enter the token
        shown on the server's console or settings page.
      </p>
      <div class="auth-card-field">
        <input
          class="auth-card-input"
          type="password"
          placeholder="粘贴身份验证令牌"
          bind:value={全局Auth到ken}
          onkeydown={(e) => { if (e.key === "Enter") handleGlobalAuth(); }}
        />
        <button
          class="auth-card-btn"
          disabled={!全局Auth到ken.trim()}
          onclick={handleGlobalAuth}
        >
          验证
        </button>
      </div>
      <button
        class="auth-card-disconnect"
        onclick={() => {
          setAuth到ken("");
          set服务器Url("");
          settings.needsAuth = false;
          settings.load();
        }}
      >
        断开并重置
      </button>
    </div>
  </div>
{:else}

<AppHeader />

{#if router.route === "usage"}
  <div class="page-scroll">
    <用量Page />
  </div>
{:else if router.route === "trends"}
  <div class="page-scroll">
    <趋势Page />
  </div>
{:else if router.route === "insights"}
  <div class="page-scroll">
    <洞察Page />
  </div>
{:else if router.route === "pinned"}
  <div class="page-scroll">
    <已固定Page />
  </div>
{:else if router.route === "trash"}
  <div class="page-scroll">
    <回收站Page />
  </div>
{:else if router.route === "settings"}
  <div class="page-scroll">
    <设置Page />
  </div>
{:else}
  <ThreeColumnLayout>
    {#snippet sidebar()}
      <SessionList />
    {/snippet}

    {#snippet content()}
      {#if 个会话.activeSessionId}
        {@const session = 个会话.activeSession}
        <SessionBreadcrumb
          session={session}
          onBack={() => 个会话.deselectSession()}
        />
        <MessageList bind:this={messageListRef} />
      {:else}
        <AnalyticsPage />
      {/if}
    {/snippet}

    {#snippet vitals()}
      {#if 个会话.activeSessionId}
        <SessionVitals sessionId={个会话.activeSessionId} />
      {/if}
    {/snippet}
  </ThreeColumnLayout>
{/if}

<状态Bar />

{#if ui.activeModal === "about"}
  <AboutModal />
{/if}

{#if ui.activeModal === "commandPalette"}
  <CommandPalette />
{/if}

{#if ui.activeModal === "shortcuts"}
  <ShortcutsModal />
{/if}

{#if ui.activeModal === "publish"}
  <PublishModal />
{/if}

{#if ui.activeModal === "resync"}
  <ResyncModal />
{/if}

{#if ui.activeModal === "update"}
  <UpdateModal />
{/if}

{#if ui.activeModal === "confirm删除"}
  <Confirm删除Modal />
{/if}

{/if}

{#if 个会话.recently删除d.length > 0}
  <div class="undo-toast">
    <span>会话已删除</span>
    <button
      class="undo-btn"
      onclick={async (e) => {
        const btn = e.currentTarget;
        if (btn.disabled) return;
        const last = 个会话.recently删除d[个会话.recently删除d.length - 1];
        if (!last) return;
        btn.disabled = true;
        try {
          await 个会话.restoreSession(last.id);
        } catch {
          // restore failed — toast will remain
        } finally {
          btn.disabled = false;
        }
      }}
    >
      撤销
    </button>
  </div>
{/if}

<style>
  .page-scroll {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
  }


  .undo-toast {
    position: fixed;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    padding: 10px 18px;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
    z-index: 10000;
    font-size: 13px;
    color: var(--text-primary);
    animation: slide-up 0.2s ease-out;
  }

  @keyframes slide-up {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  .undo-btn {
    background: none;
    border: none;
    color: var(--accent-blue);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .undo-btn:hover {
    background: color-mix(in srgb, var(--accent-blue) 12%, transparent);
  }

  .auth-overlay {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: var(--bg-default);
  }

  .auth-card {
    text-align: center;
    max-width: 420px;
    padding: 32px 24px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: 12px;
    box-shadow: var(--shadow-lg);
  }

  .auth-card-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 8px;
  }

  .auth-card-desc {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0 0 20px;
  }

  .auth-card-field {
    display: flex;
    gap: 8px;
  }

  .auth-card-input {
    flex: 1;
    height: 34px;
    padding: 0 12px;
    border-radius: 6px;
    font-size: 13px;
    font-family: var(--font-mono, monospace);
    color: var(--text-primary);
    background: var(--bg-inset);
    border: 1px solid var(--border-muted);
  }

  .auth-card-input:focus {
    outline: none;
    border-color: var(--accent-blue);
  }

  .auth-card-btn {
    height: 34px;
    padding: 0 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    color: white;
    background: var(--accent-blue);
    border: none;
    cursor: pointer;
    white-space: nowrap;
  }

  .auth-card-btn:disabled {
    opacity: 0.6;
    cursor: default;
  }

  .auth-card-btn:hover:not(:disabled) {
    opacity: 0.9;
  }

  .auth-card-disconnect {
    margin-top: 12px;
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 12px;
    cursor: pointer;
    text-decoration: underline;
  }

  .auth-card-disconnect:hover {
    color: var(--text-secondary);
  }
</style>
