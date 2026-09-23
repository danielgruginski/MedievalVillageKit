"""Extract every Blender MCP call (and shell / file-write command) from this session's transcripts into readable logs."""
import json, os, glob, re, sys
PROJ = r"C:\Users\danie\.claude\projects\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817"
MAIN = os.path.join(PROJ, "421a57cc-0ba3-43b1-888d-34ef79f58bc6.jsonl")
SUB = os.path.join(PROJ, "421a57cc-0ba3-43b1-888d-34ef79f58bc6", "subagents")
OUT = sys.argv[1]
WF_NAMES = {"wf_b4907a13-928": "valley-review", "wf_0eb94baf-61d": "valley-rereview",
            "wf_a3b3c835-925": "village-kit-buildings-continue", "wf_b274fa73-285": "village-kit-buildings",
            "wf_f739cf47-3de": "nature-mesh-fixes", "wf_597d9ca5-41a": "village-expansion-design"}
BLENDER = "mcp__blender__execute_blender_code"

def parse(path):
    """-> (calls, first_prompt): calls = [dict(kind, ts, code, id, status, result)]"""
    calls, by_id, first_prompt = [], {}, None
    with open(path, encoding="utf8", errors="replace") as f:
        for line in f:
            try: d = json.loads(line)
            except Exception: continue
            msg = d.get("message") or {}
            role = msg.get("role"); content = msg.get("content")
            ts = d.get("timestamp", "")
            if role == "user" and first_prompt is None:
                if isinstance(content, str): first_prompt = content
                elif isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text": first_prompt = c.get("text"); break
            if not isinstance(content, list): continue
            for c in content:
                if not isinstance(c, dict): continue
                if c.get("type") == "tool_use":
                    name, inp = c.get("name"), c.get("input") or {}
                    rec = None
                    if name == BLENDER: rec = dict(kind="blender", code=inp.get("code", ""))
                    elif name == "Bash": rec = dict(kind="shell", code=inp.get("command", ""), desc=inp.get("description", ""))
                    elif name == "PowerShell": rec = dict(kind="shell", code="# (PowerShell)\n" + inp.get("command", ""), desc=inp.get("description", ""))
                    elif name == "Write" and str(inp.get("file_path", "")).endswith((".py", ".js", ".bat", ".sh")):
                        rec = dict(kind="write", code=inp.get("content", ""), path=inp.get("file_path"))
                    if rec is not None:
                        rec.update(ts=ts, id=c.get("id"), status="?", result="")
                        calls.append(rec); by_id[c.get("id")] = rec
                elif c.get("type") == "tool_result" and c.get("tool_use_id") in by_id:
                    rec = by_id[c["tool_use_id"]]
                    res = c.get("content")
                    if isinstance(res, list):
                        res = " ".join(x.get("text", "") for x in res if isinstance(x, dict) and x.get("type") == "text")
                    res = str(res or "")
                    err = c.get("is_error") or "Error executing code" in res or "Traceback" in res or "Exit code" in res[:40]
                    rec["status"] = "ERROR" if err else "ok"; rec["result"] = res
    return calls, first_prompt

def comment_block(text, width=150, max_lines=6):
    text = re.sub(r"\s+", " ", text).strip()
    lines = [text[i:i + width] for i in range(0, min(len(text), width * max_lines), width)]
    return "\n".join("# " + l for l in lines)

def write_log(calls, path_prefix, title, kinds=("blender",), chunk_bytes=900_000):
    sel = [c for c in calls if c["kind"] in kinds]
    parts, cur, size = [], [], 0
    for n, c in enumerate(sel, 1):
        head = f"\n# {'=' * 110}\n# [{n:04d}] {c['ts'][:19].replace('T', ' ')}  {c['kind']}  {c['status']}"
        if c.get("desc"): head += f"  -- {c['desc']}"
        if c.get("path"): head += f"  -> {c['path']}"
        block = head + "\n# " + "=" * 110 + "\n" + c["code"].rstrip() + "\n"
        if c["result"]:
            block += "# ---- result ----\n" + comment_block(c["result"]) + "\n"
        if size + len(block) > chunk_bytes and cur:
            parts.append(cur); cur, size = [], 0
        cur.append(block); size += len(block)
    if cur: parts.append(cur)
    files = []
    ext = ".py" if kinds == ("blender",) else ".log"
    for i, p in enumerate(parts, 1):
        fn = f"{path_prefix}_part{i:02d}{ext}" if len(parts) > 1 else f"{path_prefix}{ext}"
        with open(fn, "w", encoding="utf8", newline="\n") as f:
            f.write(f"# {title}  (part {i}/{len(parts)})\n# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:\n"
                    f"# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.\n")
            f.write("".join(p))
        files.append(fn)
    return sel, files

