# AI Fact-Checker Bot

A simple, end-to-end fact-checking bot implementing prompt chaining, web search, and structured reasoning.
Includes Streamlit, Gradio, and CLI interfaces.

> Built to match the assignment spec and directory structure. Works **with or without** paid LLM APIs by
> falling back to a light rule-based model when no API keys are present.

## Features
- LangChain-style prompt chaining: initial response → assumptions → verification → evidence → synthesis
- DuckDuckGo web search + page scraping for evidence
- Source credibility scoring (domain + recency)
- Claim classification (Factual / Opinion / Mixed / Unverifiable)
- Streamlit UI, Gradio UI, and CLI
- Tests and examples

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# (optional) set API keys in .env
```

Optional providers (set in `.env`):
- `PROVIDER=openai` and `OPENAI_API_KEY=...`
- `PROVIDER=anthropic` and `ANTHROPIC_API_KEY=...`
- `PROVIDER=ollama` (requires local Ollama server and a chat-capable model, e.g., `llama3.1`)
- otherwise the app uses a light rule-based fallback (still completes the pipeline).

## Run

### Streamlit
```bash
streamlit run src/ui/streamlit_app.py
```

### Gradio
```bash
python -m src.ui.gradio_app
```

### CLI
```bash
python -m src.ui.cli --claim "The capital of France is Paris."
```

or via main entry:
```bash
python main.py --mode cli --claim "What happened in the latest SpaceX launch?"
```

## Tests
```bash
pytest -q
```

## Project Structure
```
fact_checker_bot/
  src/
    __init__.py
    fact_checker.py
    prompt_chains.py
    search_tools.py
    utils.py
    ui/
      streamlit_app.py
      gradio_app.py
      cli.py
  config/
    prompts.yaml
    settings.py
  tests/
    test_fact_checker.py
    test_search_tools.py
  examples/
    example_queries.txt
    demo_notebook.ipynb
  requirements.txt
  .env.example
  README.md
  main.py
```

## Notes
- The fallback model is intentionally simple; when you set an API provider, you’ll get stronger reasoning quality.
- The demo notebook is a lightweight placeholder showing the pipeline; feel free to expand it.
