""" Load fixtures into PostgreSQL and Elastic Search """

from lib.es_tools import es_is_available, load_json_file
from lib.pg_tools import load_sql_file, pg_is_available
from lib.tools import show_status, wait_for


def load_fixtures():
    """ Load fixtures into PostgreSQL and Elastic Search """

    show_status("Loading fixtures")

    show_status("Waiting for PostgreSQL...")
    wait_for(pg_is_available)

    show_status("Loading PostgreSQL schema...")
    load_sql_file("schema.sql")

    show_status("Loading PostgreSQL data...")
    load_sql_file("data.sql")

    show_status("Waiting for Elastic Search...")
    wait_for(es_is_available)

    show_status("Loading Elastic Search data...")
    load_json_file("data.json")
    load_json_file("nested-data.json")