os.makedirs(OUT, exist_ok=True)
index = ["# Script log index", "",
         "Every script this project ran through the Blender MCP connection (and the shell/patch commands), extracted from the",
         "session transcripts on 2026-09-23. Each block has its timestamp, `ok`/`ERROR`, and a short excerpt of the result.",
         "The maintained code is in `src/`; these logs are the history (how pieces, maps and fixes were made).", ""]
# main session
calls, _ = parse(MAIN)
d = os.path.join(OUT, "main_session"); os.makedirs(d, exist_ok=True)
sel, files = write_log(calls, os.path.join(d, "blender_calls"), "Main session: Blender MCP calls")
index.append(f"## Main session\n\n- Blender calls: {len(sel)} ({sum(1 for c in sel if c['status']=='ERROR')} errors) -> " + ", ".join(f"`{os.path.relpath(f, OUT)}`" for f in files))
sel2, files2 = write_log(calls, os.path.join(d, "shell_and_writes"), "Main session: shell commands and script writes", kinds=("shell", "write"))
index.append(f"- Shell commands / script writes: {len(sel2)} -> " + ", ".join(f"`{os.path.relpath(f, OUT)}`" for f in files2) + "\n")
# workflow agents
index.append("## Workflow agents (multi-agent runs)\n")
for wf in sorted(glob.glob(os.path.join(SUB, "workflows", "wf_*"))):
    wid = os.path.basename(wf); wname = WF_NAMES.get(wid, wid)
    rows = []
    for ag in sorted(glob.glob(os.path.join(wf, "agent-*.jsonl"))):
        c2, prompt = parse(ag)
        if not any(c["kind"] == "blender" for c in c2): continue
        dd = os.path.join(OUT, "agents", wname); os.makedirs(dd, exist_ok=True)
        label = re.sub(r"[^a-z0-9]+", "_", (prompt or "agent")[:0].lower()) or ""
        base = os.path.join(dd, os.path.basename(ag).replace(".jsonl", ""))
        s3, f3 = write_log(c2, base, f"{wname} / {os.path.basename(ag)}: Blender MCP calls")
        with open(base + "_prompt.md", "w", encoding="utf8", newline="\n") as f:
            f.write(f"# Prompt given to {os.path.basename(ag)} ({wname})\n\n{prompt or ''}\n")
        rows.append(f"  - `{os.path.relpath(base, OUT)}*`: {len(s3)} calls")
    if rows:
        index.append(f"- **{wname}** (`{wid}`)"); index += rows
# other subagents (Agent tool)
other = [p for p in glob.glob(os.path.join(SUB, "*.jsonl"))]
for ag in other:
    c2, prompt = parse(ag)
    if not any(c["kind"] == "blender" for c in c2): continue
    dd = os.path.join(OUT, "agents", "single_agents"); os.makedirs(dd, exist_ok=True)
    base = os.path.join(dd, os.path.basename(ag).replace(".jsonl", ""))
    s3, f3 = write_log(c2, base, f"agent {os.path.basename(ag)}: Blender MCP calls")
    with open(base + "_prompt.md", "w", encoding="utf8", newline="\n") as f:
        f.write(f"# Prompt given to {os.path.basename(ag)}\n\n{prompt or ''}\n")
    index.append(f"- single agent `{os.path.relpath(base, OUT)}*`: {len(s3)} calls")
with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf8", newline="\n") as f: f.write("\n".join(index) + "\n")
tot = sum(os.path.getsize(os.path.join(r, x)) for r, _, fs in os.walk(OUT) for x in fs)
print("\n".join(index)); print("total bytes", tot)
