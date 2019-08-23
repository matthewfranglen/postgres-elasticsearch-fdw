#!/usr/bin/env python
# pylint: disable=line-too-long
""" Stop the containers """

import argparse

from lib.docker_compose_tools import tear_down


def main():
    """ Stop the containers """

    parser = argparse.ArgumentParser(description="Tear down testing environment.")
    parser.add_argument("--pg", help="PostgreSQL version")
    parser.add_argument("--es", help="Elasticsearch version")
    args = parser.parse_args()

    pg_version = args.pg
    es_version = args.es
    print(
        "Halting environment with PostgreSQL {pg_version} with Elasticsearch {es_version}...".format(
            pg_version=pg_version, es_version=es_version
        )
    )
    tear_down(pg_version, es_version)


if __name__ == "__main__":
    main()
