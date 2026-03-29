"""
Competitor Scraper — anti-bot scraping for marketing intelligence.
Patterns stolen from Scrapling (TLS impersonation, resource blocking, adaptive matching).
"""

import re
import json
import time
import hashlib
import logging
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from config import settings

logger = logging.getLogger(__name__)

# Stealth headers (from Scrapling's fingerprint system)
STEALTH_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

# Resource types to block for speed (from Scrapling)
BLOCKED_RESOURCE_TYPES = {"image", "media", "font", "stylesheet", "beacon", "websocket", "csp_report"}

# Tracker detection patterns (from Argus pixel_tracker_finder)
TRACKER_SIGNALS = [
    "pixel", "track", "analytics", "beacon", "utm_", "fbq(", "gtag(",
    "ga('create", "collect?", "conversion", "ads/", "_fb_", "clarity",
    "hotjar", "intercom", "drift", "hubspot", "mailchimp",
]

# Tech stack signatures (from Argus technology_stack)
TECH_SIGNATURES = {
    "cms": {
        "WordPress": ["wp-content", "wp-includes", "/wp-admin"],
        "Shopify": ["cdn.shopify.com", "shopify-section", "Shopify.theme"],
        "Webflow": ["webflow.com", "wf-section"],
        "Squarespace": ["squarespace.com", "sqsp-"],
        "Wix": ["wix.com", "wixsite"],
    },
    "analytics": {
        "Google Analytics": ["google-analytics.com", "gtag/js", "GoogleAnalyticsObject"],
        "Facebook Pixel": ["connect.facebook.net", "fbq(", "fbevents.js"],
        "Hotjar": ["hotjar.com", "hj("],
        "Mixpanel": ["mixpanel.com", "mixpanel.init"],
        "Segment": ["segment.com", "analytics.js"],
        "Plausible": ["plausible.io"],
        "Fathom": ["usefathom.com"],
    },
    "payments": {
        "Stripe": ["js.stripe.com", "stripe.com/v3"],
        "PayPal": ["paypal.com/sdk", "paypalobjects.com"],
        "Paddle": ["paddle.com", "Paddle.Setup"],
        "LemonSqueezy": ["lemonsqueezy.com"],
    },
    "chat": {
        "Intercom": ["intercom.com", "intercomSettings"],
        "Drift": ["drift.com", "driftt"],
        "Crisp": ["crisp.chat"],
        "Zendesk": ["zendesk.com", "zE("],
    },
    "frameworks": {
        "React": ["react", "reactDOM", "__NEXT_DATA__"],
        "Vue": ["vue.js", "__vue__", "Vue.config"],
        "Angular": ["ng-version", "angular"],
        "Next.js": ["__NEXT_DATA__", "_next/"],
        "Nuxt": ["__NUXT__", "_nuxt/"],
        "Svelte": ["svelte"],
    },
}


@dataclass
class PageScan:
    """Result of scanning a single page."""
    url: str
    title: str = ""
    description: str = ""
    og_image: str = ""
    h1: str = ""
    cta_texts: List[str] = field(default_factory=list)
    tech_stack: Dict[str, List[str]] = field(default_factory=dict)
    trackers: List[str] = field(default_factory=list)
    scripts_external: List[str] = field(default_factory=list)
    meta_tags: Dict[str, str] = field(default_factory=dict)
    word_count: int = 0
    link_count: int = 0
    scanned_at: float = 0

    def to_dict(self):
        return asdict(self)


@dataclass
class CompetitorProfile:
    """Aggregated intelligence about a competitor."""
    name: str
    domain: str
    pages_scanned: int = 0
    tech_stack: Dict[str, List[str]] = field(default_factory=dict)
    trackers: List[str] = field(default_factory=list)
    avg_word_count: float = 0
    cta_patterns: List[str] = field(default_factory=list)
    last_scanned: float = 0
    tribe_avg_score: float = 0

    def to_dict(self):
        return asdict(self)


class CompetitorScraper:
    """Anti-bot scraper for competitor intelligence.

    Uses stealth techniques from Scrapling:
    - Rotating user agents
    - Stealth headers
    - Resource blocking for speed

    Uses analysis techniques from Argus:
    - Tech stack fingerprinting
    - Tracker detection
    - Third-party integration scanning
    """

    def __init__(self):
        self._ua_index = 0
        self._session = None

    def _get_headers(self) -> dict:
        headers = STEALTH_HEADERS.copy()
        headers["User-Agent"] = USER_AGENTS[self._ua_index % len(USER_AGENTS)]
        self._ua_index += 1
        return headers

    def scan_page(self, url: str) -> PageScan:
        """Scan a single page for intelligence."""
        import urllib.request

        headers = self._get_headers()
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return PageScan(url=url, scanned_at=time.time())

        scan = PageScan(url=url, scanned_at=time.time())

        # Extract title
        m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
        if m:
            scan.title = m.group(1).strip()

        # Extract meta description
        m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', html, re.I)
        if m:
            scan.description = m.group(1).strip()

        # Extract og:image
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', html, re.I)
        if m:
            scan.og_image = m.group(1).strip()

        # Extract H1
        m = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.I)
        if m:
            scan.h1 = m.group(1).strip()

        # Extract CTA texts (buttons and links with action words)
        cta_pattern = re.compile(
            r'<(?:button|a)[^>]*>([^<]*(?:start|sign up|get started|buy|try|join|subscribe|book|register|download|claim)[^<]*)</(?:button|a)>',
            re.I,
        )
        scan.cta_texts = list(set(m.strip() for m in cta_pattern.findall(html) if m.strip()))

        # Tech stack detection (from Argus)
        for category, tools in TECH_SIGNATURES.items():
            for tool_name, signatures in tools.items():
                for sig in signatures:
                    if sig.lower() in html.lower():
                        if category not in scan.tech_stack:
                            scan.tech_stack[category] = []
                        if tool_name not in scan.tech_stack[category]:
                            scan.tech_stack[category].append(tool_name)
                        break

        # Tracker detection (from Argus)
        html_lower = html.lower()
        for signal in TRACKER_SIGNALS:
            if signal in html_lower:
                scan.trackers.append(signal)
        scan.trackers = list(set(scan.trackers))

        # External scripts
        for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)', html, re.I):
            src = m.group(1)
            if src.startswith("http"):
                scan.scripts_external.append(src)

        # Word count (strip HTML)
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        scan.word_count = len(text.split())

        # Link count
        scan.link_count = html.lower().count("<a ")

        return scan

    def build_profile(self, name: str, urls: List[str]) -> CompetitorProfile:
        """Build a competitor profile from multiple page scans."""
        profile = CompetitorProfile(name=name, domain="")

        all_tech: Dict[str, set] = {}
        all_trackers: set = set()
        all_ctas: List[str] = []
        total_words = 0

        for url in urls:
            scan = self.scan_page(url)
            if not profile.domain:
                m = re.match(r"https?://([^/]+)", url)
                if m:
                    profile.domain = m.group(1)

            # Merge tech stacks
            for cat, tools in scan.tech_stack.items():
                if cat not in all_tech:
                    all_tech[cat] = set()
                all_tech[cat].update(tools)

            all_trackers.update(scan.trackers)
            all_ctas.extend(scan.cta_texts)
            total_words += scan.word_count
            profile.pages_scanned += 1

        profile.tech_stack = {k: list(v) for k, v in all_tech.items()}
        profile.trackers = list(all_trackers)
        profile.cta_patterns = list(set(all_ctas))[:20]
        profile.avg_word_count = total_words / max(profile.pages_scanned, 1)
        profile.last_scanned = time.time()

        return profile
