from __future__ import annotations
import json
from typing import List, Dict, Any
import yaml

from config.settings import PROVIDER, OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_MODEL, OLLAMA_HOST

# Optional LLM providers (soft-imported)
llm_available = False
chat_model = None

def _try_load_llm():
    """Attempt to load the selected LLM provider."""
    global llm_available, chat_model
    try:
        if PROVIDER == "openai":
            from langchain_openai import ChatOpenAI # type: ignore
            chat_model = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.2, model="gpt-4o-mini")
            llm_available = True 
        elif PROVIDER == "anthropic":
            from langchain_anthropic import ChatAnthropic
            chat_model = ChatAnthropic(api_key=ANTHROPIC_API_KEY, temperature=0.2, model_name="claude-3-5-sonnet-20240620")
            llm_available = True
        elif PROVIDER == "ollama":
            from langchain_community.chat_models import ChatOllama
            chat_model = ChatOllama(base_url=OLLAMA_HOST, model=OLLAMA_MODEL, temperature=0.2)
            llm_available = True
        else:
            llm_available = False
    except Exception:
        llm_available = False

_try_load_llm()

with open("config/prompts.yaml", "r", encoding="utf-8") as f:
    PROMPTS = yaml.safe_load(f)

def _fallback_initial(claim: str) -> str:
    """Fallback if LLM not available: produce a basic initial response."""
    return (
        f"Initial take: Based on general knowledge and without external confirmation, "
        f"There's a brief answer to the claim:\n{claim}\n"
        
    )

def _filter_factual_sentences(text: str) -> list[str]:
    """Robustly extract factual sentences, removing meta statements and prefixes."""
    bad_phrases = [
        "based on general knowledge",
        "without external confirmation",
        "there may be uncertainty",
        "we'll verify with credible sources",
        "initial take"
    ]

    # Normalize line breaks
    text = text.replace("\n", " ").strip()

    # Split on periods
    raw_sentences = text.split(".")
    sentences = []

    for s in raw_sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        if any(bp in s_clean.lower() for bp in bad_phrases):
            continue
        sentences.append(s_clean[:160])

    # Fallback: try to extract part after first colon
    if not sentences and ":" in text:
        after_colon = text.split(":", 1)[1].strip()
        if after_colon:
            sentences = [after_colon[:160]]

    return sentences or ["The claim contains verifiable factual components."]

def _fallback_assumptions(initial: str) -> list[str]:
    """Fallback method to extract factual assumptions."""
    return _filter_factual_sentences(initial)

def _fallback_verify(assumption: str) -> dict:
    """Fallback verification if LLM not available."""
    return {
        "label": "UNCERTAIN",
        "rationale": "Needs corroboration from credible recent sources."
    }

def generate_initial_response(claim: str) -> str:
    """Generate an initial reasoning step for the claim."""
    if llm_available:
        prompt = PROMPTS["initial_response"] + "\nClaim: " + claim
        return chat_model.invoke(prompt).content.strip()
    return _fallback_initial(claim)

def extract_assumptions(initial_response: str) -> list[str]:
    """Extract only factual assumptions from the initial reasoning step."""
    if llm_available:
        prompt = (
            PROMPTS["extract_assumptions"]
            + "\nInitial: " + initial_response
            + "\nOnly return verifiable factual statements as a JSON list. Do NOT include meta-statements."
        )
        out = chat_model.invoke(prompt).content.strip()
        try:
            data = json.loads(out)
            if isinstance(data, list):
                cleaned = [s for s in (str(x).strip() for x in data) if s and len(s) > 5]
                return cleaned[:6]
        except Exception:
            pass
    return _filter_factual_sentences(initial_response)

def verify_assumption_with_llm(assumption: str) -> dict:
    """Verify a single assumption using the LLM."""
    if llm_available:
        prompt = PROMPTS["verify_assumption"].format(assumption=assumption)
        raw = chat_model.invoke(prompt).content.strip()
        first_line = raw.splitlines()[0].strip().upper()
        label = "UNCERTAIN"
        if "TRUE" in first_line:
            label = "TRUE"
        elif "FALSE" in first_line:
            label = "FALSE"
        rationale = raw if len(raw) < 300 else raw[:300]
        return {"label": label, "rationale": rationale}
    return _fallback_verify(assumption)

def synthesize(final_inputs: dict) -> str:
    """Generate the final verdict synthesis."""
    if llm_available:
        prompt = PROMPTS["synthesize"] + "\nInputs: " + json.dumps(final_inputs, ensure_ascii=False)
        return chat_model.invoke(prompt).content.strip()
    verdict = final_inputs.get("verdict", "Mixed")
    conf = final_inputs.get("confidence", 60)
    return f"Verdict: {verdict} (confidence ~{conf}%). See sources for details."
