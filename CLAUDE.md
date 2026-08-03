# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

---

# Project Overview

This repository contains the implementation for **Part 2** of the Atera Forward Deployed Engineer home assignment.

The objective is **not simply to complete the assignment**, but to build a small, production-quality foundation for interacting with the Atera Public API.

Although the assignment currently requires only one feature, the architecture should naturally support future commands without becoming over-engineered.

The focus is on:

- Clean software engineering
- Maintainability
- Robustness
- Extensibility
- Good API design

Always optimize for engineering quality over implementation speed.

---

# Current Scope

The first implementation will provide a CLI tool that performs ticket analytics by:

- Pulling tickets over a configurable time window.
- Authenticating with the Atera Public API.
- Handling pagination.
- Handling retries and rate limits.
- Producing clear terminal output.
- Computing useful ticket metrics.

The first metric will be ticket resolution analytics (including Robin/Autopilot vs. technician where supported by the API or documented assumptions).

Future commands may include:

- Bulk customer creation
- Bulk site creation
- Bulk agent creation
- Additional FDE automation utilities

The project should make adding these commands straightforward without requiring major architectural changes.

---

# Engineering Philosophy

Optimize for:

- Readability
- Simplicity
- Separation of concerns
- Extensibility
- Robust error handling

Avoid unnecessary abstraction.

This repository is **not** intended to become a full Python SDK.

Do **not** introduce patterns such as:

- Dependency injection
- Repository layers
- Generic factories
- Deep inheritance hierarchies
- Abstract base classes without clear value

Prefer explicit, small, composable modules.

Every abstraction should solve a real problem, not a hypothetical future one.

---

# Design Principles

Every design decision should optimize for:

- Clear interfaces
- Low coupling
- High cohesion
- Explicit behavior over clever abstractions
- Small, composable modules
- Ease of testing
- Ease of future extension

When multiple implementations are possible, prefer the simplest solution that satisfies the current requirements while making future extensions straightforward.

Assume this repository will be reviewed by experienced software engineers.

Optimize for clarity and maintainability over minimizing line count.

---

# Expected Repository Structure

The repository should evolve approximately toward:

```
atera_fde/

    cli.py              # CLI entrypoint

    client.py           # Atera API client

    auth.py             # Authentication utilities

    pagination.py       # Pagination helpers

    exceptions.py       # Custom exceptions

    metrics.py          # Ticket analytics

    commands/

        tickets.py

        bulk_create.py
```

This structure may evolve as the project grows, but should remain intentionally lightweight.

---

# API Documentation

The repository contains:

```
api.atera.txt
```

This file is the local copy of the Atera Public API documentation.

Before implementing any endpoint:

1. Verify the endpoint exists.
2. Verify request parameters.
3. Verify response schema.
4. Verify pagination behavior.
5. Verify authentication requirements.

Never invent undocumented fields.

If assumptions are required because of limitations in the demo environment, clearly document those assumptions.

If documentation and runtime behavior differ, trust the runtime behavior and document the discrepancy.

---

# Authentication

Secrets are stored in:

```
.env
```

containing:

```
atera_api_key
```

Treat this exactly like a production credential.

Never:

- Print it
- Log it
- Hardcode it
- Commit it

Always load secrets from the environment.

---

# Error Handling Expectations

The API client should gracefully handle:

- Authentication failures
- Authorization failures
- Network failures
- Timeouts
- Rate limiting
- Pagination
- Partial failures
- Invalid responses

Never crash without producing a meaningful error message.

Prefer informative exceptions over silent failures.

---

# CLI Philosophy

Build a clean, professional command-line interface.

Example:

```bash
python cli.py tickets \
    --start 2026-07-01 \
    --end 2026-07-31
```

Future commands should naturally integrate into the same CLI.

The CLI should remain intuitive and discoverable.

---

# Code Quality Expectations

Code should prioritize:

- Correctness
- Readability
- Robustness

Use:

- Type hints
- Docstrings where appropriate
- Small focused functions
- Clear naming
- Minimal dependencies

Avoid:

- Clever code
- Premature optimization
- Hidden behavior
- Over-engineering

Readable code is preferred over highly abstract code.

Performance optimization should only be introduced when justified by actual requirements.

---

# Before Writing Code

Before implementing any significant feature:

1. Review the API documentation.
2. Confirm endpoint behavior.
3. Identify assumptions.
4. Explain the implementation plan.

Do not immediately generate code.

Discuss the design first.

---

# Collaboration Expectations

Treat me as the software architect for this project.

Before implementing significant functionality:

1. Explain the design.
2. Present alternative approaches when appropriate.
3. Recommend the option you believe is best.
4. Explain the tradeoffs.
5. Wait for approval before generating code.

During implementation:

- Explain important engineering decisions.
- Keep implementations small and focused.
- Avoid introducing abstractions unless they provide immediate value.
- Ask for clarification instead of making hidden assumptions.

When reviewing existing code:

- Critique constructively.
- Suggest improvements with reasoning.
- Preserve simplicity.

---

# Project Goal

Imagine this repository will continue to evolve after the assignment.

Every implementation should leave the codebase cleaner, easier to understand, and easier to extend than before.

Favor thoughtful engineering decisions over quickly producing code.