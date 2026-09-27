"""
utils/content_filter.py — Content moderation utilities

💡 CONCEPT: Content Guardrails
   Prevents users from posting content with derogatory/profane language.
   Uses better-profanity library for detection.
"""

from better_profanity import profanity
from typing import List


def contains_profanity(text: str) -> bool:
    """Check if text contains profanity."""
    return profanity.contains_profanity(text)


def censor_text(text: str) -> str:
    """Censor profanity in text (replaces with asterisks)."""
    return profanity.censor(text)


def validate_content(text: str, field_name: str = "content") -> tuple[bool, str]:
    """
    Validate content for profanity.
    Returns (is_valid, error_message).
    """
    if contains_profanity(text):
        return False, f"{field_name} contains inappropriate language. Please remove any profanity before submitting."
    return True, ""


def validate_multiple_fields(fields: dict) -> tuple[bool, str]:
    """
    Validate multiple fields for profanity.
    Returns (is_valid, error_message).
    """
    for field_name, field_value in fields.items():
        if field_value and contains_profanity(field_value):
            return False, f"{field_name} contains inappropriate language. Please remove any profanity before submitting."
    return True, ""
