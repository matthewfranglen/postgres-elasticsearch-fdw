""" Elastic Search foreign data wrapper """
# pylint: disable=too-many-instance-attributes, import-error, unexpected-keyword-arg, broad-except, line-too-long

import json
import logging

from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres as log2pg
from .options import ElasticsearchFDWOptions


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
        self.client = self.options.make_client()

        self.columns = columns
        self.json_columns = {
            column.column_name
            for column in columns.values()
            if column.base_type_name.upper() in {"JSON", "JSONB"}
        }
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

                for result in response["hits"]["hits"]:
                    yield self._convert_response_row(result, columns, query, sort)

                if len(response["hits"]["hits"]) < self.scroll_size:
                    return
                response = self.client.scroll(
                    scroll_id=self.scroll_id, scroll=self.scroll_duration
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

        if self.rowid_column not in new_values:
            log2pg(
                'INSERT requires "{rowid}" column. Missing in: {values}'.format(
                    rowid=self.rowid_column, values=new_values
                ),
                logging.ERROR,
            )
            return (0, 0)

        document_id = new_values[self.rowid_column]
        new_values.pop(self.rowid_column, None)

        for key in self.json_columns.intersection(new_values.keys()):
            new_values[key] = json.loads(new_values[key])

        try:
            response = self.client.index(
                id=document_id, body=new_values, refresh=self.refresh, **self.arguments
            )
            if self.complete_returning:
                return self._read_by_id(response["_id"])
            return {self.rowid_column: response["_id"]}
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

        new_values.pop(self.rowid_column, None)

        for key in self.json_columns.intersection(new_values.keys()):
            new_values[key] = json.loads(new_values[key])

        try:
            response = self.client.index(
                id=document_id, body=new_values, refresh=self.refresh, **self.arguments
            )
            if self.complete_returning:
                return self._read_by_id(response["_id"])
            return {self.rowid_column: response["_id"]}
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

        if self.complete_returning:
            document = self._read_by_id(document_id)
        else:
            document = {self.rowid_column: document_id}

        try:
            self.client.delete(id=document_id, refresh=self.refresh, **self.arguments)
            return document
        except Exception as exception:
            log2pg(
                "DELETE for {path}/{document_id} failed: {exception}".format(
                    path=self.options.path, document_id=document_id, exception=exception
                ),
                logging.ERROR,
            )
            return (0, 0)

    def _convert_response_row(self, row_data, columns, query, sort):
        return_dict = {
            column: self._convert_response_column(column, row_data)
            for column in columns
            if column in row_data["_source"]
            or column == self.rowid_column
            or column == self.score_column
        }
        if query:
            return_dict[self.query_column] = query
        return_dict[self.sort_column] = sort
        return return_dict

    def _convert_response_column(self, column, row_data):
        if column == self.rowid_column:
            return row_data["_id"]
        if column == self.score_column:
            return row_data["_score"]
        value = row_data["_source"][column]
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return value

    def _read_by_id(self, row_id):
        try:
            arguments = self.options.get_id_arguments(row_id)
            results = self.client.search(**arguments)["hits"]["hits"]
            if results:
                return self._convert_response_row(results[0], self.columns, None, None)
            log2pg(
                "SEARCH for {path} row_id {row_id} returned nothing".format(
                    path=self.options.path, row_id=row_id
                ),
                logging.WARNING,
            )
            return {self.rowid_column: row_id}
        except Exception as exception:
            log2pg(
                "SEARCH for {path} row_id {row_id} failed: {exception}".format(
                    path=self.options.path, row_id=row_id, exception=exception
                ),
                logging.ERROR,
            )
            return {}
