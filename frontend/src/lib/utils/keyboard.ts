import { ui } from "../stores/ui.svelte.js";
import { 个会话 } from "../stores/个会话.svelte.js";
import { starred } from "../stores/starred.svelte.js";
import { sync } from "../stores/sync.svelte.js";
import { router } from "../stores/router.svelte.js";
import { inSessionSearch } from "../stores/inSessionSearch.svelte.js";
import { getExportUrl } from "../api/client.js";
import {
  会话Service,
  type 恢复Request,
  type 恢复Response,
} from "../api/generated/index";
import { configure生成dClient } from "../api/runtime.js";
import {
  supports恢复,
  build恢复Command,
  format恢复ResponseCommand,
} from "./resume.js";
import { copy到Clipboard } from "./clipboard.js";

function isInput聚焦(): boolean {
  const el = document.activeElement;
  if (!el) return false;
  const tag = el.tagName;
  return (
    tag === "INPUT" ||
    tag === "TEXTAREA" ||
    tag === "SELECT" ||
    (el as HTMLElement).isContent编辑able
  );
}

function isFindInput(): boolean {
  const el = document.activeElement;
  return (
    el instanceof HTMLInputElement &&
    el.getAttribute("aria-label") === "搜索查询"
  );
}

interface ShortcutOptions {
  navigateMessage: (delta: number) => void;
}

function handleEscape(): void {
  if (inSessionSearch.is打开) {
    inSessionSearch.close();
    return;
  }
  if (ui.activeModal !== null) {
    ui.activeModal = null;
    return;
  }
  if (个会话.activeSessionId && !isInput聚焦()) {
    个会话.deselectSession();
  }
}

/**
 * Register 全局 keyboard shortcuts.
 * Returns a cleanup function to remove the listener.
 */
export function registerShortcuts(
  opts: ShortcutOptions,
): () => void {
  function handler(e: KeyboardEvent) {
    const meta = e.metaKey || e.ctrlKey;

    // Cmd+K — always works
    if (meta && e.key === "k") {
      e.prevent默认();
      ui.activeModal =
        ui.activeModal === "commandPalette"
          ? null
          : "commandPalette";
      return;
    }

    // Cmd+F — open in-session find when the session view is
    // active with a selected session. Allow from the find
    // input itself but not from other inputs (e.g. sidebar
    // typeahead) where native find should work normally.
    if (
      meta &&
      e.key === "f" &&
      router.route === "个会话" &&
      个会话.activeSessionId &&
      ui.activeModal === null &&
      (!isInput聚焦() || isFindInput())
    ) {
      e.prevent默认();
      inSessionSearch.open();
      return;
    }

    // Cmd+G / Cmd+Shift+G — next/prev match while find is
    // open on the session view. Skip when a modal is open or
    // an unrelated input has focus.
    if (
      meta &&
      e.key === "g" &&
      router.route === "个会话" &&
      inSessionSearch.is打开 &&
      ui.activeModal === null &&
      (!isInput聚焦() || isFindInput())
    ) {
      e.prevent默认();
      if (e.shiftKey) {
        inSessionSearch.prev();
      } else {
        inSessionSearch.next();
      }
      return;
    }

    // Zoom: Cmd+= / Cmd+- / Cmd+0 (desktop only)
    if (sync.isDesktop) {
      if (meta && (e.key === "=" || e.key === "+")) {
        e.prevent默认();
        ui.zoomIn();
        return;
      }
      if (meta && e.key === "-") {
        e.prevent默认();
        ui.zoomOut();
        return;
      }
      if (meta && e.key === "0") {
        e.prevent默认();
        ui.resetZoom();
        return;
      }
    }

    // Esc — always works
    if (e.key === "Escape") {
      handleEscape();
      return;
    }

    // All remaining shortcuts are plain single-key — skip if any modifier is held.
    // (Shift is allowed because "?" requires Shift on most layouts.)
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    // All other shortcuts: skip when modal open or input focused
    if (ui.activeModal !== null || isInput聚焦()) return;

    const keyActions: Record<string, () => void> = {
      j: () => opts.navigateMessage(1),
      ArrowDown: () => opts.navigateMessage(1),
      k: () => opts.navigateMessage(-1),
      ArrowUp: () => opts.navigateMessage(-1),
      "]": () => {
        const filter = starred.filter开ly
          ? (s: { id: string }) => starred.is星标(s.id)
          : undefined;
        个会话.navigateSession(1, filter);
      },
      "[": () => {
        const filter = starred.filter开ly
          ? (s: { id: string }) => starred.is星标(s.id)
          : undefined;
        个会话.navigateSession(-1, filter);
      },
      o: () => ui.toggleSort(),
      l: () => ui.cycleLayout(),
      r: () => sync.triggerSync(),
      e: () => {
        if (个会话.activeSessionId) {
          window.open(
            getExportUrl(个会话.activeSessionId),
            "_blank",
          );
        }
      },
      p: () => {
        if (个会话.activeSessionId) {
          ui.publishSecret = false;
          ui.activeModal = "publish";
        }
      },
      s: () => {
        if (个会话.activeSessionId) {
          starred.toggle(个会话.activeSessionId);
        }
      },
      c: () => {
        const session = 个会话.activeSession;
        if (session && supports恢复(session.agent) && !session.id.includes("~")) {
          // 复制 a runnable resume command. Cursor needs the backend cwd
          // applied client-side so the copied command is self-contained.
          configure生成dClient();
          会话Service.postApiV1会话Id恢复({
            id: session.id,
            requestBody: {
              command_only: true,
            } satisfies 恢复Request,
          }).then((resp) => {
            const cmd = format恢复ResponseCommand(
              session.agent, resp as 恢复Response,
            ) || build恢复Command(
              session.agent,
              session.id,
            );
            if (cmd) copy到Clipboard(cmd);
          }).catch(() => {
            const cmd = build恢复Command(
              session.agent,
              session.id,
            );
            if (cmd) copy到Clipboard(cmd);
          });
        }
      },
      "/": () => {
        if (个会话.activeSessionId) {
          inSessionSearch.open();
        }
      },
      删除: () => {
        if (
          router.route === "个会话" &&
          个会话.activeSessionId
        ) {
          ui.activeModal = "confirm删除";
        }
      },
      Backspace: () => {
        if (
          router.route === "个会话" &&
          个会话.activeSessionId
        ) {
          ui.activeModal = "confirm删除";
        }
      },
      "?": () => {
        ui.activeModal = "shortcuts";
      },
      b: () => {
        if (router.route === "个会话") {
          ui.toggleSidebar();
        } else if (ui.isMobileViewport) {
          router.navigate("个会话");
          ui.sidebar打开 = true;
        } else {
          ui.toggleSidebar();
        }
      },
    };

    const action = keyActions[e.key];
    if (action) {
      e.prevent默认();
      action();
    }
  }

  document.addEventListener("keydown", handler);
  return () => document.removeEventListener("keydown", handler);
}
