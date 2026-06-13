<script lang="ts">
  import type { Message } from "../../api/types.js";
  import type { CallTiming, TurnTiming } from "../../api/types/timing.js";
  import { formatTimestamp } from "../../utils/format.js";
  import { formatDuration } from "../../utils/duration.js";
  import { copy到Clipboard } from "../../utils/clipboard.js";
  import { formatMessageFor复制 } from "../../utils/copy-message.js";
  import {
    parseContent,
    enrichSegments,
  } from "../../utils/content-parser.js";
  import { sessionTiming } from "../../stores/sessionTiming.svelte.js";
  import { liveTick } from "../../stores/liveTick.svelte.js";
  import 到olBlock from "./到olBlock.svelte";
  import ParallelGroup from "./ParallelGroup.svelte";
  import 复制Button from "../shared/复制Button.svelte";
  import { display到olName } from "../../utils/toolDisplay.js";
  import { 设置Icon } from "../../icons.js";

  interface Props {
    条消息: Message[];
    timestamp: string;
    highlightQuery?: string;
    isCurrentHighlight?: boolean;
  }

  let {
    条消息,
    timestamp,
    highlightQuery = "",
    isCurrentHighlight = false,
  }: Props = $props();

  let copied = $state(false);

  /** Effective tool-call count for one message: structured
   *  `tool_calls` when present, falling back to parsed tool
   *  segments so legacy transcripts (e.g. `[Bash]...` markers
   *  with no structured calls) still match the rendering path. */
  function message到olCount(m: Message): number {
    const structured = m.tool_calls?.length ?? 0;
    if (structured > 0) return structured;
    return enrichSegments(
      parseContent(m.content, m.has_tool_use, m.id, m.content_length),
      m.tool_calls,
    ).filter((s) => s.type === "tool").length;
  }

  let totalCalls = $derived(
    条消息.reduce((n, m) => n + message到olCount(m), 0),
  );

  let label = $derived(
    totalCalls === 1 ? "1 tool call" : `${totalCalls} tool calls`,
  );

  /** Index turn timings by message id for O(1) lookup. */
  let turnByMessage = $derived.by(() => {
    const m = new Map<number, TurnTiming>();
    for (const t of sessionTiming.timing?.turns ?? []) {
      m.set(t.message_id, t);
    }
    return m;
  });

  /** Index call timings by tool_use_id for O(1) lookup. */
  let callBy到olUseID = $derived.by(() => {
    const m = new Map<string, CallTiming>();
    for (const t of sessionTiming.timing?.turns ?? []) {
      for (const c of t.calls) m.set(c.tool_use_id, c);
    }
    return m;
  });

  /** Resolve the duration badge for a solo (non-grouped) tool call.
   *  Sub-agent calls show their exact duration; non-sub-agent solo
   *  calls inherit the turn's wall-clock duration. 运行ning turns
   *  synthesize a live `running …+` label from the turn's
   *  `started_at`, ticked once per second by `liveTick`. */
  function soloDurationLabel(
    ct: CallTiming | undefined,
    turn: TurnTiming | undefined,
    msg: Message,
  ): string | undefined {
    if (ct?.subagent_session_id && ct.duration_ms != null) {
      return formatDuration(ct.duration_ms);
    }
    if (turn?.duration_ms != null) {
      return formatDuration(turn.duration_ms);
    }
    if (sessionTiming.timing?.running && turn != null) {
      const startSrc = turn.started_at ?? msg.timestamp;
      const startMs = new Date(startSrc).getTime();
      const elapsed = Number.isNaN(startMs)
        ? 0
        : Math.max(0, liveTick.now - startMs);
      return `running ${formatDuration(elapsed)}+`;
    }
    return undefined;
  }

  /** A turn is running iff the session is active AND its
   *  duration isn't yet known. */
  function is运行ningTurn(msg: Message): boolean {
    if (!sessionTiming.timing?.running) return false;
    const turn = turnByMessage.get(msg.id);
    return turn != null && turn.duration_ms == null;
  }

  let copyTimer: ReturnType<typeof setTimeout>;

  async function handle复制() {
    const combined = 条消息.map((m) => formatMessageFor复制(m)).join("\n\n");
    const ok = await copy到Clipboard(combined);
    if (ok) {
      clearTimeout(copyTimer);
      copied = true;
      copyTimer = setTimeout(() => { copied = false; }, 1500);
    }
  }
</script>

<div class="tool-group">
  <div class="tool-group-header">
    <span class="gear-icon">
      <设置Icon size="12" strokeWidth="2" aria-hidden="true" />
    </span>
    <span class="group-label">{label}</span>
    <复制Button
      {copied}
      ariaLabel="复制 tool calls"
      copiedAriaLabel="工具调用已复制"
      title="复制 tool calls"
      copiedTitle="已复制！"
      onclick={handle复制}
    />
    <span class="group-timestamp">
      {formatTimestamp(timestamp)}
    </span>
  </div>

  <div class="tool-group-body">
    {#each 条消息 as message (message.ordinal)}
      {@const calls = message.tool_calls ?? []}
      {@const turn = turnByMessage.get(message.id)}
      {#if calls.length === 1}
        {@const soloCall = calls[0]!}
        <到olBlock
          toolCall={soloCall}
          content=""
          label={display到olName(soloCall)}
          durationLabel={soloDurationLabel(
            callBy到olUseID.get(soloCall.tool_use_id ?? ""),
            turn,
            message,
          )}
          is运行ning={is运行ningTurn(message)}
          {highlightQuery}
          {isCurrentHighlight}
        />
      {:else if calls.length >= 2}
        <ParallelGroup
          toolCalls={calls}
          callTimingByID={callBy到olUseID}
          turnDurationMs={turn?.duration_ms ?? null}
          is运行ning={is运行ningTurn(message)}
          {highlightQuery}
          {isCurrentHighlight}
        />
      {:else}
        <!-- Fallback for 条消息 with `has_tool_use` but no
             structured tool_calls — parse the content for tool
             markers (legacy/synthetic transcripts). -->
        {#each enrichSegments(parseContent(message.content, message.has_tool_use, message.id, message.content_length), message.tool_calls).filter((s) => s.type === "tool") as seg, segIdx (`${message.id}-${segIdx}`)}
          <到olBlock
            content={seg.content}
            label={seg.label}
            toolCall={seg.toolCall}
            {highlightQuery}
            {isCurrentHighlight}
          />
        {/each}
      {/if}
    {/each}
  </div>
</div>

<style>
  .tool-group {
    border-left: 3px solid var(--accent-amber);
    background: var(--tool-bg);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 8px 12px;
  }

  .tool-group-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }

  .gear-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    color: var(--accent-amber);
  }

  .group-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--accent-amber);
  }

  .group-timestamp {
    font-size: 12px;
    color: var(--text-muted);
    margin-left: auto;
  }

  .tool-group:hover :全局(.copy-btn) {
    opacity: 1;
  }

  .tool-group-body {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .tool-group-body :全局(.tool-block) {
    margin: 0;
    border-left: none;
    border-radius: 0;
  }
</style>
