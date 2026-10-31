"""AI Content Strategist.

Calls Gemma (open-weight) through the Gemini API. If there is no API key, the
call fails, or the model returns invalid JSON, a data-driven rule-based fallback
is returned instead (marked source="offline-demo") so the demo never breaks."""
import base64
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import httpx
from pydantic import BaseModel, ValidationError

from app import config
from app.models import (
    Account, AudienceProfile, ChannelStrategy, ContentIdea, IdeasResponse,
    Post, PostInsight, Recommendation,
)

log = logging.getLogger("creator-pulse.ai")
APP_DIR = Path(__file__).resolve().parent.parent
PROMPTS = APP_DIR / "prompts"
THUMBS = APP_DIR / "static" / "thumbs"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
FALLBACK_MODEL = "rule-based fallback"


# ---------------------------------------------------------------- plumbing
def ai_is_live() -> bool:
    return bool(config.GEMINI_API_KEY)


def _prompt(name: str, data: dict, **extra) -> str:
    text = (PROMPTS / f"{name}.txt").read_text(encoding="utf-8")
    for k, v in extra.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text.replace("{{DATA}}", json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _call_gemma(prompt: str, image: Optional[tuple] = None) -> Optional[str]:
    if not config.GEMINI_API_KEY:
        return None
    parts = [{"text": prompt}]
    if image:
        mime, raw = image
        parts.insert(0, {"inline_data": {"mime_type": mime, "data": base64.b64encode(raw).decode()}})
    try:
        r = httpx.post(
            API_URL.format(model=config.GEMMA_MODEL),
            headers={"x-goog-api-key": config.GEMINI_API_KEY, "Content-Type": "application/json"},
            json={"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.7}},
            timeout=90,
        )
        r.raise_for_status()
        out = r.json()["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in out if not p.get("thought"))
    except Exception as e:  # network, quota, bad key, unexpected shape...
        log.warning("Gemma call failed: %s", e)
        return None


def _extract_json(text: str) -> Optional[dict]:
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except ValueError:
        return None


def _run(prompt_name: str, data: dict, model_cls: type[BaseModel], overrides: dict,
         fallback: Callable[[], BaseModel], image: Optional[tuple] = None, **extra) -> BaseModel:
    text = _call_gemma(_prompt(prompt_name, data, **extra), image)
    if text:
        obj = _extract_json(text)
        if obj:
            try:
                return model_cls.model_validate(
                    {**obj, **overrides, "source": "gemma", "model": config.GEMMA_MODEL})
            except ValidationError as e:
                log.warning("Gemma JSON did not match schema: %s", e.errors()[:2])
    return fallback()


def _thumbnail(post: Post) -> Optional[tuple]:
    for ext, mime in (("jpg", "image/jpeg"), ("jpeg", "image/jpeg"), ("png", "image/png"), ("webp", "image/webp")):
        f = THUMBS / f"{post.id}.{ext}"
        if f.exists():
            return mime, f.read_bytes()
    if post.thumbnail_url and post.thumbnail_url.startswith("http") and config.GEMINI_API_KEY:
        try:
            r = httpx.get(post.thumbnail_url, timeout=10)
            if r.status_code == 200:
                return r.headers.get("content-type", "image/jpeg").split(";")[0], r.content
        except httpx.HTTPError:
            pass
    return None


# ---------------------------------------------------------------- data shaping
def _post_data(p: Post) -> dict:
    v30 = max(p.views["30d"], 1)
    return {
        "id": p.id, "title": p.title, "hook": p.hook, "topics": p.topics,
        "duration_sec": p.duration_sec, "views": p.views, "likes": p.likes, "comments": p.comments,
        "follower_gain": p.follower_gain, "engagement_rate_pct": round((p.likes + p.comments) / v30 * 100, 2),
        "age_days": max((datetime.now() - p.published_at).days, 0),
    }


def _account_data(a: Account) -> dict:
    return {
        "name": a.display_name, "platform": a.platform.value, "followers": a.followers,
        "views": a.views, "follower_gain": a.follower_gain, "top_topics": a.top_topics,
        "audience": a.audience.model_dump() if a.audience else None,
    }


def _top(posts: list[Post], n: int) -> list[Post]:
    return sorted(posts, key=lambda p: -p.views["30d"])[:n]


def _fmt(n: int) -> str:
    return f"{n/1_000_000:.1f}M" if n >= 1_000_000 else f"{n/1000:.0f}K" if n >= 1000 else str(n)


# ---------------------------------------------------------------- fallbacks
def _hook_score(p: Post) -> int:
    text = f"{p.title} {p.hook}".lower()
    s = 5
    s += 1 if re.search(r"\d", text) else 0
    s += 1 if "?" in text else 0
    s += 1 if re.search(r"\b(you|your|nobody|never|stop|honest|secret|truth|mistakes?)\b", text) else 0
    s += 1 if len(p.hook.split()) <= 12 else 0
    return min(s, 9)


def _fallback_analyze(post: Post, account: Account, peers: list[Post]) -> PostInsight:
    avg = sum(x.views["30d"] for x in peers) / max(len(peers), 1)
    ratio = post.views["30d"] / avg if avg else 1
    d = post.duration_sec or 0
    pace = (f"{d}s short-form: fast pacing fits {post.platform.value} viewers who decide in the first seconds."
            if d and d <= 90 else
            f"{d // 60} min long-form: needs a strong first 30 seconds and clear chapters to hold attention."
            if d else "Duration unknown.")
    thumb = ("A thumbnail image is available; visual analysis runs when GEMINI_API_KEY is set."
             if _thumbnail(post) else
             f"No thumbnail image provided. Add app/static/thumbs/{post.id}.jpg to enable visual analysis.")
    return PostInsight(
        post_id=post.id, hook_strength=_hook_score(post),
        hook_reason=f"The opening line ({len(post.hook.split())} words) "
                    f"{'uses a number, question or direct address' if _hook_score(post) >= 7 else 'is clear but could be more provocative'}.",
        pacing=pace, thumbnail_notes=thumb,
        trend_fit=f"This post is {'above' if ratio >= 1 else 'below'} the account average by "
                  f"{abs(ratio - 1) * 100:.0f}% (30d views). Topic: {', '.join(post.topics) or 'n/a'}.",
        key_takeaways=[
            f"Engagement rate: {(post.likes + post.comments) / max(post.views['30d'], 1) * 100:.1f}% of viewers liked or commented.",
            f"Reached {_fmt(post.views['7d'])} views in 7 days, {post.views['24h'] / max(post.views['7d'], 1) * 100:.0f}% of that in the last 24h.",
            "Reuse this hook structure on related topics." if ratio >= 1 else "Test a sharper hook and thumbnail for this topic.",
        ],
        source="offline-demo", model=FALLBACK_MODEL,
    )


def _fallback_strategy(account: Account, posts: list[Post]) -> ChannelStrategy:
    a, top = account.audience, _top(posts, 3)
    topics = []
    for p in top:
        topics += p.topics
    topics = list(dict.fromkeys(topics + account.top_topics))
    if a:
        gender = max(a.gender_split, key=a.gender_split.get)
        age = max(a.age_buckets, key=a.age_buckets.get)
        country = a.top_countries[0].country if a.top_countries else "unknown"
        under25 = a.age_buckets.get("13-17", 0) + a.age_buckets.get("18-24", 0)
        segment = f"{gender.capitalize()}s {age}, mostly {country}"
        traits = [f"{a.gender_split[gender]:.0f}% {gender}", f"{under25:.0f}% are under 25",
                  f"{a.top_countries[0].pct:.0f}% from {country}" if a.top_countries else "Location unknown"]
    else:
        segment, traits = "Demographics unavailable (needs owner OAuth)", ["Advice based on content performance only"]
    fmt = {"youtube": "Long-form video", "instagram": "Reel", "facebook": "Video + poll"}[account.platform.value]
    recs = [Recommendation(
        format=fmt, topic=t, hook=f"{p.hook}",
        why=f"'{p.title}' reached {_fmt(p.views['30d'])} views; extend this proven topic.")
        for t, p in zip(topics, top)][:3]
    return ChannelStrategy(
        account_id=account.id,
        audience_profile=AudienceProfile(primary_segment=segment, key_traits=traits, inferred_interests=topics[:5]),
        what_worked=[f"'{p.title}' led with a {len(p.hook.split())}-word hook and got {_fmt(p.views['30d'])} views." for p in top[:3]],
        recommendations=recs,
        posting_advice={"youtube": "Publish 1-2 long videos a week, test titles that contain a number, and cut Shorts from each video.",
                        "instagram": "Post 4-5 Reels a week at your audience's evening hours and reuse the best hook styles.",
                        "facebook": "Post video natively 3-4 times a week and end with a poll to drive comments."}[account.platform.value],
        conclusion=f"Double down on {', '.join(topics[:2]) or 'your top topics'} for {segment}. "
                   f"Your best post ({_fmt(top[0].views['30d'])} views) shows the winning formula: short, direct hooks on proven topics."
                   if top else "Not enough posts to analyse yet.",
        source="offline-demo", model=FALLBACK_MODEL,
    )


IDEA_TEMPLATES = [
    ("{T}: what I got wrong (and the fix)", "I was wrong about {t} for years. Here is what changed my mind.",
     ["The common mistake", "What the data actually shows", "A simple fix you can try today"]),
    ("{T} in 60 seconds", "You can learn this {t} trick before your chai gets cold.",
     ["The one-sentence summary", "A quick demo", "Where to go next"]),
    ("Reacting to my most-viewed video on {t}", "This video blew up and I finally understand why.",
     ["Show the original clip", "What worked and why", "What I would change now"]),
    ("{T} challenge: 7 days, real numbers", "I will show every number for 7 days. No fake results.",
     ["Day-by-day log", "The surprising result", "Your turn: copy the challenge"]),
    ("The {t} myths your audience still believes", "Stop believing these {t} myths.",
     ["Myth one and the evidence", "Myth two and the evidence", "What to do instead"]),
]


def _fallback_ideas(scope: str, posts: list[Post], count: int) -> IdeasResponse:
    top, ideas = _top(posts, 5), []
    for i in range(count):
        p = top[i % len(top)]
        topic = (p.topics or ["your niche"])[0]
        title, hook, outline = IDEA_TEMPLATES[i % len(IDEA_TEMPLATES)]
        ideas.append(ContentIdea(
            title=title.format(T=topic.capitalize(), t=topic), hook=hook.format(t=topic), outline=outline,
            why_it_should_work=f"Builds on '{p.title}', a top performer with {_fmt(p.views['30d'])} views."))
    return IdeasResponse(scope=scope, ideas=ideas, source="offline-demo", model=FALLBACK_MODEL)


# ---------------------------------------------------------------- public API
def analyze_post(post: Post, account: Account, peers: list[Post]) -> PostInsight:
    avg = sum(p.views["30d"] for p in peers) / max(len(peers), 1)
    data = {"account": _account_data(account), "post": _post_data(post), "peer_average_views_30d": int(avg)}
    return _run("analyze", data, PostInsight, {"post_id": post.id},
                lambda: _fallback_analyze(post, account, peers), image=_thumbnail(post))


def channel_strategy(account: Account, posts: list[Post]) -> ChannelStrategy:
    data = {"account": _account_data(account), "top_posts": [_post_data(p) for p in _top(posts, 5)]}
    return _run("strategy", data, ChannelStrategy, {"account_id": account.id},
                lambda: _fallback_strategy(account, posts))


def generate_ideas(scope: str, accounts: list[Account], posts: list[Post], count: int) -> IdeasResponse:
    data = {"scope": scope, "accounts": [_account_data(a) for a in accounts],
            "top_posts": [_post_data(p) for p in _top(posts, 6)]}
    return _run("ideas", data, IdeasResponse, {"scope": scope},
                lambda: _fallback_ideas(scope, posts, count), COUNT=count)
