#!/bin/bash

set -euo pipefail

readonly COMMAND=$(readlink -f "${0}")
readonly FOLDER=$(dirname "${0}")
readonly VERSION=${1:?Please provide version to test}

cd "${FOLDER}"

source lib.sh

function main () {
    local RESULT=0

    load_test_data

    echo -n "Testing read..."
    if [ $(lib::perform_test "test/read.sql") != "t" ]
    then
        RESULT=1
        echo "FAIL"
    else
        echo "PASS"
    fi

    exit ${RESULT}
}

function load_test_data () {
    echo -n "Waiting for Postgres"
    lib::wait_for_pg

    echo "Loading schema..."
    lib::load_sql "data/schema.sql" >/dev/null

    echo "Loading Postgres data..."
    lib::load_sql "data/data.sql" >/dev/null

    echo -n "Waiting for Elastic Search"
    lib::wait_for_es

    echo "Loading Elastic Search data..."
    lib::load_json "data/data.json" >/dev/null
}

main
