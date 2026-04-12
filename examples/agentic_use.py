import datetime
import json
import os
import re
import sqlite3
from openai import OpenAI
from cn_mcp import MCPClient

# ── config ────────────────────────────────────────────────────────────────────
llm   = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "gemma4:e2b"
DB    = "agent.db"
mcp   = MCPClient(api_key=os.environ["MCP_API_KEY"])

# ── colors ────────────────────────────────────────────────────────────────────
DIM, RESET, YEL, RED, GRN, CYN = "\033[2m", "\033[0m", "\033[33m", "\033[31m", "\033[32m", "\033[36m"

# ── load tools ────────────────────────────────────────────────────────────────
TOOL_SCHEMAS = mcp.get_tools()
TOOLS = [tool["name"] for tool in TOOL_SCHEMAS]
print(f"{CYN}Tools:{RESET}", TOOLS)

# ── mcp session ───────────────────────────────────────────────────────────────
print("Creating MCP session...")
MCP_SESSION = mcp.sessions.create()["session_id"]
session_mcp = mcp.bind_session(MCP_SESSION)
print(f"MCP session: {MCP_SESSION}")

def call_tool(name: str, args: dict):
    return session_mcp.tool_call(name, **dict(args or {}))

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

PLANNER_PROMPT = f"""You are a senior engineer planning work for an autonomous agent.
Given a user request, output ONLY a JSON array of high-level tasks.

Rules:
- Tasks must be meaningful work units, NOT individual shell commands.
  BAD: ["mkdir backend", "cd backend", "touch server.js"]
  GOOD: ["scaffold Node/Express backend in todo-app/backend/ with package.json and server.js", ...]
- Each task should be completable with 1-5 tool calls.
- Never mention session_id.
- Output ONLY a JSON array of strings. No markdown. No explanation.

Available tools: {TOOLS_STR}

Example for "create a todo app and zip it":
[
  "scaffold Express backend in todo-app/backend with CRUD routes, package.json, server.js",
  "scaffold React+Tailwind frontend in todo-app/frontend using Vite",
  "write all source files for backend (routes, models)",
  "write all source files for frontend (App.jsx, components, tailwind config)",
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
3. You may emit multiple tool JSON objects in one response.
4. "arguments" must always be a dict, never a string.
5. session_id is auto-injected — NEVER include it.
6. ALWAYS use absolute paths. Do NOT rely on `cd` — it doesn't persist between calls.
   Instead of: cd backend && npm install
   Do:         terminal_exec with command "npm --prefix /abs/path/backend install"
7. After each tool result, decide: call more tools OR respond DONE.
8. Respond DONE only when you have VERIFIED the task is complete (file exists, command exit_code=0).
9. If exit_code != 0, you MUST retry with a fix. Do NOT declare DONE on error.
10. NEVER write prose. NEVER say "I cannot". Either use a tool or respond DONE.
"""

SUMMARIZER_PROMPT = """You are a helpful assistant. Summarize what was accomplished in 2-3 sentences.
Be specific: mention file paths and download URLs if available. No tool calls."""

# ── LLM call ─────────────────────────────────────────────────────────────────
THINK_OPEN, THINK_CLOSE = "<think>", "</think>"

def strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def chat(system: str, messages: list, stream: bool = False) -> str:
    full_messages = [{"role": "system", "content": system}] + messages
    resp = llm.chat.completions.create(model=MODEL, messages=full_messages, stream=stream)

    if not stream:
        return resp.choices[0].message.content.strip()

    full, buf, thinking = [], "", False
    for chunk in resp:
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

