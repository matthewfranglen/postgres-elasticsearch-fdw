# pylint: disable=line-too-long
""" Handles docker compose """

import sys

from sh import ErrorReturnCode

from lib.docker_tools import docker_compose
from lib.tools import show_status


def set_up(pg_version, es_version):
    """ Start containers """

    compose = docker_compose(pg_version, es_version)

    show_status(
        "Starting testing environment for PostgreSQL {pg_version} with Elasticsearch {es_version}...".format(
            pg_version=pg_version, es_version=es_version
        )
    )

    show_status("Stopping and Removing any old containers...")
    compose("stop")
    compose("rm", "--force")

    show_status("Building new images...")
    try:
        compose("build")
    except ErrorReturnCode as exc:
        print("Failed to build images...")
        print(exc.stdout.decode("utf-8"))
        print()
        print(exc.stderr.decode("utf-8"))
        sys.exit(1)

    show_status("Starting new containers...")
    compose("up", "-d")

    show_status("Testing environment started")


def tear_down(pg_version, es_version):
    """ Stop containers """

    compose = docker_compose(pg_version, es_version)

    show_status(
        "Stopping testing environment for PostgreSQL {pg_version} with Elasticsearch {es_version}...".format(
            pg_version=pg_version, es_version=es_version
        )
    )

    compose("down")

    show_status("Testing environment stopped")
