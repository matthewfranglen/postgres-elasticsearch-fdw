#!/usr/bin/env python
""" Run tests against a single version of PostgreSQL """

import argparse
import sys

from lib.pg_tools import run_sql_test
from lib.tools import show_result, show_status


def main():
    """ Run tests against a single version of PostgreSQL """

    parser = argparse.ArgumentParser(description="Set up testing environment.")
    parser.add_argument("--pg", help="PostgreSQL version")
    parser.add_argument("--es", help="Elasticsearch version")
    args = parser.parse_args()

    pg_version = args.pg
    es_version = args.es
    success = perform_tests(pg_version, es_version)
    sys.exit(0 if success else 1)


def perform_tests(pg_version, es_version):
    """ Run tests against a single version of PostgreSQL """

    success = True

    show_status(
        "Testing PostgreSQL {pg_version} with Elasticsearch {es_version}...".format(
            pg_version=pg_version, es_version=es_version
        )
    )

    show_status("Testing read...")
    if not show_result(pg_version, es_version, "read", run_sql_test("read.sql")):
        success = False

    show_status("Testing nested read...")
    if not show_result(
        pg_version, es_version, "nested-read", run_sql_test("nested-read.sql")
    ):
        success = False

    show_status("Testing sorted read...")
    if not show_result(
        pg_version, es_version, "sorted-read", run_sql_test("sorted-read.sql")
    ):
        success = False

    show_status("Testing query...")
    if not show_result(pg_version, es_version, "query", run_sql_test("query.sql")):
        success = False

    show_status("Testing insert returning id...")
    data, error = run_sql_test("insert-return-id.sql")
    if not show_result(
        pg_version, es_version, "insert returning id", (data == "1", error)
    ):
        success = False

    show_status("Testing insert returning row...")
    data, error = run_sql_test("insert-return-row.sql")
    if not show_result(
        pg_version,
        es_version,
        "insert returning row",
        (data == "2 | Test insert title | test insert body", error),
    ):
        success = False

    show_status("Testing insert waiting for refresh...")
    data, error = run_sql_test("insert-wait_for.sql")
    if not show_result(
        pg_version,
        es_version,
        "insert waiting for refresh",
        (data == "3 | Test insert wait for title | test insert wait for body", error),
    ):
        success = False

    return success


if __name__ == "__main__":
    main()
