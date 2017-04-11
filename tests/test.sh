#!/bin/bash

set -euo pipefail

readonly COMMAND=$(readlink -f "${0}")
readonly FOLDER=$(dirname "${0}")
readonly VERSION=${1:?Please provide version to test}

cd "${FOLDER}"

function main () {
    dc stop       || true
    dc rm --force || true
    dc build
    dc up -d

    sleep 30

    echo "Loading schema..."
    load_sql "data/schema.sql" >/dev/null

    echo "Loading Postgres data..."
    load_sql "data/data.sql" >/dev/null

    echo "Loading Elastic Search data..."
    load_json "data/data.json" >/dev/null

    echo "Testing read..."
    perform_test "test/read.sql"
    echo

    dc down
}

function wait_for_pg () {
    while ! nc localhost 5432 </dev/null
    do
        sleep 1
    done
}

function load_sql () {
    local SQL="${1:?Please provide file to load}"

    exec_container postgres psql --username postgres postgres < "${SQL}"
}

function load_json () {
    local JSON="${1:?Please provide file to load}"

    curl --data-binary "@${JSON}" -H "Content-Type: application/x-ndjson" -XPOST "http://localhost:9200/_bulk"
}

function perform_test () {
    local SQL="${1:?Please provide test file}"

    exec_container postgres psql --username postgres --tuples-only --quiet postgres < "${SQL}"
}

function exec_container () {
    local CONTAINER="${1}"
    shift

    docker exec -i $(dc ps -q "${CONTAINER}") "${@}"
}

function dc () {
    docker-compose -f "docker/${VERSION}/docker-compose.yml" "${@}"
}

main
