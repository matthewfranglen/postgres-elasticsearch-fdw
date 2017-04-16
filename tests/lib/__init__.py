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

def wait_for(condition):
    for i in range(120):
        if condition():
            return True
        time.sleep(1)

def pg_is_available():
    def condition():
        try:
            return sql('select 1 + 1;')[0][0] == 2
        except Exception:
            return False
    return condition

def es_is_available():
    url = 'http://localhost:9200'

    def condition():
        try:
            return requests.get(url).json()['tagline'] == 'You Know, for Search'
        except Exception:
            return False
    return condition

def load_sql_file(filename):
    f = join(TEST_FOLDER, 'data', filename)
    with open(f, 'r') as handle:
        sh.psql('--username', 'postgres', 'postgres', _in=handle)

def run_sql_test(filename):
    f = join(TEST_FOLDER, 'test', filename)
    with open(f, 'r') as handle:
        with io.StringIO() as buf:
            sh.psql('--username', 'postgres', '--tuples-only', '--quiet', 'postgres', _in=handle, _out=buf)
            return buf.getvalue()

def load_json_file(filename):
    url = 'http://localhost:9200/_bulk'
    f = join(TEST_FOLDER, 'data', filename)
    headers = {'Content-Type': 'application/x-ndjson'}

    with open(f, 'r') as handle:
        body = handle.read().decode('utf-8')
        requests.post(url, headers=headers, data=body)

def sql(statement):
    with psycopg2.connect(user='postgres', dbname='postgres') as conn:
        with conn.cursor() as cursor:
            cursor.execute(statement)
            return cursor.fetchall()
