# Create the skill's private venv and install the pinned Codex SDK.
# The SDK wheel bundles its own Codex runtime, so PATH and ~/.codex releases are never consulted.
param([string]$Version = "0.163.0")

$ErrorActionPreference = "Stop"
$skill = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $skill ".venv"
$py = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $py)) { python -m venv $venv }
& $py -m pip install --quiet "openai-codex==$Version"
& $py -I -c "from openai_codex._version import __version__ as v; print('openai-codex', v)"
