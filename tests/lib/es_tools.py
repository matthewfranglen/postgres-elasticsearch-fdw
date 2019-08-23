""" Commands for interacting with Elastic Search """
# pylint: disable=broad-except

from os.path import join

import requests

from lib.tools import TEST_FOLDER


def es_is_available():
    """ Test if Elastic Search is running """

    try:
        return (
            requests.get("http://localhost:9200").json()["tagline"]
            == "You Know, for Search"
        )
    except Exception:
        return False


def load_json_file(filename):
    """ Load JSON file into Elastic Search """

    url = "http://localhost:9200/_bulk"
    path = join(TEST_FOLDER, "data", filename)
    headers = {"Content-Type": "application/x-ndjson"}

    with open(path, "r") as handle:
        body = handle.read().encode(encoding="utf-8")
        requests.post(url, headers=headers, data=body)
