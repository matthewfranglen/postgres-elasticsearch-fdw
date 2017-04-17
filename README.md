PostgreSQL Elastic Search foreign data wrapper
==============================================

This allows you to index data in elastic search and then search it from
postgres. This does not store the documents in elastic search.

By using a foreign table to elastic search, which is paired with a normal table
with triggers, it is possible to search the normal table using elastic search.

Installation
------------

The configuration requirements for this can be found in the `Dockerfile` within
this folder.

The fundamental requirements are:

 * Python >=2.7
 * elastic search
 * postgres >=9.2
 * python-multicorn for the postgres version
 * python-elasticsearch

You can then install this wrapper by running `setup.py`.

Usage
-----

A running configuration for this can be found in the `docker-compose.yml`
within this folder.

The basic steps are:

 * Load the extension
 * Create the server
 * Create the foreign table
 * Populate the foreign table
 * Query the foreign table...

The first insert into the table will create the index if it does not already
exist. If you want to set the schema you should do it before using this wrapper.

If the index does not exist then several types of operation on the table will
fail.

You can pair this with an existing table using triggers. An example of that is
in the `sql/create-triggered-table.sql` file.

### Load extension and Create server

```sql
CREATE EXTENSION multicorn;

CREATE SERVER multicorn_es FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'pg_es.ElasticsearchFDW'
);
```

### Create the foreign table

```sql
CREATE FOREIGN TABLE articles_es
    (
        id BIGINT,
        title TEXT,
        content TEXT
    )
SERVER multicorn_es
OPTIONS
    (
        host 'elasticsearch',
        port '9200',
        index 'article-index',
        type 'article'
    )
;
```

### Populate the foreign table

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

### Query the foreign table

```sql
SELECT
    id,
    title,
    content
FROM
    articles_es
;
```

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
