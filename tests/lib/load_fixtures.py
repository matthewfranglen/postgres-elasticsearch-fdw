#!/usr/bin/env python

import argparse
import io
import sys

from lib.tools import wait_for
from lib.es_tools import load_json_file, es_is_available
from lib.pg_tools import load_sql_file, pg_is_available

def load_fixtures():
    print('Loading fixtures')

    print('Waiting for PostgreSQL...')
    wait_for(pg_is_available)

    print('Loading test data into PostgreSQL...')
    print('Loading schema...')
    load_sql_file('schema.sql')

    print('Loading Postgres data...')
    load_sql_file('data.sql')

    print('Waiting for Elastic Search...')
    wait_for(es_is_available)

    print('Loading Elastic Search data...')
    load_json_file('data.json')

if __name__ == "__main__":
    load_fixtures()
