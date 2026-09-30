# PocketSmart AI

A complete FastAPI + Jinja2 GenAI budget and recommendation assistant for:
- Home Interior Planning
- Party Budget Planning
- Jewelry Recommendations with optional outfit image analysis

## Architecture

Browser -> FastAPI -> Planner services -> Gemini (optional) -> structured recommendations
                         |-> SQLite history/auth
                         |-> mock catalog fallback

The project follows the uploaded specification's FastAPI routes, modular `routes/services/models` concept, authentication, session information, history, Jinja2 UI, and mock third-party sourcing.

## Important API note

The source document names Gemini 1.5 Flash Pro. The implementation keeps the model configurable through `GEMINI_MODEL` and defaults to a current Gemini Flash model so the code does not hard-code an obsolete model name. Set it to a model available to your API account if needed.

Third-party Amazon/Flipkart/IKEA/Swiggy/Zomato/OYO product data is represented by a local mock catalog. This avoids scraping and lets the project run reliably. Replace `app/services/catalog.py` with licensed/official partner APIs when credentials are available.

## Run

### Windows CMD
```bat
cd PocketSmartAI
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

### PowerShell
```powershell
cd PocketSmartAI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

### Gemini
Open `.env` and set:
`GEMINI_API_KEY=your_key_here`

For local/demo mode, leave it blank. The app automatically uses fallback recommendations. Set `USE_MOCK_DATA=true` to keep catalog links simulated.

## Test

```bash
pytest -q
```

API docs: http://127.0.0.1:8000/docs
Health: http://127.0.0.1:8000/health
