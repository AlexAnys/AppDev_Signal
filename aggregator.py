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
from typing import Dict, Optional


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

    def _load_config(self) -> Dict[str, bool]:
        if self._config is not None:
            return self._config
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Normalise keys to lowercase
                self._config = {k.lower(): bool(v) for k, v in data.items()}
                return self._config
        except FileNotFoundError:
            # Default configuration enables all sources
            self._config = {"news": True, "email": True, "report": True}
            return self._config
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {self.config_path}")

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
        if config.get("news", True):
            results["news"] = self._read_sample("news_sample.txt")
        if config.get("email", True):
            results["email"] = self._read_sample("email_sample.txt")
        if config.get("report", True):
            results["report"] = self._read_sample("report_sample.txt")
        return results


__all__ = ["Aggregator"]