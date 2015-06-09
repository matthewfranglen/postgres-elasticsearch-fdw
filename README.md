Installation
============

```bash
git clone https://github.com/Kozea/Multicorn /tmp/multicorn
cd $_
git checkout v1.1.0 # newer 1.2.0 does not compile on OS X
make install

git clone https://github.com/Mikulas/pg-es-fdw /tmp/pg-es-fdw
cd $_
python setup.py install
```

Usage
=====

```sql
CREATE EXTENSION multicorn;

CREATE SERVER multicorn_es FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'dite.ElasticsearchFDW'
);

CREATE TABLE articles (
    id serial PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    created_at timestamp
);

CREATE FOREIGN TABLE articles_es (
    id bigint,
    title text,
    content text
) SERVER multicorn_es OPTIONS (host '127.0.0.1', port '9200', node 'test', index 'articles');



CREATE OR REPLACE FUNCTION index_article() RETURNS trigger AS $def$
	BEGIN
		INSERT INTO articles_es (id, title, content) VALUES
			(NEW.id, NEW.title, NEW.content);
		RETURN NEW;
	END;
$def$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION reindex_article() RETURNS trigger AS $def$
	BEGIN
		UPDATE articles_es SET
			title = NEW.title,
			content = NEW.content
		WHERE id = NEW.id;
		RETURN NEW;
	END;
$def$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_article() RETURNS trigger AS $def$
	BEGIN
		DELETE FROM articles_es a WHERE a.id = OLD.id;
		RETURN OLD;
	END;
$def$ LANGUAGE plpgsql;


CREATE TRIGGER es_insert_article
    AFTER INSERT ON articles
    FOR EACH ROW EXECUTE PROCEDURE index_article();

CREATE TRIGGER es_update_article
    AFTER UPDATE OF title, content ON articles
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE PROCEDURE reindex_article();

CREATE TRIGGER es_delete_article
	BEFORE DELETE ON articles
	FOR EACH ROW EXECUTE PROCEDURE delete_article();

```
