#!/usr/bin/env python
""" Stop the containers """

import argparse

from lib.docker_compose_tools import tear_down


def main():
    """ Stop the containers """

    parser = argparse.ArgumentParser(description="Tear down testing environment.")
    parser.add_argument("version", help="PostgreSQL version")
    args = parser.parse_args()

    version = args.version
    print("Halting environment with PostgreSQL {version}".format(version=version))
    tear_down(version)


if __name__ == "__main__":
    main()
