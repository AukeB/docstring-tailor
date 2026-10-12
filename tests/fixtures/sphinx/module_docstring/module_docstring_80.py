"""Utilities for loading, validating, and managing application configuration.
This module provides classes and helper functions for combining configuration
values from multiple sources into a single consistent representation.

The module is designed for applications that need predictable configuration
resolution while still allowing environment-specific customization.

- ConfigurationManager: Maintains configuration state and resolves values from
  multiple sources.
- load_configuration_file: Reads configuration values from a supported file
  format.

.. note::
    Configuration objects created by this module are intended to be configured
    during application startup and then reused throughout the lifetime of the
    application.

.. warning::
    This module does not automatically persist runtime changes.

.. example::
    >>> manager = ConfigurationManager(
    ...     defaults={"host": "localhost", "port": 8080},
    ... )
    >>> manager.config["host"]
    'localhost'
"""
