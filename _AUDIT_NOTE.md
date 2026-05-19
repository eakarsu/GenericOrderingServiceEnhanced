# Audit Note — GenericOrderingServiceEnhanced

## Bucket
**HAS_CODE_NO_NODE_BACKEND (Python FastAPI project)** — NO CODE CHANGES.

## Why no scaffold
The playbook scaffolds **Node/Express** backends. This project already has a
Python FastAPI backend (`backend/app/`) and reuses the LangChain-based LLM
integration from its sibling `GenericOrderingService`. Adding a parallel Node
backend would duplicate the API surface.

## Initial state
- Source files (.js/.ts/.tsx/.jsx/.py): 55
- LLM-reference scan hits (legitimate, not detector false positives):
  - `updated_universal_service_bot.py`
  - `updated_universal_service_bot_error_handling.py`
  - `test_updated_universal_service_bot.py`
- Layout:
  - `backend/app/` — FastAPI app with `main.py`, `config.py`, `database.py`,
    `models.py`, `schemas.py`, `auth_utils.py`, `seed.py`,
    `routers/auth.py`, `routers/users.py`, `middleware/`
  - Python AI bots at the project root (enhanced versions of the
    `GenericOrderingService` originals): `updated_universal_service_bot.py`,
    `updated_universal_service_bot_enhanced.py`,
    `updated_universal_service_bot_error_handling.py`,
    `comprehensiveAnalytics.py`, `crossSectorIntelligence.py`,
    `deepAnalyticsIntegration.py`, `menuIndexerIntentCalcEnhanced.py`,
    `orderProcessorEnhanced.py`
  - `sectors/`, `prompts/`, `frontend/` (React, out of scope)
  - `Dockerfile`, `requirements.txt`, `start.sh`
- Real-domain name: yes (Generic Ordering Service across verticals, enhanced).

## Audit-report context (revised 2026-05-06)
`/_AUDIT/reports/batch_10.md` §8 calls this SKELETON with "Routes: 0, AI: 0".
That is **inaccurate** — there is a FastAPI backend with **six** wired
routers (`auth`, `users`, `sectors`, `items`, `orders`, `export`) plus
middleware (rate limit, security headers, input sanitisation, global error
handler), and Python LLM integration.

## False-positive note (LLM scan)
The three .py hits are genuine LLM usages, **not** detector false positives.

## State as of this batch

- `backend/app/main.py` mounts: `auth.router`, `users.router`,
  `sectors.router`, `items.router`, `orders.router`, `export.router`.
- Middleware: `GlobalErrorHandlerMiddleware`, `RateLimitMiddleware`
  (200 req / 60 s), `SecurityHeadersMiddleware`, `InputSanitizationMiddleware`,
  CORS.
- Health (`/api/health`) and stats (`/api/stats`) endpoints already present.
- Frontend build is mounted at `/` when present.

## Remaining genuine gaps

- **AI features are not wired into FastAPI.** All LLM logic lives in
  standalone scripts at the repo root (`updated_universal_service_bot*.py`,
  `orderProcessorEnhanced.py`, `comprehensiveAnalytics.py`,
  `crossSectorIntelligence.py`, `deepAnalyticsIntegration.py`,
  `menuIndexerIntentCalcEnhanced.py`). None of them is imported by
  `backend/app/`. There is no `routers/ai.py` and no `services/ai_service.py`.
- No FastAPI surface tests.
- No analytics router (the `*Analytics.py` scripts are not exposed).

## Audit recommendations applied this batch

**None.** Bridging the standalone AI scripts into FastAPI is the highest-
impact next move, but it requires:

1. Picking a stable LLM-call abstraction (LangChain `ChatOpenAI` vs direct
   OpenRouter — sibling repos in this batch use direct OpenRouter; mixing
   would create two competing patterns). NEEDS-PRODUCT-DECISION.
2. Refactoring the script-style code into thread-safe callables suitable
   for FastAPI request lifecycles. TOO-RISKY for an apply batch given the
   existing scripts share global state.
3. Schema work to persist analytics outputs.

This batch's mandate is mechanical wins on existing AI surfaces; this
project needs a foundational refactor first.

## Backlog (deferred, prioritised)

1. **Bridge AI scripts into FastAPI** — TOP priority. Concrete first step:
   `backend/app/services/ai_service.py` that wraps the most-used helper
   (`updated_universal_service_bot_enhanced.py`) behind a clean async
   function. Then add `backend/app/routers/ai.py` with endpoints for
   order-chat, menu-indexing, and analytics queries.
2. **Add an analytics router** that exposes `comprehensiveAnalytics.py`
   + `crossSectorIntelligence.py` + `deepAnalyticsIntegration.py` as
   GET endpoints under `/api/analytics/*`. NEEDS-PRODUCT-DECISION on
   caching/refresh cadence.
3. **Standardise on direct OpenRouter** — replace LangChain `ChatOpenAI`
   with a thin `httpx`-based client matching `investment/`, `librelane/`,
   `makepdf/`, `pos/` patterns. Reduces dependency surface.
4. **Add tests for FastAPI routers** — none exist; pytest + httpx async
   client is straightforward.
