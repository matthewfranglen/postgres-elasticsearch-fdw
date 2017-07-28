""" Handles docker compose """

from lib.docker_tools import docker_compose
from lib.tools import show_status

def set_up(version):
    """ Start containers """

    compose = docker_compose(version)

    show_status('Starting testing environment for PostgreSQL {version}...'.format(version=version))

    show_status('Stopping and Removing any old containers...')
    compose('stop')
    compose('rm', '--force')

    show_status('Building new images...')
    compose('build')

    show_status('Starting new containers...')
    compose('up', '-d')

    show_status('Testing environment started')

def tear_down(version):
    """ Stop containers """

    compose = docker_compose(version)

    show_status('Stopping testing environment for PostgreSQL {version}...'.format(version=version))

    compose('down')

    show_status('Testing environment stopped')
