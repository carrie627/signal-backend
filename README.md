# Signal backend — lead scoring API

FastAPI service that receives a lead from Zap 1, semantically matches it to
a service catalog, scores and classifies it, then writes to Google Sheets
and fires the correct Zapier webhook for Zap 2 — all in the background so
Zap 1 gets a fast response.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in the values below
```

### Required for a minimal working demo
- `WEBHOOK_SECRET` — any long random string, must match what Zap 1 sends

### Optional (degrade gracefully if left blank)
- `GROQ_API_KEY` — without it, summaries fall back to a truncated message
- `GOOGLE_SERVICE_ACCOUNT_FILE` / `GOOGLE_SHEET_ID` — without these, the
  Sheets write fails silently (logged, doesn't crash the request)
- `ZAPIER_HOT_WEBHOOK_URL` / `ZAPIER_DEFAULT_WEBHOOK_URL` — without these,
  the outbound notification step is skipped

## Google Sheets setup (5 minutes)

1. Google Cloud Console → create a project → enable the Google Sheets API
2. Create a service account, download its JSON key, save as
   `service-account.json` in this folder (already gitignored)
3. Share your target Google Sheet with the service account's email
   (found in the JSON file, ends in `@...iam.gserviceaccount.com`)
4. Copy the sheet ID from its URL into `GOOGLE_SHEET_ID`

## Run it

```bash
uvicorn app.main:app --reload --port 8000
```

Test the health check: `curl http://localhost:8000/health`

Test the webhook:

```bash
curl -X POST http://localhost:8000/webhook/lead \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: <your WEBHOOK_SECRET>" \
  -d '{
    "name": "Priya Chandrasekaran",
    "email": "priya@example.com",
    "company": "Northbeam Retail Co.",
    "message": "We need a full site rebuild before Q4, current one converts terribly on mobile."
  }'
```

## Wiring into Zapier

- **Zap 1**: trigger on new form submission → action "Webhooks by Zapier:
  POST" to `https://<your-deployed-url>/webhook/lead`, with the
  `X-Webhook-Secret` header set and the form fields mapped to `name`,
  `email`, `company`, `message`.
- **Zap 2 (hot path)**: trigger "Webhooks by Zapier: Catch Hook" using the
  URL you put in `ZAPIER_HOT_WEBHOOK_URL` → action: Slack message.
- **Zap 2 (default path)**: same pattern with `ZAPIER_DEFAULT_WEBHOOK_URL`
  → action: whatever else you want for warm/cold leads (e.g. add to a
  nurture list).
- **Zap 3**: scheduled trigger reading the Google Sheet directly — it
  doesn't need this backend at all, since the sheet is already the source
  of truth.

## Deploying free

Render or Railway free tier both work. Two things to set on either:
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Upload `service-account.json` as a secret file, or paste its contents
  into an env var and adjust `sheets_service.py` to read from that instead
  of a file path if the platform doesn't support file uploads on the free
  tier.

Cold starts on free tiers can take 10-30s after idle — worth mentioning to
the client so a first request after inactivity isn't mistaken for a bug.
