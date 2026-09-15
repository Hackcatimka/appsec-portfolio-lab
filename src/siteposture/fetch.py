from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .analyzer import HeaderBag, normalize_headers


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


@dataclass(frozen=True)
class ResponseSnapshot:
    url: str
    status: int
    headers: HeaderBag


def fetch_once(url: str, timeout: float = 10.0) -> ResponseSnapshot:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("URL must be an absolute http(s) URL")
    if parsed.username or parsed.password:
        raise ValueError("Credentials in URLs are not allowed")

    request = Request(url, headers={"User-Agent": "SitePosture/0.1 (+defensive single-request check)"}, method="GET")
    opener = build_opener(NoRedirects)
    try:
        # The URL is intentionally user-supplied; only absolute HTTP(S) URLs pass
        # validation above and redirects are disabled by the custom opener.
        with opener.open(request, timeout=timeout) as response:  # noqa: S310  # nosec B310
            response.read(1)
            return ResponseSnapshot(response.geturl(), response.status, normalize_headers(response.headers.items()))
    except HTTPError as response:
        return ResponseSnapshot(url, response.code, normalize_headers(response.headers.items()))
