""" Install file for Postgres Elasticsearch Foreign Data Wrapper """
from setuptools import setup

if __name__ == '__main__':
    setup(
        name = 'pg_es_fdw',
        packages = ['pg_es_fdw'],
        version = '0.4.0',
        description = 'Connect PostgreSQL and Elastic Search with this Foreign Data Wrapper',
        author = 'Matthew Franglen',
        author_email = 'matthew@franglen.org',
        url = 'https://github.com/matthewfranglen/postgres-elasticsearch-fdw',
        download_url = 'https://github.com/matthewfranglen/postgres-elasticsearch-fdw/archive/0.4.0.zip',
        keywords = ['postgres', 'postgresql', 'elastic', 'elastic search', 'fdw'],
        install_requires=[
            'elasticsearch',
        ],
    )
