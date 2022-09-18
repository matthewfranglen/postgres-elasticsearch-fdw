"""
Handlers for different column types
"""
# pylint: disable=useless-object-inheritance, too-many-arguments
import logging
import json
from abc import ABCMeta, abstractmethod

from multicorn.utils import log_to_postgres as log2pg  # pylint: disable=import-error


class Column(object):
    """
    The handler for a single column
    """

    __metaclass__ = ABCMeta

    def __init__(self, name):
        # (str) -> None
        self.name = name

    def _value(self, row):
        """
        Get the named value from the elasticsearch response
        """
        return row["_source"][self.name]

    @abstractmethod
    def deserialize(self, row):
        """
        Convert the value from the elasticsearch representation to the postgres representation
        """
        # (Dict[str, Any]) -> Optional[Any]
        # this is called when reading from elasticsearch
        # the response is the result of an elasticsearch client query

    @abstractmethod
    def serialize(self, value):
        """
        Convert the value from the postgres representation to the elasticsearch representation
        """
        # (Any) -> json
        # this is called when writing to elasticsearch


class IdColumn(Column):
    """
    The handler for the elasticsearch document id
    """

    def deserialize(self, row):
        return row["_id"]

    def serialize(self, value):
        raise AssertionError("The id column is not serialized into the body")


class ScoreColumn(Column):
    """
    The handler for the elasticsearch search score
    """

    def deserialize(self, row):
        return row["_score"]

    def serialize(self, value):
        raise AssertionError("The score column is not serialized into the body")


class BasicColumn(Column):
    """
    The handler for types that share representations between elasticsearch and postgres
    """

    def deserialize(self, row):
        return self._value(row)

    def serialize(self, value):
        return value


class JsonColumn(Column):
    """
    The handler for JSON and JSONB columns
    """

    def deserialize(self, row):
        return json.dumps(self._value(row))

    def serialize(self, value):
        return json.loads(value)


class Columns(object):
    """
    The collection of columns for the postgres table.
    The elasticsearch table is never queried for the structure, it is assumed to be compatible.
    """

    def __init__(self, id_column, score_column, query_column, sort_column, columns):
        # (Column, Optional[Column], Optional[str], Optional[str], List[Column]) -> None
        self.id_column = id_column
        self.score_column = score_column
        self.query_column = query_column
        self.sort_column = sort_column
        self.columns = columns
        self.columns_by_name = {column.name: column for column in columns}

    def has_id(self, data):
        """
        Test if the rowid column is present in the postgres data
        """
        # (Dict[str, Any]) -> bool
        return self.id_column.name in data

    def deserialize(self, row, query, sort, columns):
        """
        Deserialize the requested columns into the postgres format from the elasticsearch response
        """
        # (Dict[str, Any], Optional[str], Optional[str], Optional[List[str]]) -> Dict[str, Any]
        if columns is not None:
            columns = set(columns)

        data = {}
        for column in [self.id_column, self.score_column] + self.columns:
            if columns is None:
                data[column.name] = column.deserialize(row)
            elif column.name in columns:
                data[column.name] = column.deserialize(row)

        if query:
            data[self.query_column] = query
        if sort:
            data[self.sort_column] = sort

        return data

    def serialize(self, row):
        """
        Serialize the data into the elasticsearch format from the postgres format.
        This returns the id first and then the data.
        The score column is never serialized.
        """
        # (Dict[str, Any]) -> Tuple[str, Dict[str, Any]]

        rowid_column = self.id_column.name
        if rowid_column not in row:
            message = 'INSERT/UPDATE requires "{rowid}" column. Missing in: {values}'.format(
                rowid=rowid_column, values=row
            )
            log2pg(message, logging.ERROR)
            # The insert or update cannot proceed so the transaction should abort.
            # It can happen that the log2pg method is unimplemented, so this
            # value error will abort the operation.
            #
            # https://multicorn.org/implementing-a-fdw/#error-reporting
            # logging.ERROR:
            #   Maps to a PostgreSQL ERROR message. An ERROR message is passed
            #   to the client, as well as in the server logs. An ERROR message
            #   results in the current transaction being aborted. Think about
            #   the consequences when you use it!
            raise ValueError(message)

        document_id = row.pop(rowid_column)
        columns_by_name = self.columns_by_name
        data = {
            key: columns_by_name[key].serialize(value)
            for key, value in row.items()
            if key in columns_by_name
        }

        return document_id, data


def make_columns(options, columns):
    """
    Create a Columns object from the options and columns used to initialize the fdw
    """
    # (ElasticsearchFDWOptions, Dict[str, multicorn.ColumnDefinition]) -> Columns
    columns = columns.copy()

    id_column = IdColumn(name=options.rowid_column)
    columns.pop(options.rowid_column, None)
    if options.score_column:
        score_column = ScoreColumn(name=options.score_column)
        del columns[options.score_column]
    else:
        score_column = None
    if options.query_column:
        query_column = options.query_column
        del columns[options.query_column]
    else:
        query_column = None
    if options.sort_column:
        sort_column = options.sort_column
        del columns[options.sort_column]
    else:
        sort_column = None

    columns = [make_column(options, name, column) for name, column in columns.items()]
    return Columns(
        id_column=id_column,
        score_column=score_column,
        query_column=query_column,
        sort_column=sort_column,
        columns=columns,
    )


def make_column(options, name, column):
    """
    Create the individual column definition from the options and column provided
    """
    # (ElasticsearchFDWOptions, str, multicorn.ColumnDefinition) -> Column
    assert name not in {
        options.rowid_column,
        options.score_column,
        options.query_column,
    }, "Programmer error: bad name passed to make_column {name}".format(name=name)

    if column.base_type_name.upper() in {"JSON", "JSONB"}:
        return JsonColumn(name=name)
    return BasicColumn(name=name)
