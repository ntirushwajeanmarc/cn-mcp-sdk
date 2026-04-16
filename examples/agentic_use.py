import datetime
import json
import os
import re
import sqlite3
from collections import deque
from openai import OpenAI
from cn_mcp import MCPClient
import dotenv

dotenv.load_dotenv()

# ── config ────────────────────────────────────────────────────────────────────
# Demo script: keep this scoped to non-production environments unless you add
# execution policy, budget limits, and tool-level allowlists.
llm   = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "qwen3.5:397b-cloud"
DB    = "agent.db"
mcp   = MCPClient(api_key=os.getenv("MCP_API_KEY"))

# ── colors ────────────────────────────────────────────────────────────────────
DIM, RESET, YEL, RED, GRN, CYN = "\033[2m", "\033[0m", "\033[33m", "\033[31m", "\033[32m", "\033[36m"

# ── load tools ────────────────────────────────────────────────────────────────
TOOL_SCHEMAS = mcp.get_tools()
TOOLS = [tool["name"] for tool in TOOL_SCHEMAS]
print(f"{CYN}Tools:{RESET}", TOOLS)
TOOL_SCHEMA_MAP = {tool["name"]: tool for tool in TOOL_SCHEMAS}

# ── mcp session ───────────────────────────────────────────────────────────────
print("Creating MCP session...")
MCP_SESSION = mcp.sessions.create()["session_id"]
session_mcp = mcp.bind_session(MCP_SESSION)
print(f"MCP session: {MCP_SESSION}")

def call_tool(name: str, args: dict):
    return session_mcp.tool_call(name, **dict(args or {}))

def write_text_artifact(path: str, text: str) -> dict:
    return mcp.files.write(
        session_id=MCP_SESSION,
        path=path,
        content=text,
    )

# ── sqlite memory ─────────────────────────────────────────────────────────────
con = sqlite3.connect(DB)
con.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        session TEXT NOT NULL,
        role    TEXT NOT NULL,
        content TEXT NOT NULL,
        ts      TEXT DEFAULT (datetime('now'))
    )
""")
con.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        session TEXT NOT NULL,
        task    TEXT NOT NULL,
        status  TEXT DEFAULT 'pending',
        ts      TEXT DEFAULT (datetime('now'))
    )
""")
con.commit()

AGENT_SESSION = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def db_add(role: str, content: str):
    con.execute("INSERT INTO memory(session,role,content) VALUES(?,?,?)",
                (AGENT_SESSION, role, str(content)))
    con.commit()

def db_history(n=40) -> list[dict]:
    rows = con.execute(
        "SELECT role, content FROM memory WHERE session=? ORDER BY id DESC LIMIT ?",
        (AGENT_SESSION, n)
    ).fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def db_save_tasks(tasks: list[str]):
    for t in tasks:
        con.execute("INSERT INTO tasks(session,task) VALUES(?,?)", (AGENT_SESSION, t))
    con.commit()

def db_mark_task(task_id: int, status: str):
    con.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
    con.commit()

def db_get_tasks() -> list[dict]:
    rows = con.execute(
        "SELECT id, task, status FROM tasks WHERE session=? ORDER BY id",
        (AGENT_SESSION,)
    ).fetchall()
    return [{"id": r[0], "task": r[1], "status": r[2]} for r in rows]

# ── prompts ───────────────────────────────────────────────────────────────────
TOOLS_STR = ", ".join(TOOLS)
SEARCH_SCHEMA   = json.dumps(TOOL_SCHEMA_MAP.get("web_search",    {}).get("input_schema", {}), ensure_ascii=False)
TERMINAL_SCHEMA = json.dumps(TOOL_SCHEMA_MAP.get("terminal_exec", {}).get("input_schema", {}), ensure_ascii=False)
FILE_WRITE_SCHEMA = json.dumps(TOOL_SCHEMA_MAP.get("file_write",  {}).get("input_schema", {}), ensure_ascii=False)

