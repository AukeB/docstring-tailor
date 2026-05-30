"""Module for running the main repository workflow."""


def main() -> None:
    """
    Load configuration and print the loaded settings.

    1. Instantiate ConfigManager and load the config file.
    2. Print the loaded configuration as YAML.
    """
    import yaml

    from src.my_project.config_manager import ConfigManager

    manager = ConfigManager()
    config = manager.load_config_file()

    print("Loaded config:")
    print(yaml.safe_dump(config.model_dump(), sort_keys=False, default_flow_style=False))


def main_with_pygame_initialisation() -> None:
    """
    Load configuration and launch a scaled pygame window.

    1. Instantiate ConfigManager and load the config file.
    2. Initialise pygame and resolve window dimensions from screen size.
    3. Create the display surface and run the event loop until the window is closed.
    """
    import pygame as pg

    from src.my_project.config_manager import ConfigManager
    from src.my_project.utils.utils_pygame import get_window_size_from_screen_resolution

    # Config
    manager = ConfigManager()
    manager.load_config_file()

    # Pygame init
    pg.init()
    width, height = get_window_size_from_screen_resolution()
    
    pg.display.set_mode((width, height))
    pg.display.set_caption("my_project")

    # Event loop
    running: bool = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

    pg.quit()


if __name__ == "__main__":
    main()