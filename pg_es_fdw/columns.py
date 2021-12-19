"""
Handlers for different column types
"""
from abc import ABC, abstractmethod
import json


class Column(ABC):
    """
    The handler for a single column
    """

    def __init__(self, name):
        # (str) -> None
        self.name = name

    def _value(self, response):
        """
        Get the named value from the elasticsearch response
        """
        return response["_source"][self.name]

    @abstractmethod
    def deserialize(self, response):
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

    def deserialize(self, response):
        return response["_id"]

    def serialize(self, value):
        raise AssertionError("The id column is not serialized into the body")


class ScoreColumn(Column):
    """
    The handler for the elasticsearch search score
    """

    def deserialize(self, response):
        return response["_score"]

    def serialize(self, value):
        raise AssertionError("The score column is not serialized into the body")


class BasicColumn(Column):
    """
    The handler for types that share representations between elasticsearch and postgres
    """

    def deserialize(self, response):
        return self._value(response)

    def serialize(self, value):
        return value


class JsonColumn(Column):
    """
    The handler for JSON and JSONB columns
    """

    def deserialize(self, response):
        return json.dumps(self._value(response))

    def serialize(self, value):
        return json.loads(value)


class Columns(object):
    """
    The collection of columns for the postgres table.
    The elasticsearch table is never queried for the structure, it is assumed to be compatible.
    """

    def __init__(self, id_column, score_column, columns):
        # (Column, Optional[Column], List[Column]) -> None
        self.id_column = id_column
        self.score_column = score_column
        self.columns = columns

    def has_id(self, data):
        """
        Test if the rowid column is present in the postgres data
        """
        # (Dict[str, Any]) -> bool
        return self.id_column.name in data

    def deserialize(self, response, columns):
        """
        Deserialize the requested columns into the postgres format from the elasticsearch response
        """
        # (Dict[str, Any], List[str]) -> Dict[str, Any]
        data = {}

        for column in [self.id_column, self.score_column] + self.columns:
            if column.name not in columns:
                continue
            data[column.name] = column.deserialize(response)

        return data

    def serialize(self, value):
        """
        Serialize the data into the elasticsearch format from the postgres format
        """