PLANNER_PROMPT = f"""You are a senior engineer planning work for an autonomous agent.
Given a user request, output ONLY a JSON array of high-level tasks.

Rules:
- Tasks must be meaningful work units, NOT individual shell commands.
- Every task must end in a verifiable outcome: a saved file, a checked command result, or a final download-ready artifact.
- Do NOT create pure "analyze only" tasks. If analysis is needed, make the task save the analysis into a file.
- BAD: ["analyze search results"]
- GOOD: ["analyze Rwanda climate data and save structured notes to research/rwanda_climate_notes.md"]
- Each task should be completable with 1-5 tool calls.
- Never mention session_id.
- Output ONLY a JSON array of strings. No markdown. No explanation.

Available tools: {TOOLS_STR}

Example for "create a todo app and zip it":
[
  "scaffold Express backend in todo-app/backend and verify the files exist",
  "scaffold React frontend in todo-app/frontend and verify the files exist",
  "write project implementation notes to todo-app/notes/build_notes.md",
  "zip todo-app/backend into todo-app/backend.zip and verify the zip exists",
  "zip todo-app/frontend into todo-app/frontend.zip and verify the zip exists",
  "return the download URLs for backend.zip and frontend.zip"
]
"""

EXECUTOR_PROMPT = f"""You are an autonomous agent executor. You complete ONE assigned task using tools.

Available tools: {TOOLS_STR}

STRICT RULES:
1. You MUST call at least one tool before declaring DONE.
2. To call a tool respond with raw JSON only (no markdown, no prose):
   {{"tool": "tool_name", "arguments": {{"key": "value"}}}}
3. Prefer ONE tool call at a time unless two are obviously needed.
4. "arguments" must always be a dict, never a string.
5. session_id is auto-injected for workspace tools — NEVER include it.
6. ALWAYS use absolute paths. Do NOT rely on `cd` — it doesn't persist between calls.
   Instead of: cd backend && npm install
   Do:         terminal_exec with command "npm --prefix /abs/path/backend install"
7. For long text/report writing, prefer terminal_exec with a here-doc or python - <<'PY' to write the file, then verify the file exists.
8. file_write requires base64 content. For large text, DO NOT use file_write unless you provide valid content_base64.
9. After each tool result, decide: call more tools OR respond DONE.
10. Respond DONE only when you have VERIFIED the task is complete (file exists, command exit_code=0).
11. If exit_code != 0, you MUST retry with a fix. Do NOT declare DONE on error.
12. NEVER write prose. NEVER say "I cannot". Either use a tool or respond DONE.
13. For all the files you have created, you must always zip them and provide download URL for that.

Important schemas:
- web_search: {SEARCH_SCHEMA}
- terminal_exec: {TERMINAL_SCHEMA}
- file_write: {FILE_WRITE_SCHEMA}
"""

SUMMARIZER_PROMPT = """You are a helpful assistant. Summarize what was accomplished in 2-3 sentences.
Be specific: mention file paths and download URLs if available. No tool calls."""

# ── LLM call ─────────────────────────────────────────────────────────────────
THINK_OPEN, THINK_CLOSE = "<think>", "</think>"

def strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def chat(system: str, messages: list, stream: bool = False) -> str:
    import time
    full_messages = [{"role": "system", "content": system}] + messages
    
    for attempt in range(5):
        try:
            resp = llm.chat.completions.create(model=MODEL, messages=full_messages, stream=stream, timeout=120)
            break
        except Exception as e:
            err_msg = str(e).lower()
            if any(code in err_msg for code in ["503", "502", "504", "timeout", "rate limit"]) and attempt < 4:
                wait = (attempt + 1) * 3
                print(f"    {RED}[WARN] LLM error ({e}), retrying in {wait}s... ({attempt+1}/5){RESET}")
                time.sleep(wait)
                continue
            raise e

    if not stream:
        return resp.choices[0].message.content.strip()

    full, buf, thinking = [], "", False
    for chunk in resp:
        # Some models use 'reasoning' or 'reasoning_content'
        reasoning = getattr(chunk.choices[0].delta, "reasoning", None) or getattr(chunk.choices[0].delta, "reasoning_content", None)
        if reasoning and not thinking:
            print(f"\n{DIM}[thinking]\n", end="", flush=True)
            thinking = True
        if reasoning:
            print(f"{DIM}{reasoning}{RESET}", end="", flush=True)
            continue
        if thinking and not reasoning:
             # If reasoning stopped but we were thinking, and we have content now
             content = chunk.choices[0].delta.content or ""
             if content:
                 print(f"\n{DIM}[/thinking]{RESET}\n", end="", flush=True)
                 thinking = False

        delta = chunk.choices[0].delta.content or ""
        buf += delta
        if THINK_OPEN in buf and not thinking:
            before, _, buf = buf.partition(THINK_OPEN)
            if before: print(before, end="", flush=True); full.append(before)
            print(f"\n{DIM}[thinking]\n", end="", flush=True); thinking = True
        elif THINK_CLOSE in buf and thinking:
            thought, _, buf = buf.partition(THINK_CLOSE)
            print(f"{DIM}{thought}{RESET}", end="", flush=True)
            print(f"\n{DIM}[/thinking]{RESET}\n", end="", flush=True); thinking = False
        else:
            safe = buf
            for tag in (THINK_OPEN, THINK_CLOSE):
                for i in range(1, len(tag)):
                    if safe.endswith(tag[:i]):
                        safe, buf = safe[:-i], buf[-i:]; break
                else: continue
                break
            else: buf = ""
            if safe:
                print(f"{DIM if thinking else ''}{safe}{RESET if thinking else ''}", end="", flush=True)
                if not thinking: full.append(safe)
    if buf:
        print(buf, end="", flush=True)
        if not thinking: full.append(buf)
    print()
    return "".join(full)

