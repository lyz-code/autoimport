"""Tests for the `Config` classes."""

from pathlib import Path
from typing import Callable

import toml

from autoimport.config import AutoImportConfig, Config


class TestConfig:
    """Tests for the `Config` class."""

    def test_get_valid_option(self) -> None:
        """
        Given: a `Config` instance with a `config_dict` populated,
        When a value is retrieved for an existing option,
        Then the value of the option is returned
        """
        config_dict = {"foo": "bar"}
        config = Config(config_dict=config_dict)

        result = config.get_option("foo")

        assert result == "bar"

    def test_get_value_for_missing_option(self) -> None:
        """
        Given: a `Config` instance with a `config_dict` populated,
        When: a value is retrieved for a option not defined in the `config_dict`,
        Then: `None` is returned
        """
        config_dict = {"foo": "bar"}
        config = Config(config_dict=config_dict)

        result = config.get_option("baz")

        assert result is None

    def test_get_value_for_no_config_dict(self) -> None:
        """
        Given: a `Config` instance without a given `config_dict`,
        When: a value is retrieved for an option,
        Then: `None` is returned
        """
        config = Config()

        result = config.get_option("foo")

        assert result is None

    def test_given_config_path(self) -> None:
        """
        Given: a `Config` instance with a given `config_path`,
        When: the `config_path` attribute is retrieved,
        Then: the given `config_path` is returned
        """
        config_path = Path("/")
        config = Config(config_path=config_path)

        result = config.config_path

        assert result is config_path


class TestAutoImportConfig:
    """Tests for the `AutoImportConfig`."""

    def test_valid_pyproject(self, create_tmp_file: Callable) -> None:
        """
        Given: a valid `pyproject.toml`,
        When: the `AutoImportConfig` class is instantiated,
        Then: a config value can be retrieved
        """
        config_toml = toml.dumps({"tool": {"autoimport": {"foo": "bar"}}})
        pyproject_path = create_tmp_file(content=config_toml, filename="pyproject.toml")
        autoimport_config = AutoImportConfig(starting_path=pyproject_path)

        result = autoimport_config.get_option("foo")

        assert result == "bar"

    def test_no_pyproject(self) -> None:
        """
        Given: no supplied `pyproject.toml`,
        When: the `AutoImportConfig` class is instantiated,
        Then: the situation is handled gracefully
        """
        autoimport_config = AutoImportConfig(starting_path=Path("/"))

        result = autoimport_config.get_option("foo")

        assert result is None

    def test_valid_pyproject_with_no_autoimport_section(
        self, create_tmp_file: Callable
    ) -> None:
        """
        Given: a valid `pyproject.toml`,
        When: the `AutoImportConfig` class is instantiated,
        Then: a config value can be retrieved
        """
        config_toml = toml.dumps({"foo": "bar"})
        pyproject_path = create_tmp_file(content=config_toml, filename="pyproject.toml")
        autoimport_config = AutoImportConfig(starting_path=pyproject_path)

        result = autoimport_config.get_option("foo")

        assert result is None
