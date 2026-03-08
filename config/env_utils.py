from urllib.parse import urlparse


def split_env_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def normalize_host(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""

    if "://" in raw:
        parsed = urlparse(raw)
        return parsed.hostname or ""

    return raw.split("/")[0]


def normalize_origin(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""

    if "://" in raw:
        parsed = urlparse(raw)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
        return ""

    return ""
