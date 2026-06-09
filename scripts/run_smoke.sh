#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"
to_windows_path() {
  local path="$1"
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$path"
  elif command -v wslpath >/dev/null 2>&1; then
    wslpath -w "$path"
  elif [[ "$path" == /mnt/?/* ]]; then
    local drive="${path:5:1}"
    local rest="${path:7}"
    rest="${rest//\//\\}"
    printf '%s:\\%s' "${drive^^}" "$rest"
  else
    printf '%s' "$path"
  fi
}
if [ -x /mnt/c/Users/wangz/AppData/Local/Programs/Python/Python310/python.exe ]; then
  PYTHON_BIN=/mnt/c/Users/wangz/AppData/Local/Programs/Python/Python310/python.exe
  PROJECT_SRC="$(to_windows_path "${PROJECT_ROOT}/src")"
  PYTHONPATH_SEP=";"
elif command -v python.exe >/dev/null 2>&1; then
  PYTHON_BIN=python.exe
  PROJECT_SRC="$(to_windows_path "${PROJECT_ROOT}/src")"
  PYTHONPATH_SEP=";"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
  PROJECT_SRC="${PROJECT_ROOT}/src"
  PYTHONPATH_SEP=":"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
  PROJECT_SRC="${PROJECT_ROOT}/src"
  PYTHONPATH_SEP=":"
else
  PYTHON_BIN=py.exe
  PROJECT_SRC="$(to_windows_path "${PROJECT_ROOT}/src")"
  PYTHONPATH_SEP=";"
fi
"${PYTHON_BIN}" -c "import runpy, sys; sys.path.insert(0, r'${PROJECT_SRC}'); runpy.run_module('tokenized_world_best_of_n.pipeline', run_name='__main__')" --mode smoke
"${PYTHON_BIN}" -c "import runpy, sys; sys.path.insert(0, r'${PROJECT_SRC}'); runpy.run_module('tokenized_world_best_of_n.audit', run_name='__main__')"
