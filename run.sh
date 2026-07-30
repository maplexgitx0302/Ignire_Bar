#!/usr/bin/env zsh

set -euo pipefail
cd "${0:A:h}"

if ! python -c "import streamlit" >/dev/null 2>&1; then
  print -u2 "Streamlit is not installed in the active Python environment."
  print -u2 "Run: conda env create -f environment.yml && conda activate calendar-app"
  exit 1
fi

exec python -m streamlit run calendar_app.py "$@"
