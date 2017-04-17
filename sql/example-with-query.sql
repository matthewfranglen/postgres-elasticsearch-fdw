CREATE EXTENSION multicorn;

CREATE SERVER multicorn_es FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'pg_es_fdw.ElasticsearchFDW'
);

CREATE FOREIGN TABLE articles_es
    (
        id BIGINT,
        title TEXT,
        content TEXT,
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

INSERT INTO articles_es
    (
        id,
        title,
        content
    )
VALUES
    (
        1,
        'Cameron seeks parliament backing for bombing Islamic State in Syria',
        'LONDON Prime Minister David Cameron is likely to ask parliament to vote on Wednesday to approve British air strikes against Islamic State militants in Syria after months of wrangling over whether enough opposition Labour members of parliament would'
    ),
    (
        2,
        'Luton anti-terror arrests: Four men held over alleged plot for attack on',
        'Police have broken up a suspected Islamist terror cell planning to launch an attack in the UK. Counter-terrorism officers arrested four men in the Luton area on Wednesday morning and are searching seven addresses, Scotland Yard said.'
    ),
    (
        3,
        'Priscilla Chan and Mark Zuckerberg''s 99% pledge is born with strings attached',
        'Mark Zuckerberg and Priscilla Chan are part of a cycle that perpetuates inequality even if they try to fight it. Photograph: Scott Olson/Getty Images.'
    );

SELECT
    id,
    title,
    content
FROM
    articles_es
;

SELECT
    id,
    title,
    content,
    score
FROM
    articles_es
WHERE
    query = 'content:officer* or title:cameron'
;
