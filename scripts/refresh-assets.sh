#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_FILE="${REPO_ROOT}/data/contribution_calendar_summary.json"

if [[ ! -f "${DATA_FILE}" ]]; then
  echo "Missing contribution data file: ${DATA_FILE}" >&2
  exit 1
fi

python3 "${REPO_ROOT}/scripts/build_profile_assets.py" \
  --output-dir "${REPO_ROOT}/assets" \
  --contributions-json "${DATA_FILE}"

echo "Profile assets refreshed in ${REPO_ROOT}/assets"
