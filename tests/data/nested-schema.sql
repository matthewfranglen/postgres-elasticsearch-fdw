CREATE EXTENSION multicorn;

CREATE SERVER multicorn_es FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'pg_es_fdw.ElasticsearchFDW'
);

CREATE FOREIGN TABLE nested_articles_es
    (
        id BIGINT,
        name TEXT,
        "user" JSONB,
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
        score_column 'score',
        timeout '20'
    )
;

\q
