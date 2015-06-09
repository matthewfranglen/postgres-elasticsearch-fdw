DROP EXTENSION multicorn;
CREATE EXTENSION multicorn;

DROP SERVER multicorn_es CASCADE;

CREATE SERVER multicorn_es FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'dite.ElasticsearchFDW'
);

DROP FOREIGN TABLE mytable;
CREATE FOREIGN TABLE mytable (
    id bigint,
    key text,
    fajn int
) SERVER multicorn_es OPTIONS (host '127.0.0.1', port '9200', node 'test', index 'foo');
