---
type: agent/information
description: Brief project context for agents working in this repository.
---

# Project

`django-npm-finder` is a Python package for Django projects that exposes selected assets from `node_modules` through Django staticfiles and supports collecting those assets for deployment. It is intended to avoid vendoring frontend packages directly into a Django codebase while still keeping static asset handling predictable.

## History

This repository is a fork of the earlier `django-npm` project. The fork modernized packaging and development tooling, added support for multiple Node package managers (`npm`, `yarn`, `pnpm`), improved finder behavior and caching, and expanded test coverage.

## Agent Context

Treat this as a small library project rather than an application. Prefer changes that preserve backward compatibility, keep configuration explicit, and avoid widening the public API without a clear need.

Primary stack and tooling:
- Python package managed with `uv`
- Django dependency and integration surface
- `pytest` for tests
- `ruff` for linting

When getting oriented, start with `README.md`, `pyproject.toml`, and the `django_npm/` package.
