SELECT
    title
FROM
    articles_es_json_query
WHERE
    query = '{"bool":{"filter":[{"term":{"body":"chess"}}]}}'
;
