.. _api:

API Interface Developer Docs
=======================================

This page contains in-depth documentation on the Toolchest client API.

Tools
-----

All tools should be able to be called directly as
`toolchest_client.your_tool_name()`.

..
  TODO: Use automodule, especially after adding new members, but exclude the module docstring

.. module:: toolchest_client

.. autofunction:: bowtie2

.. autofunction:: kraken2

.. autofunction:: STAR

.. autofunction:: test

.. autofunction:: unicycler

Authorization
-------------

.. module:: toolchest_client
   :noindex:

Toolchest uses the `TOOLCHEST_KEY` environment variable to store the key
needed to authorize its API use. The key can be stored and retrieved via
the functions below.

.. autofunction:: get_key

.. autofunction:: set_key


Exceptions
----------

.. automodule:: toolchest_client.api.exceptions
   :members:

Queries
-------

Each query to Toolchest is handled by a `Query` object. The `run_query`
function handles the actual functionality of a Query.

.. autoclass:: toolchest_client.api.query.Query

.. autofunction:: toolchest_client.api.query.Query.run_query
