---
name: codex-delegate
description: 把一个定义清楚的编码、调查、审查或第二意见任务委派给 Codex,通过固定版本的 Python SDK 并使用 ChatGPT 订阅登录,返回结构化 JSON。用户要求"让 Codex 做/看/审"、"委派给 Codex"、"用 Codex 验证"时使用。不要在 Windows 上直接调用裸 `codex` 或 `codex exec`。
---

# 委派任务给 Codex

通过 `scripts/codex_run.py` 调用 `openai-codex` SDK。SDK 自带固定版本的 Codex 运行时,不读 PATH,也不读 `~/.codex/packages/standalone/releases`,所以不受机器上多个 Codex 版本的影响。认证沿用本机已有的 ChatGPT 订阅登录(`~/.codex/auth.json`),不需要 API key。

## 首次使用

如果 `.venv` 不存在,先运行一次:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\setup.ps1"
```

它会创建 skill 私有的 venv，并安装固定版本的 `openai-codex`。仓库本身只有几十 KB。体积来自依赖 `openai-codex-cli-bin`（Windows x64 的 wheel 约 147MB，需联网），里面是随 SDK 固定的 Codex 运行时。pip 只下当前系统这一份。升级版本时给 `-Version` 传新版本号。

## 调用方式

1. 把任务写进一个临时文件,用 UTF-8 编码,不要把长提示塞进命令行参数。
2. 运行脚本。必须使用 venv 的解释器,并加 `-I`:

```powershell
& "$env:USERPROFILE\.claude\skills\codex-delegate\.venv\Scripts\python.exe" -I `
  "$env:USERPROFILE\.claude\skills\codex-delegate\scripts\codex_run.py" `
  --cwd "<工作目录>" --prompt-file "<提示文件>" --sandbox read-only
```

3. stdout 只有一行 JSON,解析它。诊断信息在 stderr。

| 参数 | 说明 |
|---|---|
| `--cwd` | 必填,Codex 的工作目录 |
| `--prompt-file` | 必填,提示文件路径,`-` 表示从 stdin 读 |
| `--sandbox` | `read-only`(默认)、`workspace-write`、`full-access` |
| `--thread-id` | 续接此前的线程,保留上下文 |
| `--model` | 不填则用账户默认模型 |
| `--effort` | `none`/`minimal`/`low`/`medium`/`high`/`xhigh` |
| `--timeout` | 秒,默认 1800 |

## 返回值

字段:`ok`、`thread_id`、`status`、`final_response`、`error`、`duration_ms`、`item_types`、`sdk_version`、`sandbox`。

退出码:0 完成,1 Codex 报告失败,2 超时,3 参数或环境错误。

## 选沙箱

- 调查、审查、第二意见:`read-only`。
- 需要 Codex 改文件:`workspace-write`,只能写工作目录。委派前先说明会改哪个目录。
- `full-access` 不限制文件系统访问。只有用户明确同意才能用。

## 写好委派提示

Codex 看不到当前对话,提示必须自包含:

- 目标和完成标准。
- 相关文件路径、已知约束、已经排除的方向。
- 想要的输出格式,例如"只列问题,不要改代码"。
- 要它改文件时,写清范围和不能碰的文件。

## 收到结果之后

- `final_response` 是 Codex 的自述,不是证据。要改文件的任务,用 `git diff` 或直接读文件核对,必要时重新运行测试,再向用户汇报。
- `ok` 为 false 时,把 `error` 如实告诉用户,不要说成功。
- 追问同一件事时用 `--thread-id` 续接,不要新开线程重讲背景。
- 不要为了并发在同一目录同时启动多个可写任务。

## 注意

- 环境里不要设置 `OPENAI_API_KEY` 或 `CODEX_API_KEY`,否则可能改走按量计费。脚本检测到会在 stderr 警告。
- 订阅额度由手动使用和委派共用,批量委派会消耗额度。
- 超时路径已实测:返回 `ok: false`、退出码 2,退出 3 秒后没有遗留 `codex.exe` 进程。超时只中断等待,Codex 可能已经改了一部分文件,需要检查工作目录。
