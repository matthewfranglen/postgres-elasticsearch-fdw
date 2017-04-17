from os.path import join

import sh

from .tools import DOCKER_FOLDER

def docker_compose(version):
    compose_file = join(DOCKER_FOLDER, version, 'docker-compose.yml')
    return sh.docker_compose.bake('-f', compose_file)

def exec_container(version, container):
    container = container_name(version, container)
    return sh.docker.bake('exec', '-i', container)

def container_name(version, container):
    with io.StringIO() as buf:
        docker_compose(version)('ps', '-q', container, _out=buf)
        return re.sub(r'\n.*', '', buf.getvalue())

def container_port(version, container, port):
    with io.StringIO() as buf:
        docker_compose(version)('port', container, port, _out=buf)
        host_and_port = re.sub(r'\n.*', '', buf.getvalue())
        return re.sub(r'.*:', '', host_and_port)
