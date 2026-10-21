"""The module contains the main entry points for the SWE API project."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from library.asgi_server import run
    from library.fastapi_app import app

__all__: list[str] = ["app", "run"]


def __getattr__(name: str) -> Any:
    """Load application entry points only when requested, without starting services on import."""
    if name == "app":
        return import_module("library.fastapi_app").app
    if name == "run":
        return import_module("library.asgi_server").run
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main() -> None:
    """Start the main entry point for the SWE API project."""
    import_module("library.asgi_server").run()
