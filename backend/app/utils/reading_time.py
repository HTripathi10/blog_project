"""
utils/reading_time.py — Estimate reading time from post content

💡 CONCEPT: Pure utility functions
   These have no dependencies on the DB or HTTP — just pure logic.
   Keeping them separate makes them easy to test and reuse.

Average adult reading speed ≈ 200 words/minute.
We strip markdown syntax before counting to avoid counting # and ** as words.
"""

import re


def calculate_reading_time(content: str) -> int:
    """
    Returns estimated reading time in minutes (minimum 1).

    Example:
        1000 words → 1000 / 200 = 5 minutes
        50 words   → 50 / 200 = 0.25 → rounded up to 1 minute
    """
    # Strip markdown syntax (headers, bold, code blocks, links, etc.)
    clean = re.sub(r"[#*`\[\]()!_>~]", " ", content)
    # Split on whitespace and count non-empty tokens
    word_count = len([w for w in clean.split() if w])
    minutes = max(1, round(word_count / 200))
    return minutes
