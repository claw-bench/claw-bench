"""Lightweight IP geolocation with special region handling.

Uses ip-api.com (free, no key needed, 45 req/min).
Caches results to minimize API calls.
Special handling: Taiwan, Hong Kong, Macau as separate regions.
"""

from __future__ import annotations

import logging
import time
from threading import Lock
from typing import Dict, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

_cache: Dict[str, Tuple[str, str, float]] = {}
_cache_lock = Lock()
_CACHE_TTL = 86400

REGION_FLAGS: Dict[str, str] = {
    "CN": "🇨🇳", "US": "🇺🇸", "JP": "🇯🇵", "KR": "🇰🇷", "GB": "🇬🇧",
    "DE": "🇩🇪", "FR": "🇫🇷", "CA": "🇨🇦", "AU": "🇦🇺", "IN": "🇮🇳",
    "SG": "🇸🇬", "TW": "🇨🇳", "HK": "🇨🇳", "MO": "🇨🇳", "BR": "🇧🇷",
    "RU": "🇷🇺", "IL": "🇮🇱", "NL": "🇳🇱", "SE": "🇸🇪", "CH": "🇨🇭",
    "AE": "🇦🇪", "IE": "🇮🇪", "NZ": "🇳🇿", "PL": "🇵🇱", "ES": "🇪🇸",
    "IT": "🇮🇹", "FI": "🇫🇮", "NO": "🇳🇴", "DK": "🇩🇰", "MY": "🇲🇾",
    "TH": "🇹🇭", "VN": "🇻🇳", "PH": "🇵🇭", "ID": "🇮🇩", "MX": "🇲🇽",
    "AR": "🇦🇷", "CL": "🇨🇱", "CO": "🇨🇴", "ZA": "🇿🇦", "NG": "🇳🇬",
    "EG": "🇪🇬", "SA": "🇸🇦", "PK": "🇵🇰", "BD": "🇧🇩", "UA": "🇺🇦",
    "CZ": "🇨🇿", "RO": "🇷🇴", "PT": "🇵🇹", "AT": "🇦🇹", "BE": "🇧🇪",
}

REGION_NAMES_ZH: Dict[str, str] = {
    "CN": "中国大陆", "TW": "中国台湾", "HK": "中国香港", "MO": "中国澳门",
    "US": "美国", "JP": "日本", "KR": "韩国", "GB": "英国",
    "DE": "德国", "FR": "法国", "CA": "加拿大", "AU": "澳大利亚",
    "IN": "印度", "SG": "新加坡", "BR": "巴西", "RU": "俄罗斯",
    "IL": "以色列", "NL": "荷兰", "SE": "瑞典", "CH": "瑞士",
    "AE": "阿联酋", "IE": "爱尔兰", "NZ": "新西兰",
}

REGION_NAMES_EN: Dict[str, str] = {
    "CN": "China", "TW": "China", "HK": "China", "MO": "China",
    "US": "United States", "JP": "Japan", "KR": "South Korea", "GB": "United Kingdom",
    "DE": "Germany", "FR": "France", "CA": "Canada", "AU": "Australia",
    "IN": "India", "SG": "Singapore", "BR": "Brazil", "RU": "Russia",
}


def _detect_special_region(region_name: str, country_code: str) -> Tuple[str, str]:
    """Handle Taiwan, Hong Kong, Macau — all map to China."""
    rn = region_name.lower() if region_name else ""

    if country_code == "TW" or "taiwan" in rn:
        return "CN", "China"
    if country_code == "HK" or "hong kong" in rn:
        return "CN", "China"
    if country_code == "MO" or "macau" in rn or "macao" in rn:
        return "CN", "China"

    return country_code, region_name


async def lookup_ip(ip: str) -> Tuple[str, str]:
    """Return (country_code, country_name) for an IP.

    Returns ("XX", "Unknown") on failure.
    """
    if not ip or ip in ("unknown", "127.0.0.1", "::1", "localhost"):
        return "XX", "Unknown"

    now = time.time()
    with _cache_lock:
        if ip in _cache:
            code, name, ts = _cache[ip]
            if now - ts < _CACHE_TTL:
                return code, name

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,countryCode,country,regionName"},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    raw_code = data.get("countryCode", "XX")
                    raw_name = data.get("country", "Unknown")
                    region_name = data.get("regionName", "")

                    code, name = _detect_special_region(region_name, raw_code)
                    if code == raw_code:
                        name = raw_name

                    with _cache_lock:
                        _cache[ip] = (code, name, now)
                    return code, name
    except Exception as e:
        logger.debug("GeoIP lookup failed for %s: %s", ip, e)

    return "XX", "Unknown"


def get_flag(code: str) -> str:
    return REGION_FLAGS.get(code, "🌍")
