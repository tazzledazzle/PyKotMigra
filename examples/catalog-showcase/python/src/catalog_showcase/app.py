"""FastAPI app wiring all catalog components."""

from __future__ import annotations

from fastapi import FastAPI

from catalog_showcase.auth_stub import router as auth_router
from catalog_showcase.background_tasks import router as background_router
from catalog_showcase.config import get_settings
from catalog_showcase.health import router as health_router
from catalog_showcase.logging_conf import configure_logging
from catalog_showcase.middleware import install_correlation_middleware
from catalog_showcase.routes import router as items_router
from catalog_showcase.validation import router as validation_router


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title=settings.service_name, version="0.1.0")
    install_correlation_middleware(app)
    app.include_router(health_router)
    app.include_router(items_router)
    app.include_router(validation_router)
    app.include_router(background_router)
    app.include_router(auth_router)

    @app.get("/upstream-sample")
    async def upstream_sample() -> dict:
        """Uses outbound client module (catalog: outbound HTTP client)."""
        from catalog_showcase.outbound_client import DownstreamClient

        base = settings.downstream_base_url
        client = DownstreamClient(base)
        return await client.fetch_json_placeholder(1)

    return app


app = create_app()
