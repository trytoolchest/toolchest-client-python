.. _api:

API Interface Developer Docs
=======================================

This page contains in-depth documentation on the Toolchest client API.

.. module:: toolchest_client

Tools
-----

All tools should be able to be called directly as
`toolchest_client.your_tool()`. Tools are run via the
`toolchest_client.client.run_tool()` function.

.. autofunction:: cutadapt

.. autofunction:: kraken2

.. autofunction:: run_tool


Authorization
-------------

Toolchest uses the `TOOLCHEST_KEY` environment variable to store the key
needed to authorize its API use. The key can be stored and retrieved via
the functions below.

.. autofunction:: get_key

.. autofunction:: set_key


Exceptions
----------

.. autoexception:: toolchest_client.ToolchestException

.. autoexception:: toolchest_client.DataLimitError

Queries
-------

Each query to Toolchest is handled by a `Query` object. The `run_query`
function handles the actual functionality of a Query.

.. autoclass:: toolchest_client.query.Query

.. autofunction:: toolchest_client.query.Query.run_query
