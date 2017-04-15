#!/usr/bin/env python

import argparse
import io
import lib
import sys

def main(version):
    success = True

    print('Testing PostgreSQL {version}...'.format(version=version))

    load_data(version)

    print('Testing read...')
    result = lib.run_sql_test(version, 'read.sql').strip()
    if result == 't':
        print('PASS')
    else:
        print('FAIL')
        success = False

    sys.exit(0 if success else 1)

def load_data(version):
    print('Waiting for PostgreSQL...')
    lib.wait_for(lib.pg_is_available(version))

    print('Loading test data into PostgreSQL...')
    print('Loading schema...')
    lib.load_sql_file(version, 'schema.sql')

    print('Loading Postgres data...')
    lib.load_sql_file(version, 'data.sql')

    print('Showing container logs...')
    with io.StringIO() as buf:
        lib.docker_compose(version)('logs', _out=buf)
        print(buf.getvalue())

    print('Waiting for Elastic Search...')
    lib.wait_for(lib.es_is_available(version))

    print('Loading Elastic Search data...')
    lib.load_json_file(version, 'data.json')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up testing environment.')
    parser.add_argument('version', help='PostgreSQL version')
    args = parser.parse_args()

    version = args.version
    main(version)
