"""Allowlisted, cached public HTML retrieval and Nuxt SSR data decoding."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx

ORIGIN = "https://catalog.nmt.edu"
USER_AGENT = "EdPlan-NMT-Catalog-Importer/1.0 (public academic catalog verification)"
LOGGER = logging.getLogger(__name__)


def approved_url(url: str) -> str:
    parts = urlsplit(urljoin(ORIGIN, url))
    if (
        parts.scheme != "https"
        or parts.hostname != "catalog.nmt.edu"
        or parts.port not in (None, 443)
        or parts.username
        or parts.password
    ):
        raise ValueError("URL outside the approved official catalog domain")
    if parts.query:
        raise ValueError("Query URLs require explicit review")
    return urlunsplit((parts.scheme, parts.netloc, parts.path or "/", "", ""))


class PageParser(HTMLParser):
    """Read public SSR state and real hrefs, without executing website scripts."""

    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.nuxt = ""
        self.links: list[dict] = []
        self.text: list[str] = []
        self._nuxt = False
        self._skip = 0
        self._anchor: dict | None = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self._nuxt = attrs.get("id") == "__NUXT_DATA__"
        if tag in {"script", "style"}:
            self._skip += 1
        if tag == "a" and attrs.get("href"):
            self._anchor = {"href": attrs["href"], "text": ""}
            self.links.append(self._anchor)
        if tag in {"h1", "h2", "h3", "p", "li", "tr", "br", "div"}:
            self.text.append("\n")

    def handle_endtag(self, tag):
        if tag == "script":
            self._nuxt = False
        if tag in {"script", "style"}:
            self._skip = max(0, self._skip - 1)
        if tag == "a":
            self._anchor = None

    def handle_data(self, data):
        if self._nuxt:
            self.nuxt += data
        if not self._skip:
            self.text.append(data)
            if self._anchor is not None:
                self._anchor["text"] += data


def decode_nuxt(raw: str):
    """Decode devalue's index graph, preserving unknown wrappers instead of dropping them.

    Numbers inside containers are references, not literal values. Negative sentinels
    and cycles are represented explicitly. No eval, imports, or network endpoints.
    """
    values = json.loads(raw)
    if not isinstance(values, list):
        raise ValueError("Expected Nuxt devalue array")
    memo: dict[int, object] = {}

    def decode(index):
        if not isinstance(index, int) or isinstance(index, bool):
            return index
        if index < 0:
            return None if index in {-1, -3} else {"devalue_sentinel": index}
        if index >= len(values):
            raise ValueError("Invalid Nuxt reference")
        if index in memo:
            return memo[index]
        value = values[index]
        if isinstance(value, dict):
            result = {}
            memo[index] = result
            result.update((k, decode(v)) for k, v in value.items())
            return result
        if isinstance(value, list):
            if value and isinstance(value[0], str):
                if value[0] in {"Reactive", "ShallowReactive", "Ref", "ShallowRef"}:
                    memo[index] = None
                    result = decode(value[1])
                    memo[index] = result
                    return result
                result = {"devalue_type": value[0], "values": []}
                memo[index] = result
                result["values"] = [decode(v) for v in value[1:]]
                return result
            result = []
            memo[index] = result
            result.extend(decode(v) for v in value)
            return result
        memo[index] = value
        return value

    return decode(0)


class PublicCatalogClient:
    def __init__(self, cache: Path, *, offline=False, delay=1.5, client=None):
        self.cache = cache
        self.offline = offline
        self.delay = max(1.0, delay)
        self.client = client or httpx.Client(
            headers={"User-Agent": USER_AGENT},
            timeout=httpx.Timeout(30),
            follow_redirects=False,
        )
        self.cache.mkdir(parents=True, exist_ok=True)
        self.last_request = 0.0
        self.robots: RobotFileParser | None = None
        self.access_stopped = False

    def close(self):
        self.client.close()

    def _request(self, url):
        for attempt in range(3):
            time.sleep(max(0, self.delay - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                response = self.client.get(url)
                if response.status_code in {401, 403, 405, 429}:
                    self.access_stopped = True
                    raise PermissionError(
                        f"Access restricted or rate limited: {response.status_code}"
                    )
                if response.status_code >= 500:
                    response.raise_for_status()
                return response
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError):
                if attempt == 2:
                    raise
                time.sleep(2 ** (attempt + 1))

    def fetch(self, url: str, *, _policy=False) -> tuple[str, dict]:
        url = approved_url(url)
        key = hashlib.sha256(url.encode()).hexdigest()
        data_path, meta_path = self.cache / f"{key}.html", self.cache / f"{key}.json"
        failure_path = self.cache / f"{key}.failure.json"
        if data_path.exists() and meta_path.exists():
            content = data_path.read_bytes()
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            if hashlib.sha256(content).hexdigest() != metadata["sha256"]:
                raise ValueError("Cached source checksum mismatch")
            return content.decode("utf-8"), metadata
        if failure_path.exists():
            self.access_stopped = True
            raise PermissionError(
                "Previously recorded access restriction; review before refreshing"
            )
        if self.offline:
            raise FileNotFoundError(f"Uncached source in offline mode: {url}")
        if self.access_stopped:
            raise PermissionError("Further live retrieval stopped after an access restriction")
        if not _policy:
            self._ensure_robots()
            if not self.robots.can_fetch(USER_AGENT, url):
                raise PermissionError("Disallowed by official robots policy")
        current = url
        for _ in range(4):
            try:
                response = self._request(current)
            except PermissionError as error:
                failure_path.write_text(
                    json.dumps(
                        {
                            "url": current,
                            "observed_at": datetime.now(UTC).isoformat(),
                            "error": str(error),
                            "automatic_retry": False,
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                raise
            if response.is_redirect:
                current = approved_url(urljoin(current, response.headers["location"]))
                if not _policy and not self.robots.can_fetch(USER_AGENT, current):
                    raise PermissionError("Redirect disallowed by robots policy")
                continue
            response.raise_for_status()
            break
        else:
            raise ValueError("Redirect limit exceeded")
        content = response.content
        if len(content) > 20_000_000:
            raise ValueError("Unexpectedly large public HTML page")
        metadata = {
            "url": url,
            "resolved_url": current,
            "source_type": "official_html",
            "retrieved_at": datetime.now(UTC).isoformat(),
            "sha256": hashlib.sha256(content).hexdigest(),
            "status": response.status_code,
        }
        data_path.write_bytes(content)
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        LOGGER.info(
            json.dumps({"event": "source_cached", "url": url, "sha256": metadata["sha256"]})
        )
        return content.decode("utf-8"), metadata

    def _ensure_robots(self):
        if self.robots is None:
            text, _ = self.fetch(ORIGIN + "/robots.txt", _policy=True)
            self.robots = RobotFileParser()
            self.robots.parse(text.splitlines())
            self.delay = max(self.delay, self.robots.crawl_delay(USER_AGENT) or 0)
