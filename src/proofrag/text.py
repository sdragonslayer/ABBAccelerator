from __future__ import annotations

import re

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[-_.][a-z0-9]+)*", re.IGNORECASE)
LIGATURES = str.maketrans({"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"})


def normalize_unicode(text: str) -> str:
    return text.translate(LIGATURES)


def normalize_text(text: str) -> str:
    return " ".join(normalize_unicode(text).casefold().split())


def tokenize(text: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_PATTERN.finditer(text)]


def concise_quote(text: str, limit: int = 420) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    shortened = cleaned[: limit - 1].rsplit(" ", 1)[0]
    return f"{shortened}…"
