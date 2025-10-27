"""
summarizer.py
================

This module contains a handful of lightweight summarisation
utilities that do not rely on any external services or large
language models.  The goal of these functions is to provide a
stable baseline for condensing long passages of text into a more
digestible form.  They are intentionally simple: summarisation
is performed by splitting the input into sentences and returning
the first ``n`` sentences as a summary.  This approach is far
from state‑of‑the‑art, but it provides a predictable and
deterministic way to verify that the broader system plumbing
works end‑to‑end.

The module exposes three top‑level helper functions:

* ``summarize_general`` – generic summary for arbitrary prose.
* ``summarize_email`` – extract action items and due dates from
  informal email correspondence in addition to a general summary.
* ``summarize_report`` – break down structured reports into
  problem, method and conclusion sections and then summarise each
  part individually.

These helpers can be extended in the future to integrate more
sophisticated summarisation algorithms.  They currently operate
on plain English text.  For other languages a different
segmentation strategy may be required.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple


def _split_sentences(text: str) -> List[str]:
    """Split a paragraph into sentences using a simple heuristic.

    This function looks for punctuation marks that typically
    terminate sentences (period, exclamation mark, question mark)
    followed by whitespace.  It returns a list of sentences
    preserving the order in which they appear in the original text.

    Parameters
    ----------
    text:
        The input string to be split.

    Returns
    -------
    List[str]
        A list of sentence strings.
    """
    # Normalise whitespace and strip leading/trailing space
    cleaned = ' '.join(text.strip().split())
    # Use regex to split on punctuation followed by a space
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    # Filter out any empty strings
    return [s for s in sentences if s]


def summarize_general(text: str, max_sentences: int = 3) -> str:
    """Return the first ``max_sentences`` sentences of ``text``.

    If the input contains fewer than ``max_sentences`` sentences
    then the entire string is returned unchanged.  This function
    deliberately avoids complex natural language processing to
    minimise dependencies and provide deterministic behaviour.

    Parameters
    ----------
    text:
        The text to be summarised.
    max_sentences:
        The maximum number of sentences to include in the summary.

    Returns
    -------
    str
        A concise summary consisting of the first ``max_sentences``
        sentences.
    """
    sentences = _split_sentences(text)
    if len(sentences) <= max_sentences:
        return text.strip()
    return ' '.join(sentences[:max_sentences])


def summarize_email(text: str, max_sentences: int = 2) -> str:
    """Summarise an email by returning a short overview and key actions.

    The summary consists of the first ``max_sentences`` sentences of
    the email body along with a list of lines that look like
    actionable items.  Lines are considered actionable if they
    contain keywords such as ``todo``, ``action``, ``deadline`` or
    ``due`` (case insensitive).  If no such lines are found, only
    the generic summary is returned.

    Parameters
    ----------
    text:
        The raw email content.
    max_sentences:
        Number of leading sentences to include in the overview.

    Returns
    -------
    str
        A string combining the overview and any detected action
        items.
    """
    overview = summarize_general(text, max_sentences=max_sentences)
    # Find potential action items by scanning individual lines
    action_keywords = ["todo", "to do", "action", "deadline", "due", "请办理", "待办"]
    actions: List[str] = []
    for line in text.splitlines():
        lower = line.lower()
        if any(keyword in lower for keyword in action_keywords):
            # Preserve original line formatting
            cleaned_line = line.strip()
            if cleaned_line:
                actions.append(cleaned_line)
    if not actions:
        return overview
    actions_block = "\n".join(f"- {a}" for a in actions)
    return f"{overview}\n\nAction items:\n{actions_block}"


def summarize_report(text: str, max_sentences_per_section: int = 2) -> str:
    """Summarise a structured report by its apparent sections.

    Many reports follow a problem–method–conclusion structure or
    include headings separated by blank lines.  This function
    attempts to break the input into sections using two or more
    consecutive newline characters as a delimiter.  Each section is
    then summarised individually using ``summarize_general``.

    Parameters
    ----------
    text:
        The report to be summarised.
    max_sentences_per_section:
        Number of sentences to extract from each section.

    Returns
    -------
    str
        A multi‑section summary with each section clearly
        separated by a blank line.
    """
    sections = [section.strip() for section in re.split(r'\n{2,}', text) if section.strip()]
    summaries: List[str] = []
    for idx, section in enumerate(sections):
        heading = f"Section {idx + 1}"
        summary = summarize_general(section, max_sentences=max_sentences_per_section)
        summaries.append(f"{heading}: {summary}")
    return "\n\n".join(summaries)


__all__ = [
    "summarize_general",
    "summarize_email",
    "summarize_report",
]