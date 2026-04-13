# -*- coding: utf-8 -*-
import contextlib
import fnmatch
import os
import json
import subprocess
from functools import cache, lru_cache
from pathlib import Path
from typing import List, Dict, Union, Iterable, Optional

from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage

NPM_EXECUTABLE_PATH = "NPM_EXECUTABLE_PATH"
NPM_ROOT_PATH = "NPM_ROOT_PATH"
NPM_STATIC_FILES_PREFIX = "NPM_STATIC_FILES_PREFIX"
NPM_FILE_PATTERNS = "NPM_FILE_PATTERNS"
NPM_IGNORE_PATTERNS = "NPM_IGNORE_PATTERNS"
NPM_FINDER_USE_CACHE = "NPM_FINDER_USE_CACHE"

DEFAULT_IGNORE_PATTERNS = (
    ".*",
    "*.coffee",
    "*.es6",
    "*.htm",
    "*.html",
    "*.json",
    "*.less",
    "*.litcoffee",
    "*.lock",
    "*.map",
    "*.markdown",
    "*.md",
    "*.patch",
    "*.php",
    "*.rb",
    "*.rst",
    "*.scss",
    "*.sh",
    "*.styl",
    "*.ts",
    "*.txt",
    "*.xml",
    "*.yaml",
    "*.yml",
    "*bin*",
    "*demo*",
    "*docs*",
    "*example*",
    "*samples*",
    "*test*",
    "CHANGELOG*",
    "CHANGES*",
    "CONTRIBUTING*",
    "COPYING*",
    "Gemfile*",
    "Gruntfile*",
    "HISTORY*",
    "LICENCE*",
    "LICENSE*",
    "Makefile*",
    "NOTICE*",
    "README*",
    "bower_components",
    "coffee",
    "grunt",
    "gulp",
    "gulpfile.js",
    "jspm_packages",
    "less",
    "license",
    "node_modules",
    "sass",
    "scss",
    "tasks",
)


def splitpath(path: str | bytes | Path | None):
    if path is not None:
        path = str(path).replace("\\", "/")
        if path.endswith("/"):
            return path[:-1], "*"
        p = path.rsplit("/", maxsplit=1)
        return (
            tuple(p) if len(p) == 2 else (p[0], "*") if path.endswith("/") else ("", p[0])
        )
    return "", ""


