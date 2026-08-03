"""Pure analytics functions, one module per resource (tickets, and later others).

Modules in this package take plain dictionaries in and return plain
dictionaries/values out. They must never import requests or
atera_cli.client, so they can be tested with fixture data alone,
independent of any HTTP implementation detail.
"""
