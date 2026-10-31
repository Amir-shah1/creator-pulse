import hashlib
import html
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import config
from app.models import (
    Account, AddAccountRequest, AnalyzeRequest, ChannelStrategy, IdeasRequest,
    IdeasResponse, LeaderboardResponse, Post, PostInsight, StrategyRequest,
)
from app.services import ai_strategist as ai
from app.services.aggregator import build_leaderboard
from app.store import store

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Creator Pulse", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ------------------------------------------------------------------ pages
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {
        "demo_mode": config.DEMO_MODE,
        "ai_live": ai.ai_is_live(),
        "model": config.GEMMA_MODEL,
    })


@app.get("/health")
def health():
    return {"status": "ok", "demo_mode": config.DEMO_MODE, "ai_live": ai.ai_is_live(),
            "model": config.GEMMA_MODEL}


# ------------------------------------------------------------------ leaderboard & accounts
@app.get("/api/leaderboard", response_model=LeaderboardResponse)
def leaderboard(
    platform: Literal["all", "youtube", "instagram", "facebook"] = Query("all"),
    window: Literal["24h", "36h", "7d", "30d"] = Query("7d"),
    metric: Literal["views", "conversions"] = Query("views"),
):
    return build_leaderboard(platform, window, metric)


@app.get("/api/accounts", response_model=list[Account])
def list_accounts():
    return store.list_accounts()


@app.post("/api/accounts", response_model=Account, status_code=201)
def add_account(body: AddAccountRequest):
    try:
        return store.add(body.platform, body.handle)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _account_or_404(account_id: str) -> Account:
    acc = store.get(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc


@app.get("/api/accounts/{account_id}", response_model=Account)
def get_account(account_id: str):
    return _account_or_404(account_id)


@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: str):
    _account_or_404(account_id)
    store.remove(account_id)
    return {"deleted": account_id}


@app.get("/api/accounts/{account_id}/posts", response_model=list[Post])
def account_posts(account_id: str, window: Literal["24h", "36h", "7d", "30d"] = "30d"):
    _account_or_404(account_id)
    return sorted(store.posts_for(account_id), key=lambda p: -p.views[window])


# ------------------------------------------------------------------ thumbnails
@app.get("/api/thumb/{post_id}")
def thumbnail(post_id: str):
    """Real image from app/static/thumbs/<post_id>.(jpg|png|webp) if present,
    otherwise a generated SVG placeholder."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        f = BASE_DIR / "static" / "thumbs" / f"{post_id}.{ext}"
        if f.exists():
            return FileResponse(f)
    post = store.find_post(post_id)
    title = post.title if post else post_id
    h = int(hashlib.md5(post_id.encode()).hexdigest(), 16)
    h1, h2 = h % 360, (h // 360 + 40) % 360
    words, lines, line = title.split(), [], ""
    for w in words:
        if len(line) + len(w) > 22:
            lines.append(line)
            line = ""
        line += (" " if line else "") + w
    lines.append(line)
    text = "".join(
        f'<tspan x="16" dy="{0 if i == 0 else 22}">{html.escape(l)}</tspan>' for i, l in enumerate(lines[:3]))
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="hsl({h1},55%,32%)"/><stop offset="1" stop-color="hsl({h2},60%,18%)"/>'
        '</linearGradient></defs><rect width="320" height="180" fill="url(#g)"/>'
        f'<text x="16" y="96" fill="#fff" font-family="system-ui,sans-serif" font-size="18" font-weight="600">{text}</text>'
        '</svg>'
    )
    return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "max-age=3600"})


# ------------------------------------------------------------------ AI (Gemma)
@app.post("/api/ai/analyze", response_model=PostInsight)
def ai_analyze(body: AnalyzeRequest):
    post = store.find_post(body.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return ai.analyze_post(post, _account_or_404(post.account_id), store.posts_for(post.account_id))


@app.post("/api/ai/channel-strategy", response_model=ChannelStrategy)
def ai_strategy(body: StrategyRequest):
    acc = _account_or_404(body.account_id)
    return ai.channel_strategy(acc, store.posts_for(acc.id))


@app.post("/api/ai/ideas", response_model=IdeasResponse)
def ai_ideas(body: IdeasRequest):
    if body.account_id:
        acc = _account_or_404(body.account_id)
        accounts, posts, scope = [acc], store.posts_for(acc.id), acc.display_name
    else:
        accounts, posts, scope = store.list_accounts(), store.all_posts(), "All accounts"
    if not posts:
        raise HTTPException(status_code=400, detail="Add at least one account first")
    return ai.generate_ideas(scope, accounts, posts, body.count)
