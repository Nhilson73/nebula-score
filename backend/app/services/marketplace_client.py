import logging
from typing import Any, cast

import httpx

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


def publish_evaluation_to_marketplace(evaluation_public_id: str, lot_name: str | None = None) -> dict[str, Any] | None:
    """Push a newly created evaluation to the Nebula Marketplace import endpoint.

    This is best-effort: failures are logged but never block evaluation creation.
    """
    base_url = settings.nebula_marketplace_api_base_url
    if not base_url:
        return None

    payload: dict[str, Any] = {
        "nebula_score_public_id": evaluation_public_id,
        "status": "published",
        "is_demo": False,
    }
    if lot_name:
        payload["lot_name"] = lot_name

    try:
        response = httpx.post(
            f"{base_url}/lots/import-from-score",
            json=payload,
            timeout=5.0,
        )
        if response.is_success:
            return cast(dict[str, Any], response.json())
        logger.warning("Marketplace import failed: %s %s", response.status_code, response.text)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not reach marketplace at %s: %s", base_url, exc)
    return None
