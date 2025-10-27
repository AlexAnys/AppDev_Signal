"""
main.py
=======

Entry point for the signal prototype.  This script wires
together the aggregator and summariser components to provide
a simple command‑line interface.  Running the script will read
enabled sample sources from ``config.json``, summarise each
according to its type and print the resulting summaries to
standard output.

Future versions of this entry point could expose an HTTP
service (for example, via Flask or FastAPI), integrate with
message queues or schedule periodic pulls from external APIs.
"""

from __future__ import annotations

import argparse
from typing import Dict

from aggregator import Aggregator
from summarizer import (
    summarize_general,
    summarize_email,
    summarize_report,
)


def run() -> None:
    parser = argparse.ArgumentParser(description="Aggregate and summarise information sources")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration JSON file (defaults to config.json in project directory)",
    )
    parser.add_argument(
        "--max-sentences",
        type=int,
        default=3,
        help="Maximum number of sentences for generic summaries",
    )
    args = parser.parse_args()
    # Initialise aggregator with optional custom config
    aggregator = Aggregator(config_path=args.config or "config.json")
    contents: Dict[str, str] = aggregator.collect()
    for source_name, text in contents.items():
        if not text.strip():
            print(f"[warning] Source '{source_name}' has no content to summarise.\n")
            continue
        print(f"=== {source_name.upper()} SUMMARY ===")
        if source_name == "email":
            summary = summarize_email(text, max_sentences=max(args.max_sentences - 1, 1))
        elif source_name == "report":
            summary = summarize_report(text, max_sentences_per_section=max(args.max_sentences - 1, 1))
        else:
            summary = summarize_general(text, max_sentences=args.max_sentences)
        print(summary)
        print()


if __name__ == "__main__":
    run()