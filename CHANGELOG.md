# Changelog
# v1.0.0 - 2024-07-16
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
