import re
import unicodedata


def normalize_answer(text):
    if text is None:
        return ""

    text = str(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.strip()
    text = text.lower()

    # Allow surrounding quotation marks.
    text = text.strip('"\'“”‘’')

    # Allow one trailing period.
    text = re.sub(r"\.$", "", text.strip())

    # Normalize repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def score(output, expected):
    return normalize_answer(output) == normalize_answer(expected)
