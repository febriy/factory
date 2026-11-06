#!/usr/bin/env bash
# Template version 1. Configure product_checks before enabling this harness.
set -uo pipefail

root=$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel) || exit 2
cd "$root" || exit 2
mode=${1:-full}
if [[ $# -gt 1 || ( "$mode" != fast && "$mode" != full ) ]]; then
  echo "Usage: bash scripts/agent-check.sh [fast|full]" >&2
  exit 2
fi

failures=0
checks=0
configuration_errors=0
run_check() {
  if [[ $# -lt 2 ]]; then
    echo "FAIL: run_check requires a label and command." >&2
    configuration_errors=$((configuration_errors + 1))
    return 0
  fi
  local label=$1 result
  shift
  checks=$((checks + 1))
  "$@"
  result=$?
  if [[ $result -eq 0 ]]; then
    echo "PASS: $label"
  else
    echo "FAIL: $label (exit $result)" >&2
    failures=$((failures + 1))
  fi
  return 0
}

product_checks() {
  # Replace this body with the target's verified native commands.
  # Use run_check LABEL COMMAND ARG...; select any fast subset with $1.
  echo "NOT CONFIGURED: inspect the product and configure product_checks." >&2
  return 2
}

product_checks "$mode"
configuration_result=$?
if [[ $configuration_result -ne 0 || $configuration_errors -ne 0 || $checks -eq 0 ]]; then
  echo "FAIL: check configuration incomplete; no acceptance evidence produced." >&2
  exit 2
fi
if [[ $failures -ne 0 ]]; then
  echo "FAIL: $failures of $checks checks failed ($mode)." >&2
  exit 1
fi
echo "PASS: $checks checks ($mode)."
