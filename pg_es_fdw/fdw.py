""" Elastic Search foreign data wrapper """
# pylint: disable=too-many-instance-attributes, import-error, unexpected-keyword-arg, broad-except, line-too-long

import logging

from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres as log2pg
from .options import ElasticsearchFDWOptions
from .columns import make_columns


class ElasticsearchFDW(ForeignDataWrapper):
    """ Elastic Search Foreign Data Wrapper """

    @property
    def rowid_column(self):
        """ Returns a column name which will act as a rowid column for
            delete/update operations.

            This can be either an existing column name, or a made-up one. This
            column name should be subsequently present in every returned
            resultset. """

        return self.options.rowid_column

    def __init__(self, options, columns):
        super(ElasticsearchFDW, self).__init__(options, columns)

        self.options = ElasticsearchFDWOptions(options)
        self.columns = make_columns(options=self.options, columns=columns)
        self.client = self.options.make_client()
        self.scroll_id = None

    def get_rel_size(self, quals, columns):
        """ Helps the planner by returning costs.
            Returns a tuple of the form (number of rows, average row width) """

        try:
            query = self.options.get_query(quals)
            arguments = self.options.get_query_arguments(query)
            response = self.client.count(**arguments)
            return (response["count"], len(columns) * 100)
        except Exception as exception:
            log2pg(
                "COUNT for {path} failed: {exception}".format(
                    path=self.options.path, exception=exception
                ),
                logging.ERROR,
            )
            return (0, 0)

    def execute(self, quals, columns):
        """ Execute the query """

        try:
            query = self.options.get_query(quals)
            sort = self.options.get_sort(quals)
            arguments = self.options.get_query_arguments(query)
            arguments.update(self.options.get_pagination_arguments(sort))

            response = self.client.search(**arguments)

            while True:
                self.scroll_id = response["_scroll_id"]

                for row in response["hits"]["hits"]:
                    yield self.columns.deserialize(
                        row=row, query=query, sort=sort, columns=columns
                    )

                if len(response["hits"]["hits"]) < self.options.scroll_size:
                    return
                response = self.client.scroll(
                    scroll_id=self.scroll_id, scroll=self.options.scroll_duration
                )
        except Exception as exception:
            log2pg(
                "SEARCH for {path} failed: {exception}".format(
                    path=self.options.path, exception=exception
                ),
                logging.ERROR,
            )
            return

    def end_scan(self):
        """ Hook called at the end of a foreign scan. """
        if self.scroll_id:
            self.client.clear_scroll(scroll_id=self.scroll_id)
            self.scroll_id = None

    def insert(self, new_values):
        """ Insert new documents into Elastic Search """
        document_id, document = self.columns.serialize(new_values)

        try:
            response = self.client.index(
                id=document_id,
                body=document,
                refresh=self.options.refresh,
                **self.options.arguments
            )
            if self.options.complete_returning:
                return self._read_by_id(response["_id"])
            return {self.options.rowid_column: response["_id"]}
        except Exception as exception:
            log2pg(
                "INDEX for {path}/{document_id} and document {document} failed: {exception}".format(
                    path=self.options.path,
                    document_id=document_id,
                    document=new_values,
                    exception=exception,
                ),
                logging.ERROR,
            )
            return (0, 0)

    def update(self, document_id, new_values):
        """ Update existing documents in Elastic Search """
        _, document = self.columns.serialize(new_values)

        try:
            response = self.client.index(
                id=document_id,
                body=document,
                refresh=self.options.refresh,
                **self.options.arguments
            )
            if self.complete_returning:
                return self._read_by_id(response["_id"])
            return {self.options.rowid_column: response["_id"]}
        except Exception as exception:
            log2pg(
                "INDEX for {path}/{document_id} and document {document} failed: {exception}".format(
                    path=self.options.path,
                    document_id=document_id,
                    document=new_values,
                    exception=exception,
                ),
                logging.ERROR,
            )
            return (0, 0)

    def delete(self, document_id):
        """ Delete documents from Elastic Search """

        if self.options.complete_returning:
            document = self._read_by_id(document_id)
        else:
            document = {self.options.rowid_column: document_id}

        try:
            self.client.delete(
                id=document_id, refresh=self.options.refresh, **self.options.arguments
            )
            return document
        except Exception as exception:
            log2pg(
                "DELETE for {path}/{document_id} failed: {exception}".format(
                    path=self.options.path, document_id=document_id, exception=exception
                ),
                logging.ERROR,
            )
            return (0, 0)

    def _read_by_id(self, row_id):
        try:
            arguments = self.options.get_id_arguments(row_id)
            results = self.client.search(**arguments)["hits"]["hits"]
            if results:
                return self.columns.deserialize(
                    row=results[0], query=None, sort=None, columns=None
                )
            log2pg(
                "SEARCH for {path} row_id {row_id} returned nothing".format(
                    path=self.options.path, row_id=row_id
                ),
                logging.WARNING,
            )
            return {self.options.rowid_column: row_id}
        except Exception as exception:
            log2pg(
                "SEARCH for {path} row_id {row_id} failed: {exception}".format(
                    path=self.options.path, row_id=row_id, exception=exception
                ),
                logging.ERROR,
            )
            return {}
