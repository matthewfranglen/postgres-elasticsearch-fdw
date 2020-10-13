INSERT INTO articles_es (id, title, body)
VALUES (1, 'Test insert title', 'test insert body') RETURNING id;
