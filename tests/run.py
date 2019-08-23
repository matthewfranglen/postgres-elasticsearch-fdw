#!/usr/bin/env python
""" Runs the tests """

import argparse
import sys
import time

from lib.docker_compose_tools import set_up, tear_down
from lib.load_fixtures import load_fixtures
from lib.test import perform_tests
from lib.tools import show_status


def main():
    """ Runs the tests """

    parser = argparse.ArgumentParser(description="Perform end to end tests.")
    parser.add_argument("--pg", nargs="+", help="PostgreSQL version")
    parser.add_argument("--es", nargs="+", help="Elasticsearch version")
    args = parser.parse_args()

    result = all(
        run_tests(pg_version, es_version)
        for pg_version in args.pg
        for es_version in args.es
    )
    show_status("PASS" if result else "FAIL", newline=True)

    sys.exit(0 if result else 1)


def run_tests(pg_version, es_version):
    """ Runs the tests """

    show_status(
        "Testing PostgreSQL {pg_version} with Elasticsearch {es_version}".format(
            pg_version=pg_version, es_version=es_version
        ),
        newline=True,
    )

    set_up(pg_version, es_version)
    load_fixtures()

    time.sleep(10)

    success = perform_tests(pg_version, es_version)

    tear_down(pg_version, es_version)

    return success


if __name__ == "__main__":
    main()