# ── planner ───────────────────────────────────────────────────────────────────
def plan(user_input: str, existing_tasks: list[dict] | None = None) -> list[str]:
    print(f"\n{YEL}[planning...]{RESET}")

    context = user_input
    if existing_tasks:
        done = [t["task"] for t in existing_tasks if t["status"] == "done"]
        pending = [t["task"] for t in existing_tasks if t["status"] in ("pending", "failed")]
        if done or pending:
            context = (
                f"Original request: {user_input}\n\n"
                + (("Already completed:\n" + "\n".join(f"  ✓ {t}" for t in done) + "\n\n") if done else "")
                + (("Still need to do:\n" + "\n".join(f"  • {t}" for t in pending)) if pending else "")
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
MAX_ROUNDS  = 25
MAX_ESCAPES = 3

def execute_task(task_id: int, task: str, task_num: int, total: int) -> bool:
    print(f"\n{YEL}━━ Task {task_num}/{total} ━━{RESET} {task}")
    db_add("user", f"[TASK {task_num}/{total}]: {task}")

    tool_calls_made = 0
    escape_count = 0

    for round_num in range(1, MAX_ROUNDS + 1):
        history = db_history(n=50)
        reply = chat(EXECUTOR_PROMPT, history)
        reply_clean = strip_think(reply)
        reply_clean = re.sub(r"```[a-z]*\n?", "", reply_clean).strip()

        # ── DONE ──
        if reply_clean.strip().upper() == "DONE":
            if tool_calls_made == 0:
                print(f"    {RED}[WARN] DONE with no tool calls — forcing retry{RESET}")
                db_add("tool", "[SYSTEM] You declared DONE without calling any tools. Call at least one tool to verify completion.")
                continue
            print(f"  {GRN}✓ Task {task_num} done ({tool_calls_made} calls){RESET}")
            db_mark_task(task_id, "done")
            db_add("assistant", "DONE")
            return True

        # ── escape detection ──
        if is_escape(reply_clean):
            escape_count += 1
            print(f"    {RED}[WARN] prose escape #{escape_count}/{MAX_ESCAPES}{RESET}: {reply_clean[:150]}")
            if escape_count >= MAX_ESCAPES:
                print(f"  {RED}✗ Task {task_num} FAILED: model refused to act{RESET}")
                db_mark_task(task_id, "failed")
                return False
            db_add("assistant", reply_clean)
            db_add("tool", "[SYSTEM] STOP. You are writing prose instead of calling tools. Respond ONLY with tool call JSON or the word DONE. No explanations.")
            continue

        # ── tool calls ──
        tools_found = parse_all_tools(reply_clean)
        if tools_found:
            db_add("assistant", reply_clean)
            results, any_error = [], False
            for tc in tools_found:
                name = tc.get("tool", "")
                args = tc.get("arguments", {})
                if isinstance(args, str): args = {"query": args}
                result = run_tool(name, args)
                results.append(f"[{name}]: {result}")
                tool_calls_made += 1
                if '"exit_code": 1' in result or "[TOOL ERROR]" in result:
                    any_error = True
            combined = "\n".join(results)
            db_add("tool", combined)
            print(f"    {DIM}round {round_num}: {len(tools_found)} tool(s) | errors={'yes' if any_error else 'no'}{RESET}")
        else:
            # short non-escape reply
            print(f"    {RED}[WARN] unrecognized reply: {reply_clean[:100]}{RESET}")
            db_add("assistant", reply_clean)
            db_add("tool", "[SYSTEM] Unrecognized response. Respond with tool call JSON or DONE.")

    print(f"  {RED}✗ Task {task_num} hit MAX_ROUNDS{RESET}")
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

    all_tasks = db_get_tasks()
    done_count  = sum(1 for t in all_tasks if t["status"] == "done")
    fail_count  = sum(1 for t in all_tasks if t["status"] == "failed")
    print(f"\n{GRN}[done]{RESET} {done_count}/{total} tasks complete, {fail_count} failed\n")

    if fail_count:
        print(f"{RED}Failed tasks:{RESET}")
        for t in all_tasks:
            if t["status"] == "failed":
                print(f"  ✗ {t['task']}")
        print()

    print(f"{CYN}Summary:{RESET} ", end="", flush=True)
    summary = chat(SUMMARIZER_PROMPT,
                   [{"role": "user", "content": f"Request: {user_input}\nSummarize what was done."}],
                   stream=True)
    db_add("assistant", summary)

# ── repl ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n🚀 Agent | session={AGENT_SESSION} | mcp={MCP_SESSION} | db={DB}\n")
    last_input = ""
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye."); break
        if not user: continue
        if user.lower() in {"exit", "quit"}: break

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
