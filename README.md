PostgreSQL Elastic Search foreign data wrapper
==============================================

This allows you to index data in Elastic Search and then search it from
PostgreSQL. You can write as well as read.

SYNOPSIS
--------

### Supported Versions

| Elastic Search | Dependency Installation Command |
|----------------|---------------------------------|
| 5 | `sudo pip install "elasticsearch>=5,<6"` |
| 6 | `sudo pip install "elasticsearch>=6,<7"` |
| 7 | `sudo pip install "elasticsearch>=7,<8"` |

| PostgreSQL | Dependency Installation Command |
|------------|---------------------------------|
| 9.4 | `sudo apt-get install postgresql-9.4-python-multicorn` |
| 9.5 | `sudo apt-get install postgresql-9.5-python-multicorn` |
| 9.6 | `sudo apt-get install postgresql-9.6-python-multicorn` |
| 10 | `sudo apt-get install postgresql-10-python-multicorn` |
| 11 | `sudo apt-get install postgresql-11-python-multicorn` |
| 12 | `sudo apt-get install postgresql-12-python3-multicorn` |

Please note that the Debian package for Multicorn on PostgreSQL 12 requires Python 3.

### Installation

This requires installation on the PostgreSQL server, and has system level dependencies.
You can install the dependencies with:

```
sudo apt-get install python python-pip
```

