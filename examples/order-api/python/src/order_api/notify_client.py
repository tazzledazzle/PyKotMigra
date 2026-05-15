from __future__ import annotations

import logging

import httpx

logger = logging.getLogger("order_api.notify")


def notify_order_created(base_url: str | None, order_id: str) -> None:
    if not base_url or not base_url.strip():
        logger.info("notify skipped: EXTERNAL_HTTP_URL unset", extra={"order_id": order_id})
        return
    url = f"{base_url.rstrip('/')}/notify"
    try:
        with httpx.Client(timeout=2.0) as client:
            r = client.post(url, json={"order_id": order_id})
            logger.info(
                "notify done",
                extra={"order_id": order_id, "status_code": r.status_code, "url": url},
            )
    except httpx.HTTPError as e:
        logger.warning("notify failed", extra={"order_id": order_id, "error": str(e)})
