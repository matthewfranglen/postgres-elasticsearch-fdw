#!/usr/bin/env python

import argparse
import sys
import time

from lib.set_up import set_up
from lib.load_fixtures import load_fixtures
from lib.test import perform_tests
from lib.tear_down import tear_down

def run_tests(version):
    set_up(version)
    load_fixtures()

    time.sleep(10)

    success = perform_tests(version)

    tear_down(version)

    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up testing environment.')
    parser.add_argument('version', help='PostgreSQL version')
    args = parser.parse_args()

    version = args.version
    result = run_tests(version)

    sys.exit(0 if result else 1)
