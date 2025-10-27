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
from summarization_service import Summarizer


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
        help=(
            "Maximum number of sentences for heuristic summaries. "
            "Ignored when using an AI backend."
        ),
    )
    parser.add_argument(
        "--backend",
        type=str,
        default=None,
        help=(
            "Name of the AI backend to use (openai, deepseek, qwen, gemini). "
            "Defaults to heuristic methods if omitted."
        ),
    )
    args = parser.parse_args()
    # Initialise aggregator with optional custom config
    aggregator = Aggregator(config_path=args.config or "config.json")
    contents: Dict[str, str] = aggregator.collect()
    summarizer = Summarizer()
    for source_name, text in contents.items():
        if not text.strip():
            print(f"[warning] Source '{source_name}' has no content to summarise.\n")
            continue
        print(f"=== {source_name.upper()} SUMMARY ===")
        # Determine content type; unknown keys use general heuristics
        ctype = source_name.lower()
        # Use AI backend if provided; heuristics ignore max_sentences differently for each type
        backend = args.backend.lower() if args.backend else None
        if backend is None:
            # For heuristics, adjust sentence count for email/report
            if ctype == "email":
                summary = summarizer.summarise(text, ctype, backend=None)
            elif ctype == "report":
                summary = summarizer.summarise(text, ctype, backend=None)
            else:
                summary = summarizer.summarise(text, ctype, backend=None)
        else:
            summary = summarizer.summarise(text, ctype, backend=backend)
        print(summary)
        print()


if __name__ == "__main__":
    run()