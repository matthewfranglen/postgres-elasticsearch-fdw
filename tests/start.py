#!/usr/bin/env python
""" Start the containers """

import argparse

from lib.docker_compose_tools import set_up


def main():
    """ Start the containers """

    parser = argparse.ArgumentParser(description="Set up testing environment.")
    parser.add_argument("version", help="PostgreSQL version")
    args = parser.parse_args()

    version = args.version
    print("Starting environment with PostgreSQL {version}".format(version=version))
    set_up(version)


if __name__ == "__main__":
    main()
