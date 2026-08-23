#!/usr/bin/env bash
# Idempotent bootstrap for the sf-technical-designer plugin engine.
#
# Creates a persistent Python venv (in CLAUDE_PLUGIN_DATA, so it survives plugin
# updates) with the rendering dependencies, then exports the paths the plugin's
# agents need via $CLAUDE_ENV_FILE — which Claude Code sources before every Bash
# command in the session. Cross-platform (Windows Git Bash / macOS / Linux).
set -u

ROOT="${CLAUDE_PLUGIN_ROOT:?CLAUDE_PLUGIN_ROOT not set}"
DATA="${CLAUDE_PLUGIN_DATA:-$HOME/.sf-technical-designer}"
VENV="$DATA/venv"

venv_py() {
  if [ -x "$VENV/Scripts/python.exe" ]; then echo "$VENV/Scripts/python.exe"
  elif [ -x "$VENV/bin/python" ]; then echo "$VENV/bin/python"
  else echo ""; fi
}

PY="$(venv_py)"
if [ -z "$PY" ]; then
  if command -v python3 >/dev/null 2>&1; then BASE_PY=python3
  elif command -v python >/dev/null 2>&1; then BASE_PY=python
  else
    echo "[sf-technical-designer] Python 3 not found on PATH — install it, then restart the session." >&2
    exit 0
  fi
  mkdir -p "$DATA"
  if "$BASE_PY" -m venv "$VENV" 2>/dev/null; then
    PY="$(venv_py)"
    "$PY" -m pip install -q --upgrade pip >/dev/null 2>&1
    "$PY" -m pip install -q -r "$ROOT/requirements.txt" >/dev/null 2>&1 \
      || echo "[sf-technical-designer] dependency install failed (offline?). Run: \"$PY\" -m pip install -r \"$ROOT/requirements.txt\"" >&2
  else
    echo "[sf-technical-designer] venv creation failed; using base Python (deps may be missing)." >&2
    PY="$BASE_PY"
  fi
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export SFTD_PYTHON=\"$PY\""
    echo "export SFTD_ROOT=\"$ROOT\""
    echo "export PYTHONPATH=\"$ROOT:\${PYTHONPATH:-}\""
    echo "export PYTHONUTF8=1"
  } >> "$CLAUDE_ENV_FILE"
fi
exit 0
