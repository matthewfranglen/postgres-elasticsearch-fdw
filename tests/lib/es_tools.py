""" Commands for interacting with Elastic Search """
# pylint: disable=broad-except

from os.path import join

import requests

from lib.tools import TEST_FOLDER


def es_is_available():
    """ Test if Elastic Search is running """

    try:
        response = requests.get("http://localhost:9200", auth=("elastic", "changeme"))
        if response.status_code != 200:
            return False
        data = response.json()
        return data["tagline"] == "You Know, for Search"
    except Exception:
        return False

def es_version():
    """ Get the major version number """
    try:
        response = requests.get("http://localhost:9200", auth=("elastic", "changeme"))
        assert response.status_code == 200, response.content
        data = response.json()
        version = data.get("version", {}).get("number", "-1")
        major_version = int(version.split(".")[0])
        return major_version
    except Exception:
        return -1

def load_json_file(filename):
    """ Load JSON file into Elastic Search """

    version = es_version()
    # _type field removed from bulk operations
    # see https://www.elastic.co/guide/en/elasticsearch/reference/7.17/removal-of-types.html
    if version >= 8:
        filename = "no-type-" + filename

    url = "http://localhost:9200/_bulk"
    path = join(TEST_FOLDER, "data", filename)
    headers = {"Content-Type": "application/x-ndjson"}

    with open(path, "r") as handle:
        body = handle.read().encode(encoding="utf-8")
        response = requests.post(
            url, headers=headers, data=body, auth=("elastic", "changeme")
        )
        assert response.status_code < 400, response.content
        return response
