from os.path import abspath, dirname, join

import psycopg2
import requests
import sh
import time

PROJECT_FOLDER=dirname(dirname(dirname(abspath(__file__))))
TEST_FOLDER=join(PROJECT_FOLDER, 'tests')
DOCKER_FOLDER=join(TEST_FOLDER, 'docker')

def docker_compose(version, *args):
    compose_file=join(DOCKER_FOLDER, version, 'docker-compose.yml')
    sh.docker_compose('-f', compose_file, *args)

def wait_for(condition):
    for i in xrange(120):
        if condition():
            return True
        time.sleep(1)

def test_pg():
    try:
        return sql('select 1 + 1;')[0][0] == 2
    except Exception:
        return False

def test_es():
    try:
        return requests.get('http://localhost:9200').json()['tagline'] == 'You Know, for Search'
    except Exception:
        return False

def sql(statement):
    with psycopg2.connect(host='localhost', port=5432, user='postgres', dbname='postgres') as conn:
        with conn.cursor() as cursor:
            cursor.execute(statement)
            return cursor.fetchall()
