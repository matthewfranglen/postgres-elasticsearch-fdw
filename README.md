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
