SELECT
    DISTINCT (pg.id = es.id AND pg.title = es.title AND pg.body = es.body)
FROM
    articles AS pg
FULL OUTER JOIN
    articles_es AS es
ON
    pg.id = es.id
;
