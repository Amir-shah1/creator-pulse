from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# Time windows used by the leaderboard
WINDOWS = ("24h", "36h", "7d", "30d")


class Platform(str, Enum):
    youtube = "youtube"
    instagram = "instagram"
    facebook = "facebook"


class CountryShare(BaseModel):
    country: str
    pct: float


class Audience(BaseModel):
    """Audience demographics. In production this comes from each platform's
    analytics API (owner OAuth). Interests are NOT here: the AI infers them."""

    gender_split: dict[str, float]
    age_buckets: dict[str, float]
    top_countries: list[CountryShare]


class Post(BaseModel):
    id: str
    account_id: str
    platform: Platform
    title: str
    hook: str                        # opening line / first seconds (AI input)
    topics: list[str]
    published_at: datetime
    duration_sec: Optional[int] = None
    thumbnail_url: Optional[str] = None
    views: dict[str, int]            # keyed by WINDOWS
    likes: int
    comments: int
    follower_gain: int


class Account(BaseModel):
    id: str
    platform: Platform
    handle: str
    display_name: str
    followers: int
    views: dict[str, int]
    prev_views: dict[str, int]
    follower_gain: dict[str, int]
    top_topics: list[str]
    audience: Optional[Audience] = None   # None = demographics unavailable (needs OAuth)
    data_source: str = "demo"             # "demo" | "youtube_api"


# ---------- Leaderboard ----------
class AccountSummary(BaseModel):
    id: str
    platform: Platform
    handle: str
    display_name: str
    followers: int
    data_source: str = "demo"


class TopPost(BaseModel):
    id: str
    title: str
    views: int


class LeaderboardRow(BaseModel):
    rank: int
    rank_change: int                 # +2 = moved up two places vs previous period
    account: AccountSummary
    views: int
    follower_gain: int
    top_post: Optional[TopPost] = None


class LeaderboardResponse(BaseModel):
    platform: str
    window: str
    metric: str
    total: int
    rows: list[LeaderboardRow]


# ---------- Requests ----------
class AddAccountRequest(BaseModel):
    platform: Platform
    handle: str = Field(min_length=2, max_length=120)


class AnalyzeRequest(BaseModel):
    post_id: str


class StrategyRequest(BaseModel):
    account_id: str


class IdeasRequest(BaseModel):
    account_id: Optional[str] = None   # None = across all accounts
    count: int = Field(5, ge=1, le=8)


# ---------- AI outputs ----------
class PostInsight(BaseModel):
    post_id: str = ""
    hook_strength: int = Field(5, ge=1, le=10)
    hook_reason: str
    pacing: str
    thumbnail_notes: str
    trend_fit: str
    key_takeaways: list[str]
    source: str = "gemma"            # "gemma" | "offline-demo"
    model: str = ""


class Recommendation(BaseModel):
    format: str
    topic: str
    hook: str
    why: str


class AudienceProfile(BaseModel):
    primary_segment: str
    key_traits: list[str]
    inferred_interests: list[str]


class ChannelStrategy(BaseModel):
    account_id: str = ""
    audience_profile: AudienceProfile
    what_worked: list[str]
    recommendations: list[Recommendation]
    posting_advice: str
    conclusion: str
    source: str = "gemma"
    model: str = ""


class ContentIdea(BaseModel):
    title: str
    hook: str
    outline: list[str]
    why_it_should_work: str


class IdeasResponse(BaseModel):
    scope: str = ""
    ideas: list[ContentIdea]
    source: str = "gemma"
    model: str = ""
