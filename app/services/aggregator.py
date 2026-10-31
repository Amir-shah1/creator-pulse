"""Ranking logic for the leaderboard (accounts ranked by views or follower gain)."""
from app.models import (
    AccountSummary, LeaderboardResponse, LeaderboardRow, TopPost,
)
from app.store import store


def build_leaderboard(platform: str, window: str, metric: str) -> LeaderboardResponse:
    accounts = store.list_accounts()
    if platform != "all":
        accounts = [a for a in accounts if a.platform.value == platform]

    def value(a):
        return a.views[window] if metric == "views" else a.follower_gain[window]

    ranked = sorted(accounts, key=lambda a: (-value(a), a.display_name))

    # Previous-period rank (only views have previous-period data)
    prev_rank: dict[str, int] = {}
    if metric == "views":
        prev_sorted = sorted(accounts, key=lambda a: (-a.prev_views[window], a.display_name))
        prev_rank = {a.id: i for i, a in enumerate(prev_sorted, start=1)}

    # Best post per account in this window
    best_post: dict[str, TopPost] = {}
    for p in store.all_posts():
        current = best_post.get(p.account_id)
        if current is None or p.views[window] > current.views:
            best_post[p.account_id] = TopPost(id=p.id, title=p.title, views=p.views[window])

    rows = []
    for rank, a in enumerate(ranked, start=1):
        rows.append(LeaderboardRow(
            rank=rank,
            rank_change=(prev_rank[a.id] - rank) if a.id in prev_rank else 0,
            account=AccountSummary(
                id=a.id, platform=a.platform, handle=a.handle,
                display_name=a.display_name, followers=a.followers,
                data_source=a.data_source,
            ),
            views=a.views[window],
            follower_gain=a.follower_gain[window],
            top_post=best_post.get(a.id),
        ))

    return LeaderboardResponse(
        platform=platform, window=window, metric=metric, total=len(rows), rows=rows,
    )
