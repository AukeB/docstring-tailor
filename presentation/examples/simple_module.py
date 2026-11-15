def greet(name: str, excited: bool = False) -> str:
    """Builds a short greeting for a person, optionally with an exclamation mark.

    The greeting always starts with "Hello", followed by the name exactly as it was
    given, so the caller stays in control of capitalisation.

    Args:
        name (str): The name of the person to greet.
        excited (bool): Whether to end the greeting with an exclamation mark instead
            of a full stop.

    Returns:
        str: The complete greeting, starting with "Hello" and ending with either an
            exclamation mark or a full stop.
    """
    ending = "!" if excited else "."

    return f"Hello {name}{ending}"
