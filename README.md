# Signal Prototype

This repository contains a prototype of an **AI‑driven information hub**.
The goal is to explore how disparate sources of information can be
aggregated, filtered and distilled into concise updates.  The original
version demonstrated a self‑contained workflow using sample files and
simple heuristics.  The current iteration extends that foundation with
optional AI back‑ends, rudimentary RSS ingestion and a web interface for
interactive use.

## What’s Included

| Module        | Description                                                                                                                                       |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| `aggregator.py` | Provides the `Aggregator` class, which currently reads sample content from the `samples/` directory and, if configured, fetches additional items from RSS feeds.  The module defines placeholders and stubs for future integrations with **Factiva**, **Euromonitor**, **Financial** data and **WRDS** (Wharton Research Data Services).  Real API calls are only invoked if corresponding configuration flags and API keys are provided. |
| `summarizer.py` | Implements three simple summarisation functions (`summarize_general`, `summarize_email` and `summarize_report`).  These functions perform deterministic, sentence‑based summarisation without relying on any third‑party APIs or large language models. |
| `summarization_service.py` | Defines a `Summarizer` class that wraps the basic heuristics and adds optional AI back‑ends (`openai`, `deepseek`, `qwen`, `gemini`).  The Gemini integration uses the `google-generativeai` package and reads a `GEMINI_API_KEY` from the environment.  When no backend is specified or no key is available, the heuristics from `summarizer.py` are used as a fallback. |
| `main.py`      | A command‑line entry point that ties everything together.  It loads the enabled sources from `config.json`, runs the appropriate summariser for each source and prints the results. |
| `web_app.py`   | A simple Flask application that exposes a web interface for summarising text.  Users can choose a content type, select an AI back‑end and optionally provide custom text to summarise. |
| `templates/`   | Contains Jinja2 templates used by the web app.  The `index.html` file defines a minimal UI for selecting summarisation options and viewing results. |
| `config.json`  | Configuration file specifying which sample sources are enabled, an optional list of RSS feeds to ingest (`rss_feeds`), and flags for external services (`factiva`, `euromonitor`, `financial`, `wrds`).  Additional fields may store API keys directly if you prefer not to use environment variables. |
| `samples/`     | A directory of sample text files standing in for news articles, emails and reports.  These files allow the prototype to operate without network connectivity. |

## Running the Prototype

To try out the prototype locally, ensure you have Python 3.8 or later installed.  No external dependencies beyond the Python standard library are required.

```bash
python main.py --max-sentences 3
```

By default the script reads `config.json` in the project root.  You can supply an alternative configuration file using `--config /path/to/config.json`.  The `--max-sentences` flag controls how many sentences will be included in the generic summaries (email and report summaries derive this value internally).

### Example Output

Running the command above with the provided samples produces the following output:

```
=== NEWS SUMMARY ===
President John Doe visited France on Tuesday to discuss economic cooperation. During a joint press conference, he highlighted the strength of bilateral trade and announced plans for new investments. Analysts say the visit underscores a shift in foreign policy priorities.

=== EMAIL SUMMARY ===
Hi team, Thanks for joining yesterday's planning session. We agreed to finalise the project timeline by Friday and to circulate draft specifications by next Wednesday.

Action items:
- Action: compile the first draft of the timeline (due Thursday).
- Todo: review the scope document and add any missing sections.

=== REPORT SUMMARY ===
Section 1: Problem Statement Our sales pipeline has grown increasingly complex, leading to longer cycle times and lower conversion rates.

Section 2: Methodology We collected quantitative data from our CRM over the past 18 months and conducted interviews with key sales personnel.

Section 3: Conclusion The investigation revealed that delays in responding to inbound leads account for nearly 40 percent of lost opportunities.
```

## Next Steps

The current iteration still aims to run in constrained environments but
adds a few conveniences.  There remain many open avenues for
development:

### AI Summarisation

The `summarization_service.Summarizer` allows you to select between
heuristic summaries and AI providers.  To enable the OpenAI back‑end,
set the `OPENAI_API_KEY` environment variable before running the
application.  Likewise, enabling the Gemini back‑end requires the
`GEMINI_API_KEY` environment variable and the optional
`google-generativeai` dependency.  Placeholders for DeepSeek and
Qwen remain until suitable APIs are released.  Without a valid key
for the chosen provider, the service silently falls back to the
offline heuristics.

### Web Interface

`web_app.py` exposes a basic Flask server that renders an HTML form for
summarisation.  To use it, install the dependencies and run the
development server:

```bash
pip install flask feedparser openai
export OPENAI_API_KEY=sk-...   # if using OpenAI
export FLASK_APP=web_app.py
flask run
```

By default the server loads sample content from `samples/`, but you can
paste arbitrary text into the form.  Choosing a different back‑end will
dispatch the request to the respective summariser.

### Data Sources

`aggregator.py` has been extended with rudimentary RSS support.  If
`rss_feeds` is populated in `config.json`, the aggregator will fetch up
to five entries from each feed and append them to the local news
content.  This requires the optional `feedparser` dependency.  Flags
such as `factiva`, `euromonitor`, `financial` and `wrds` instruct the
aggregator to query those services.  For WRDS integration, supply a
`wrds` entry in `config.json` (either `true` or your API key) or set the
`WRDS_API_KEY` environment variable.  Without a key or network access,
the aggregator returns empty strings for these sources.

### Deployment & Custom Domain

To expose the web interface under your own domain (e.g., `signal.app`),
consider hosting the Flask app on a platform such as Heroku, Render or
Railway, or containerising it for deployment on a virtual machine.  If
you choose a static hosting solution like GitHub Pages, you can serve
the frontend only—API requests would need to be proxied to a backend
running elsewhere.  Mapping the domain involves creating a DNS `A` or
`CNAME` record via your registrar (e.g., Porkbun) and pointing it at
your hosting provider.  Consult the provider’s documentation for
instructions.  **Note:** domain changes are live operations; ensure you
have the correct IP addresses before updating DNS.

### Persistence and Storage

Persisting fetched content and generated summaries (e.g., in a SQLite
database) would enable historical search and incremental updates.  This
feature has not been implemented yet but is a natural next step.

The repository remains a starting point for more sophisticated
functionality.  Feel free to fork and extend it to suit your needs.