"""Delegate one task to Codex through the pinned Python SDK and print a JSON result.

Run with the skill's own venv interpreter, never the system Python:
    .venv\\Scripts\\python.exe -I scripts\\codex_run.py --cwd <dir> --prompt-file <file>

The prompt comes from --prompt-file, or from stdin when --prompt-file is "-".
stdout carries exactly one JSON object; progress and diagnostics go to stderr.
Exit code: 0 completed, 1 Codex reported failure, 2 timeout, 3 usage/setup error.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from pathlib import Path


def emit(obj: dict, code: int) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    os._exit(code)  # do not wait on a still-running SDK thread/subprocess


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cwd", required=True, help="working directory Codex operates in")
    ap.add_argument("--prompt-file", required=True, help="file holding the task prompt, or - for stdin")
    ap.add_argument("--sandbox", choices=["read-only", "workspace-write", "full-access"], default="read-only")
    ap.add_argument("--thread-id", help="resume an earlier thread to continue its context")
    ap.add_argument("--model", help="omit to use the account default")
    ap.add_argument("--effort", choices=["none", "minimal", "low", "medium", "high", "xhigh"])
    ap.add_argument("--timeout", type=int, default=1800, help="seconds before giving up (default 1800)")
    args = ap.parse_args()

    cwd = Path(args.cwd)
    if not cwd.is_dir():
        emit({"ok": False, "error": f"cwd does not exist: {cwd}"}, 3)
    prompt = sys.stdin.read() if args.prompt_file == "-" else Path(args.prompt_file).read_text(encoding="utf-8")
    if not prompt.strip():
        emit({"ok": False, "error": "empty prompt"}, 3)

    # A stray API key would silently switch billing away from the ChatGPT subscription.
    stray = [k for k in ("OPENAI_API_KEY", "CODEX_API_KEY") if os.environ.get(k)]
    if stray:
        print(f"warning: {', '.join(stray)} is set and may override ChatGPT-subscription auth", file=sys.stderr)

    try:
        from openai_codex import Codex, Sandbox
        from openai_codex._version import __version__ as sdk_version
    except ImportError as e:
        emit({"ok": False, "error": f"openai_codex not importable ({e}); run scripts/setup.ps1"}, 3)

    sandbox = Sandbox(args.sandbox)
    result_box: dict = {}

    def work() -> None:
        try:
            with Codex() as codex:
                kw = {"cwd": str(cwd), "sandbox": sandbox}
                if args.model:
                    kw["model"] = args.model
                if args.thread_id:
                    thread = codex.thread_resume(args.thread_id, **kw)
                else:
                    thread = codex.thread_start(**kw)
                run_kw = {}
                if args.effort:
                    run_kw["effort"] = args.effort
                turn = thread.run(prompt, **run_kw)
                result_box["thread_id"] = thread.id
                result_box["turn"] = turn
        except BaseException as e:  # report every failure as JSON
            result_box["exc"] = f"{type(e).__name__}: {e}"

    t = threading.Thread(target=work, daemon=True)
    t.start()
    t.join(args.timeout)
    if t.is_alive():
        emit({"ok": False, "error": f"timeout after {args.timeout}s", "sdk_version": sdk_version}, 2)
    if "exc" in result_box:
        emit({"ok": False, "error": result_box["exc"], "sdk_version": sdk_version}, 1)

    turn = result_box["turn"]
    status = str(getattr(turn.status, "value", turn.status))
    ok = status == "completed" and turn.error is None
    emit(
        {
            "ok": ok,
            "thread_id": result_box["thread_id"],
            "status": status,
            "final_response": turn.final_response,
            "error": None if turn.error is None else str(turn.error),
            "duration_ms": turn.duration_ms,
            "item_types": [type(getattr(i, "root", i)).__name__ for i in turn.items],
            "sdk_version": sdk_version,
            "sandbox": args.sandbox,
        },
        0 if ok else 1,
    )


if __name__ == "__main__":
    main()