You should install the version of multicorn that is specific to your postgres
version. See the table in _Supported Versions_ for installation commands. The
multicorn package is also only available from Ubuntu Xenial (16.04) onwards. If
you cannot install multicorn in this way then you can use
[pgxn](http://pgxnclient.projects.pgfoundry.org/) to install it.

This uses the Elastic Search client which has release versions that correspond
to the major version of the Elastic Search server. You should install the
`elasticsearch` dependency separately. See the table in _Supported Versions_
for installation commands.

Once the dependencies are installed you can install the foreign data wrapper
using pip:

```
sudo pip install pg_es_fdw
```

### Usage

A running configuration for this can be found in the `docker-compose.yml`
within this folder.

The basic steps are:

 * Load the extension
 * Create the server
 * Create the foreign table
 * Populate the foreign table
 * Query the foreign table...

#### Load extension and Create server

```sql
CREATE EXTENSION multicorn;

CREATE SERVER multicorn_es FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'pg_es_fdw.ElasticsearchFDW'
);
```

#### Create the foreign table

```sql
CREATE FOREIGN TABLE articles_es
    (
        id BIGINT,
        title TEXT,
        body TEXT,
        metadata JSON,
        query TEXT,
        score NUMERIC,
        sort TEXT
    )
SERVER multicorn_es
OPTIONS
    (
        host 'elasticsearch',
        port '9200',
        index 'article-index',
        type 'article',
        rowid_column 'id',
        query_column 'query',
        score_column 'score',
        default_sort 'last_updated:desc',
        sort_column 'sort',
        refresh 'false',
        complete_returning 'false',
        timeout '20',
        username 'elastic',
        password 'changeme'
    )
;
```

Elastic Search 7 and greater does not require the `type` option, which
corresponds to the `doc_type` used in prior versions of Elastic Search.

This corresponds to an Elastic Search index which contains a `title` and `body`
fields. The other fields have special meaning:

 * The `rowid_column` (`id` above) is mapped to the Elastic Search document id
 * The `query_column` (`query` above) accepts Elastic Search queries to filter the rows
 * The `score_column` (`score` above) returns the score for the document against the query
 * The `sort_column` (`sort` above) accepts an Elastic Search column to sort by
 * The `refresh` option controls if inserts and updates should wait for an index refresh ([Elastic Search documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-refresh.html)). The acceptable values are `"false"` (default), `"wait_for"` and `"true"`
 * The `complete_returning` options controls if Elastic Search is queries for the document after an insert to support `RETURNING` fields other than the document id. The acceptable values are `"false"` (default) and `"true"`
 * The `timeout` field specifies the connection timeout in seconds
 * The `username` field specifies the basic auth username used
 * The `password` field specifies the basic auth password used
 * Any other options are passed through to the elasticsearch client, use this to specify things like ssl

All of these are optional.
Enabling `refresh` or `complete_returning` comes with a performance penalty.

To use basic auth you must provide both a username and a password,
even if the password is blank.

##### JSON and JSONB

When elasticsearch returns nested data it is serialized to TEXT as json before being returned.
This means you can create columns with JSON or JSONB types and the data will be correctly converted on read.
If you write to a JSON or JSONB column then the data is passed to elasticsearch as json.

As the data is converted on the fly per query the benefits of using JSONB over JSON are limited.

##### Elastic Search Authentication

Currently basic auth is supported for authentication.
You can provide the username and password by setting the `username` and `password` options when creating the table.
You must provide both, even if the password is blank.
If you do not provide them then basic auth is disabled for the table.

If you need to use other forms of authentication then please open an issue.

#### Populate the foreign table

```sql
INSERT INTO articles_es
    (
        id,
        title,
        body,
        metadata
    )
VALUES
    (
        1,
        'foo',
        'spike',
        '{"score": 3}'::json
    );
```

It is possible to write documents to Elastic Search using the foreign data
wrapper. This feature was introduced in PostgreSQL 9.3.

#### Query the foreign table

To select all documents:

```sql
SELECT
    id,
    title,
    body,
    metadata
FROM
    articles_es
;
```

To filter the documents using a query:

```sql
SELECT
    id,
    title,
    body,
    metadata,
    score
FROM
    articles_es
WHERE
    query = 'body:chess'
;
```

This uses the [URI Search](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-uri-request.html) from Elastic Search.

#### Sorting the Results

By default Elastic Search returns the documents in score order, descending.
If you wish to sort by a different field you can use the `sort_column` option.

The `sort_column` accepts a column to sort by and a direction, for example `last_updated:desc`.
This is passed to Elastic Search so it should be the name of the Elastic Search column.
If you always want sorted results then you can use the `default_sort` option to specify the sort when creating the table.

To break ties you can specify further columns to sort on.
You just need to separate the columns with a comma, for example `unit:asc,last_updated:desc`.

```
SELECT
    id,
    title,
    body,
    metadata,
    score
FROM
    articles_es
WHERE
    sort = 'id:asc'
;
```

#### Refresh and RETURNING

When inserting or updating documents in Elastic Search the document ID is returned.
This can be accessed through the `RETURNING` statement without any additional performance loss.

To get further fields requires reading the document from Elastic Search again.
This comes at a cost because an immediate read after an insert may not return the updated document.
Elastic Search periodically refreshes the indexes and at that point the document will be available.

To wait for a refresh before returning you can use the `refresh` parameter.
This accepts three values: `"false"` (the default), `"true"` and `"wait_for"`.
You can read about them [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-refresh.html).
If you choose to use the refresh setting then it is recommended to use `"wait_for"`.

Once you have chosen to wait for the refresh you can enable full returning support by setting `complete_returning` to `"true"`.
Both the `refresh` and `complete_returning` options are set during table creation.
If you do not wish to incur the associated costs for every query then you can create two tables with different settings.

Caveats
-------

Elastic Search does not support transactions, so the elasticsearch index
is not guaranteed to be synchronized with the canonical version in PostgreSQL.
Unfortunately this is the case even for serializable isolation level transactions.
It would however be possible to check against Elastic Search version field and locking.

Rollback is currently not supported.

Tests
-----

There are end to end tests that use docker to create a PostgreSQL and Elastic
Search database. These are then populated with data and tests are run against
them.

These require docker and docker-compose. These also require python packages
which you can install with:

```bash
pip install -r tests/requirements.txt
```

The makefile will test all versions if you run `make test`:

```bash
➜ make test
poetry run tests/run.py --pg 9.4 9.5 9.6 10 11 12 --es 5 6 7
Testing PostgreSQL 9.4 with Elasticsearch 5
PostgreSQL 9.4 with Elasticsearch 5: Test read - PASS
PostgreSQL 9.4 with Elasticsearch 5: Test nested-read - PASS
PostgreSQL 9.4 with Elasticsearch 5: Test query - PASS
Testing PostgreSQL 9.4 with Elasticsearch 6
PostgreSQL 9.4 with Elasticsearch 6: Test read - PASS
PostgreSQL 9.4 with Elasticsearch 6: Test nested-read - PASS
PostgreSQL 9.4 with Elasticsearch 6: Test query - PASS
Testing PostgreSQL 9.4 with Elasticsearch 7
PostgreSQL 9.4 with Elasticsearch 7: Test read - PASS
PostgreSQL 9.4 with Elasticsearch 7: Test nested-read - PASS
PostgreSQL 9.4 with Elasticsearch 7: Test query - PASS
Testing PostgreSQL 9.5 with Elasticsearch 5
PostgreSQL 9.5 with Elasticsearch 5: Test read - PASS
PostgreSQL 9.5 with Elasticsearch 5: Test nested-read - PASS
PostgreSQL 9.5 with Elasticsearch 5: Test query - PASS
Testing PostgreSQL 9.5 with Elasticsearch 6
PostgreSQL 9.5 with Elasticsearch 6: Test read - PASS
PostgreSQL 9.5 with Elasticsearch 6: Test nested-read - PASS
PostgreSQL 9.5 with Elasticsearch 6: Test query - PASS
Testing PostgreSQL 9.5 with Elasticsearch 7
PostgreSQL 9.5 with Elasticsearch 7: Test read - PASS
PostgreSQL 9.5 with Elasticsearch 7: Test nested-read - PASS
PostgreSQL 9.5 with Elasticsearch 7: Test query - PASS
Testing PostgreSQL 9.6 with Elasticsearch 5
PostgreSQL 9.6 with Elasticsearch 5: Test read - PASS
PostgreSQL 9.6 with Elasticsearch 5: Test nested-read - PASS
PostgreSQL 9.6 with Elasticsearch 5: Test query - PASS
Testing PostgreSQL 9.6 with Elasticsearch 6
PostgreSQL 9.6 with Elasticsearch 6: Test read - PASS
PostgreSQL 9.6 with Elasticsearch 6: Test nested-read - PASS
PostgreSQL 9.6 with Elasticsearch 6: Test query - PASS
Testing PostgreSQL 9.6 with Elasticsearch 7
PostgreSQL 9.6 with Elasticsearch 7: Test read - PASS
PostgreSQL 9.6 with Elasticsearch 7: Test nested-read - PASS
PostgreSQL 9.6 with Elasticsearch 7: Test query - PASS
Testing PostgreSQL 10 with Elasticsearch 5
PostgreSQL 10 with Elasticsearch 5: Test read - PASS
PostgreSQL 10 with Elasticsearch 5: Test nested-read - PASS
PostgreSQL 10 with Elasticsearch 5: Test query - PASS
Testing PostgreSQL 10 with Elasticsearch 6
PostgreSQL 10 with Elasticsearch 6: Test read - PASS
PostgreSQL 10 with Elasticsearch 6: Test nested-read - PASS
PostgreSQL 10 with Elasticsearch 6: Test query - PASS
Testing PostgreSQL 10 with Elasticsearch 7
PostgreSQL 10 with Elasticsearch 7: Test read - PASS
PostgreSQL 10 with Elasticsearch 7: Test nested-read - PASS
PostgreSQL 10 with Elasticsearch 7: Test query - PASS
Testing PostgreSQL 11 with Elasticsearch 5
PostgreSQL 11 with Elasticsearch 5: Test read - PASS
PostgreSQL 11 with Elasticsearch 5: Test nested-read - PASS
PostgreSQL 11 with Elasticsearch 5: Test query - PASS
Testing PostgreSQL 11 with Elasticsearch 6
PostgreSQL 11 with Elasticsearch 6: Test read - PASS
PostgreSQL 11 with Elasticsearch 6: Test nested-read - PASS
PostgreSQL 11 with Elasticsearch 6: Test query - PASS
Testing PostgreSQL 11 with Elasticsearch 7
PostgreSQL 11 with Elasticsearch 7: Test read - PASS
PostgreSQL 11 with Elasticsearch 7: Test nested-read - PASS
PostgreSQL 11 with Elasticsearch 7: Test query - PASS
Testing PostgreSQL 12 with Elasticsearch 5
PostgreSQL 12 with Elasticsearch 5: Test read - PASS
PostgreSQL 12 with Elasticsearch 5: Test nested-read - PASS
PostgreSQL 12 with Elasticsearch 5: Test query - PASS
Testing PostgreSQL 12 with Elasticsearch 6
PostgreSQL 12 with Elasticsearch 6: Test read - PASS
PostgreSQL 12 with Elasticsearch 6: Test nested-read - PASS
PostgreSQL 12 with Elasticsearch 6: Test query - PASS
Testing PostgreSQL 12 with Elasticsearch 7
PostgreSQL 12 with Elasticsearch 7: Test read - PASS
PostgreSQL 12 with Elasticsearch 7: Test nested-read - PASS
PostgreSQL 12 with Elasticsearch 7: Test query - PASS
PASS
```

If you want to run the tests for specific versions then you can then run the
tests using `tests/run.py`.  This takes the PostgreSQL version(s) to test using
the `--pg` argument and the Elastic Search versions to test with the `--es`
argument.  The currently supported versions of PostgreSQL are 9.4 through to 12.
The currently supported versions of Elastic Search are 5 to 7. You can pass
multiple versions to test it against all of them.

### Test Failure Messages

```
Error starting userland proxy: listen tcp 0.0.0.0:5432: bind: address already in use
```
You are already running something that listens to 5432.
Try stopping your running postgres server:
```
sudo /etc/init.d/postgresql stop
```

```
max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
```
Your system does not have the appropriate limits in place to run a production ready instance of elasticsearch.
Try increasing it:
```
sudo sysctl -w vm.max_map_count=262144
```
This setting will revert after a reboot.

### Migrating from <=0.6.0

In version 0.7.0 the TEXT representation of json objects changed from HSTORE to JSON.
If you have been mapping json objects to HSTORE columns then you should change the column type to JSON.
The arrow operator exists for json so queries should not need rewriting.
