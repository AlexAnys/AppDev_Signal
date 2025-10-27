# Signal Prototype

This repository contains a very early prototype of an **AI‑driven
information hub**.  Its purpose is to explore how disparate
sources of information could be aggregated, filtered and
condensed into concise updates.  While the long‑term vision
includes deep integrations with third‑party platforms (Factiva,
email providers, social media, etc.) and adaptive summarisation
strategies, this prototype focuses on demonstrating a minimal,
fully offline workflow.

## What’s Included

| Module        | Description                                                                                                                                       |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| `aggregator.py` | Provides the `Aggregator` class, which currently reads sample content from the `samples/` directory.  In a production system this module would wrap external data sources and apply initial filtering. |
| `summarizer.py` | Implements three simple summarisation functions (`summarize_general`, `summarize_email` and `summarize_report`).  These functions perform deterministic, sentence‑based summarisation without relying on any third‑party APIs or large language models. |
| `main.py`      | A command‑line entry point that ties everything together.  It loads the enabled sources from `config.json`, runs the appropriate summariser for each source and prints the results. |
| `config.json`  | A minimal configuration file specifying which sample sources are enabled.  Users can toggle sources on or off by setting the corresponding boolean value. |
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

This codebase is intentionally simple to ensure it runs reliably in
isolated environments.  Several areas are open for further
development:

- **Data source integrations:** Replace the sample file reader with
  connectors to real systems such as RSS feeds, email APIs or
  social platforms.  Authentication and rate limiting will need
  careful handling.
- **Adaptive summarisation:** Incorporate more advanced
  techniques—either via open‑source models or third‑party APIs—to
  tailor summaries to the user’s needs and the content’s genre.
- **Configuration UI:** Provide a user interface for selecting
  sources, defining preferences and scheduling summary deliveries.
- **Persistence and storage:** Store fetched content and
  generated summaries in a database to allow historical search and
  incremental updates.

For now, the prototype offers a concrete starting point upon
which more sophisticated features can be layered.