# ── tool call parser ──────────────────────────────────────────────────────────
def parse_all_tools(text: str) -> list[dict]:
    results, depth, start = [], 0, None
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0: start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                chunk = text[start:i+1]
                try:
                    data = json.loads(chunk)
                    if "tool" in data:
                        results.append(data)
                except json.JSONDecodeError:
                    pass
                start = None
    return results

# ── prose-escape detector ─────────────────────────────────────────────────────
ESCAPE_PATTERNS = [
    r"i cannot", r"i can'?t", r"as an ai", r"i don'?t have",
    r"i'?m unable", r"unfortunately", r"please provide", r"let me know",
    r"this requires", r"you (would|should|can|need to)", r"assuming you",
    r"here is the", r"here'?s (the|a|how)", r"```",
]

def is_escape(text: str) -> bool:
    t = text.lower().strip()
    if t.startswith('{') or t.startswith('['):
        return False
    for pat in ESCAPE_PATTERNS:
        if re.search(pat, t):
            return True
    if len(t) > 120 and not parse_all_tools(t):
        return True
    return False

def _slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return text[:60] or "task"

def _artifact_path_for_task(task: str, task_num: int) -> str:
    slug = _slugify(task)
    if any(word in task.lower() for word in ("report", "draft", "pdf", "summary")):
        return f"research/task_{task_num:02d}_{slug}.md"
    return f"research/task_{task_num:02d}_{slug}.txt"

def auto_capture_analysis(task: str, reply: str, task_num: int) -> dict | None:
    if len(reply.strip()) < 200:
        return None
    if not any(word in task.lower() for word in ("analy", "synth", "draft", "report", "format", "research")):
        return None
    path = _artifact_path_for_task(task, task_num)
    file_resp = write_text_artifact(path, reply)
    return {
        "path": path,
        "file_id": file_resp.get("file_id"),
        "download_url": file_resp.get("download_url"),
    }

# ── run a single tool ─────────────────────────────────────────────────────────
def run_tool(name: str, args: dict) -> str:
    if isinstance(args, str): args = {"query": args}
    if name not in TOOLS:
        return f"[ERROR] Unknown tool: {name}"
    print(f"    {YEL}→ {name}{RESET} {json.dumps(args, ensure_ascii=False)[:300]}")
    try:
        result = call_tool(name, args)
        if isinstance(result, dict):
            result_text = json.dumps(result, ensure_ascii=False, default=str)
        else:
            result_text = str(result)
        preview = result_text[:500]
        print(f"    {DIM}{preview}{RESET}")
        return result_text
    except Exception as e:
        err = f"[TOOL ERROR] {type(e).__name__}: {e}"
        print(f"    {RED}{err}{RESET}")
        return err

# ── stall detection ───────────────────────────────────────────────────────────
# Replaces the flat MAX_ROUNDS cap. A smart model will say DONE when it's done;
# we only abort if it's clearly stuck: repeating the same call or consecutive errors.

BACKSTOP_ROUNDS   = 60   # absolute last-resort ceiling (not expected to be hit)
STALL_WINDOW      = 3    # how many recent calls to inspect
STALL_REPEAT_MAX  = 2    # identical calls in window → stall
CONSEC_ERROR_MAX  = 4    # consecutive tool errors in a row → stall
MAX_ESCAPES       = 3    # unchanged: model refusing to act

def _call_sig(name: str, args: dict) -> str:
    """Stable fingerprint for a tool call."""
    return f"{name}:{json.dumps(args, sort_keys=True, ensure_ascii=False)}"

