from os.path import abspath, dirname, join

import io
import json
import psycopg2
import re
import requests
import sh
import time

PROJECT_FOLDER=dirname(dirname(dirname(abspath(__file__))))
TEST_FOLDER=join(PROJECT_FOLDER, 'tests')
DOCKER_FOLDER=join(TEST_FOLDER, 'docker')

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

def wait_for(condition):
    for i in range(120):
        if condition():
            return True
        time.sleep(1)

def pg_is_available(version):
    port = container_port(version, 'postgres', 5432)

    def condition():
        try:
            return sql('select 1 + 1;', port)[0][0] == 2
        except Exception:
            return False
    return condition

def es_is_available(version):
    port = container_port(version, 'elasticsearch', 9200)
    url = 'http://localhost:{port}'.format(port=port)

    def condition():
        try:
            return requests.get(url).json()['tagline'] == 'You Know, for Search'
        except Exception:
            return False
    return condition

def load_sql_file(version, filename):
    f = join(TEST_FOLDER, 'data', filename)
    with open(f, 'r') as handle:
        exec_container(version, 'postgres')('psql', '--username', 'postgres', 'postgres', _in=handle)

def run_sql_test(version, filename):
    f = join(TEST_FOLDER, 'test', filename)
    with open(f, 'r') as handle:
        with io.StringIO() as buf:
            exec_container(version, 'postgres')('psql', '--username', 'postgres', '--tuples-only', '--quiet', 'postgres', _in=handle, _out=buf)
            return buf.getvalue()

def load_json_file(version, filename):
    port = container_port(version, 'elasticsearch', 9200)
    url = 'http://localhost:{port}/_bulk'.format(port=port)
    f = join(TEST_FOLDER, 'data', filename)
    headers = {'Content-Type': 'application/x-ndjson'}

    with open(f, 'r') as handle:
        body = handle.read().encode(encoding='utf-8')
        requests.post(url, headers=headers, data=body)

def sql(statement, port):
    with psycopg2.connect(host='localhost', port=port, user='postgres', dbname='postgres') as conn:
        with conn.cursor() as cursor:
            cursor.execute(statement)
            return cursor.fetchall()
