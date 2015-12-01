""" Elastic Search foreign data wrapper
    Author: Mikulas Dite
"""
# pylint: disable=super-on-old-class, unused-argument, import-error

from functools import partial

import httplib
import json
import logging

from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres as log2pg


class ElasticsearchFDW(ForeignDataWrapper):
    """ Elastic Search Foreign Data Wrapper """

    @property
    def rowid_column(self):
        """ Returns a column name which will act as a rowid column for
            delete/update operations.

            This can be either an existing column name, or a made-up one. This
            column name should be subsequently present in every returned
            resultset. """

        return self._rowid_column

    def __init__(self, options, columns):
        super(ElasticsearchFDW, self).__init__(options, columns)

        self.host = options.get('host', 'localhost')
        self.port = int(options.get('port', '9200'))
        self.node = options.get('node', '')
        self.index = options.get('index', '')

        self._rowid_column = options.get('rowid_column', 'id')

        self.columns = columns

    def get_rel_size(self, quals, columns):
        """ Helps the planner by returning costs.
            Returns a tuple of the form (nb_row, avg width) """

        response = self._make_request(
            "GET", "/{0}/{1}/_count".format(self.node, self.index)
        )

        if response.status != 200:
            return (0, 0)

        data = json.loads(response.read())
        return (data['count'], len(columns) * 100)

    def execute(self, quals, columns):
        """ Execute the query """

        response = self._make_request(
            "GET", "/{0}/{1}/_search?q=*:*&size=100000000".format(self.node, self.index)
        )

        if response.status != 200:
            return (0, 0)

        data = json.loads(response.read())
        out = []
        for hit in data['hits']['hits']:
            row = {}
            for col in columns:
                if col == self.rowid_column:
                    row[col] = hit['_id']
                elif col in hit['_source']:
                    row[col] = hit['_source'][col]
            out.append(row)

        return out

    def insert(self, new_values):
        """ Insert new documents into Elastic Search """
        log2pg('MARK Insert Request - new values: {}'.format(new_values), logging.DEBUG)

        if self.rowid_column not in new_values:
            log2pg(
                'INSERT requires "id" column. Missing in: {}'.format(new_values),
                logging.ERROR
            )

        document_id = new_values[self.rowid_column]
        new_values.pop(self.rowid_column, None)
        return self._upsert(document_id, new_values)

    def update(self, document_id, new_values):
        """ Update existing documents in Elastic Search """

        new_values.pop(self.rowid_column, None)
        return self._upsert(document_id, new_values)

    def delete(self, document_id):
        """ Delete documents from Elastic Search """

        response = self._make_request(
            "DELETE", "/{0}/{1}/{2}".format(self.node, self.index, document_id)
        )

        if response.status != 200:
            log2pg('Failed to delete: {}'.format(response.read()), logging.ERROR)
            return

        return json.loads(response.read())

    def _upsert(self, document_id, values):
        """ Insert or Update the document in Elastic Search """
        content = json.dumps(values)

        response = self._make_request(
            "PUT", "/{0}/{1}/{2}".format(self.node, self.index, document_id), content
        )

        if response.status != 200:
            log2pg('Failed to upsert: {}'.format(response.read()), logging.ERROR)
            return None

        return json.loads(response.read())

    def _make_request(self, method, url, content=None):
        """ Make a HTTP request to Elastic Search and return the response """

        connection = httplib.HTTPConnection(self.host, self.port)
        connection.request(method, url, content)
        return connection.getresponse()
