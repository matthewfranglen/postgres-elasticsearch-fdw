#!/usr/bin/env python

import argparse

from lib.docker_tools import docker_compose
from lib.tools import show_status

def set_up(version):
    dc = docker_compose(version)

    show_status('Starting testing environment for PostgreSQL {version}...'.format(version=version))

    show_status('Stopping and Removing any old containers...')
    dc('stop')
    dc('rm', '--force')

    show_status('Building new images...')
    dc('build')

    show_status('Starting new containers...')
    dc('up', '-d')

    show_status('Testing environment started')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up testing environment.')
    parser.add_argument('version', help='PostgreSQL version')
    args = parser.parse_args()

    version = args.version
    set_up(version)
