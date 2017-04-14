#!/usr/bin/env python

import argparse
import lib

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up testing environment.')
    parser.add_argument('version', help='PostgreSQL version')
    args = parser.parse_args()

    version = args.version

    print('Testing PostgreSQL {version}...'.format(version=version))

    print('Waiting for PostgreSQL...')
    lib.wait_for(lib.pg_is_available)

    print('Loading test data into PostgreSQL...')
    print('Loading schema...')
    lib.load_sql_file(version, 'schema.sql')

    print('Loading Postgres data...')
    lib.load_sql_file(version, 'data.sql')
