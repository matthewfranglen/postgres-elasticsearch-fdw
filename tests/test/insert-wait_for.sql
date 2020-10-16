WITH
inserted AS (
  INSERT INTO articles_es_wait_for (id, title, body)
  VALUES (3, 'Test insert wait for title', 'test insert wait for body') RETURNING id
)
SELECT es.id, es.title, es.body FROM inserted
LEFT JOIN articles_es_wait_for as es ON es.id = inserted.id;
