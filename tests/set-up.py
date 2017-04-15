#!/usr/bin/env python

import argparse
import lib

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up testing environment.')
    parser.add_argument('version', help='PostgreSQL version')
    args = parser.parse_args()

    version = args.version
    dc = lib.docker_compose(version)

    print('Starting testing environment for PostgreSQL {version}...'.format(version=version))

    print('Stopping and Removing any old containers...')
    dc('stop')
    dc('rm', '--force')

    print('Building new images...')
    dc('build')

    print('Starting new containers...')
    dc('up', '-d')

    print('Testing environment started')
