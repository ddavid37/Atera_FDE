# [CLAUDE.md](http://CLAUDE.md)

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

This repository is currently empty of code. It contains only:

- `Robin_FDE_Home_Assignment.pdf` — the assignment brief (see below).
- `.env` — holds `atera_api_key` (an Atera Public API key for the demo environment). Gitignored; never print its value or commit it.
- `.gitignore` — ignores `.env` and `.DS_Store`.

There is no build, lint, or test tooling yet because no code exists. When code is added for this assignment, update this file with the actual commands (language/framework, how to run, how to test).

## What this repository is for:



**Tha code part of this assignment is only for the question of Part 2**



This is the working repo for an Atera "Forward Deployed Engineer" home assignment. The assignment has three parts:

1. **Part 1 — Robin automation (built in Atera's hosted demo environment, not in this repo's code):** Design a script action + playbook inside Robin (Atera's AI service-desk agent) that solves one of: intelligent network triage/self-heal, software vulnerability check via a public API (e.g. OSV.dev), endpoint health/compliance scorecard, or smart application repair. Scripts run on a Windows test endpoint via the Atera agent (PowerShell/Bash/Python) and must return structured, parseable output, be idempotent/safe to run unattended, and include guardrails for verification and escalation to a human. Any external call must hit a public API needing no private credentials. This part's artifacts (action + playbook) live in the Atera demo environment (app.atera.com), not as files here — if scripts are drafted locally in this repo before pasting into Robin, keep them under a clearly named directory (e.g. `robin-actions/`) with the action/playbook names noted in a comment or README.
2. **Part 2 — Atera Public API automation:** A standalone program (any language) that talks to the real Atera Public API using the key in `.env` (`atera_api_key`). It must do one concrete task an FDE would need — e.g. pull tickets over a time window and compute a resolution-rate metric (Robin vs. technician), or bulk-create sites/agents from a CSV — with real auth, pagination, error/rate-limit handling, and idempotency where relevant. This is expected to be actual runnable code checked into this repo.
3. **Part 3 — Written engineering judgment answers** (escalation boundaries, diagnosing stalled FRR, safety for destructive scripts under full autonomy). Likely delivered as a short write-up, not code.



## Key constraints to respect when building here

- No admin/API access to external systems (Entra, Okta, Zoom, ServiceNow) is available — Part 1 solutions must be fully self-contained: an endpoint script action plus, optionally, a call to a *public, credential-free* API.
- Every Robin action runs autonomously with no human double-checking each run — scripts must be safe by default, idempotent, and must escalate/report rather than guess when they hit an ambiguous or risky state.
- Don't duplicate Robin's existing built-in actions (endpoint hygiene scripts like disk/cache cleanup, print spooler, DNS flush; cloud actions like Okta password/MFA reset, enable/disable user, group membership). Confirm nothing existing already covers a chosen use case before building.
- `atera_api_key` in `.env` is a demo-environment credential — treat it like a real secret (never hardcode it in scripts or commit it; read it from the environment).

