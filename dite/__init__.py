###
### Author: Mikulas Dite
### Time-stamp: <2015-06-09 21:54:14 dwa>

from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres as log2pg

from functools import partial

import httplib
import json
import logging

class ElasticsearchFDW (ForeignDataWrapper):

    def __init__(self, options, columns):
        super(ElasticsearchFDW, self).__init__(options, columns)

        self.host = options.get('host', 'localhost')
        self.port = int(options.get('port', '9200'))
        self.node = options.get('node', '')
        self.index = options.get('index', '')

        self.columns = columns

    def get_rel_size(self, quals, columns):
        """Helps the planner by returning costs.

        Returns a tuple of the form (nb_row, avg width)
        """

        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("GET", "/%s/%s/_count" % (self.node, self.index))
        resp = conn.getresponse()
        if not 200 == resp.status:
            return (0, 0)

        raw = resp.read()
        data = json.loads(raw)
        # log2pg('MARK RESPONSE: >>%d<<' % data['count'], logging.DEBUG)
        return (data['count'], len(columns) * 100)

    def execute(self, quals, columns):
        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("GET", "/%s/%s/_search?q=*:*&size=100000000" % (self.node, self.index))
        resp = conn.getresponse()
        if not 200 == resp.status:
            return (0, 0)

        raw = resp.read()
        data = json.loads(raw)
        out = []
        for hit in data['hits']['hits']:
            row = {}
            for col in columns:
                if col == 'id':
                    row[col] = hit['_id']
                elif col in hit['_source']:
                    row[col] = hit['_source'][col]
            out.append(row)

        return out

    @property
    def rowid_column(self):
        """Returns a column name which will act as a rowid column,
        for delete/update operations. This can be either an existing column
        name, or a made-up one.
        This column name should be subsequently present in every
        returned resultset.
        """
        return 'id';

    def es_index(self, id, values):
        content = json.dumps(values)

        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("PUT", "/%s/%s/%s" % (self.node, self.index, id), content)
        resp = conn.getresponse()
        if not 200 == resp.status:
            return

        raw = resp.read()
        data = json.loads(raw)

        return data

    def insert(self, new_values):
        log2pg('MARK Insert Request - new values:  %s' % new_values, logging.DEBUG)

        if not 'id' in new_values:
             log2pg('INSERT requires "id" column.  Missing in: %s' % new_values, logging.ERROR)

        id = new_values['id']
        new_values.pop('id', None)
        return self.es_index(id, new_values)

    def update(self, id, new_values):
        new_values.pop('id', None)
        return self.es_index(id, new_values)

    def delete(self, id):
        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("DELETE", "/%s/%s/%s" % (self.node, self.index, id))
        resp = conn.getresponse()
        if not 200 == resp.status:
            log2pg('Failed to delete: %s' % resp.read(), logging.ERROR)
            return

        raw = resp.read()
        return json.loads(raw)

## Local Variables: ***
## mode:python ***
## coding: utf-8 ***
## End: ***
