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
    parser.add_argument("version", nargs="+", help="PostgreSQL version")
    args = parser.parse_args()

    result = all(list(run_tests(version) for version in args.version))
    show_status("PASS" if result else "FAIL", newline=True)

    sys.exit(0 if result else 1)


def run_tests(version):
    """ Runs the tests """

    show_status("Testing PostgreSQL {version}".format(version=version), newline=True)

    set_up(version)
    load_fixtures()

    time.sleep(10)

    success = perform_tests(version)

    tear_down(version)

    return success


if __name__ == "__main__":
    main()
