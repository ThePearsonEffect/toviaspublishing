from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import math
import re


POWER_WORDS = {
    "discover", "proven", "secret", "unveil", "transform", "unlock", "master",
    "essential", "remarkable", "ultimate", "powerful", "inspiring", "timeless",
}
STOPWORDS = {
    "the","a","an","and","or","but","if","then","when","of","for","on","in","to","with",
}


@dataclass
class QuoteScore:
    quote: str
    score: float
    details: dict


def _word_list(text: str) -> List[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def compute_quote_score(quote: str) -> QuoteScore:
    words = _word_list(quote)
    num_words = len(words)
    if num_words == 0:
        return QuoteScore(quote=quote, score=0.0, details={})

    # Length score: Gaussian centered around 14 words
    mu, sigma = 14.0, 6.0
    length_score = math.exp(-((num_words - mu) ** 2) / (2 * sigma ** 2))

    # Power word bonus
    power_hits = sum(1 for w in words if w in POWER_WORDS)
    power_score = min(1.0, power_hits / 3.0)

    # Stopword ratio (too many stopwords reduces clarity)
    stop_hits = sum(1 for w in words if w in STOPWORDS)
    stop_ratio = stop_hits / num_words
    clarity_score = max(0.0, 1.0 - stop_ratio)

    # Punctuation/structure bonus: presence of dash/colon/comma indicates rhythm
    struct_bonus = 0.2 if re.search(r"[,:—–-]", quote) else 0.0

    # Capitalization emphasis bonus: words in Title Case mid-sentence (heuristic)
    cap_bonus = 0.2 if re.search(r"\b[A-Z][a-z]+\b.*\b[A-Z][a-z]+\b", quote) else 0.0

    score = 0.5 * length_score + 0.2 * power_score + 0.2 * clarity_score + 0.05 * struct_bonus + 0.05 * cap_bonus
    return QuoteScore(quote=quote, score=score, details={
        "num_words": num_words,
        "length_score": round(length_score, 3),
        "power_score": round(power_score, 3),
        "clarity_score": round(clarity_score, 3),
        "struct_bonus": struct_bonus,
        "cap_bonus": cap_bonus,
    })


def score_quotes(quotes: List[str]) -> List[QuoteScore]:
    scores = [compute_quote_score(q) for q in quotes]
    # Basic novelty: downweight near-duplicates (same starting 8 words)
    seen_starts = set()
    for qs in scores:
        start = " ".join(_word_list(qs.quote)[:8])
        if start in seen_starts:
            qs.score *= 0.7
        else:
            seen_starts.add(start)
    return sorted(scores, key=lambda x: x.score, reverse=True)


def compose_variants(book_title: str, author: str, quote: str) -> List[str]:
    base_tag = f"#{book_title.strip().replace(' ', '')}" if book_title else "#books"
    sign = f"— {author}" if author else ""
    variants = [
        f"{quote}\n\n{sign}\n\n{base_tag} #booklover #reading",
        f"{quote}\n\n{sign}\n\nWhat line would you underline? {base_tag}",
        f"{quote}\n\n{sign}\n\nPreorder now. {base_tag} #amreading",
    ]
    return variants