class StallDetector:
    def __init__(self):
        self.recent: deque[str] = deque(maxlen=STALL_WINDOW)
        self.consec_errors: int = 0

    def record(self, name: str, args: dict, had_error: bool) -> tuple[bool, str]:
        """
        Record a tool call. Returns (is_stalled, reason).
        """
        sig = _call_sig(name, args)
        self.recent.append(sig)

        if had_error:
            self.consec_errors += 1
        else:
            self.consec_errors = 0

        if self.consec_errors >= CONSEC_ERROR_MAX:
            return True, f"{CONSEC_ERROR_MAX} consecutive tool errors"

        if (len(self.recent) == STALL_WINDOW
                and self.recent.count(sig) >= STALL_REPEAT_MAX):
            return True, f"same call repeated {STALL_REPEAT_MAX}x in last {STALL_WINDOW} rounds"

        return False, ""

# ── planner ───────────────────────────────────────────────────────────────────
def plan(user_input: str, existing_tasks: list[dict] | None = None) -> list[str]:
    print(f"\n{YEL}[planning...]{RESET}")

    context = user_input
    if existing_tasks:
        done    = [t["task"] for t in existing_tasks if t["status"] == "done"]
        pending = [t["task"] for t in existing_tasks if t["status"] in ("pending", "failed")]
        if done or pending:
            context = (
                f"Original request: {user_input}\n\n"
                + (("Already completed:\n" + "\n".join(f"  ✓ {t}" for t in done) + "\n\n") if done else "")
                + (("Still need to do:\n"  + "\n".join(f"  • {t}" for t in pending)) if pending else "")
            )

    raw = chat(PLANNER_PROMPT, [{"role": "user", "content": context}])
    raw = strip_think(raw)
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if not m:
        raise ValueError(f"Planner returned no task list:\n{raw}")
    tasks = json.loads(m.group())
    print(f"{YEL}[plan]{RESET} {len(tasks)} tasks:")
    for i, t in enumerate(tasks, 1):
        print(f"  {i}. {t}")
    print()
    return tasks

# ── executor ──────────────────────────────────────────────────────────────────
def execute_task(task_id: int, task: str, task_num: int, total: int) -> bool:
    print(f"\n{YEL}━━ Task {task_num}/{total} ━━{RESET} {task}")
    db_add("user", f"[TASK {task_num}/{total}]: {task}")

    tool_calls_made = 0
    escape_count    = 0
    stall           = StallDetector()

    for round_num in range(1, BACKSTOP_ROUNDS + 1):
        history = db_history(n=50)
        reply = chat(EXECUTOR_PROMPT, history)
        reply_clean = strip_think(reply)
        reply_clean = re.sub(r"```[a-z]*\n?", "", reply_clean).strip()

        # ── DONE ──────────────────────────────────────────────────────────────
        if reply_clean.strip().upper() == "DONE":
            if tool_calls_made == 0:
                print(f"    {RED}[WARN] DONE with no tool calls — forcing retry{RESET}")
                db_add("tool", "[SYSTEM] You declared DONE without calling any tools. Call at least one tool to verify completion.")
                continue
            print(f"  {GRN}✓ Task {task_num} done ({tool_calls_made} calls, {round_num} rounds){RESET}")
            db_mark_task(task_id, "done")
            db_add("assistant", "DONE")
            return True

        # ── escape detection ───────────────────────────────────────────────────
        if is_escape(reply_clean):
            captured = auto_capture_analysis(task, reply_clean, task_num)
            if captured:
                tool_calls_made += 1
                msg = f"[AUTO-CAPTURED ANALYSIS] saved to {captured['path']} url={captured.get('download_url', '')}"
                print(f"    {YEL}[auto-captured analysis]{RESET} {captured['path']}")
                db_add("assistant", reply_clean)
                db_add("tool", msg)
                continue
            escape_count += 1
            print(f"    {RED}[WARN] prose escape #{escape_count}/{MAX_ESCAPES}{RESET}: {reply_clean[:150]}")
            if escape_count >= MAX_ESCAPES:
                print(f"  {RED}✗ Task {task_num} FAILED: model refused to act{RESET}")
                db_mark_task(task_id, "failed")
                return False
            db_add("assistant", reply_clean)
            db_add("tool", "[SYSTEM] STOP. You are writing prose instead of calling tools. Respond ONLY with tool call JSON or the word DONE. No explanations.")
            continue

        # ── tool calls ────────────────────────────────────────────────────────
        tools_found = parse_all_tools(reply_clean)
        if tools_found:
            db_add("assistant", reply_clean)
            results = []
            for tc in tools_found:
                name = tc.get("tool", "")
                args = tc.get("arguments", {})
                if isinstance(args, str): args = {"query": args}

                result    = run_tool(name, args)
                had_error = '"exit_code": 1' in result or "[TOOL ERROR]" in result
                results.append(f"[{name}]: {result}")
                tool_calls_made += 1

                # stall check per call
                stalled, reason = stall.record(name, args, had_error)
                if stalled:
                    combined = "\n".join(results)
                    db_add("tool", combined)
                    print(f"  {RED}✗ Task {task_num} STALLED: {reason}{RESET}")
                    db_mark_task(task_id, "failed")
                    return False

            combined = "\n".join(results)
            db_add("tool", combined)
            any_error = any('"exit_code": 1' in r or "[TOOL ERROR]" in r for r in results)
            print(f"    {DIM}round {round_num}: {len(tools_found)} tool(s) | errors={'yes' if any_error else 'no'}{RESET}")

        else:
            # short non-escape reply — no tool call, no DONE
            print(f"    {RED}[WARN] unrecognized reply: {reply_clean[:100]}{RESET}")
            db_add("assistant", reply_clean)
            db_add("tool", "[SYSTEM] Unrecognized response. Respond with tool call JSON or DONE.")

    # backstop hit — shouldn't happen with a capable model
    print(f"  {RED}✗ Task {task_num} hit BACKSTOP_ROUNDS ({BACKSTOP_ROUNDS}){RESET}")
    db_mark_task(task_id, "failed")
    return False

