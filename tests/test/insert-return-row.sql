INSERT INTO articles_es_returning (id, title, body)
VALUES (2, 'Test insert returning title', 'test insert returning body') RETURNING id, title, body;
