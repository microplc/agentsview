<script lang="ts">
  import { onDestroy } from "svelte";
  import type { Virtualizer } from "@tanstack/virtual-core";
  import { 条消息 } from "../../stores/条消息.svelte.js";
  import { ui } from "../../stores/ui.svelte.js";
  import { 个会话 } from "../../stores/个会话.svelte.js";
  import { MessageSquareIcon } from "../../icons.js";
  import { createVirtualizer } from "../../virtual/createVirtualizer.svelte.js";
  import MessageContent from "./MessageContent.svelte";
  import 紧凑BoundaryDivider from "./紧凑BoundaryDivider.svelte";
  import SystemBoundaryCard from "../system/SystemBoundaryCard.svelte";
  import 到olCallGroup from "./到olCallGroup.svelte";
  import type { Message } from "../../api/types.js";
  import {
    buildDisplayItems,
    type DisplayItem,
  } from "../../utils/display-items.js";
  import { filterDisplayItemsByTranscriptMode } from "../../utils/transcript-mode.js";
  import {
    hasVisibleSegments,
  } from "../../utils/content-parser.js";
  import { isSystemMessage } from "../../utils/条消息.js";
  import { inSessionSearch } from "../../stores/inSessionSearch.svelte.js";
  import { sessionActivity } from "../../stores/sessionActivity.svelte.js";
  import SessionFindBar from "./SessionFindBar.svelte";
  import {
    getAligned关setScrollAlign,
    getLatestDisplayIndex,
    type ScrollAlign,
  } from "./message-scroll.js";

  let containerRef: HTMLDivElement | undefined = $state(undefined);
  let scrollRaf: number | null = null;
  let lastScrollRequest = 0;
  let activeFollowScrollRequest: number | null = null;
  let followingScrollRaf: number | null = null;
  let followSettleTimer:
    | ReturnType<typeof setTimeout>
    | null = null;

  let baseMessages: Message[] = $derived.by(() =>
    条消息.条消息.filter((m) => !isSystemMessage(m)),
  );

  let baseDisplayItemsAsc = $derived(
    buildDisplayItems(baseMessages),
  );

  let filteredDisplayItemsAsc = $derived(
    buildDisplayItems(baseMessages, {
      skip到olGrouping: !ui.isBlockVisible("tool"),
    }),
  );

  function isItemVisible(item: DisplayItem): boolean {
    if (item.kind === "tool-group") {
      return true;
    }
    return hasVisibleSegments(item.message, (type) =>
      ui.isBlockVisible(type),
    );
  }

  let normalDisplayItemsAsc = $derived.by(() => {
    if (!ui.hasBlockFilters) return baseDisplayItemsAsc;
    return filteredDisplayItemsAsc.filter(isItemVisible);
  });

  let displayItemsAsc = $derived.by(() => {
    if (ui.transcriptMode === "normal") {
      return normalDisplayItemsAsc;
    }

    if (!ui.hasBlockFilters) {
      return filterDisplayItemsByTranscriptMode(
        baseDisplayItemsAsc,
        "focused",
      );
    }

    return filterDisplayItemsByTranscriptMode(
      filteredDisplayItemsAsc,
      "focused",
      {
        isMessageVisible: (message) =>
          hasVisibleSegments(message, (type) =>
            ui.isBlockVisible(type),
          ),
      },
    ).filter(isItemVisible);
  });

  function itemAt(index: number) {
    if (ui.sortNewestFirst) {
      const mapped = displayItemsAsc.length - 1 - index;
      return displayItemsAsc[mapped];
    }
    return displayItemsAsc[index];
  }

  const virtualizer = createVirtualizer(() => {
    const count = displayItemsAsc.length;
    const el = containerRef ?? null;
    const sid = 个会话.activeSessionId ?? "";
    return {
      count,
      getScrollElement: () => el,
      estimateSize: () => 120,
      overscan: 5,
      useAnimationFrameWithResizeObserver: true,
      measureCacheKey: sid,
      getItemKey: (index: number) => {
        const item = itemAt(index);
        if (!item) return `${sid}-${index}`;
        if (item.kind === "tool-group") {
          return `${sid}-tg-${item.ordinals[0]}`;
        }
        return `${sid}-m-${item.message.ordinal}`;
      },
    };
  });

  /** Svelte action: measure element for variable-height virtualizer */
  function measureElement(
    node: HTMLElement,
    virt: Virtualizer<HTMLElement, HTMLElement> | undefined,
  ) {
    virt?.measureElement(node);
    return {
      update(
        nextVirt:
          | Virtualizer<HTMLElement, HTMLElement>
          | undefined,
      ) {
        nextVirt?.measureElement(node);
      },
      destroy() {
        // Cleanup handled by virtualizer
      },
    };
  }

  function publishVisibleTimestamp() {
    const v = virtualizer.instance;
    if (!v) return;
    const items = v.getVirtualItems();
    // Skip overscanned items above the viewport.
    const scroll到p = v.scroll关set ?? 0;
    for (const vi of items) {
      if (vi.end <= scroll到p) continue;
      const item =
        displayItemsAsc[
          ui.sortNewestFirst
            ? displayItemsAsc.length - 1 - vi.index
            : vi.index
        ];
      if (!item) continue;
      const ts =
        item.kind === "message"
          ? item.message.timestamp
          : item.timestamp;
      if (ts) {
        sessionActivity.firstVisibleTimestamp = ts;
        return;
      }
    }
    sessionActivity.firstVisibleTimestamp = null;
  }

  // Recompute visible timestamp when minimap opens or
  // message content changes (e.g. SSE reload).
  $effect(() => {
    if (ui.vitals打开) {
      // Track message array so the effect re-runs after
      // content changes while the minimap is open.
      void 条消息.条消息.length;
      publishVisibleTimestamp();
    }
  });

  function handleScroll() {
    if (!containerRef) return;
    if (scrollRaf !== null) return;
    scrollRaf = requestAnimationFrame(() => {
      scrollRaf = null;
      if (!containerRef) return;
      const items =
        virtualizer.instance?.getVirtualItems() ?? [];
      if (items.length > 0 && 条消息.hasOlder) {
        const firstVisible = items[0]!.index;
        const lastVisible =
          items[items.length - 1]!.index;
        const threshold = 30;
        if (
          (ui.sortNewestFirst &&
            lastVisible >=
              displayItemsAsc.length - threshold) ||
          (!ui.sortNewestFirst &&
            firstVisible <= threshold)
        ) {
          条消息.loadOlder();
        }
      }

      if (ui.vitals打开) {
        publishVisibleTimestamp();
      }

    });
  }

  function handleManualScrollIntent() {
    if (ui.followLatest) {
      cancelFollowLatestWork();
      ui.setFollowLatest(false);
    }
  }

  function manualScrollIntent(node: HTMLElement) {
    const handleKeydown = (event: KeyboardEvent) => {
      if (
        [
          "ArrowDown",
          "ArrowUp",
          "End",
          "首页",
          "PageDown",
          "PageUp",
          " ",
        ].includes(event.key)
      ) {
        handleManualScrollIntent();
      }
    };
    node.addEventListener("wheel", handleManualScrollIntent, {
      passive: true,
    });
    node.addEventListener("pointerdown", handleManualScrollIntent);
    node.addEventListener("touchmove", handleManualScrollIntent, {
      passive: true,
    });
    node.addEventListener("keydown", handleKeydown);
    return {
      destroy() {
        node.removeEventListener(
          "wheel",
          handleManualScrollIntent,
        );
        node.removeEventListener(
          "pointerdown",
          handleManualScrollIntent,
        );
        node.removeEventListener(
          "touchmove",
          handleManualScrollIntent,
        );
        node.removeEventListener("keydown", handleKeydown);
      },
    };
  }

  onDestroy(() => {
    if (scrollRaf !== null) {
      cancelAnimationFrame(scrollRaf);
      scrollRaf = null;
    }
    if (followingScrollRaf !== null) {
      cancelAnimationFrame(followingScrollRaf);
      followingScrollRaf = null;
    }
    if (followSettleTimer !== null) {
      clearTimeout(followSettleTimer);
      followSettleTimer = null;
    }
  });

  function cancelFollowLatestWork() {
    if (
      activeFollowScrollRequest !== null &&
      activeFollowScrollRequest === lastScrollRequest
    ) {
      lastScrollRequest += 1;
    }
    activeFollowScrollRequest = null;
    if (followingScrollRaf !== null) {
      cancelAnimationFrame(followingScrollRaf);
      followingScrollRaf = null;
    }
    if (followSettleTimer !== null) {
      clearTimeout(followSettleTimer);
      followSettleTimer = null;
    }
  }

  function scroll到DisplayIndex(
    index: number,
    waitFrames: number = 0,
    scrollRetries: number = 0,
    reqId: number = lastScrollRequest,
    align: ScrollAlign = "start",
  ) {
    if (reqId !== lastScrollRequest) return;

    const v = virtualizer.instance;
    if (!v) return;

    // Phase 1: wait up to 5 frames for virtualCount to sync.
    const desiredCount = displayItemsAsc.length;
    const virtualCount = v.options.count;
    if (
      waitFrames < 5 &&
      (virtualCount !== desiredCount || index >= virtualCount)
    ) {
      requestAnimationFrame(() => {
        scroll到DisplayIndex(
          index, waitFrames + 1, 0, reqId,
          align,
        );
      });
      return;
    }

    // Phase 2a: item already rendered — use exact measured offset.
    const virtualItems = v.getVirtualItems();
    const isRendered = virtualItems.some(
      (vi) => vi.index === index,
    );
    if (isRendered) {
      const offsetAndAlign =
        v.get关setForIndex(index, align);
      if (offsetAndAlign) {
        const [offset] = offsetAndAlign;
        v.scroll到关set(
          Math.round(offset),
          { align: getAligned关setScrollAlign(align) },
        );
      }
      return;
    }

    // Phase 2b: item not yet in render window. scroll到Index
    // scrolls to an estimated position, but TanStack's reconcile
    // loop exits after 1 stable frame — before ResizeObserver
    // measurements (delayed by bump版本's setTimeout(0)) have
    // updated the offsets.
    //
    // 重试 in 2 frames: by then ResizeObserver + bump版本 have
    // fired, measurements are updated, and the next attempt either
    // finds the item rendered (for an exact offset scroll) or
    // repeats with a more accurate estimate. Limit to 15 scroll
    // retries (~480 ms) to avoid looping forever.
    v.scroll到Index(index, { align });
    if (scrollRetries < 15) {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          scroll到DisplayIndex(
            index,
            waitFrames,
            scrollRetries + 1,
            reqId,
            align,
          );
        });
      });
    }
  }

  function raf(): Promise<void> {
    return new Promise((r) => requestAnimationFrame(() => r()));
  }

  async function scroll到OrdinalInternal(ordinal: number) {
    const reqId = ++lastScrollRequest;
    activeFollowScrollRequest = null;

    const idxAsc = displayItemsAsc.findIndex((item) =>
      item.ordinals.includes(ordinal),
    );
    if (idxAsc >= 0) {
      const idx = ui.sortNewestFirst
        ? displayItemsAsc.length - 1 - idxAsc
        : idxAsc;
      scroll到DisplayIndex(idx, 0, 0, reqId);
      return;
    }

    await 条消息.ensureOrdinalLoaded(ordinal);
    if (reqId !== lastScrollRequest) return;

    // Let Svelte re-derive displayItemsAsc and the
    // virtualizer update its count after loading.
    // Two frames: one for Svelte reactivity, one for
    // virtualizer resize observation.
    await raf();
    await raf();
    if (reqId !== lastScrollRequest) return;

    const loadedIdxAsc = displayItemsAsc.findIndex(
      (item) => item.ordinals.includes(ordinal),
    );
    if (loadedIdxAsc < 0) return;
    const loadedIdx = ui.sortNewestFirst
      ? displayItemsAsc.length - 1 - loadedIdxAsc
      : loadedIdxAsc;
    scroll到DisplayIndex(loadedIdx, 0, 0, reqId);
  }

  export function scroll到Ordinal(ordinal: number) {
    void scroll到OrdinalInternal(ordinal);
  }

  function scroll到LatestInternal() {
    const reqId = ++lastScrollRequest;
    activeFollowScrollRequest = reqId;
    const idx = getLatestDisplayIndex(
      displayItemsAsc.length,
      ui.sortNewestFirst,
    );
    if (idx < 0) return;
    scroll到DisplayIndex(
      idx,
      0,
      0,
      reqId,
      ui.sortNewestFirst ? "start" : "end",
    );
    startFollowLatestSettle(reqId);
  }

  function forceLatestEdge() {
    if (!containerRef) return;
    containerRef.scroll到p = ui.sortNewestFirst
      ? 0
      : containerRef.scrollHeight;
  }

  function startFollowLatestSettle(reqId: number) {
    if (followSettleTimer !== null) {
      clearTimeout(followSettleTimer);
      followSettleTimer = null;
    }

    const tick = () => {
      followSettleTimer = null;
      if (
        reqId !== lastScrollRequest ||
        !ui.followLatest ||
        !containerRef
      ) {
        return;
      }

      forceLatestEdge();
      followSettleTimer = setTimeout(tick, 100);
    };

    tick();
  }

  function queueFollowLatestScroll() {
    if (!ui.followLatest) return;
    if (followingScrollRaf !== null) {
      cancelAnimationFrame(followingScrollRaf);
    }
    followingScrollRaf = requestAnimationFrame(() => {
      followingScrollRaf = null;
      if (!ui.followLatest) return;
      scroll到LatestInternal();
    });
  }

  function latestDisplaySignature(): string {
    const item = displayItemsAsc[displayItemsAsc.length - 1];
    if (!item) return "";
    if (item.kind === "tool-group") {
      return item.条消息
        .map((m) => `${m.ordinal}:${m.content_length}:${m.timestamp}`)
        .join("|");
    }
    const m = item.message;
    return `${m.ordinal}:${m.content_length}:${m.timestamp}`;
  }

  $effect(() => {
    const follow = ui.followLatest;
    if (!follow) {
      cancelFollowLatestWork();
    }
  });

  $effect(() => {
    const follow = ui.followLatest;
    const request = ui.followLatestRequest;
    const count = displayItemsAsc.length;
    const latest = latestDisplaySignature();
    const newestFirst = ui.sortNewestFirst;
    const sessionId = 条消息.sessionId;
    if (!follow || count === 0 || !sessionId) return;
    void request;
    void latest;
    void newestFirst;
    queueFollowLatestScroll();
  });

  export function scroll到Latest() {
    scroll到LatestInternal();
  }

  export function getDisplayItems(): DisplayItem[] {
    return displayItemsAsc;
  }

  export function get普通DisplayItems(): DisplayItem[] {
    return normalDisplayItemsAsc;
  }

  let highlightQuery = $derived(
    inSessionSearch.is打开 && inSessionSearch.query.trim().length > 0
      ? inSessionSearch.query
      : "",
  );
