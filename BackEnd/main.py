# A simple web framework for building APIs in Python
from fastapi import FastAPI

# A library for data validation in Python, used here to define the structure of incoming data
from pydantic import BaseModel

# A library for working with file paths in an easy to read and platform independent way
from pathlib import Path

# Regular expressions - String manipulation and pattern matching
import re

# Very small, beginner-friendly FastAPI app.
app = FastAPI()


class TextIn(BaseModel):
    text: str


def load_stop_words():
    """Read single-quoted words from `setup_database.sql` and return a set.

    This is a simple way to get stop words the beginner can understand.
    """
    p = Path(__file__).parent / "setup_database.sql"
    if not p.exists():
        return set()
    s = p.read_text(encoding="utf-8", errors="ignore")
    words = re.findall(r"'([^']+)'", s)
    # lower-case for easy comparison
    return set(w.lower().strip() for w in words)


# Load once at import time so the code stays simple
STOP_WORDS = load_stop_words()


def tokenize(text):
    """Return a list of lowercase words from the input string."""
    return re.findall(r"\b\w+\b", text.lower())


@app.post("/process")
def process(payload: TextIn):
    """Return tokens and tokens with stop words removed."""
    tokens = tokenize(payload.text)
    filtered = [t for t in tokens if t not in STOP_WORDS]
    return {"tokens": tokens, "filtered_tokens": filtered}
