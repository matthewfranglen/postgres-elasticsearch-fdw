from os.path import join

import io
import psycopg2
import sh
import re

from lib.tools import TEST_FOLDER

def pg_is_available():
    try:
        return sql('select 1 + 1;')[0][0] == 2
    except Exception:
        return False

def load_sql_file(filename):
    f = join(TEST_FOLDER, 'data', filename)
    with open(f, 'r') as handle:
        sh.psql('postgres', '--no-psqlrc', host='localhost', port='5432', username='postgres', _in=handle)

def run_sql_test(filename):
    f = join(TEST_FOLDER, 'test', filename)
    with open(f, 'r') as handle:
        with io.StringIO() as buf:
            sh.psql('postgres', '--no-psqlrc', '--tuples-only', host='localhost', port='5432', username='postgres', quiet=True, _in=handle, _out=buf)
            return buf.getvalue().strip()

def sql(statement):
    with psycopg2.connect(host='localhost', port=5432, user='postgres', dbname='postgres') as conn:
        with conn.cursor() as cursor:
            cursor.execute(statement)
            return cursor.fetchall()
