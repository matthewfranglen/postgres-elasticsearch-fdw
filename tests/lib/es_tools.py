from os.path import join

import requests

from lib.tools import TEST_FOLDER

def es_is_available():
    try:
        return requests.get('http://localhost:9200').json()['tagline'] == 'You Know, for Search'
    except Exception:
        return False

def load_json_file(filename):
    url = 'http://localhost:9200/_bulk'
    f = join(TEST_FOLDER, 'data', filename)
    headers = {'Content-Type': 'application/x-ndjson'}

    with open(f, 'r') as handle:
        body = handle.read().encode(encoding='utf-8')
        requests.post(url, headers=headers, data=body)
