# Creator Pulse

**An AI-powered creator analytics leaderboard.** Add multiple YouTube, Instagram and Facebook accounts, see them ranked in one F1-style view, and let an open-weight model (**Gemma 4**) explain *why* top content worked, who the audience is, and what to create next.

Built at the MLH Hacktoberfest hackathon, National Incubation Center (NIC) Islamabad.
Tracks: **DigitalOcean: Best Open-Source AI Project** and **Google: Best Use of Gemma 4**.

## Features

- Unified leaderboard across YouTube, Instagram and Facebook, with **multiple accounts per platform** (add/remove live)
- Rank by **views** or **follower gain** over **24h / 36h / 7d / 30d**, with rank-change arrows
- Platform tabs: All, YouTube, Instagram, Facebook
- **AI Content Strategist (Gemma):** per-channel audience profile (age, gender, country, AI-inferred interests), what worked, what to create next, and a conclusion
- **Post analysis:** hook strength, pacing, thumbnail (image) analysis, trend fit
- **Idea generator:** hooks and outlines based on a channel's own top history
- Works fully offline from the AI: without a key it uses a rule-based fallback, clearly labelled in the UI

## Run it (2 minutes)

Requires Python 3.10+.

```bash
cd creator-pulse
python -m venv .venv
# macOS/Linux:           source .venv/bin/activate
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000**. Check **http://127.0.0.1:8000/health** (`"ai_live": true` means Gemma is connected) and **/docs** for the interactive API.

## Where to put keys and photos

| What | Where | Needed? |
|---|---|---|
| `GEMINI_API_KEY` | `.env` in the project root. Get it free at https://aistudio.google.com/apikey | Optional. Without it the app uses the offline fallback; **with it you get real Gemma output (needed for the Gemma track)** |
| `GEMMA_MODEL` | `.env` (default `gemma-4-26b-a4b-it`; stronger: `gemma-4-31b-it`) | Optional |
| `YOUTUBE_API_KEY` | `.env`. Google Cloud Console, enable "YouTube Data API v3", create an API key | Only for `DEMO_MODE=false` (live YouTube accounts) |
| Thumbnail photos | `app/static/thumbs/<post_id>.jpg` (see `docs/THUMBNAILS.md` for ids) | Optional. Placeholders are generated automatically; real images enable Gemma's image analysis |

Never commit `.env`.

## How the AI works

1. The backend builds a compact JSON of real numbers (audience, top posts, views, engagement, hooks).
2. A prompt from `app/prompts/` tells Gemma to use **only** that data and return strict JSON.
3. The reply is parsed and validated with Pydantic. If the key is missing, the call fails, or the JSON is invalid, a data-driven fallback answers instead (`source: "offline-demo"`), so the demo never breaks.
4. Interests are **inferred** by the AI. No platform API provides them, and the UI labels them that way.

## Demo data vs real data

The demo runs on seeded and generated dummy data. Production path:

| Need | Real API |
|---|---|
| Public stats, video lists | YouTube Data API v3 (implemented behind `DEMO_MODE=false`) |
| Audience demographics (YouTube) | YouTube Analytics API (owner OAuth) |
| Posts and insights (Instagram) | Instagram Graph API (business/creator account) |
| Page posts and insights (Facebook) | Facebook Graph API (Pages) |

Notes: live YouTube mode estimates the 24h/7d windows from totals (production would store periodic snapshots) and has no demographics without OAuth. Instagram and Facebook need Meta app review, so they stay demo data. The live YouTube path could not be tested against Google's servers during development; try it with your key before relying on it.

## API

| Endpoint | Description |
|---|---|
| `GET /api/leaderboard?platform=&window=&metric=` | Ranked accounts with `rank_change` and top post |
| `GET /api/accounts` / `POST /api/accounts` / `DELETE /api/accounts/{id}` | List, add (`{"platform","handle"}`), remove |
| `GET /api/accounts/{id}` / `GET /api/accounts/{id}/posts` | Account with audience; its posts |
| `GET /api/thumb/{post_id}` | Real thumbnail if present, else generated SVG |
| `POST /api/ai/channel-strategy` `{"account_id"}` | Audience profile, recommendations, conclusion |
| `POST /api/ai/analyze` `{"post_id"}` | Why a post worked |
| `POST /api/ai/ideas` `{"account_id"?, "count"}` | Content ideas (all accounts if no id) |

## Project structure

```
app/
  main.py                 routes
  config.py               env settings
  models.py               Pydantic models (Account, Post, AI outputs)
  store.py                in-memory accounts (add/remove)
  providers/              demo.py (seed + generator), youtube.py (live)
  services/               aggregator.py (ranking), ai_strategist.py (Gemma)
  prompts/                analyze / strategy / ideas prompt templates
  templates/, static/     dark SaaS-style UI (vanilla JS, no build step)
data/demo_data.json       seeded creators (regenerate: python scripts/generate_demo_data.py)
tests/                    pytest suite
docs/                     GitHub, DigitalOcean, thumbnails, demo script
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Deploy

See `docs/DEPLOY_DIGITALOCEAN.md` (Dockerfile included) and `docs/DEMO_SCRIPT.md`.

## Team

| Name | Role | GitHub |
|---|---|---|
| Amir | TBD | @username |
| Ibrahim | TBD | @username |
| Member 3 | TBD | @username |

Workflow: one branch per task (`feature/<name>`), Pull Request, one review, merge. Keep `main` runnable. See `docs/GITHUB_SETUP.md`.

## License

MIT. See [LICENSE](LICENSE).
