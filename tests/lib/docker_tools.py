""" Commands for interacting with docker """
# pylint: disable=no-member

import os
from os.path import join

import io
import re
import sh

from .tools import DOCKER_FOLDER


def docker_compose(pg_version, es_version):
    """ Wrapper around the docker compose command """

    base_compose_file = join(DOCKER_FOLDER, "docker-compose.yml")
    pg_compose_file = join(
        DOCKER_FOLDER, "pg-{version}".format(version=pg_version), "docker-compose.yml"
    )
    es_compose_file = join(
        DOCKER_FOLDER, "es-{version}".format(version=es_version), "docker-compose.yml"
    )
    new_env = os.environ.copy()
    new_env["ES_VERSION"] = es_version
    return sh.docker.compose.bake(
        "-f",
        base_compose_file,
        "-f",
        pg_compose_file,
        "-f",
        es_compose_file,
        _env=new_env,
    )


def exec_container(pg_version, es_version, container):
    """ Wrapper around executing commands in a container """

    container = container_name(pg_version, es_version, container)
    return sh.docker.bake("exec", "-i", container)


def container_name(pg_version, es_version, container):
    """ Determine container name """

    with io.StringIO() as buf:
        docker_compose(pg_version, es_version)("ps", "-q", container, _out=buf)
        return re.sub(r"\n.*", "", buf.getvalue())


def container_port(pg_version, es_version, container, port):
    """ Determine mapped container port """

    with io.StringIO() as buf:
        docker_compose(pg_version, es_version)("port", container, port, _out=buf)
        host_and_port = re.sub(r"\n.*", "", buf.getvalue())
        return re.sub(r".*:", "", host_and_port)
