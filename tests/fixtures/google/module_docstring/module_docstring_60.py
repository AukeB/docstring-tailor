"""Utilities for loading, validating, and managing
application configuration.

This module provides classes and helper functions for
combining configuration values from multiple sources into a
single consistent representation. Configuration can
originate from default values, files, environment variables,
and runtime overrides.

The module is designed for applications that need
predictable configuration resolution while still allowing
environment-specific customization.

Available components:

- ConfigurationManager: Maintains configuration state and
  resolves values from multiple sources.
- load_configuration_file: Reads configuration values from a
  supported file format.
- validate_configuration: Checks configuration values
  against application requirements.

Module workflow:

~~~
defaults
    |
    v
configuration manager
    |
    +--> configuration files
    |
    +--> environment variables
    |
    +--> runtime overrides
    |
    v
validated configuration
~~~

Note:
    Configuration objects created by this module are
    intended to be configured during application startup and
    then reused throughout the lifetime of the application.

Warning:
    This module does not automatically persist runtime
    changes. Applications that modify configuration values
    after startup must explicitly write those changes if
    persistence is required.

Example:
    Loading a basic application configuration.

    >>> manager = ConfigurationManager(
    ...     defaults={"host": "localhost", "port": 8080},
    ...     environment_prefix="APP_",
    ... )
    >>> manager.config["host"]
    'localhost'
"""