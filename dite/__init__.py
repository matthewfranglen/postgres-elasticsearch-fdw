""" Elastic Search foreign data wrapper
    Author: Mikulas Dite
"""
# pylint: disable=super-on-old-class, unused-argument

from functools import partial

import httplib
import json
import logging

from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres as log2pg


class ElasticsearchFDW(ForeignDataWrapper):
    """ Elastic Search Foreign Data Wrapper """

    def __init__(self, options, columns):
        super(ElasticsearchFDW, self).__init__(options, columns)

        self.host = options.get('host', 'localhost')
        self.port = int(options.get('port', '9200'))
        self.node = options.get('node', '')
        self.index = options.get('index', '')

        self.columns = columns

    def get_rel_size(self, quals, columns):
        """ Helps the planner by returning costs.
            Returns a tuple of the form (nb_row, avg width) """

        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("GET", "/%s/%s/_count" % (self.node, self.index))
        resp = conn.getresponse()

        if resp.status != 200:
            return (0, 0)

        raw = resp.read()
        data = json.loads(raw)

        return (data['count'], len(columns) * 100)

    def execute(self, quals, columns):
        """ Execute the query """

        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("GET", "/%s/%s/_search?q=*:*&size=100000000" % (self.node, self.index))
        resp = conn.getresponse()

        if resp.status != 200:
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
        """ Returns a column name which will act as a rowid column for
            delete/update operations.

            This can be either an existing column name, or a made-up one. This
            column name should be subsequently present in every returned
            resultset. """

        return 'id'

    def insert(self, new_values):
        """ Insert new documents into Elastic Search """
        log2pg('MARK Insert Request - new values:  %s' % new_values, logging.DEBUG)

        if 'id' not in new_values:
            log2pg('INSERT requires "id" column.  Missing in: %s' % new_values, logging.ERROR)

        document_id = new_values['id']
        new_values.pop('id', None)
        return self._upsert(document_id, new_values)

    def update(self, document_id, new_values):
        """ Update existing documents in Elastic Search """

        new_values.pop('id', None)
        return self._upsert(document_id, new_values)

    def delete(self, document_id):
        """ Delete documents from Elastic Search """

        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("DELETE", "/%s/%s/%s" % (self.node, self.index, document_id))
        resp = conn.getresponse()
        if resp.status != 200:
            log2pg('Failed to delete: %s' % resp.read(), logging.ERROR)
            return

        raw = resp.read()
        return json.loads(raw)

    def _upsert(self, document_id, values):
        """ Insert or Update the document in Elastic Search """
        content = json.dumps(values)

        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("PUT", "/%s/%s/%s" % (self.node, self.index, document_id), content)
        resp = conn.getresponse()

        if resp.status != 200:
            return

        raw = resp.read()
        data = json.loads(raw)

        return data
