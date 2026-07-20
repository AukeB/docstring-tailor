"""Factory for looking up the correct docstring renderer class for a style."""

from docstring_tailor.cli_config import DocstringStyle
from docstring_tailor.renderer.base_renderer import DocstringRendererBase
from docstring_tailor.renderer.google_renderer import GoogleDocstringRenderer
from docstring_tailor.renderer.numpy_renderer import NumpyDocstringRenderer

# Maps each supported style to its renderer class. Sphinx and Epydoc will add
# entries here once their renderers exist.
_RENDERER_CLASSES: dict[str, type[DocstringRendererBase]] = {
    DocstringStyle.google: GoogleDocstringRenderer,
    DocstringStyle.numpy: NumpyDocstringRenderer,
}


def get_renderer_class(style: DocstringStyle) -> type[DocstringRendererBase]:
    """Looks up the renderer class for the given docstring style.

    Args:
        style (DocstringStyle): The docstring style to render.

    Returns:
        renderer_class (type[DocstringRendererBase]): The renderer class for
            style. Not yet instantiated, since renderer instances are created
            fresh per docstring by DocstringVisitor.

    Raises:
        ValueError: If style has no registered renderer.
    """
    renderer_class = _RENDERER_CLASSES.get(style)

    if renderer_class is None:
        raise ValueError(f"No renderer registered for style {style.value!r}.")

    return renderer_class
