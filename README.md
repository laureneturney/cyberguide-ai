# CyberGuide.AI

Agentic AI career navigation for aspiring cybersecurity professionals — built for the IBM Experiential AI Learning Lab.

CyberGuide.AI is a Streamlit prototype that coordinates **four agents** to take a newcomer or career changer from "I'm interested in cyber" to "I have job-ready, role-specific evidence":

1. **Career Navigation Graph agent** — a curated map of domains → roles → skills → evidence.
2. **Pathfinding agent** — generates a personalized week-by-week roadmap; re-plans on demand.
3. **Just-in-Time Resource Retriever** — surfaces the right curated + live-web resources for the user's *current* step.
4. **Decision Support agent** — walks the user through critical forks with structured trade-offs and a recommendation gated on human review.

The orchestrator threads the user's profile through every call and writes a transparent audit trail you can inspect on the **Audit & Trust** page.

---

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # edit if you want a real LLM
streamlit run streamlit_app.py
```

The default `LLM_PROVIDER=mock` runs the entire app offline with a deterministic, demo-friendly model — no API keys required. Perfect for Streamlit Cloud previews.

---

## Switching LLM providers

The backend is provider-agnostic. Pick one in `.env`:

```dotenv
# Pick one: "watsonx" | "custom" | "mock"
LLM_PROVIDER=mock

# IBM watsonx.ai — fill these to use IBM Cloud foundation models.
WATSONX_APIKEY=
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct

# OpenAI-compatible / open-source endpoint (vLLM, Ollama, LM Studio, OpenAI…).
CUSTOM_LLM_BASE_URL=http://localhost:8080/v1
CUSTOM_LLM_API_KEY=not-needed
CUSTOM_LLM_MODEL=llama-3.1-8b-instruct
```

If a chosen provider's credentials are missing or its SDK fails to load, the factory **silently falls back to mock** so the demo never breaks.

> **UI branding note**: regardless of the configured provider, the interface labels the service as **IBM watsonx** by design — this is set in [src/config.py](src/config.py) (`display_provider_name`).

---

## Project layout

```
streamlit_app.py             # Streamlit entry point
src/
  config.py                  # env-driven settings
  llm/                       # pluggable LLM providers (watsonx, custom, mock)
  agents/                    # the four agents + orchestrator + pydantic schemas
  data/                      # cybersecurity career graph + curated resources
  tools/                     # web_search (DuckDuckGo + fallback)
  ui/                        # Streamlit pages, theme, components, graph view
.env / .env.example          # configuration
requirements.txt
```

---

## Responsible AI

The app is built around the principles in the brief:

- **Personalized** — every output is conditioned on the user profile.
- **Transparent** — recommendations include a rationale; the Audit page shows every agent action.
- **Human-in-the-loop** — decisions surface as trade-offs requiring confirmation.
- **No fabrication** — the retriever only surfaces URLs from a vetted candidate pool; agents never invent role titles outside the curated graph.
- **Privacy** — profile and chat live in the Streamlit session only.

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub.
2. On Streamlit Cloud, point the deployment at `streamlit_app.py`.
3. (Optional) Add your `WATSONX_*` env vars as secrets if you want a real backend; otherwise mock just works.
