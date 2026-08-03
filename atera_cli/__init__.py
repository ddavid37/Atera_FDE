"""Command-line tools for the Atera Public API.

This package is organized in layers, each depending only on the one
below it:

    cli          -> argument parsing and command dispatch (composition root)
    analytics    -> pure functions that compute metrics from plain data
    client       -> AteraClient, the HTTP interface to the Atera Public API
    pagination   -> generic page-walking helper used by AteraClient

`analytics` modules never import `requests` or `client`; they operate
only on plain dictionaries returned by `AteraClient`.
"""

__version__ = "0.1.0"
