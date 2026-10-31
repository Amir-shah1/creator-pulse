"""In-memory store of the accounts currently on the dashboard.
Starts with the seeded demo accounts; users can add/remove during the session."""
import re
from typing import Optional

from app import config
from app.models import Account, Platform, Post
from app.providers import demo, youtube


def handle_key(handle: str) -> str:
    """'@Name', 'https://youtube.com/@Name/' or 'Name' -> 'name'"""
    h = handle.strip().rstrip("/").split("/")[-1].lstrip("@").lower()
    return re.sub(r"[^a-z0-9._\-]", "", h)


class Store:
    def __init__(self):
        self.reset()

    def reset(self):
        self.seed_accounts = {a.id: a for a in demo.load_accounts()}
        self.accounts: dict[str, Account] = dict(self.seed_accounts)
        self.posts: dict[str, list[Post]] = {a: demo.load_posts(a) for a in self.accounts}
        self._seed_posts = {a: list(p) for a, p in self.posts.items()}

    def list_accounts(self) -> list[Account]:
        return list(self.accounts.values())

    def get(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)

    def posts_for(self, account_id: str) -> list[Post]:
        return self.posts.get(account_id, [])

    def all_posts(self) -> list[Post]:
        return [p for ps in self.posts.values() for p in ps]

    def find_post(self, post_id: str) -> Optional[Post]:
        return next((p for p in self.all_posts() if p.id == post_id), None)

    def add(self, platform: Platform, handle: str) -> Account:
        key = handle_key(handle)
        if len(key) < 2:
            raise ValueError("Please enter a valid handle (at least 2 characters).")
        for a in self.accounts.values():
            if a.platform == platform and handle_key(a.handle) == key:
                raise ValueError(f"{a.display_name} is already on the dashboard.")

        # Re-adding a removed seed account restores its original data
        for sid, seed in self.seed_accounts.items():
            if seed.platform == platform and handle_key(seed.handle) == key:
                self.accounts[sid] = seed
                self.posts[sid] = list(self._seed_posts[sid])
                return seed

        taken = set(self.accounts)
        live = platform == Platform.youtube and not config.DEMO_MODE and config.YOUTUBE_API_KEY
        if live:
            try:
                account, posts = youtube.fetch_channel(key, taken)
            except youtube.ProviderError as e:
                raise ValueError(str(e))
        else:
            account, posts = demo.generate_account(platform.value, key, taken)
        self.accounts[account.id] = account
        self.posts[account.id] = posts
        return account

    def remove(self, account_id: str) -> bool:
        self.posts.pop(account_id, None)
        return self.accounts.pop(account_id, None) is not None


store = Store()
