#! /usr/bin/env bash

set -euo pipefail

main() {
    mypy wat --ignore-missing-imports
}

main "$@"
