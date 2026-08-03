# Atera CLI Toolkit

Command-line tools for the Atera Public API v3, built for the Atera
Forward Deployed Engineer home assignment (Part 2: automate with the
Atera API).

## Overview

`atera_cli` is a small Python CLI that talks to the real Atera Public
API. The first command computes a **ticket resolution-rate metric**:
how many tickets in a time window were resolved by Robin/Autopilot
versus by a human technician.

The project is organized in layers, each depending only on the one
below it:

```
cli          -> argument parsing and command dispatch (composition root)
analytics    -> pure functions that compute metrics from plain data
client       -> AteraClient, the HTTP interface to the Atera Public API
pagination   -> generic page-walking helper used by AteraClient
```

`analytics` modules never import `requests` or `client` — they operate
only on plain dictionaries, so they can be tested without any network
access.

## Installation

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuring `.env`

The client reads your Atera Public API key from a `.env` file in the
project root (never commit this file — it's already gitignored):

```
atera_api_key=<your Atera Public API key, from Admin > API in app.atera.com>
```

## Running

```bash
python -m atera_cli --help
python -m atera_cli tickets resolution-rate --since 2026-06-01 --until 2026-08-01 --format table
```

## Planned CLI commands

- `tickets resolution-rate --since --until --format` — Robin vs.
  technician resolution rate over a date window. **(in progress)**
- Additional commands (e.g. bulk customer/agent creation from CSV) may
  be added later as new subcommands under the same CLI, following the
  same layering.

## Status

This is a skeleton: the CLI, HTTP client, and analytics modules are
stubbed out (imports and argument parsing work; the actual API calls
and metric calculations raise `NotImplementedError` until built out).
