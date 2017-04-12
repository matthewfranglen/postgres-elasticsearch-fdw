#!/bin/bash

set -euo pipefail

readonly COMMAND=$(readlink -f "${0}")
readonly FOLDER=$(dirname "${0}")

cd "${FOLDER}"

source lib.sh

function main () {
    lib::dc down
}

main
