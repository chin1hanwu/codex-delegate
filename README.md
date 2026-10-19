# codex-delegate

Claude Code skill that delegates well-scoped coding, investigation, review, or second-opinion tasks to **Codex** through a **pinned** [`openai-codex`](https://pypi.org/project/openai-codex/) Python SDK. Authentication uses your existing **ChatGPT subscription** login (`~/.codex/auth.json`); no OpenAI API key is required.

The SDK bundles its own Codex runtime and does not read `PATH` or `~/.codex/packages/standalone/releases`, so delegation is not affected by multiple Codex CLI versions on the machine.

## What is in this repo

| Path | Purpose |
|------|---------|
| `SKILL.md` | Claude Code skill instructions (Chinese) |
| `scripts/setup.ps1` | Creates a private `.venv` and installs pinned `openai-codex` |
| `scripts/codex_run.py` | Runs one Codex task; prints a single JSON line on stdout |

Default pinned SDK version: **0.163.0** (override with `setup.ps1 -Version`).

## Requirements

- Windows (PowerShell setup script)
- Python 3 with `venv` and `pip`
- ChatGPT subscription already signed in to Codex (`~/.codex/auth.json`)
- Network access for first-time SDK install (~150 MB)

Avoid setting `OPENAI_API_KEY` or `CODEX_API_KEY` in the environment; the runner warns if they are present because they can switch billing away from subscription auth.

## Install as a Claude Code skill

Clone or copy this repository into your Claude skills directory:

```powershell
git clone https://github.com/chin1hanwu/codex-delegate.git "$env:USERPROFILE\.claude\skills\codex-delegate"
```

Then run setup once:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\setup.ps1"
```

Claude will load `SKILL.md` when you ask to delegate work to Codex (e.g. “让 Codex 审查这段代码”).

## Run a task manually

1. Write the task prompt to a UTF-8 file (do not pass long prompts on the command line).
2. Invoke the script with the skill venv interpreter and `-I`:

```powershell
$skill = "$env:USERPROFILE\.claude\skills\codex-delegate"
& "$skill\.venv\Scripts\python.exe" -I `
  "$skill\scripts\codex_run.py" `
  --cwd "C:\path\to\your\project" `
  --prompt-file "C:\path\to\prompt.txt" `
  --sandbox read-only
```

3. Parse the one-line JSON on **stdout**; diagnostics appear on **stderr**.

### CLI options

| Flag | Description |
|------|-------------|
| `--cwd` | Required. Working directory for Codex |
| `--prompt-file` | Required. Prompt file path, or `-` for stdin |
| `--sandbox` | `read-only` (default), `workspace-write`, or `full-access` |
| `--thread-id` | Resume a previous thread |
| `--model` | Optional; account default if omitted |
| `--effort` | `none` / `minimal` / `low` / `medium` / `high` / `xhigh` |
| `--timeout` | Seconds before abort (default `1800`) |

### JSON result fields

`ok`, `thread_id`, `status`, `final_response`, `error`, `duration_ms`, `item_types`, `sdk_version`, `sandbox`

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Completed successfully |
| `1` | Codex reported failure |
| `2` | Timeout |
| `3` | Invalid arguments or environment |

### Sandbox guidance

- **read-only** — audits, reviews, read-only investigation
- **workspace-write** — Codex may modify files under `--cwd` only
- **full-access** — unrestricted filesystem; use only with explicit consent

## Writing delegation prompts

Codex does not see your chat history. Prompts must be self-contained: goal, done criteria, relevant paths, constraints, and desired output format. For file edits, specify scope and files that must not change.

After a run, treat `final_response` as Codex’s summary, not proof—verify with `git diff`, file reads, and tests. Use `--thread-id` for follow-ups on the same task.

## License

See repository defaults; skill content is provided as-is for personal and team use with Claude Code and Codex.
