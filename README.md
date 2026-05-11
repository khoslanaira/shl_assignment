# SHL Assessment Recommender

Conversational FastAPI service that recommends SHL assessments from the official SHL product catalog. It supports clarifying vague requests, refusing off-topic questions, recommending catalog-grounded assessments, comparing assessment options, and falling back to deterministic retrieval if the LLM is unavailable.

## Tech Stack

- FastAPI
- Google GenAI SDK
- Python 3.12
- Official SHL catalog data normalized into `data/catalog.json`

## Setup

```powershell
python -m venv .venv312
.\.venv312\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a root-level `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

## Run Locally

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## API

```text
GET /health
POST /chat
```

Example `/chat` body:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "I am hiring a Java developer"
    }
  ]
}
```

## Evaluation

```powershell
python -m pytest -q
python evaluation/evaluate.py
```

The evaluator measures recall, precision, groundedness, and behavior accuracy across representative recommendation, clarification, refusal, and comparison cases.

## Deployment

The repo includes `render.yaml`.

Render settings:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set `GEMINI_API_KEY` in Render environment variables.
