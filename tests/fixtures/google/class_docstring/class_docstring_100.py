class ConfigurationManager:
    """Manage application configuration loaded from multiple sources.

    A configuration manager combines settings from defaults, configuration files, environment
    variables, and runtime overrides into a single interface. Values are resolved according to a
    configurable precedence order, allowing applications to expose consistent configuration
    behaviour across different environments.

    Configuration sources:

    - Built-in default values.
    - One or more configuration files.
    - Environment variables.
    - Runtime overrides provided by the application.

    Attributes:
        defaults (dict[str, object]): Immutable default configuration values.
        config (dict[str, object]): The merged configuration currently in use.
        config_files (list[str]): Paths to configuration files that have been loaded.
        environment_prefix (str): Prefix used when resolving environment variables.
        allow_unknown_keys (bool): Whether keys not present in the defaults are accepted.
        has_unsaved_changes (bool): Whether the configuration has been modified since it was last
            written to disk.

    Resolution order:

    ~~~
    text
    start with default values
    
    for each configuration file:
        merge values
    
    merge matching environment variables
    
    merge runtime overrides
    
    return the resulting configuration
    ~~~

    Note:
        Configuration values are merged lazily. Changes made through the public API are reflected
        immediately, but configuration files are only read when explicitly requested.

    Warning:
        Runtime overrides always take precedence over configuration files and environment variables.
        Supplying unexpected overrides may therefore mask configuration problems that would
        otherwise be detected.

    Examples:
        Creating a configuration manager with default settings.

        >>> manager = ConfigurationManager(
        ...     defaults={"host": "localhost", "port": 8080},
        ...     environment_prefix="APP_",
        ... )
        >>> manager.environment_prefix
        'APP_'

        Updating a configuration value at runtime.

        >>> manager.config["port"] = 9090
        >>> manager.has_unsaved_changes = True
        >>> manager.config["port"]
        9090
    """

    def __init__(
        self,
        defaults: dict[str, object],
        environment_prefix: str = "",
        allow_unknown_keys: bool = False,
    ):
        self.defaults = defaults
        self.config = defaults.copy()
        self.config_files: list[str] = []
        self.environment_prefix = environment_prefix
        self.allow_unknown_keys = allow_unknown_keys
        self.has_unsaved_changes = False
        """Initialize a configuration manager.

        Create a new manager using the supplied default values and prepare the internal
        configuration state. The initial configuration is populated from the defaults and can later
        be extended or overridden by additional sources.

        Args:
            defaults (dict[str, object]): The base configuration values used when no other source
                provides a value.
            environment_prefix (str): Prefix used to identify relevant environment variables when
                loading configuration from the environment. Defaults to an empty string.
            allow_unknown_keys (bool): Whether configuration keys that are not present in the
                defaults are accepted. Defaults to False.
        """