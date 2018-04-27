#! /usr/bin/env bash

set -euo pipefail

main() {
    pylint wat --errors-only
}

main "$@"
