CREATE EXTENSION multicorn;

CREATE SERVER multicorn_es FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'pg_es.ElasticsearchFDW'
);

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
        node 'test',
        index 'articles'
    )
;

SELECT
    id,
    title,
    content
FROM
    articles_es
;

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

SELECT
    id,
    title,
    content
FROM
    articles_es
;
