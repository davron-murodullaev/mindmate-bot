"""Telegram WebApp initData HMAC validation."""
import hashlib
import hmac
import json
import logging
import time
import urllib.parse
from typing import Optional

logger = logging.getLogger(__name__)

INIT_DATA_MAX_AGE = 3600  # 1 hour — stale data is rejected


def validate_telegram_init_data(init_data: str, bot_token: str) -> Optional[dict]:
    """Validate Telegram WebApp initData via HMAC-SHA256.

    Returns the parsed *user* dict on success, None on any failure.
    Ref: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not init_data or not bot_token:
        return None
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))

        received_hash = parsed.pop("hash", "")
        if not received_hash:
            logger.warning("initData: missing 'hash' field")
            return None

        # Replay-attack protection
        auth_date_str = parsed.get("auth_date")
        if not auth_date_str:
            logger.warning("initData: missing 'auth_date' field")
            return None
        auth_date = int(auth_date_str)
        age = int(time.time()) - auth_date
        if not (0 <= age <= INIT_DATA_MAX_AGE):
            logger.warning("initData rejected: age=%ds (limit=%ds)", age, INIT_DATA_MAX_AGE)
            return None

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed.items())
        )

        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_hash, received_hash):
            logger.warning("initData: HMAC mismatch")
            return None

        user_str = parsed.get("user")
        if not user_str:
            logger.warning("initData: missing 'user' field")
            return None

        return json.loads(user_str)

    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logger.warning("initData parse error: %s", e)
        return None
    except Exception:
        logger.exception("Unexpected error in initData validation")
        return None
