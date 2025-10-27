"""
aggregator.py
==============

This module provides a very simple framework for aggregating
information from a handful of sources.  In a production system,
each source would wrap an external API (for example, Gmail,
Factiva, YouTube or Douyin) and authenticate on behalf of the
user.  Because this is a local prototype without network access,
the ``Aggregator`` class here simply reads sample text files from
the ``samples`` directory.  These files stand in for news
articles, emails and longer reports.

The aggregator exposes a single method, ``collect()``, which
returns a dictionary mapping each source name to its raw text
content.  Sources can be enabled or disabled via a configuration
dictionary passed at initialisation time.

Future extensions might include:

* Polling real APIs on a schedule and caching results.
* Allowing users to register arbitrary RSS feeds or email
  accounts.
* Applying filters at ingestion time to discard low‑value
  content.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    import feedparser  # type: ignore
except Exception:
    feedparser = None


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")


@dataclass
class Aggregator:
    """Aggregate information from multiple local sample sources.

    Parameters
    ----------
    config_path:
        Path to a JSON file describing which sources are enabled.
        The configuration file should be a mapping where keys are
        source identifiers (``news``, ``email``, ``report``) and
        values are booleans indicating whether that source is
        active.
    """

    config_path: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "config.json"))
    _config: Optional[Dict[str, bool]] = field(init=False, default=None)

    def _load_config(self) -> Dict[str, object]:
        """Load and normalise the configuration file.

        The configuration allows enabling/disabling certain sources as booleans
        and specifying additional parameters such as a list of RSS feeds.  Keys
        are normalised to lowercase.  If the file cannot be found, a default
        configuration enabling all sources is returned.
        """
        if self._config is not None:
            return self._config
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            # Default configuration enables all built‑in sources
            data = {"news": True, "email": True, "report": True, "rss_feeds": []}
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {self.config_path}")
        # Normalise keys; booleans remain booleans, lists remain lists
        normalised: Dict[str, object] = {}
        for key, value in data.items():
            lower_key = key.lower()
            normalised[lower_key] = value
        self._config = normalised
        return self._config

    def _read_sample(self, filename: str) -> str:
        path = os.path.join(SAMPLES_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def collect(self) -> Dict[str, str]:
        """Collect raw content from all enabled sources.

        Returns
        -------
        Dict[str, str]
            A mapping of source names to their respective text
            content.  Disabled sources will not appear in the
            returned dictionary.
        """
        config = self._load_config()
        results: Dict[str, str] = {}
        # Local samples
        if bool(config.get("news", True)):
            results["news"] = self._read_sample("news_sample.txt")
        if bool(config.get("email", True)):
            results["email"] = self._read_sample("email_sample.txt")
        if bool(config.get("report", True)):
            results["report"] = self._read_sample("report_sample.txt")
        # Remote RSS feeds – concatenate all entries into a single text blob
        rss_feeds: List[str] = config.get("rss_feeds", []) if isinstance(config.get("rss_feeds"), list) else []
        if rss_feeds and feedparser is not None:
            articles: List[str] = []
            for url in rss_feeds:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:5]:
                        title = getattr(entry, "title", "")
                        summary = getattr(entry, "summary", "")
                        articles.append(f"{title} {summary}")
                except Exception:
                    continue
            if articles:
                # Prepend remote articles to news or create a separate key
                combined = "\n\n".join(articles)
                # Append to existing news content if present
                if "news" in results:
                    results["news"] = f"{combined}\n\n{results['news']}"
                else:
                    results["news"] = combined
        # Placeholders for future APIs (Factiva, Euromonitor, financial)
        for key in ("factiva", "euromonitor", "financial"):
            if bool(config.get(key, False)):
                # At this stage we cannot fetch real data; return empty string
                results[key] = ""
        return results


__all__ = ["Aggregator"]