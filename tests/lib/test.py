#!/usr/bin/env python

import argparse
import io
import sys

from lib.pg_tools import run_sql_test

def perform_tests(version):
    success = True

    print('Testing PostgreSQL {version}...'.format(version=version))

    print('Testing read...')
    result = run_sql_test('read.sql')
    if result == 't':
        print('PASS')
    else:
        print('FAIL')
        success = False

    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up testing environment.')
    parser.add_argument('version', help='PostgreSQL version')
    args = parser.parse_args()

    version = args.version
    success = perform_tests(version)
    sys.exit(0 if success else 1)
