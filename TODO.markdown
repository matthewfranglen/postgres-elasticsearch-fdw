TODOs
=====

I need to add a column that gets the score against the query. This should then be used to preserve ordering of results.

I need to add support for LIMIT and I need to fetch all results by default. Currently limited to 10 results. Supporting scroll might be nice.
It might be good to explicitly require a limit over the es query all the time.

Looks like LIMIT isn't pushed down to the FDW at this time: https://www.postgresql.org/message-id/31924.1459344783%40sss.pgh.pa.us

So I need to support scroll better.
