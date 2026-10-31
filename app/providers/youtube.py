"""Real YouTube provider (YouTube Data API v3, API key only).
Public API limits: no audience demographics (needs owner OAuth) and no 24h/7d view
windows (needs periodic snapshots). Windows are therefore ESTIMATED from totals and
audience is left empty. Used only when DEMO_MODE=false and YOUTUBE_API_KEY is set."""
import re
from datetime import datetime

import httpx

from app import config
from app.models import Account, Post

BASE = "https://www.googleapis.com/youtube/v3"


class ProviderError(Exception):
    pass


def _get(path: str, params: dict) -> dict:
    try:
        r = httpx.get(f"{BASE}/{path}", params={**params, "key": config.YOUTUBE_API_KEY}, timeout=15)
    except httpx.HTTPError as e:
        raise ProviderError(f"Network error talking to YouTube: {e}")
    if r.status_code != 200:
        try:
            msg = r.json().get("error", {}).get("message", "")
        except ValueError:
            msg = r.text[:120]
        raise ProviderError(f"YouTube API error {r.status_code}: {msg}")
    return r.json()


def _duration(iso: str) -> int:
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def _estimate(total: int) -> dict:
    return {"24h": int(total * 0.07), "36h": int(total * 0.1), "7d": int(total * 0.4), "30d": total}


def fetch_channel(key: str, taken_ids: set) -> tuple[Account, list[Post]]:
    data = _get("channels", {"part": "snippet,statistics,contentDetails", "forHandle": "@" + key})
    items = data.get("items") or []
    if not items:
        raise ProviderError(f"No YouTube channel found for @{key}")
    ch = items[0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = _get("playlistItems", {"part": "contentDetails", "playlistId": uploads, "maxResults": 6})
    ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
    vids = _get("videos", {"part": "snippet,statistics,contentDetails", "id": ",".join(ids)})["items"] if ids else []

    acc_id, n = f"yt_{re.sub(r'[^a-z0-9]+', '_', key.lower())}", 2
    base = acc_id
    while acc_id in taken_ids:
        acc_id, n = f"{base}_{n}", n + 1

    posts = []
    for v in vids:
        st, sn = v.get("statistics", {}), v["snippet"]
        total = int(st.get("viewCount", 0))
        desc_line = (sn.get("description") or sn["title"]).strip().splitlines()[0][:140] if (sn.get("description") or sn["title"]).strip() else sn["title"]
        posts.append(Post(
            id=f"{acc_id}_{v['id']}", account_id=acc_id, platform="youtube", title=sn["title"],
            hook=desc_line, topics=(sn.get("tags") or [])[:3],
            published_at=datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00")).replace(tzinfo=None),
            duration_sec=_duration(v.get("contentDetails", {}).get("duration", "")),
            thumbnail_url=(sn.get("thumbnails", {}).get("high") or {}).get("url"),
            views=_estimate(total), likes=int(st.get("likeCount", 0)),
            comments=int(st.get("commentCount", 0)), follower_gain=0,
        ))
    views = {w: sum(p.views[w] for p in posts) for w in ("24h", "36h", "7d", "30d")}
    return Account(
        id=acc_id, platform="youtube", handle="@" + key,
        display_name=ch["snippet"]["title"],
        followers=int(ch["statistics"].get("subscriberCount", 0)),
        views=views, prev_views=dict(views),
        follower_gain={"24h": 0, "36h": 0, "7d": 0, "30d": 0},
        top_topics=list({t for p in posts for t in p.topics})[:4],
        audience=None, data_source="youtube_api",
    ), posts
