"""Telegram WebApp initData HMAC validation."""
import hashlib
import hmac
import json
from urllib.parse import unquote


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict | None:
    """Validate Telegram WebApp initData signature.

    Returns parsed data dict (including ``user`` as a dict) on success,
    or None if the signature is invalid or data is malformed.
    """
    if not init_data or not bot_token:
        return None
    try:
        params: dict[str, str] = {}
        for pair in init_data.split("&"):
            if "=" in pair:
                key, _, value = pair.partition("=")
                params[key] = unquote(value)

        hash_value = params.pop("hash", "")
        if not hash_value:
            return None

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(params.items())
        )

        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256,
        ).digest()

        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(computed_hash, hash_value):
            return None

        result = dict(params)
        if "user" in result:
            result["user"] = json.loads(result["user"])

        return result
    except Exception:
        return None
