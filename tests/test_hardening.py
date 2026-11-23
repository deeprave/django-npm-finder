# -*- coding: utf-8 -*-
import logging
from pathlib import Path

import pytest
from django.core.management.base import CommandError
from django.test.utils import override_settings

from django_npm import finders
from django_npm.finders import (
    NpmFinder,
    get_npm_environment,
    get_npm_root_path,
    get_package_patterns,
    npm_install,
)
from django_npm.management.commands import npm_install as npm_install_command

from .util import configure_settings

configure_settings()


@pytest.fixture(autouse=True)
def fresh_caches():
    get_npm_root_path.cache_clear()
    get_package_patterns.cache_clear()
    yield
    get_npm_root_path.cache_clear()
    get_package_patterns.cache_clear()


def test_npm_environment_keeps_what_package_managers_need():
    environ = {
        "PATH": "/usr/bin",
        "Path": "C:\\Windows",
        "HOME": "/home/user",
        "SystemRoot": "C:\\Windows",
        "npm_config_registry": "https://registry.example.com",
        "NPM_CONFIG_CACHE": "/cache",
        "PNPM_HOME": "/pnpm",
        "YARN_RC_FILENAME": ".yarnrc.yml",
        "NODE_EXTRA_CA_CERTS": "/ca.pem",
        "HTTPS_PROXY": "http://proxy:3128",
        "XDG_CACHE_HOME": "/xdg",
    }
    assert get_npm_environment(environ) == environ


def test_npm_environment_drops_everything_else():
    environ = {
        "PATH": "/usr/bin",
        "DJANGO_SECRET_KEY": "secret",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "DATABASE_URL": "postgres://user:pass@host/db",
        "NPM_ROOT_PATH": "/srv",
    }
    assert get_npm_environment(environ) == {"PATH": "/usr/bin"}


def test_npm_install_runs_with_filtered_environment(tmp_path, monkeypatch):
    calls = []

    class FakePopen:
        def __init__(self, command, env=None):
            calls.append((command, env))

        def wait(self):
            return 0

    monkeypatch.setattr(finders.subprocess, "Popen", FakePopen)
    monkeypatch.setenv("HOME", "/home/user")
    monkeypatch.setenv("npm_config_registry", "https://registry.example.com")
    monkeypatch.setenv("DJANGO_SECRET_KEY", "secret")

    with override_settings(NPM_ROOT_PATH=str(tmp_path), NPM_EXECUTABLE_PATH="pnpm"):
        assert npm_install() == 0

    ((command, env),) = calls
    assert command[:2] == ["pnpm", "install"]
    assert env["HOME"] == "/home/user"
    assert env["npm_config_registry"] == "https://registry.example.com"
    assert "DJANGO_SECRET_KEY" not in env


@pytest.mark.parametrize("returncode", [0, 1, 127])
def test_command_fails_on_nonzero_exit(monkeypatch, returncode):
    monkeypatch.setattr(npm_install_command, "npm_install", lambda: returncode)
    command = npm_install_command.Command()
    if returncode:
        with pytest.raises(CommandError, match=f"exit code {returncode}"):
            command.handle()
    else:
        command.handle()


def test_command_fails_when_package_manager_cannot_run(monkeypatch):
    def missing():
        raise FileNotFoundError("npm")

    monkeypatch.setattr(npm_install_command, "npm_install", missing)
    with pytest.raises(CommandError, match="Could not run the package manager"):
        npm_install_command.Command().handle()


def test_package_patterns_from_dependencies(tmp_path):
    (tmp_path / "package.json").write_text('{"dependencies": {"a": "1", "@s/b": "2"}}')
    assert get_package_patterns(tmp_path) == {"a": ["**"], "@s/b": ["**"]}


def test_package_patterns_read_package_json_once(tmp_path, monkeypatch):
    (tmp_path / "package.json").write_text('{"dependencies": {"a": "1"}}')
    opened = []
    original = Path.open

    def counting_open(self, *args, **kwargs):
        opened.append(self)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", counting_open)
    get_package_patterns(tmp_path)
    assert opened == [tmp_path / "package.json"]


def test_package_patterns_missing_package_json_is_quiet(tmp_path, caplog):
    with caplog.at_level(logging.WARNING, logger="django_npm.finders"):
        assert get_package_patterns(tmp_path) == {"*": ["*"]}
    assert not caplog.records


def test_package_patterns_malformed_package_json_warns(tmp_path, caplog):
    (tmp_path / "package.json").write_text("{not json")
    with caplog.at_level(logging.WARNING, logger="django_npm.finders"):
        assert get_package_patterns(tmp_path) == {"*": ["*"]}
    assert any("package.json" in record.getMessage() for record in caplog.records)


def test_check_warns_when_node_modules_is_missing(tmp_path):
    with override_settings(NPM_ROOT_PATH=str(tmp_path)):
        errors = NpmFinder().check()
    assert [error.id for error in errors] == ["django_npm.W001"]


def test_check_is_clean_when_node_modules_exists(tmp_path):
    (tmp_path / "node_modules").mkdir()
    with override_settings(NPM_ROOT_PATH=str(tmp_path)):
        assert NpmFinder().check() == []
