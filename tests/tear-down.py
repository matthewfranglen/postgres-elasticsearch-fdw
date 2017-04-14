#!/usr/bin/env python

import argparse
import lib

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up testing environment.')
    parser.add_argument('version', help='PostgreSQL version')
    args = parser.parse_args()

    version = args.version
    dc = lambda *args: lib.docker_compose(version, *args)

    print('Stopping testing environment for PostgreSQL {version}...'.format(version=version))

    dc('down')

    print('Testing environment stopped')