@cache
def _ignorelist(ignore_patterns: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    return tuple(splitpath(patt) for patt in ignore_patterns)


def _ignored(relpath: Path, ignore_patterns: tuple[str, ...]) -> bool:
    reldir, relname = splitpath(relpath)
    return any(
        fnmatch.fnmatch(relname, ignorefile)
        and (not ignorepath or fnmatch.fnmatch(reldir, ignorepath))
        for (ignorepath, ignorefile) in _ignorelist(ignore_patterns)
    )


@lru_cache(maxsize=32767)
def _rglob(
    root: Path,
    topdir: Path,
    glob_pattern: Optional[str],
    find_pattern: str | bytes | None,
    ignore_patterns: tuple[str, ...],
) -> tuple[Path, ...]:
    results = []
    patternpath, patternname = splitpath(glob_pattern or "*")
    findpath, findname = splitpath(find_pattern)
    for path in topdir.iterdir():
        relpath = path.relative_to(root)
        if _ignored(relpath, ignore_patterns):
            continue
        if path.is_dir():
            results.extend(
                _rglob(root, path, glob_pattern or "*", find_pattern, ignore_patterns)
            )
        elif path.is_file():
            reldir, relname = splitpath(relpath)
            if fnmatch.fnmatch(relname, patternname):
                if not find_pattern:
                    if not patternpath or fnmatch.fnmatch(reldir, patternpath):
                        results.append(relpath)
                elif not findpath or reldir == findpath:
                    if fnmatch.fnmatch(relname, findname):
                        results.append(relpath)
    return tuple(results)


def get_setting(
    setting_name: str, default: Union[bool, str, None] = None
) -> Union[bool, str, Path, None]:
    """
    Get a Django setting by name, or return a default value if it doesn't exist.
    :param setting_name: Name of the setting
    :param default: default value if unset
    :return: setting value or default
    """
    return getattr(settings, setting_name, default)


@lru_cache(maxsize=None)
def get_npm_root_path() -> Path:
    """
    Get the root path for the node_modules directory.
    If NPM_ROOT_PATH is unset, assume BASE_DIR.
    :return: Resolved Path
    """
    if not (base_dir := get_setting(NPM_ROOT_PATH)):
        base_dir = get_setting("BASE_DIR", ".")
    return Path(base_dir).resolve()


def npm_install():
    """
    Run npm install in the node_modules directory.
    :return: Return code of the process
    """
    npm = get_setting(NPM_EXECUTABLE_PATH) or "npm"

    prefix = (
        "--dir"
        if npm.endswith("pnpm")
        else "--cwd"
        if npm.endswith("yarn")
        else "--prefix"
    )

    command = [str(npm), "install", prefix, get_npm_root_path().as_posix()]
    print(" ".join(command))
    proc = subprocess.Popen(
        command,
        env={"PATH": os.environ.get("PATH")},
    )
    return proc.wait()


@lru_cache
def get_package_patterns(node_modules_root: Union[str, Path]) -> Dict[str, List[str]]:
    """
    Get the package.json file from the node_modules directory and return the dependencies.
    :param node_modules_root: Root path to the node_modules directory
    :return:
    """
    package_json = Path(node_modules_root) / "package.json"
    packages = {"*": ["*"]}
    with contextlib.suppress(IOError, json.JSONDecodeError):
        with package_json.open() as f:
            pkg_json = json.load(f)
            with package_json.open() as f:
                pkg_json = json.load(f)
                if "dependencies" in pkg_json:
                    packages = {pkg: ["**"] for pkg in pkg_json["dependencies"]}
    return packages


def flatten_patterns(patterns: Dict[str, Iterable[str]]) -> List[str]:
    """
    Flatten a dictionary of patterns into a list of module/pattern strings.
    :param patterns: Dictionary of module/pattern lists
    :return: flattened list of module/pattern strings
    """
    if patterns is None:
        return []
    return [
        f"{str(module).strip('/')}/{str(module_pattern).lstrip('/')}"
        for module, module_patterns in patterns.items()
        for module_pattern in module_patterns
    ]


def get_files(
    storage,
    match_patterns: Iterable[str] = None,
    ignore_patterns: Iterable[str] = None,
    find_pattern: str | bytes | None = None,
):
    if match_patterns is None:
        match_patterns = ["*"]
    elif not isinstance(match_patterns, Iterable):
        match_patterns = [match_patterns]

    root = Path(storage.base_location).resolve()

    if not ignore_patterns:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS

    ignore_patterns = tuple(ignore_patterns)

    for pattern in match_patterns:
        yield from _rglob(root, root, pattern, find_pattern, ignore_patterns)


class NpmFinder(FileSystemFinder):
    # noinspection PyMissingConstructor,PyUnusedLocal
    def __init__(self, *args, **kwargs):
        self.node_modules_path = get_npm_root_path()
        self.destination = get_setting(NPM_STATIC_FILES_PREFIX, "")
        self.cache_enabled = get_setting(NPM_FINDER_USE_CACHE, True)
        self.ignore_patterns = (
            get_setting(NPM_IGNORE_PATTERNS, None) or DEFAULT_IGNORE_PATTERNS
        )
        patterns = get_setting(NPM_FILE_PATTERNS, None) or get_package_patterns(
            self.node_modules_path
        )
        self.match_patterns = flatten_patterns(patterns) or ["*"]
        self.locations = [(self.destination, self.node_modules_path / "node_modules")]

        filesystem_storage = FileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages = {self.locations[0][1]: filesystem_storage}
        self.cached_list = None

    # noinspection PyShadowingBuiltins
    def find(self, path, **_kwargs):
        relpath = os.path.relpath(path, self.destination)
        for prefix, root in self.locations:
            storage = self.storages[root]
            for p in get_files(
                storage, self.match_patterns, self.ignore_patterns, relpath
            ):
                return root / p
        return []

    def list(self, ignore_patterns=None):
        """List all files in all locations."""
        if not ignore_patterns:
            ignore_patterns = self.ignore_patterns
        elif self.ignore_patterns:
            for pattern in self.ignore_patterns:
                if pattern not in ignore_patterns:
                    ignore_patterns.append(pattern)
        if self.cache_enabled:
            if self.cached_list is None:
                self.cached_list = list(self._make_list_generator(ignore_patterns))
            return self.cached_list
        return self._make_list_generator(ignore_patterns)

    def _make_list_generator(self, ignore_patterns=None):
        for prefix, root in self.locations:
            storage = self.storages[root]
            for path in get_files(storage, self.match_patterns, ignore_patterns):
                yield path, storage
