readonly TIMEOUT=30

function lib::wait_for_pg () {
    lib::wait_for "lib::postgres_available"
}

function lib::wait_for_es () {
    lib::wait_for "lib::es_available"
}

function lib::wait_for () {
    local CONDITION="${1}"
    local COUNT=0

    while ! eval ${CONDITION}
    do
        echo -n .

        COUNT=$((${COUNT} + 1))
        if [ ${COUNT} -gt ${TIMEOUT} ]
        then
            echo "Timeout!"
            exit 1
        fi

        sleep 1
    done
    echo
}

function lib::postgres_available () {
    lib::exec_container postgres psql --username postgres -l 2>/dev/null >/dev/null
}

function lib::es_available () {
    curl --fail "http://localhost:9200" >/dev/null
}

function lib::load_sql () {
    local SQL="${1:?Please provide file to load}"

    lib::exec_container postgres psql --username postgres postgres < "${SQL}"
}

function lib::load_json () {
    local JSON="${1:?Please provide file to load}"

    curl --data-binary "@${JSON}" -H "Content-Type: application/x-ndjson" -XPOST "http://localhost:9200/_bulk"
}

function lib::perform_test () {
    local SQL="${1:?Please provide test file}"

    lib::exec_container postgres psql --username postgres --tuples-only --quiet postgres < "${SQL}"
}

function lib::exec_container () {
    local CONTAINER="${1}"
    shift

    docker exec -i $(lib::dc ps -q "${CONTAINER}") "${@}"
}

function lib::dc () {
    docker-compose -f "docker/${VERSION}/docker-compose.yml" "${@}"
}

