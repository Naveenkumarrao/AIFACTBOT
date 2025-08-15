from typing import List, Dict, Any
import datetime as dt
import sys
import os

# Add src/ to path to allow imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from prompt_chains import (
    generate_initial_response,
    extract_assumptions,
    verify_assumption_with_llm,
    synthesize
)
from search_tools import search_web, fetch_page
from utils import credibility_score, classify_claim, pick_verdict


class FactChecker:
    def __init__(self):
        pass

    def _verify_with_evidence(self, assumption: str) -> dict:
        results = search_web(assumption, max_results=6)
        pages = []
        for r in results:
            url = r.get("href") or r.get("url")
            if not url:
                continue
            page = fetch_page(url)
            page["score"] = credibility_score(
                page.get("domain", ""),
                page.get("published")
            )
            pages.append(page)

        # Keep top 4 most credible
        pages = sorted(pages, key=lambda x: x.get("score", 0), reverse=True)[:4]

        llm_judgement = verify_assumption_with_llm(assumption)

        # Heuristic check
        text_blobs = " ".join([p.get("text", "") for p in pages]).lower()
        assumption_terms = [
            t for t in assumption.lower().split() if len(t) > 3
        ]
        hits = sum(1 for t in set(assumption_terms) if t in text_blobs)
        heuristic_label = "TRUE" if hits >= 3 else "UNCERTAIN"

        label = (
            llm_judgement.get("label")
            if llm_judgement.get("label") != "UNCERTAIN"
            else heuristic_label
        )

        return {
            "assumption": assumption,
            "label": label,
            "llm_label": llm_judgement.get("label"),
            "rationale": llm_judgement.get("rationale"),
            "evidence": pages,
        }

    def check_claim(self, claim: str) -> dict:
        claim_type = classify_claim(claim)
        initial = generate_initial_response(claim)
        assumptions = extract_assumptions(initial)

        verifications = [self._verify_with_evidence(a) for a in assumptions]
        labels = [v["label"] for v in verifications if v]
        verdict = pick_verdict(labels)

        # Confidence mapping
        conf_map = {"True": 80, "False": 80, "Mixed": 60, "Uncertain": 50}
        confidence = conf_map.get(verdict, 60)

        # Collect top sources
        top_sources = []
        for v in verifications:
            for ev in v.get("evidence", [])[:2]:
                top_sources.append({
                    "domain": ev.get("domain"),
                    "url": ev.get("url"),
                    "title": ev.get("title"),
                    "published": ev.get("published").isoformat() if ev.get("published") else None
                })
            if len(top_sources) >= 4:
                break

        synthesis = synthesize({
            "claim": claim,
            "claim_type": claim_type,
            "verifications": [{"assumption": x["assumption"], "label": x["label"]} for x in verifications],
            "sources": top_sources,
            "verdict": verdict,
            "confidence": confidence
        })

        return {
            "claim": claim,
            "claim_type": claim_type,
            "initial_response": initial,
            "assumptions": assumptions,
            "verifications": verifications,
            "verdict": verdict,
            "confidence": confidence,
            "synthesis": synthesis,
            "sources": top_sources
        }
