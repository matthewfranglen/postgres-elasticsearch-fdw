"""
Wrapper for the foreign data wrapper table options.
Provides a facade over everything that the options detail.
"""
# pylint: disable=too-many-instance-attributes
import json

from elasticsearch import VERSION as ELASTICSEARCH_VERSION
from elasticsearch import Elasticsearch


class ElasticsearchFDWOptions(object):
    """
    Wrapper for the foreign data wrapper table options.
    """

    def __init__(self, options):
        # (Dict[str, str]) -> None
        self.path, self.arguments = _get_path_and_arguments(options)

        self.query_column = options.pop("query_column", None)
        self.is_json_query = _boolean_option(options, key="query_dsl", default=False)
        self.score_column = options.pop("score_column", None)
        self.default_sort = options.pop("default_sort", None)
        self.sort_column = options.pop("sort_column", None)
        self.scroll_size = _int_option(options, key="scroll_size", default=1000)
        self.scroll_duration = options.pop("scroll_duration", "10m")
        self.rowid_column = options.pop("rowid_column", "id")
        self.refresh = _get_refresh(options)
        self.complete_returning = _boolean_option(
            options, key="complete_returning", default=False
        )

        self.host = options.pop("host", "localhost")
        self.scheme = options.pop("scheme", None)
        self.port = _int_option(options, key="port", default=9200)
        self.timeout = _int_option(options, key="timeout", default=10)
        self.auth = _get_authentication(options)
        self.options = options

    def make_client(self):
        """
        Creates an elasticsearch client from the options
        """
        # () -> Elasticsearch
        settings = {"host": self.host, "port": self.port}
        if self.scheme:
            settings["scheme"] = self.scheme
        return Elasticsearch(
            [settings],
            basic_auth=self.auth,
            timeout=self.timeout,
            **self.options,
        )

    def get_query(self, quals):
        """
        Gets the query string from the query qualifiers
        """
        # (List[multicorn.Qual]) -> Optional[str]
        # quals - A list of Qual instances describing the filters applied to this scan.
        return _get_qual_value(quals, name=self.query_column, default=None)

    def get_query_arguments(self, query):
        """
        Get the elasticsearch client options that identify the query, path and doc type
        """
        # (str) -> Dict[str, Any]
        arguments = self.arguments.copy()
        if query:
            if self.is_json_query:
                arguments["body"] = json.loads(query)
            else:
                arguments["q"] = query
        return arguments

    def get_id_arguments(self, row_id):
        """
        Get the elasticsearch client options that identify the query, path and doc type
        """
        # (str) -> Dict[str, Any]
        arguments = self.arguments.copy()
        arguments["body"] = {"query": {"ids": {"values": [row_id]}}}
        return arguments

    def get_sort(self, quals):
        """
        Gets the sort string from the query qualifiers, falling back to the default sort
        """
        # (List[multicorn.Qual]) -> str
        # quals - A list of Qual instances describing the filters applied to this scan.
        return _get_qual_value(quals, name=self.sort_column, default=self.default_sort)

    def get_pagination_arguments(self, sort):
        """
        Get the elasticsearch client options that identify the sort, page size and scroll duration
        """
        # (str) -> Dict[str, Any]
        return {
            "sort": sort,
            "size": self.scroll_size,
            "scroll": self.scroll_duration,
        }


def _get_path_and_arguments(options):
    """
    Extracts the path and arguments for queries from the options according
    to the elasticsearch version
    """
    # (Dict[str, str]) -> Tuple[str, Dict[str, str]]
    index = options.pop("index", "")
    doc_type = options.pop("type", "")
    if ELASTICSEARCH_VERSION[0] >= 7:
        path = "/{index}".format(index=index)
        arguments = {"index": index}
    else:
        path = "/{index}/{doc_type}".format(index=index, doc_type=doc_type)
        arguments = {"index": index, "doc_type": doc_type}
    return path, arguments


def _get_authentication(options):
    """
    Extracts the username and password for the elasticsearch client
    """
    # (Dict[str, str]) -> Optional[Tuple[str, str]]
    username = options.pop("username", None)
    password = options.pop("password", None)

    if (username is None) != (password is None):
        raise ValueError("Must provide both username and password")
    if username is not None:
        return (username, password)
    return None


def _get_refresh(options):
    """
    Extracts the refresh parameter which has a restricted set of acceptable values
    """
    # (Dict[str, str]) -> str
    if "refresh" not in options:
        return "false"
    refresh = options.pop("refresh").lower()
    if refresh not in {"true", "false", "wait_for"}:
        raise ValueError("refresh option must be one of true, false, or wait_for")
    return refresh


def _boolean_option(options, key, default):
    # (Dict[str, str], str, bool) -> bool
    if key not in options:
        return default
    return options.pop(key).lower() == "true"


def _int_option(options, key, default):
    # (Dict[str, str], str, int) -> int
    if key not in options:
        return default
    return int(options.pop(key))


def _get_qual_value(quals, name, default):
    # (List[multicorn.Qual], str, object) -> object
    if not name:
        return default

    for qualifier in quals:
        if qualifier.field_name == name:
            return qualifier.value
    return default
