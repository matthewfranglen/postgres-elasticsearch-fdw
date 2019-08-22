""" Commands for interacting with PostgreSQL """
# pylint: disable=broad-except, no-member

from os.path import join

import io
import psycopg2
import sh

from lib.tools import TEST_FOLDER

def pg_is_available():
    """ Test if PostgreSQL is running """

    try:
        return sql('select 1 + 1;')[0][0] == 2
    except Exception:
        return False

def load_sql_file(filename):
    """ Load SQL file into PostgreSQL """

    path = join(TEST_FOLDER, 'data', filename)
    with open(path, 'r') as handle:
        sh.psql(
            'postgres',
            '--no-psqlrc',
            host='localhost',
            port='5432',
            username='postgres',
            _in=handle
        )

def run_sql_test(filename):
    """ Run SQL test file """

    path = join(TEST_FOLDER, 'test', filename)
    with open(path, 'r') as handle:
        with io.StringIO() as out, io.StringIO() as err:
            sh.psql(
                'postgres',
                '--no-psqlrc',
                '--tuples-only',
                host='localhost',
                port='5432',
                username='postgres',
                quiet=True,
                _in=handle,
                _out=out,
                _err=err
            )
            return out.getvalue().strip(), err.getvalue().strip()

def sql(statement):
    """ Execute SQL statement """

    with psycopg2.connect(host='localhost', port=5432, user='postgres', dbname='postgres') as conn:
        with conn.cursor() as cursor:
            cursor.execute(statement)
            return cursor.fetchall()
