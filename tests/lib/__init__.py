from os.path import abspath, dirname, join

import sh
import psycopg2
import requests

PROJECT_FOLDER=dirname(dirname(abspath(__file__)))
DOCKER_FOLDER=join(PROJECT_FOLDER, 'docker')

def docker_compose(version, *args):
    sh.docker_compose('-f', 'docker/{version}/docker-compose.yml'.format(version=version), *args)

def test_pg():
    try:
        with psycopg2.connect(host='localhost', port=5432, user='postgres', dbname='postgres') as conn:
            with conn.cursor() as cursor:
                cursor.execute('select 1 + 1;')
                return cursor.fetchone()[0] == 2
    except Exception:
        return False

def test_es():
    try:
        return requests.get('http://localhost:9200').json()['tagline'] == 'You Know, for Search'
    except Exception:
        return False
