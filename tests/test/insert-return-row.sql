INSERT INTO articles_es_returning (id, title, body)
VALUES (1, 'Test insert title', 'test insert body') RETURNING id, title, body;
