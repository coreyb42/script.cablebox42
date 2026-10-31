"""Translate Jellyfin plugin playback without persisting resolved auth URLs."""
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def jellyfin_id(path):
    url = urlsplit(path)
    if url.scheme != "plugin" or url.netloc != "plugin.video.jellyfin":
        return None
    params = dict(parse_qsl(url.query))
    return params.get("id") if params.get("mode") == "play" else None


def with_offset(path, offset):
    """Jellyfin replaces the ListItem, so StartOffset alone does not survive."""
    if not jellyfin_id(path):
        return path
    url = urlsplit(path)
    params = [(k, v) for k, v in parse_qsl(url.query) if k != "timestamp"]
    params.append(("timestamp", str(max(0.0, float(offset)))))
    return urlunsplit(url._replace(query=urlencode(params)))


def source_for_stream(requested, playing):
    """Only associate the requested Jellyfin item with its resolved stream."""
    item = jellyfin_id(requested)
    if not item:
        return None
    url = urlsplit(playing)
    parts = url.path.strip("/").split("/")
    if (url.scheme in ("http", "https") and len(parts) >= 3
            and parts[-3].lower() == "videos"
            and parts[-2].replace("-", "").lower() == item.replace("-", "").lower()
            and (parts[-1].lower() == "stream" or parts[-1].lower().startswith("stream."))):
        return requested
    return None
