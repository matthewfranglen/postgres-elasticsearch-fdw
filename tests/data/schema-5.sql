CREATE EXTENSION multicorn;

CREATE SERVER multicorn_es FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'pg_es_fdw.ElasticsearchFDW'
);

CREATE TABLE articles
    (
        id BIGINT,
        title TEXT,
        body TEXT
    )
;

CREATE FOREIGN TABLE articles_es
    (
        id BIGINT,
        title TEXT,
        body TEXT,
        query TEXT,
        sort TEXT,
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
        sort_column 'sort',
        score_column 'score',
        timeout '20',
        username 'elastic',
        password 'changeme',
        es_version '5'
    )
;

CREATE FOREIGN TABLE articles_es_wait_for
    (
        id BIGINT,
        title TEXT,
        body TEXT,
        query TEXT,
        sort TEXT,
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
        sort_column 'sort',
        score_column 'score',
        timeout '20',
        username 'elastic',
        password 'changeme',
        refresh 'wait_for',
        es_version '5'
    )
;

CREATE FOREIGN TABLE articles_es_returning
    (
        id BIGINT,
        title TEXT,
        body TEXT,
        query TEXT,
        sort TEXT,
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
        sort_column 'sort',
        score_column 'score',
        timeout '20',
        username 'elastic',
        password 'changeme',
        refresh 'wait_for',
        complete_returning 'true',
        es_version '5'
    )
;

CREATE FOREIGN TABLE nested_articles_es
    (
        id BIGINT,
        name TEXT,
        "user" JSONB,
        query TEXT,
        sort TEXT,
        score NUMERIC
    )
SERVER multicorn_es
OPTIONS
    (
        host 'elasticsearch',
        port '9200',
        index 'nested-article-index',
        type 'article',
        rowid_column 'id',
        query_column 'query',
        sort_column 'sort',
        score_column 'score',
        timeout '20',
        username 'elastic',
        password 'changeme',
        es_version '5'
    )
;

CREATE FOREIGN TABLE articles_es_json_query
    (
        id BIGINT,
        title TEXT,
        body TEXT,
        query TEXT,
        sort TEXT,
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
        query_dsl 'true',
        sort_column 'sort',
        score_column 'score',
        timeout '20',
        username 'elastic',
        password 'changeme',
        es_version '5'
    )
;


\q
