# codex-delegate

Claude Code 用的 skill。你说「让 Codex 看看」，它就把这件事交给本机的 Codex。

走的是固定版本的 [`openai-codex`](https://pypi.org/project/openai-codex/)（当前 **0.163.0**），登录用已经登好的 ChatGPT 订阅：`~/.codex/auth.json`。SDK 自己带运行时，不看 `PATH`，也不看 `~/.codex` 里另外装的那些版本。

```text
codex-delegate/
├── SKILL.md              Claude 读的说明
├── scripts/setup.ps1     装一次依赖
└── scripts/codex_run.py  跑一次任务，stdout 打一行 JSON
```

换 SDK 版本：`setup.ps1 -Version x.y.z`。

## 安装

Windows，本机有 Python 3，Codex 已经登录过。第一次大约要下 150MB。

```powershell
git clone https://github.com/chin1hanwu/codex-delegate.git "$env:USERPROFILE\.claude\skills\codex-delegate"

powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\setup.ps1"
```

装好之后直接说就行，比如「让 Codex 审查这段代码」。

环境里放着 `OPENAI_API_KEY` 或 `CODEX_API_KEY` 时，计费可能改走 API。脚本会在 stderr 里提一句。

## 自己调用

提示写进 UTF-8 文件。解释器用 skill 目录里的 `.venv`，并加上 `-I`。

```powershell
$skill = "$env:USERPROFILE\.claude\skills\codex-delegate"

& "$skill\.venv\Scripts\python.exe" -I `
  "$skill\scripts\codex_run.py" `
  --cwd "C:\path\to\project" `
  --prompt-file "C:\path\to\prompt.txt" `
  --sandbox read-only
```

stdout 只有那一行 JSON，其余都在 stderr。

| 参数 | 说明 |
| --- | --- |
| `--cwd` | 工作目录 |
| `--prompt-file` | 提示文件；`-` 表示从 stdin 读 |
| `--sandbox` | `read-only`（默认）、`workspace-write`、`full-access` |
| `--thread-id` | 接着上次的线程聊 |
| `--model` | 不填就用账户默认模型 |
| `--effort` | `none` `minimal` `low` `medium` `high` `xhigh` |
| `--timeout` | 秒，默认 `1800` |

退出码 `0` 完成，`1` Codex 报失败，`2` 超时，`3` 参数或环境有问题。

JSON 字段：`ok` `thread_id` `status` `final_response` `error` `duration_ms` `item_types` `sdk_version` `sandbox`。

查代码、审 diff 用 `read-only`。要改文件用 `workspace-write`，只能动 `--cwd`。`full-access` 不限制文件系统，先说清楚再用。

## 交给它之前

Codex 看不到你们这段聊天。目标、怎样算做完、路径、约束、想要的格式，都写进提示里。要改代码，就写明动哪些、别动哪些。

`final_response` 是它的说法。文件改过的话，看 diff、读文件、跑测试。同一件事接着问，带 `--thread-id`。超时只是这边不再等，目录里可能已经有改动。订阅额度和你平常开 Codex 是同一份。

<details>
<summary>English</summary>

A Claude Code skill. Ask it to hand a task to the Codex already signed in on this machine.

It calls pinned [`openai-codex`](https://pypi.org/project/openai-codex/) **0.163.0**. Auth is the ChatGPT subscription file `~/.codex/auth.json`. The SDK ships its own runtime, so `PATH` and other copies under `~/.codex` stay out of the way. Bump the pin with `setup.ps1 -Version x.y.z`.

Windows, Python 3, Codex already logged in. First install is about 150MB.

```powershell
git clone https://github.com/chin1hanwu/codex-delegate.git "$env:USERPROFILE\.claude\skills\codex-delegate"

powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\setup.ps1"
```

Then just ask, for example: “让 Codex 审查这段代码”.

If `OPENAI_API_KEY` or `CODEX_API_KEY` is set, billing can switch to the API. The script mentions that on stderr.

Put the prompt in a UTF-8 file. Use this skill’s `.venv` Python, with `-I`:

```powershell
$skill = "$env:USERPROFILE\.claude\skills\codex-delegate"

& "$skill\.venv\Scripts\python.exe" -I `
  "$skill\scripts\codex_run.py" `
  --cwd "C:\path\to\project" `
  --prompt-file "C:\path\to\prompt.txt" `
  --sandbox read-only
```

stdout is one JSON line. Everything else goes to stderr.

| Flag | Meaning |
| --- | --- |
| `--cwd` | working directory |
| `--prompt-file` | prompt file, or `-` for stdin |
| `--sandbox` | `read-only` (default), `workspace-write`, `full-access` |
| `--thread-id` | continue an earlier thread |
| `--model` | account default if omitted |
| `--effort` | `none` `minimal` `low` `medium` `high` `xhigh` |
| `--timeout` | seconds, default `1800` |

Exit `0` done, `1` Codex failed, `2` timed out, `3` bad arguments or environment.

JSON fields: `ok` `thread_id` `status` `final_response` `error` `duration_ms` `item_types` `sdk_version` `sandbox`.

Use `read-only` to inspect or review. `workspace-write` can change files under `--cwd` only. `full-access` is unrestricted; say so before using it.

Codex never sees the chat. Put the goal, the finish line, paths, constraints, and the format you want in the prompt. If it should edit, name what it may touch.

`final_response` is its own account of the run. After edits, read the diff and run the tests. Follow up with `--thread-id`. A timeout only stops the wait; the directory may already have changes. Delegated runs draw on the same subscription quota as using Codex yourself.

</details>