</script>

{#if !个会话.activeSessionId}
  <div class="empty-state">
    <div class="empty-icon">
      <MessageSquareIcon size="36" strokeWidth="1.5" aria-hidden="true" />
    </div>
    <p class="empty-text">Select a session to view 条消息</p>
  </div>
{:else if 条消息.loading && 条消息.条消息.length === 0}
  <div class="empty-state">
    <p class="empty-text">Loading 条消息...</p>
  </div>
{:else}
  <SessionFindBar />
  <div
    class="message-list-scroll layout-{ui.messageLayout}"
    bind:this={containerRef}
    data-session-id={个会话.activeSessionId}
    data-条消息-session-id={条消息.sessionId}
    data-loaded={!条消息.loading}
    onscroll={handleScroll}
    use:manualScrollIntent
  >
    <div
      style="height: {virtualizer.instance?.get到talSize() ?? 0}px; width: 100%; position: relative;"
    >
      {#each virtualizer.instance?.getVirtualItems() ?? [] as row (row.key)}
        {@const item = itemAt(row.index)}
        {#if item}
          <!-- svelte-ignore a11y_click_events_have_key_events -->
          <!-- svelte-ignore a11y_no_static_element_interactions -->
          <div
            class="virtual-row"
            class:selected={ui.selectedOrdinal !== null &&
              item.ordinals.includes(ui.selectedOrdinal)}
            data-index={row.index}
            style="position: absolute; top: 0; left: 0; width: 100%; transform: translateY({row.start}px);"
            use:measureElement={virtualizer.instance}
            onclick={() => {
              const sel = window.getSelection();
              if (sel && sel.toString().length > 0) return;
              ui.selectOrdinal(item.ordinals[0]!);
            }}
          >
            {#if item.kind === "tool-group"}
              <到olCallGroup
                条消息={item.条消息}
                timestamp={item.timestamp}
                highlightQuery={highlightQuery}
                isCurrentHighlight={item.ordinals.includes(inSessionSearch.currentOrdinal ?? -1)}
              />
            {:else if item.message.is_compact_boundary}
              <紧凑BoundaryDivider message={item.message} />
            {:else if item.message.is_system && item.message.source_subtype && item.message.source_subtype !== 'compact_boundary'}
              <SystemBoundaryCard
                subtype={item.message.source_subtype}
                content={item.message.content}
                timestamp={item.message.timestamp}
              />
            {:else}
              <MessageContent
                message={item.message}
                highlightQuery={highlightQuery}
                isCurrentHighlight={inSessionSearch.currentOrdinal === item.message.ordinal}
              />
            {/if}
          </div>
        {/if}
      {/each}
    </div>
  </div>
{/if}

<style>
  .message-list-scroll {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 8px 0;
    overflow-anchor: none;
  }

  .virtual-row {
    padding: 5px 12px;
    overflow-anchor: none;
  }

  .virtual-row.selected > :全局(*) {
    outline: 2px solid var(--accent-blue);
    outline-offset: -2px;
    border-radius: var(--radius-md, 6px);
  }

  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    gap: 12px;
  }

  .empty-icon {
    opacity: 0.25;
  }

  .empty-text {
    font-size: 14px;
    font-weight: 500;
  }

  /* ── 紧凑 layout ── */
  .layout-compact {
    padding: 4px 0;
  }

  .layout-compact .virtual-row {
    padding: 2px 12px;
  }

  .layout-compact :全局(.message) {
    padding: 6px 12px;
    border-left-width: 2px;
    border-radius: 0;
  }

  .layout-compact :全局(.message-header) {
    margin-bottom: 4px;
    gap: 6px;
  }

  .layout-compact :全局(.role-icon) {
    width: 16px;
    height: 16px;
    font-size: 9px;
  }

  .layout-compact :全局(.role-label) {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 700;
  }

  .layout-compact :全局(.timestamp),
  .layout-compact :全局(.group-timestamp) {
    font-size: 10px;
  }

  .layout-compact :全局(.text-content) {
    font-size: 13px;
    line-height: 1.55;
  }

  .layout-compact :全局(.message-body) {
    gap: 4px;
  }

  /* ── 流式 layout ── */
  .layout-stream {
    padding: 0;
  }

  .layout-stream .virtual-row {
    padding: 0;
  }

  .layout-stream :全局(.message) {
    border-left: none;
    border-radius: 0;
    padding: 16px 24px;
  }

  .layout-stream :全局(.message.is-user) {
    background: color-mix(
      in srgb,
      var(--accent-blue) 5%,
      transparent
    ) !important;
  }

  .layout-stream :全局(.message:not(.is-user)) {
    background: transparent !important;
  }

  .layout-stream :全局(.message-header) {
    display: none;
  }

  .layout-stream :全局(.text-content) {
    font-size: 14px;
    line-height: 1.75;
  }
</style>
