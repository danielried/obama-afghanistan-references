#!/usr/bin/env bash
# Re-run all 12 correlation analyses with the project venv.
# Setup once (from the project root):
#   python3 -m venv .venv && .venv/bin/pip install -r output/analyses/requirements.txt
# Usage: output/analyses/run_all.sh [key ...]   e.g. run_all.sh 02_election 08_casualties
# Offline only: 12_congress/fetch_house.py (network) is never run here.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(cd "$HERE/../.." && pwd)"
PY="$PROJECT/.venv/bin/python"
[ -x "$PY" ] || { echo "missing $PY; see setup line at top of this file" >&2; exit 1; }

if [ $# -gt 0 ]; then keys=("$@"); else
  keys=(); for d in "$HERE"/[01][0-9]_*/; do [ -f "$d/analysis.py" ] && keys+=("$(basename "$d")"); done
fi

fail=0
for k in "${keys[@]}"; do
  s="$HERE/$k/analysis.py"
  [ -f "$s" ] || { echo "$k: no analysis.py" >&2; fail=1; continue; }
  start=$SECONDS
  if "$PY" -I "$s" > "$HERE/$k/last_run.log" 2>&1; then
    echo "$k ok ($((SECONDS - start))s)"
  else
    echo "$k FAILED ($((SECONDS - start))s) - see $k/last_run.log" >&2; fail=1
  fi
done
exit $fail
