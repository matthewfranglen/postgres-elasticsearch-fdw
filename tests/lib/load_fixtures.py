""" Load fixtures into PostgreSQL and Elastic Search """

from lib.es_tools import es_is_available, load_json_file
from lib.pg_tools import load_sql_file, pg_is_available
from lib.tools import show_status, wait_for


def load_fixtures(es_version, es_version_option):
    """ Load fixtures into PostgreSQL and Elastic Search """

    show_status("Loading fixtures")

    show_status("Waiting for PostgreSQL...")
    wait_for(pg_is_available)

    show_status("Loading PostgreSQL schema...")
    if es_version_option and es_version in ["7", "8"]:
        load_sql_file("schema-{es_version}.sql".format(es_version=es_version))
    else:
        load_sql_file("schema.sql")

    show_status("Loading PostgreSQL data...")
    load_sql_file("data.sql")

    show_status("Waiting for Elastic Search...")
    wait_for(es_is_available)

    show_status("Loading Elastic Search data...")
    if es_version and es_version in ["7", "8"]:
        load_json_file("data-{}.json".format(es_version))
        load_json_file("nested-data-{}.json".format(es_version))
    else:
        load_json_file("data.json")
        load_json_file("nested-data.json")
