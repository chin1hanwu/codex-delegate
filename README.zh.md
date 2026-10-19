<h1 align="center">codex-delegate</h1>

<p align="center">把 Claude Code 里的一件事，交给本机已经登录的 Codex。</p>

<p align="center">
  <a href="#快速开始"><img src="https://img.shields.io/badge/get_started-quickstart-149954?style=flat-square" alt="快速开始"></a>
  <a href="#它怎么跑"><img src="https://img.shields.io/badge/runtime-pinned%20sdk-007ec6?style=flat-square" alt="运行时"></a>
  <a href="#参数"><img src="https://img.shields.io/badge/cli-parameters-68448b?style=flat-square" alt="参数"></a>
  <a href="#沙箱"><img src="https://img.shields.io/badge/sandbox-three%20modes-e65100?style=flat-square" alt="沙箱"></a>
  <a href="https://pypi.org/project/openai-codex/0.163.0/"><img src="https://img.shields.io/badge/sdk-openai--codex%200.163.0-ffd21e?style=flat-square" alt="openai-codex 0.163.0"></a>
  <a href="SKILL.md"><img src="https://img.shields.io/badge/Claude%20Code-SKILL.md-f28c45?style=flat-square" alt="SKILL.md"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-4c6ef5?style=flat-square" alt="MIT License"></a>
</p>

[English](README.md) | 中文

**codex-delegate** 是给 Claude Code 用的 skill。一件任务通过固定版本的 [`openai-codex`](https://pypi.org/project/openai-codex/) **0.163.0** 交给 Codex。登录用的是已经写在磁盘上的 ChatGPT 订阅，`~/.codex/auth.json`。运行时打在这个 wheel 里，调用时用这一份，不跟 `PATH` 上的 `codex`，也不跟 `~/.codex/packages` 里的其他拷贝。

<p align="center"><code>Claude Code</code> → <code>codex_run.py</code> → <code>openai-codex 0.163.0</code> → <code>Codex</code></p>

---

## 快速开始

### 1. 安装

Windows，本机有 Python 3，Codex 已经登录过。第一次大约下载 150MB。

```powershell
git clone https://github.com/chin1hanwu/codex-delegate.git "$env:USERPROFILE\.claude\skills\codex-delegate"

powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\setup.ps1"
```

要换 SDK 版本：`setup.ps1 -Version x.y.z`。

### 2. 对 Claude 说

skill 放到目录里之后，直接在对话里说，例如「让 Codex 审查这段代码」。Claude 会读 [SKILL.md](SKILL.md)，再去跑脚本。

### 3. 自己调用

提示写成 UTF-8 文件。解释器用 skill 目录里的 `.venv`，加上 `-I`。

```powershell
$skill = "$env:USERPROFILE\.claude\skills\codex-delegate"

& "$skill\.venv\Scripts\python.exe" -I `
  "$skill\scripts\codex_run.py" `
  --cwd "C:\path\to\project" `
  --prompt-file "C:\path\to\prompt.txt" `
  --sandbox read-only
```

stdout 只有一个 JSON。其余输出在 stderr。

---

## 它怎么跑

| 路径 | 做什么 |
| --- | --- |
| `SKILL.md` | Claude 读的说明 |
| `scripts/setup.ps1` | 私有 `.venv`，装上固定版本的 `openai-codex` |
| `scripts/codex_run.py` | 进一个任务，出一行 JSON |

| 退出码 | 含义 |
| --- | --- |
| `0` | 完成 |
| `1` | Codex 报了失败 |
| `2` | 超时 |
| `3` | 参数或环境不对 |

返回字段：`ok`、`thread_id`、`status`、`final_response`、`error`、`duration_ms`、`item_types`、`sdk_version`、`sandbox`。

`final_response` 是 Codex 自己对这次运行的说法。改过文件就看 diff，再跑测试。同一件事接着问，带上 `--thread-id`。超时是脚本不再等，`--cwd` 里可能已经有改动。

---

## 参数

| 参数 | 含义 |
| --- | --- |
| `--cwd` | 工作目录，必填 |
| `--prompt-file` | 提示文件；`-` 表示从 stdin 读。必填 |
| `--sandbox` | `read-only`（默认）、`workspace-write`、`full-access` |
| `--thread-id` | 接着上次的线程 |
| `--model` | 不填就用账户默认模型 |
| `--effort` | `none` `minimal` `low` `medium` `high` `xhigh` |
| `--timeout` | 秒，默认 `1800` |

---

## 沙箱

| 模式 | 能碰到什么 |
| --- | --- |
| `read-only` | 查看、审查。默认是这个 |
| `workspace-write` | 只能改 `--cwd` 下面的文件 |
| `full-access` | 不限制文件系统。用之前先说清楚 |

Codex 看不到这段聊天。目标、怎样算做完、路径、约束、想要的格式，都写在提示里。要改代码，就写明可以动哪里。

---

## 说明

- 别在环境里留 `OPENAI_API_KEY` 或 `CODEX_API_KEY`。有的话，计费可能离开 ChatGPT 订阅。脚本会在 stderr 里说一声。
- 委派和你自己开 Codex 用的是同一份订阅额度。
- `setup.ps1` 是 PowerShell，这条安装路径是 Windows。

给 Claude 看的说明在 [SKILL.md](SKILL.md)。

### 许可证

[MIT](LICENSE)。Copyright (c) 2026 chin1hanwu。
