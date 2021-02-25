SELECT
    title
FROM
    articles_es_json_query
WHERE
    query = '{"query":{"bool":{"filter":[{"term":{"body":"chess"}}]}}}'
;
