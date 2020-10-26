DELETE FROM articles_es_returning
WHERE id = 39357158
RETURNING id, title;
