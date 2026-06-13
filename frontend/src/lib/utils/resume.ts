/** 代理 types that support CLI session resumption. */
const RESUME_AGENTS: Record<
  string,
  (sessionId: string) => string
> = Object.create(null);
RESUME_AGENTS["claude"] = (id) =>
  `claude --resume ${shellQuote(id)}`;
RESUME_AGENTS["codex"] = (id) =>
  `codex resume ${shellQuote(id)}`;
RESUME_AGENTS["copilot"] = (id) =>
  `copilot --resume=${shellQuote(id)}`;
RESUME_AGENTS["cursor"] = (id) =>
  `cursor agent --resume ${shellQuote(id)}`;
RESUME_AGENTS["gemini"] = (id) =>
  `gemini --resume ${shellQuote(id)}`;
RESUME_AGENTS["opencode"] = (id) =>
  `opencode --session ${shellQuote(id)}`;
RESUME_AGENTS["amp"] = (id) =>
  `amp --resume ${shellQuote(id)}`;

/**
 * 代理s whose resume commands require server-resolved parameters
 * (e.g. --workspace, cwd) that the client cannot compute locally.
 * build恢复Command returns null for these agents so callers
 * don't produce incomplete fallback commands.
 */
const SERVER_ONLY_RESUME = new Set(["cursor"]);

/** Flags available for Claude Code resume. */
export interface Claude恢复Flags {
  skipPermissions?: boolean;
  forkSession?: boolean;
  print?: boolean;
}

/** Minimal shape of a backend resume response used for clipboard copy. */
export interface 恢复CommandResponse {
  command: string;
  cwd?: string;
}

/**
 * POSIX-safe shell quoting using single quotes.
 * Any embedded single quotes are escaped as '"'"'.
 * Skips quoting for IDs that are purely alphanumeric + hyphens.
 */
function shellQuote(s: string): string {
  if (/^[a-zA-Z0-9_][\w-]*$/.test(s)) return s;
  return "'" + s.replace(/'/g, "'\"'\"'") + "'";
}

function commandWithCwd(cmd: string, cwd?: string): string {
  if (!cwd) return cmd;
  return `cd ${shellQuote(cwd)} && ${cmd}`;
}

/**
 * Strip the agent-type prefix from a compound session ID, but only
 * when the prefix matches a known agent. Raw IDs that happen to
 * contain ":" are left untouched.
 */
export function stripIdPrefix(id: string, agent?: string): string {
  if (agent) {
    const prefix = agent + ":";
    if (id.startsWith(prefix)) return id.slice(prefix.length);
  }
  return id;
}

/**
 * Returns true if the given agent supports CLI session resumption.
 */
export function supports恢复(agent: string): boolean {
  return Object.hasOwn(RESUME_AGENTS, agent);
}

/**
 * Build a CLI command to resume the given session in a terminal.
 *
 * @param agent - The agent type (e.g. "claude", "codex", "cursor")
 * @param sessionId - The session ID (may include agent prefix)
 * @param flags - Optional Claude-specific resume flags
 * @returns The shell command string, or null if the agent is not supported
 */
export function build恢复Command(
  agent: string,
  sessionId: string,
  flags?: Claude恢复Flags,
): string | null {
  if (SERVER_ONLY_RESUME.has(agent)) return null;
  const builder = RESUME_AGENTS[agent];
  if (!builder) return null;

  const rawId = stripIdPrefix(sessionId, agent);
  let cmd = builder(rawId);

  if (agent === "claude" && flags) {
    if (flags.skipPermissions)
      cmd += " --dangerously-skip-permissions";
    if (flags.forkSession) cmd += " --fork-session";
    if (flags.print) cmd += " --print";
  }

  return cmd;
}

/**
 * Format a backend-built resume response for clipboard copy.
 *
 * Cursor keeps `command` and `cwd` separate in the API so callers can
 * choose whether to apply the cwd directly. Clipboard copy needs a
 * runnable one-liner, so rebuild it here only for Cursor.
 */
export function format恢复ResponseCommand(
  agent: string,
  response: 恢复CommandResponse | null | undefined,
): string | null {
  if (!response?.command) return null;
  if (agent !== "cursor") return response.command;
  return commandWithCwd(response.command, response.cwd);
}
