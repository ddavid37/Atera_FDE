# Atera CLI Toolkit

Command-line tools for the Atera Public API v3, built for the Atera
Forward Deployed Engineer home assignment (Part 2: automate with the
Atera API).

## Overview

`atera_cli` is a small Python CLI that talks to the real Atera Public
API. The first command computes a **ticket resolution-rate metric**:
how many tickets in a time window were resolved by Robin/Autopilot
versus by a human technician.

## Layout (what each file is for)

Everything that matters for the CLI lives under `atera_cli/`. The split
is intentional and small on purpose — each file has one job:

```
atera_cli/
  __main__.py          # enables: python -m atera_cli
  cli.py               # argparse + wires client → analytics → print
  client.py            # HTTP: auth, retries, ticket endpoints
  pagination.py        # walks Atera's page envelope (used only by client)
  exceptions.py        # AteraError / AteraAPIError / AteraRateLimitError
  analytics/
    tickets.py         # pure metric functions (no HTTP)
tests/                 # unit tests mirroring the modules above
```

Root docs / config (not “code clutter”):


| Path                            | Role                                |
| ------------------------------- | ----------------------------------- |
| `.env`                          | your API key (gitignored)           |
| `requirements.txt`              | `requests`, `python-dotenv`         |
| `api.atera.txt`                 | local copy of Atera Public API docs |
| `CLAUDE.md`                     | project engineering guidance        |
| `Robin_FDE_Home_Assignment.pdf` | assignment brief                    |


Dependency direction (so nothing cycles):

```
cli  →  analytics (pure) + client
client  →  pagination + exceptions
```

`analytics` never imports `requests` or `client`, so metrics can be
tested with plain dict fixtures and no network.

## Installation

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On macOS, use the venv (or `.venv/bin/python`) — bare `python` is often
not on PATH.

## Configuring `.env`

The client reads your Atera Public API key from a `.env` file in the
project root (never commit this file — it's already gitignored):

```
atera_api_key=<your Atera Public API key, from Admin > API in app.atera.com>
```



## CLI reference

Entry point (always via the module):

```bash
python -m atera_cli --help
python -m atera_cli tickets --help
python -m atera_cli tickets list --help
python -m atera_cli tickets get --help
python -m atera_cli tickets resolution-rate --help
```



### Commands available today


| Command                   | Purpose                                                                       |
| ------------------------- | ----------------------------------------------------------------------------- |
| `tickets list`            | View/triage tickets by status + priority (like the UI filter drawer)          |
| `tickets get`             | Pull a single ticket by ID (`GET /api/v3/tickets/{ticketId}`)                 |
| `tickets resolution-rate` | Robin/Autopilot vs. technician resolution counts and rates over a date window |




### `tickets list` options


| Option                  | Required | Default    | Description                                                              |
| ----------------------- | -------- | ---------- | ------------------------------------------------------------------------ |
| `--status`              | no       | `Open`     | Passed to the API `ticketStatus` filter                                  |
| `--priority`            | no       | `Critical` | Client-side filter on `TicketPriority` (API has no priority query param) |
| `--format {table,json}` | no       | `table`    | Output format                                                            |
| `-h`, `--help`          | no       |            | Show command help                                                        |


Critical-open triage (defaults — mirrors filtering Open + Critical in the UI):

```bash
python -m atera_cli tickets list
```

Same thing, explicit:

```bash
python -m atera_cli tickets list --status Open --priority Critical
```

Other priorities / JSON:

```bash
python -m atera_cli tickets list --status Open --priority High
python -m atera_cli tickets list --status Pending --priority Critical --format json
```



### `tickets get` options


| Option                  | Required | Description                      |
| ----------------------- | -------- | -------------------------------- |
| `ticket_id`             | yes      | Positional TicketID (e.g. `912`) |
| `--format {table,json}` | no       | Output format (default: `table`) |
| `-h`, `--help`          | no       | Show command help                |


Pull a single ticket by ID (same ticket as in the UI below — `#912 Printers XYZ`):

```bash
python -m atera_cli tickets get 912
```

Daniel Ticket Printers XYZ 912

Example table result:

```
Ticket #912
  Title:       Printers XYZ
  Status:      Open
  Priority:    High
  Customer:    CodeCraft
  Technician:  Daniel Interview
```



### `tickets resolution-rate` options


| Option                  | Required | Description                                             |
| ----------------------- | -------- | ------------------------------------------------------- |
| `--since YYYY-MM-DD`    | yes      | Window start (inclusive), based on `TicketResolvedDate` |
| `--until YYYY-MM-DD`    | yes      | Window end (inclusive), based on `TicketResolvedDate`   |
| `--format {table,json}` | no       | Output format (default: `table`)                        |
| `-h`, `--help`          | no       | Show command help                                       |


```bash
python -m atera_cli tickets resolution-rate \
  --since 2026-06-01 \
  --until 2026-08-01

python -m atera_cli tickets resolution-rate \
  --since 2026-06-01 \
  --until 2026-08-01 \
  --format json
```

Example `resolution-rate` table result:

```
Ticket resolution rate
  Total resolved:     1
  Robin/Autopilot:    0 (0.0%)
  Technician:         1 (100.0%)
```



## Tests

From the project root with the venv active:

```bash
python -m unittest discover -s tests -v
```

Or one module at a time:

```bash
python -m unittest tests.test_client -v
python -m unittest tests.test_analytics_tickets -v
python -m unittest tests.test_pagination -v
```

Do **not** run `python tests/test_*.py` directly — that skips the package
path and fails with `ModuleNotFoundError: No module named 'atera_cli'`.

These are offline unit tests (mocked HTTP / plain ticket dicts). When they
pass you should see `OK` at the end, e.g.:

```
Ran 15 tests in 0.XXXs

OK
```



## Assumption

Robin/Autopilot resolution is currently detected as
`TechnicianContactID == -1`, based on documented write-side Autopilot
assignment behavior. If live read data shows a better signal, change
only `is_robin_resolved()` in `analytics/tickets.py`.

## Status

`tickets list`, `tickets get`, and `tickets resolution-rate` are
implemented and work against the live API. Additional commands
(e.g. bulk create) can be added later as new CLI subcommands without
changing the client/analytics split.