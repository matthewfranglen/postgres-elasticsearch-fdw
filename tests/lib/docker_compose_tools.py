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

def tear_down(version):
    dc = docker_compose(version)

    show_status('Stopping testing environment for PostgreSQL {version}...'.format(version=version))

    dc('down')

    show_status('Testing environment stopped')
