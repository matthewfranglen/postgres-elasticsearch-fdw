PostgreSQL Elastic Search foreign data wrapper
==============================================

This allows you to index data in elastic search and then search it from
postgres. You can write as well as read.

SYNOPSIS
--------

### Installation

This requires installation on the PostgreSQL server, and has system level dependencies.
You can install the dependencies with:

```
sudo apt-get install postgresql-9.4-python-multicorn python python-pip
```

You should install the version of multicorn that is specific to your postgres
version. The multicorn package is also only available from Ubuntu Xenial
(16.04) onwards. If you cannot install multicorn in this way then you can use
[pgxn](http://pgxnclient.projects.pgfoundry.org/) to install it.

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
        query TEXT,
        score NUMERIC
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
        score_column 'score'
    )
;
```

This corresponds to an Elastic Search index which contains a `title` and `body`
fields. The other fields have special meaning:

 * The `id` field is mapped to the Elastic Search document id
 * The `query` field accepts Elastic Search queries to filter the rows
 * The `score` field returns the score for the document against the query

These are configured using the `rowid_column`, `query_column` and
`score_column` options. All of these are optional.

#### Populate the foreign table

```sql
INSERT INTO articles_es
    (
        id,
        title,
        content
    )
VALUES
    (
        1,
        'foo',
        'spike'
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
    content
FROM
    articles_es
;
```

To filter the documents using a query:

```sql
SELECT
    id,
    title,
    content,
    score
FROM
    articles_es
WHERE
    query = 'body:chess'
;
```

This uses the [URI Search](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-uri-request.html) from Elastic Search.

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

You can then run the tests using `tests/run.py`, which takes the PostgreSQL
version to test. The currently supported versions are 9.2 through to 9.6. You
can pass multiple versions to test it against all of them:

```bash
➜ ./tests/run.py 9.2 9.3 9.4 9.5 9.6
Testing PostgreSQL 9.2
PostgreSQL 9.2: Test read - PASS
PostgreSQL 9.2: Test query - PASS
Testing PostgreSQL 9.3
PostgreSQL 9.3: Test read - PASS
PostgreSQL 9.3: Test query - PASS
Testing PostgreSQL 9.4
PostgreSQL 9.4: Test read - PASS
PostgreSQL 9.4: Test query - PASS
Testing PostgreSQL 9.5
PostgreSQL 9.5: Test read - PASS
PostgreSQL 9.5: Test query - PASS
Testing PostgreSQL 9.6
PostgreSQL 9.6: Test read - PASS
PostgreSQL 9.6: Test query - PASS
PASS
```
