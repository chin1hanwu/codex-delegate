# codex-delegate

[中文](#中文) · [English](#english)

通过固定版本的 [`openai-codex`](https://pypi.org/project/openai-codex/) Python SDK，把定义清楚的编码、调查、审查或第二意见任务委派给 **Codex**。认证沿用本机已有的 **ChatGPT 订阅**登录（`~/.codex/auth.json`），不需要 OpenAI API key。

Claude Code skill that delegates well-scoped coding, investigation, review, or second-opinion tasks to **Codex** through a **pinned** `openai-codex` Python SDK. Authentication uses the existing **ChatGPT subscription** login (`~/.codex/auth.json`).

## 中文

SDK 自带固定版本的 Codex 运行时，不读 `PATH`，也不读 `~/.codex/packages/standalone/releases`，所以不受机器上多个 Codex CLI 版本的影响。

### 仓库内容

| 路径 | 作用 |
|------|------|
| `SKILL.md` | Claude Code skill 说明（中文） |
| `scripts/setup.ps1` | 创建私有 `.venv`，并安装固定版本的 `openai-codex` |
| `scripts/codex_run.py` | 执行一次 Codex 任务；stdout 只输出一行 JSON |

默认固定 SDK 版本：**0.163.0**（可用 `setup.ps1 -Version` 覆盖）。

### 环境要求

- Windows（安装脚本为 PowerShell）
- 带 `venv` 和 `pip` 的 Python 3
- 已用 ChatGPT 订阅登录 Codex（`~/.codex/auth.json`）
- 首次安装 SDK 需要联网（约 150 MB）

环境里不要设置 `OPENAI_API_KEY` 或 `CODEX_API_KEY`。脚本检测到它们会在 stderr 警告，因为这可能把计费从订阅切到按量计费。

### 安装为 Claude Code skill

把仓库克隆到 Claude skills 目录：

```powershell
git clone https://github.com/chin1hanwu/codex-delegate.git "$env:USERPROFILE\.claude\skills\codex-delegate"
```

然后运行一次安装：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\setup.ps1"
```

之后对 Claude 说「让 Codex 审查这段代码」一类请求时，会加载 `SKILL.md`。

### 手动运行一次任务

1. 把任务写成 UTF-8 文本文件。长提示不要塞进命令行参数。
2. 必须使用 skill 自己的 venv 解释器，并加 `-I`：

```powershell
$skill = "$env:USERPROFILE\.claude\skills\codex-delegate"
& "$skill\.venv\Scripts\python.exe" -I `
  "$skill\scripts\codex_run.py" `
  --cwd "C:\path\to\your\project" `
  --prompt-file "C:\path\to\prompt.txt" `
  --sandbox read-only
```

3. **stdout** 只有一行 JSON；诊断信息在 **stderr**。

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--cwd` | 必填。Codex 的工作目录 |
| `--prompt-file` | 必填。提示文件路径；`-` 表示从 stdin 读取 |
| `--sandbox` | `read-only`（默认）、`workspace-write`、`full-access` |
| `--thread-id` | 续接此前的线程，保留上下文 |
| `--model` | 可选；省略则用账户默认模型 |
| `--effort` | `none` / `minimal` / `low` / `medium` / `high` / `xhigh` |
| `--timeout` | 超时秒数，默认 `1800` |

### JSON 字段

`ok`、`thread_id`、`status`、`final_response`、`error`、`duration_ms`、`item_types`、`sdk_version`、`sandbox`

### 退出码

| 退出码 | 含义 |
|--------|------|
| `0` | 完成 |
| `1` | Codex 报告失败 |
| `2` | 超时 |
| `3` | 参数或环境错误 |

### 沙箱

- **read-only**：调查、审查、只读分析
- **workspace-write**：只能改 `--cwd` 下的文件。委派前先说明会改哪个目录
- **full-access**：不限制文件系统访问。只有明确同意时才使用

### 怎么写委派提示

Codex 看不到当前对话，提示必须自包含：目标、完成标准、相关路径、约束，以及期望的输出格式。要它改文件时，写清范围和不能碰的文件。

`final_response` 是 Codex 的自述。改文件的任务要用 `git diff`、读文件和测试核对。追问同一件事时用 `--thread-id` 续接。超时只中断等待，Codex 可能已经改了一部分文件，需要检查工作目录。订阅额度由手动使用和委派共用。

### 许可

按仓库现状提供，供个人或团队配合 Claude Code 与 Codex 使用。

## English

The SDK bundles its own Codex runtime and does not consult `PATH` or `~/.codex/packages/standalone/releases`, so delegation stays on the pinned runtime even when several Codex CLI versions are installed.

### What is in this repo

| Path | Purpose |
|------|---------|
| `SKILL.md` | Claude Code skill instructions (Chinese) |
| `scripts/setup.ps1` | Creates a private `.venv` and installs pinned `openai-codex` |
| `scripts/codex_run.py` | Runs one Codex task; prints a single JSON line on stdout |

Default pinned SDK version: **0.163.0** (override with `setup.ps1 -Version`).

### Requirements

- Windows (PowerShell setup script)
- Python 3 with `venv` and `pip`
- ChatGPT subscription already signed in to Codex (`~/.codex/auth.json`)
- Network access for the first SDK install (~150 MB)

Leave `OPENAI_API_KEY` and `CODEX_API_KEY` unset. The runner warns on stderr if either is present, because they can switch billing away from subscription auth.

### Install as a Claude Code skill

Clone this repository into your Claude skills directory:

```powershell
git clone https://github.com/chin1hanwu/codex-delegate.git "$env:USERPROFILE\.claude\skills\codex-delegate"
```

Then run setup once:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\setup.ps1"
```

Claude loads `SKILL.md` when you ask to delegate work to Codex (for example, “让 Codex 审查这段代码”).

### Run a task manually

1. Write the task prompt to a UTF-8 file. Keep long prompts out of the command line.
2. Invoke the script with the skill venv interpreter and `-I`:

```powershell
$skill = "$env:USERPROFILE\.claude\skills\codex-delegate"
& "$skill\.venv\Scripts\python.exe" -I `
  "$skill\scripts\codex_run.py" `
  --cwd "C:\path\to\your\project" `
  --prompt-file "C:\path\to\prompt.txt" `
  --sandbox read-only
```

3. **stdout** is one JSON line; diagnostics go to **stderr**.

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
| `0` | Completed |
| `1` | Codex reported failure |
| `2` | Timeout |
| `3` | Invalid arguments or environment |

### Sandbox guidance

- **read-only** — investigation, review, and read-only analysis
- **workspace-write** — Codex may modify files under `--cwd` only. State the directory before delegating
- **full-access** — unrestricted filesystem access; use only with explicit consent

### Writing delegation prompts

Codex does not see the current chat. Prompts need a goal, done criteria, relevant paths, constraints, and the output format you want. For file edits, name the scope and the files that must stay unchanged.

Treat `final_response` as Codex’s summary. For edits, check `git diff`, the files, and tests. Continue the same task with `--thread-id`. A timeout only stops the wait; Codex may already have changed some files, so inspect the working directory. Subscription quota is shared between manual use and delegated runs.

### License

Provided as-is for personal and team use with Claude Code and Codex.
