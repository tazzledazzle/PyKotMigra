"""FastAPI Depends wiring (reference for catalog `di` component)."""

from order_api.app import get_settings, get_store

__all__ = ["get_settings", "get_store"]
