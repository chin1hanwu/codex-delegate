<h1 align="center">codex-delegate</h1>

<p align="center">Hand a Claude Code task to the Codex already signed in on this machine.</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/get_started-quickstart-149954?style=flat-square" alt="Quick Start"></a>
  <a href="#how-it-runs"><img src="https://img.shields.io/badge/runtime-pinned%20sdk-007ec6?style=flat-square" alt="Runtime"></a>
  <a href="#parameters"><img src="https://img.shields.io/badge/cli-parameters-68448b?style=flat-square" alt="Parameters"></a>
  <a href="#sandbox"><img src="https://img.shields.io/badge/sandbox-three%20modes-e65100?style=flat-square" alt="Sandbox"></a>
  <a href="https://pypi.org/project/openai-codex/0.163.0/"><img src="https://img.shields.io/badge/sdk-openai--codex%200.163.0-ffd21e?style=flat-square" alt="openai-codex 0.163.0"></a>
  <a href="SKILL.md"><img src="https://img.shields.io/badge/Claude%20Code-SKILL.md-f28c45?style=flat-square" alt="SKILL.md"></a>
</p>

English | [中文](README.zh.md)

**codex-delegate** is a Claude Code skill. One task goes to Codex through the pinned Python package [`openai-codex`](https://pypi.org/project/openai-codex/) **0.163.0**. Login is the ChatGPT subscription already on disk, `~/.codex/auth.json`. The wheel ships its own runtime, so the call uses that build: not whatever `codex` happens to be on `PATH`, and not the copies under `~/.codex/packages`.

<p align="center"><code>Claude Code</code> → <code>codex_run.py</code> → <code>openai-codex 0.163.0</code> → <code>Codex</code></p>

---

## Quick Start

### 1. Install

Windows, Python 3, Codex already logged in. The first download is about 150MB.

```powershell
git clone https://github.com/chin1hanwu/codex-delegate.git "$env:USERPROFILE\.claude\skills\codex-delegate"

powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\setup.ps1"
```

To pin a different SDK build: `setup.ps1 -Version x.y.z`.

### 2. Ask Claude

Once the skill is on disk, ask in the chat. For example: 「让 Codex 审查这段代码」. Claude loads [SKILL.md](SKILL.md) and runs the script.

### 3. Call it yourself

Put the prompt in a UTF-8 file. The interpreter is the venv inside the skill, with `-I`.

```powershell
$skill = "$env:USERPROFILE\.claude\skills\codex-delegate"

& "$skill\.venv\Scripts\python.exe" -I `
  "$skill\scripts\codex_run.py" `
  --cwd "C:\path\to\project" `
  --prompt-file "C:\path\to\prompt.txt" `
  --sandbox read-only
```

stdout is one JSON object. Everything else is on stderr.

---

## How It Runs

| Path | Role |
| --- | --- |
| `SKILL.md` | What Claude reads |
| `scripts/setup.ps1` | Private `.venv`, pinned `openai-codex` |
| `scripts/codex_run.py` | One task in, one JSON line out |

| Exit | Meaning |
| --- | --- |
| `0` | Finished |
| `1` | Codex reported a failure |
| `2` | Timed out |
| `3` | Arguments or environment |

Returned fields: `ok`, `thread_id`, `status`, `final_response`, `error`, `duration_ms`, `item_types`, `sdk_version`, `sandbox`.

`final_response` is Codex’s write-up of the run. After an edit, look at the diff and run the tests. Pick up the same thread with `--thread-id`. On timeout the script stops waiting; files in `--cwd` may already have changed.

---

## Parameters

| Flag | Meaning |
| --- | --- |
| `--cwd` | Working directory. Required |
| `--prompt-file` | Prompt file, or `-` for stdin. Required |
| `--sandbox` | `read-only` (default), `workspace-write`, `full-access` |
| `--thread-id` | Continue an earlier thread |
| `--model` | Account default when omitted |
| `--effort` | `none` `minimal` `low` `medium` `high` `xhigh` |
| `--timeout` | Seconds. Default `1800` |

---

## Sandbox

| Mode | Reach |
| --- | --- |
| `read-only` | Inspect and review. Default |
| `workspace-write` | Write files under `--cwd` only |
| `full-access` | No filesystem limit. Settle that before you use it |

Codex never sees this chat. The prompt itself needs the goal, what done looks like, the paths, the constraints, and the shape of the answer. For edits, name what it may change.

---

## Support

- Leave `OPENAI_API_KEY` and `CODEX_API_KEY` unset. Either one can move billing off the ChatGPT subscription. The script prints a warning on stderr when it sees them.
- Delegated runs draw on the same subscription quota as opening Codex yourself.
- `setup.ps1` is PowerShell. This install path is Windows.

Claude’s copy of the instructions is [SKILL.md](SKILL.md).