5. **Persist AI calls** — add an `ai_results` table (mirrors what
   `investment/` and `makepdf/` do) so token-usage/error rates can be
   tracked.

## Files touched this batch
None.

## Apply pass 3 (frontend)

**Action: SKIPPED-NO-DOMAIN.** No backend AI HTTP endpoints exist for the frontend to wire.

The FastAPI backend (`backend/app/`) mounts `auth`, `users`, `sectors`, `items`, `orders`, `export` — no `routers/ai.py`. All LLM logic lives in standalone Python scripts at the repo root (`updated_universal_service_bot*.py`, `*Analytics.py`, `orderProcessorEnhanced.py`, `menuIndexerIntentCalcEnhanced.py`) which are **not** imported by the FastAPI app.

This batch's mandate is to wire frontends to existing backend AI endpoints. Adding a frontend page before the backend exposes a stable AI surface would create dead UI. The correct sequencing is the existing backlog item: introduce `backend/app/services/ai_service.py` + `backend/app/routers/ai.py` first (NEEDS-PRODUCT-DECISION on LLM-call abstraction; TOO-RISKY because the standalone scripts share global state and need refactoring), then add frontend.

No code changes this pass. See `_AUDIT/apply3_logs/ab3_62.md`.

## Apply pass 3 (Group B — FastAPI bootstrap)

**Action: BOOTSTRAPPED.** Bridged the standalone AI scripts into FastAPI as
thin wrappers and added a minimal HTML/JS dev console. The previously
deferred backlog item #1 ("Bridge AI scripts into FastAPI") is now done as
a thin pass; deeper refactoring remains future work.

### Backend changes

- Added `backend/app/routers/ai.py` — a new router mounted at `/api/ai/*`.
  The router does **not** rewrite any LLM logic. It lazily imports
  `updated_universal_service_bot.UniversalServiceBot` from the repo
  root (`sys.path.insert`) on first request and caches the instance.
- Mounted in `backend/app/main.py` via
  `app.include_router(ai.router)`.
- Each endpoint returns `503 {"error": "AI not configured"}` if
  `OPENROUTER_API_KEY` is unset, and a `503` with a structured
  `reason` if a heavy dep (chromadb, langchain, fuzzywuzzy, ...) is
  missing — surfacing the missing-module name to the operator.
- CORS was already set to `allow_origins=["*"]`; no change needed.

### Endpoints exposed

| Method | Path                       | Wraps                                        |
| ------ | -------------------------- | -------------------------------------------- |
| GET    | `/api/ai/health`           | (cheap; no bot init)                         |
| GET    | `/api/ai/sectors`          | filesystem listing of `sectors/`             |
| POST   | `/api/ai/chat`             | `UniversalServiceBot.chatAway2` (stateless)  |
| POST   | `/api/ai/conversation`     | `UniversalServiceBot.process_conversation`   |
| POST   | `/api/ai/detect-sector`    | `UniversalServiceBot.detect_sector_with_ai`  |
| POST   | `/api/ai/order`            | `SectorSpecificProcessor.process_order`      |

`chatAway2` was deliberately chosen over `chatAway` because the former
is stateless and HTTP-safe; the latter mutates per-bot `self.state` and
would cause cross-request bleed since the bot is process-singleton.

### Frontend

- Added `backend/app/static/index.html` — vanilla JS forms for all four
  POST endpoints plus a header status badge wired to `/api/ai/health`
  and a sector-list dropdown wired to `/api/ai/sectors`.
- The existing React SPA at `frontend/dist/` continues to be served at
  `/`. The new minimal AI console is exposed at **`/ai-console`** (and
  also at `/` if the React build is missing). This avoids touching
  the existing React frontend convention.

### Files written / modified

- `backend/app/routers/ai.py` (new, 232 lines)
- `backend/app/static/index.html` (new, 213 lines)
- `backend/app/main.py` (modified — import + include_router + minimal
  static mount + `/ai-console` route)
- `requirements.txt` (modified — added a header comment documenting the
  AI-deps situation; no new packages added since langchain-openai,
  langchain-core, chromadb, fuzzywuzzy, python-levenshtein are all
  already listed)

### py_compile results

- `backend/app/routers/ai.py` — **OK**
- `backend/app/main.py` — **OK**

### Blockers / caveats

- No `pip install` was run.
- The wrapper assumes the chromadb database at
  `<repo>/universal_chroma_database` has been indexed. Bot
  construction will raise `RuntimeError("Universal database not
  healthy")` if not — surfaced to the client as a `503` with
  `reason`. Indexing is out of scope for a bootstrap pass.
- The bot uses a process-singleton with mutable `self.state` for
  `chatAway`. We use the stateless `chatAway2` to avoid cross-request
  bleed; `/api/ai/conversation` accepts a full message list per call
  and is therefore safe.
- Heavy deps (chromadb, langchain) are imported lazily on first AI
  request, not at FastAPI startup, so the rest of the API works even
  if AI deps are missing.

### Launch instructions

```bash
cd /Users/erolakarsu/projects/GenericOrderingServiceEnhanced
pip install -r requirements.txt -r backend/requirements.txt
export OPENROUTER_API_KEY=sk-...   # 503 without this
uvicorn backend.app.main:app --reload --port 8000
# open http://localhost:8000/ai-console
```