# ── main run ──────────────────────────────────────────────────────────────────
def run(user_input: str):
    existing = db_get_tasks()
    pending_existing = [t for t in existing if t["status"] == "pending"]

    if pending_existing:
        tasks_to_run = pending_existing
        print(f"{YEL}[resuming]{RESET} {len(tasks_to_run)} pending tasks")
    else:
        db_add("user", f"[USER REQUEST]: {user_input}")
        new_tasks = plan(user_input, existing if existing else None)
        if not new_tasks:
            print(f"{RED}[ERROR] Planner returned 0 tasks{RESET}")
            return
        db_save_tasks(new_tasks)
        tasks_to_run = db_get_tasks()
        tasks_to_run = [t for t in tasks_to_run if t["status"] == "pending"]

    total = len(db_get_tasks())

    for task_num, t in enumerate(tasks_to_run, 1):
        execute_task(t["id"], t["task"], task_num, total)

    all_tasks  = db_get_tasks()
    done_count = sum(1 for t in all_tasks if t["status"] == "done")
    fail_count = sum(1 for t in all_tasks if t["status"] == "failed")
    print(f"\n{GRN}[done]{RESET} {done_count}/{total} tasks complete, {fail_count} failed\n")

    if fail_count:
        print(f"{RED}Failed tasks:{RESET}")
        for t in all_tasks:
            if t["status"] == "failed":
                print(f"  ✗ {t['task']}")
        print()

    print(f"{CYN}Summary:{RESET} ", end="", flush=True)
    summary = chat(
        SUMMARIZER_PROMPT,
        [{"role": "user", "content": f"Request: {user_input}\nSummarize what was done."}],
        stream=True,
    )
    db_add("assistant", summary)

# ── repl ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n🚀 Agent | session={AGENT_SESSION} | mcp={MCP_SESSION} | db={DB}\n")
    last_input = ""
    try:
        while True:
            try:
                user = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break
            if not user:
                continue
            if user.lower() in {"exit", "quit"}:
                break

            RETRY_WORDS = {"retry", "check again", "not done", "not yet", "redo", "try again", "resume"}
            if any(w in user.lower() for w in RETRY_WORDS) and last_input:
                print(f"{YEL}[retrying — re-marking failed/pending tasks]{RESET}")
                for t in db_get_tasks():
                    if t["status"] in ("failed", "pending"):
                        db_mark_task(t["id"], "pending")
                run(last_input)
            else:
                last_input = user
                AGENT_SESSION = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                run(user)
    finally:
        try:
            session_mcp.dispose()
        except Exception:
            pass
        con.close()
        mcp.close()