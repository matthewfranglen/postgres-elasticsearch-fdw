readonly TIMEOUT=30

function lib::wait_for_pg () {
    local COUNT=0

    while ! exec_container postgres psql --username postgres -l 2>/dev/null >/dev/null
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

function lib::wait_for_es () {
    local COUNT=0

    while ! curl --fail "http://localhost:9200" >/dev/null
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

function lib::load_sql () {
    local SQL="${1:?Please provide file to load}"

    exec_container postgres psql --username postgres postgres < "${SQL}"
}

function lib::load_json () {
    local JSON="${1:?Please provide file to load}"

    curl --data-binary "@${JSON}" -H "Content-Type: application/x-ndjson" -XPOST "http://localhost:9200/_bulk"
}

function lib::perform_test () {
    local SQL="${1:?Please provide test file}"

    exec_container postgres psql --username postgres --tuples-only --quiet postgres < "${SQL}"
}

function lib::exec_container () {
    local CONTAINER="${1}"
    shift

    docker exec -i $(dc ps -q "${CONTAINER}") "${@}"
}

function lib::dc () {
    docker-compose -f "docker/${VERSION}/docker-compose.yml" "${@}"
}

