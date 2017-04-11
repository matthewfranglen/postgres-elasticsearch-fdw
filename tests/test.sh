#!/bin/bash

set -euo pipefail

readonly COMMAND=$(readlink -f "${0}")
readonly FOLDER=$(dirname "${0}")
readonly VERSION=${1:?Please provide version to test}

cd "${FOLDER}"

function exec_container () {
    readonly CONTAINER="${1}"
    shift

    docker exec -i $(docker-compose -f "docker/${VERSION}/docker-compose.yml" ps -q "${CONTAINER}") "${@}"
}

function load_sql () {
    readonly SQL="${1:?Please provide file to load}"

    exec_container postgres psql -U postgres postgres < "${SQL}"
}

function load_json () {
    readonly JSON="${1:?Please provide file to load}"

    curl --data-binary "@${JSON}" -H "Content-Type: application/x-ndjson" -XPOST "http://localhost:9200/_bulk"
}

load_sql data/schema.sql
load_sql data/data.sql
load_json data/data.json
