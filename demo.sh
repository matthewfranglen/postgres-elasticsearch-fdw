curl 'localhost:9200/test/articles/_search?q=*:*&pretty'
psql -c 'SELECT * FROM articles'
psql -c "INSERT INTO articles (title, content, created_at) VALUES ('foo', 'spike', Now());"
psql -c 'SELECT * FROM articles'
curl 'localhost:9200/test/articles/_search?q=*:*&pretty'
psql -c "UPDATE articles SET content='yeay it updates\!' WHERE title='foo'"
curl 'localhost:9200/test/articles/_search?q=*:*&pretty'
