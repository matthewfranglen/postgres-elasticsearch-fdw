#!/usr/bin/env python
# pylint: disable=line-too-long
""" Start the containers """

import argparse

from lib.docker_compose_tools import set_up


def main():
    """ Start the containers """

    parser = argparse.ArgumentParser(description="Set up testing environment.")
    parser.add_argument("--pg", help="PostgreSQL version")
    parser.add_argument("--es", help="Elasticsearch version")
    args = parser.parse_args()

    pg_version = args.pg
    es_version = args.es
    print(
        "Starting environment with PostgreSQL {pg_version} with Elasticsearch {es_version}...".format(
            pg_version=pg_version, es_version=es_version
        )
    )
    set_up(pg_version, es_version)


if __name__ == "__main__":
    main()
