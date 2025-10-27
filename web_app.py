"""
web_app.py
===========

This module defines a simple Flask application that exposes a web UI for
summarising text.  Users can either provide their own text or choose to
summarise one of the built‑in content types (news, email, report) collected
by the ``Aggregator``.  A selection of summarisation back‑ends is offered:

* **Heuristic** – uses the local summariser functions (default).
* **OpenAI** – calls the OpenAI Chat API, if credentials are available.
* **DeepSeek/Qwen/Gemini** – placeholders for future integrations.

Before running the application you must install Flask and any AI clients
you wish to use::

    pip install flask feedparser openai

To start the development server::

    export FLASK_APP=web_app.py
    flask run --reload

The web interface will be available at http://127.0.0.1:5000/.
"""

from __future__ import annotations

import os
from typing import Dict

from flask import Flask, render_template, request

from aggregator import Aggregator
from summarization_service import Summarizer


app = Flask(__name__)

# Instantiate services
summarizer = Summarizer()
aggregator = Aggregator()


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """Handle the main form for summarisation."""
    summary: str | None = None
    content_type = request.form.get("content_type", "news")
    backend = request.form.get("backend", "heuristic")
    manual_text = request.form.get("manual_input", "").strip()
    # On POST, attempt summarisation
    if request.method == "POST":
        if manual_text:
            text_to_summarise = manual_text
        else:
            content_map: Dict[str, str] = aggregator.collect()
            text_to_summarise = content_map.get(content_type, "")
        # Determine backend (None for heuristic)
        selected_backend = None if backend == "heuristic" else backend
        summary = summarizer.summarise(text_to_summarise, content_type, backend=selected_backend)
    return render_template(
        "index.html",
        summary=summary,
        content_type=content_type,
        backend=backend,
        manual_input=manual_text,
    )


if __name__ == "__main__":
    # Allow running with ``python web_app.py``
    app.run(debug=True)