TODOs
=====

Need Scrolling
--------------

The LIMIT clause is not pushed down to FDWs at this time: https://www.postgresql.org/message-id/31924.1459344783%40sss.pgh.pa.us

So this needs to support scrolling. When creating the table the scroll size can be set.

Need Tests / Travis
-------------------

Should be able to build this on every version of postgres that multicorn supports.

The test can be a script that uses docker-compose to run an end to end test.

Need Cleanup
------------

It's all sort of smushed together.
