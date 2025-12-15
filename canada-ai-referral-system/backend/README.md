# Canada AI Referral System (backend)

This folder contains a FastAPI skeleton and agent placeholders for a Canada-specific referral prioritisation system.

Run locally:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Replace agent placeholders with production-grade NLP, rules, and models.

## OpenAI integration (optional)

To enable optional LLM-based parsing, set the `OPENAI_API_KEY` environment variable before starting the backend and install the `openai` package (already listed in `requirements.txt`). Example (Windows PowerShell):

```powershell
$Env:OPENAI_API_KEY = "sk-..."
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

When the API key is present the Referral Parsing Agent will call the LLM to extract structured JSON. If no key is set the system falls back to a conservative local heuristic so the service remains testable offline.
