import os
import time
from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception


class RateLimiter:
    def __init__(self, rps: float = 3.0):
        self.min_interval = 1.0 / max(0.1, rps)
        self._last = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self._last
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last = time.time()


def _should_retry(exc: Exception) -> bool:
    if isinstance(exc, requests.RequestException):
        resp = getattr(exc, 'response', None)
        if resp is not None:
            return resp.status_code in (429, 500, 502, 503, 504)
    return isinstance(exc, requests.Timeout)


_session = requests.Session()
_limiter = RateLimiter(rps=float(os.getenv("HTTP_RPS", "3")))


@retry(reraise=True, stop=stop_after_attempt(int(os.getenv("HTTP_RETRIES", "5"))), wait=wait_exponential_jitter(initial=0.5, max=8), retry=retry_if_exception(_should_retry))
def request(method: str, url: str, *, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, json: Any = None, files: Any = None, timeout: int = 30) -> requests.Response:
    _limiter.wait()
    resp = _session.request(method=method.upper(), url=url, headers=headers, params=params, json=json, files=files, timeout=timeout)
    if resp.status_code in (429, 500, 502, 503, 504):
        err = requests.RequestException(f"HTTP {resp.status_code}")
        setattr(err, 'response', resp)
        raise err
    return resp

