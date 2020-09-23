""" Install file for Postgres Elasticsearch Foreign Data Wrapper """
# pylint: disable=line-too-long
from os.path import dirname, join

from setuptools import setup

README_FILE = join(dirname(__file__), "README.md")
with open(README_FILE, "r") as handle:
    LONG_DESCRIPTION = handle.read()

if __name__ == "__main__":
    setup(
        name="pg_es_fdw",
        packages=["pg_es_fdw"],
        version="0.8.0",
        description="Connect PostgreSQL and Elastic Search with this Foreign Data Wrapper",
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        author="Kyle Kubis",
        author_email="kyle.kubis@gmail.com",
        keywords=["postgres", "postgresql", "elastic", "elastic search", "fdw"],
        install_requires=["elasticsearch"],
    )
