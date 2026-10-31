"""Seeded + generated dummy data. Real providers (youtube.py) return the same
Account/Post models, so the rest of the app never changes."""
import json
import random
import re
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Optional

from app.models import Account, Audience, CountryShare, Post

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "demo_data.json"
PREFIX = {"youtube": "yt", "instagram": "ig", "facebook": "fb"}
NICHES = ["tech reviews", "fitness", "street food", "travel", "personal finance",
          "gaming", "fashion", "study tips"]
TITLE_PATTERNS = [
    "{N}: 5 mistakes beginners make",
    "I tried {n} for 30 days, here is what happened",
    "The truth about {n} nobody tells you",
    "{N} on a budget: the full guide",
    "Why most people fail at {n}",
]
HOOK_PATTERNS = [
    "Stop scrolling, this changes how you think about {n}.",
    "I did this for 30 days so you do not have to.",
    "Nobody talks about this part of {n}.",
    "Be honest, are you making this {n} mistake?",
    "Here is the number that surprised me most.",
]
COUNTRIES = ["Pakistan", "UAE", "UK", "USA", "Saudi Arabia", "Canada", "Germany", "India"]
AGE_LABELS = ["13-17", "18-24", "25-34", "35-44", "45+"]
DURATION = {"youtube": (240, 900), "instagram": (15, 60), "facebook": (60, 300)}


@lru_cache
def _raw() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def load_accounts() -> list[Account]:
    return [Account(**a) for a in _raw()["accounts"]]


def load_posts(account_id: Optional[str] = None) -> list[Post]:
    posts = [Post(**p) for p in _raw()["posts"]]
    return [p for p in posts if account_id is None or p.account_id == account_id]


def _windows(rng: random.Random, v30: int) -> dict:
    v7 = int(v30 * rng.uniform(0.3, 0.6))
    v36 = int(v7 * rng.uniform(0.2, 0.35))
    v24 = int(v36 * rng.uniform(0.6, 0.8))
    return {"24h": v24, "36h": v36, "7d": v7, "30d": int(v30)}


def _split(rng: random.Random, n: int) -> list[int]:
    weights = [rng.random() + 0.2 for _ in range(n)]
    vals = [int(w / sum(weights) * 100) for w in weights]
    vals[0] += 100 - sum(vals)
    return vals


def generate_account(platform: str, key: str, taken_ids: set) -> tuple[Account, list[Post]]:
    """Deterministic dummy account for any handle (same handle -> same data)."""
    rng = random.Random(f"{platform}:{key}")
    niche = rng.choice(NICHES)
    base_id = f"{PREFIX[platform]}_{re.sub(r'[^a-z0-9]+', '_', key)}"
    acc_id, n = base_id, 2
    while acc_id in taken_ids:
        acc_id, n = f"{base_id}_{n}", n + 1

    followers = int(rng.uniform(15000, 650000))
    posts: list[Post] = []
    for i in range(1, 6):
        v = _windows(rng, int(followers * rng.uniform(0.15, 2.2)))
        lo, hi = DURATION[platform]
        posts.append(Post(
            id=f"{acc_id}_p{i}", account_id=acc_id, platform=platform,
            title=rng.choice(TITLE_PATTERNS).format(N=niche.capitalize(), n=niche),
            hook=rng.choice(HOOK_PATTERNS).format(n=niche),
            topics=[niche, rng.choice([x for x in NICHES if x != niche])][: rng.randint(1, 2)],
            published_at=datetime.now() - timedelta(days=rng.randint(1, 25)),
            duration_sec=rng.randint(lo, hi), views=v,
            likes=int(v["30d"] * rng.uniform(0.03, 0.09)),
            comments=int(v["30d"] * rng.uniform(0.002, 0.012)),
            follower_gain=int(v["30d"] * rng.uniform(0.002, 0.01)),
        ))

    views = {w: int(sum(p.views[w] for p in posts) * 1.4) for w in ("24h", "36h", "7d", "30d")}
    fg30 = int(sum(p.follower_gain for p in posts) * 1.3)
    fg7 = int(fg30 * 0.3)
    fg36 = int(fg7 * 0.25)
    male = rng.randint(20, 80)
    countries = rng.sample(COUNTRIES[1:], 3)
    country_pcts = sorted(_split(rng, 4), reverse=True)
    account = Account(
        id=acc_id, platform=platform,
        handle=key if platform == "facebook" else f"@{key}",
        display_name=re.sub(r"[._\-]+", " ", key).title(),
        followers=followers, views=views,
        prev_views={w: int(v * rng.uniform(0.7, 1.3)) for w, v in views.items()},
        follower_gain={"24h": int(fg36 * 0.7), "36h": fg36, "7d": fg7, "30d": fg30},
        top_topics=posts[0].topics[:1] + [t for p in posts[1:3] for t in p.topics[:1]],
        audience=Audience(
            gender_split={"male": male, "female": 98 - male, "other": 2},
            age_buckets=dict(zip(AGE_LABELS, _split(rng, 5))),
            top_countries=[CountryShare(country=c, pct=p)
                           for c, p in zip(["Pakistan"] + countries, country_pcts)],
        ),
    )
    return account, posts
