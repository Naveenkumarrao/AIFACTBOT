from __future__ import annotations
import re, time, urllib.parse, datetime as dt
from collections import defaultdict

TLD_AUTHORITY = {
    ".gov": 1.0, ".edu": 0.9, ".int": 0.9, ".org": 0.7, ".com": 0.6, ".net": 0.5,
}

def domain_from_url(url: str) -> str:
    try:
        netloc = urllib.parse.urlparse(url).netloc.lower()
        return netloc
    except Exception:
        return ""

def tld_weight(domain: str) -> float:
    for tld, w in TLD_AUTHORITY.items():
        if domain.endswith(tld):
            return w
    return 0.5

def recency_weight(published: dt.datetime | None) -> float:
    if not published:
        return 0.6
    days = (dt.datetime.utcnow() - published).days
    if days <= 7:
        return 1.0
    if days <= 30:
        return 0.9
    if days <= 180:
        return 0.8
    if days <= 365:
        return 0.7
    return 0.6

def credibility_score(domain: str, published: dt.datetime | None) -> float:
    return round(0.6 * tld_weight(domain) + 0.4 * recency_weight(published), 3)

def classify_claim(text: str) -> str:
    # naive heuristic classifier
    t = text.strip().lower()
    opinion_markers = ["best", "should", "i think", "we believe", "opinion", "prefer"]
    unverifiable_markers = ["cannot be known", "no one knows"]
    if any(m in t for m in opinion_markers):
        return "Opinion"
    if any(m in t for m in unverifiable_markers):
        return "Unverifiable"
    # if it includes numbers, entities, capital names—assume factual/mixed
    if re.search(r"\b\d{4}\b|capital of|population|launch|temperature|score|ceo|president", t):
        return "Factual"
    return "Mixed"

def pick_verdict(labels: list[str]) -> str:
    if not labels:
        return "Uncertain"
    if all(l == "TRUE" for l in labels):
        return "True"
    if all(l == "FALSE" for l in labels):
        return "False"
    if any(l == "UNCERTAIN" for l in labels):
        return "Mixed"
    return "Mixed"
