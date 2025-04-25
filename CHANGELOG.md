# Changelog

## v1.2.0 - 2025-04-21

- Converted project management to uv
- fixed bug in npm_install
- fixed bug in find() function that caused an unknown arg exception
- dropped test/release support for python 3.10

## v1.1.0 - 2024-09-08

- Added "**" as pattern to match all files and directories when auto-importing npm dependencies from `project.json`.
- Upgraded versions in poetry.lock to the latest compatible versions.

## v1.0.0 - 2024-07-16

- Forked from the [original repo](https://github.com/kevin1024/django-npm)
- Added a comprehensive list of default ignore patterns for npm files.
- Introduced type annotations and docstrings for better code clarity and maintainability.
- Implemented caching for the get_npm_root_path function.
- Refactored get_package_patterns to dynamically fetch dependencies from package.json.
- Updated get_files function to use default ignore patterns.
- Improved NpmFinder class to use default ignore patterns and autoconfigure match patterns from package.json.
- Updated README.md with detailed installation and configuration instructions.
- Simplified and cleaned up tests in test_finder.py.
- Removed outdated CONTRIBUTING.md file.
