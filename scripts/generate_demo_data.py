"""Generates data/demo_data.json (fictional creators, dummy numbers).
Run from the repo root:  python scripts/generate_demo_data.py
Deterministic: same output every run."""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

rng = random.Random(42)
ANCHOR = datetime(2026, 10, 30, 12, 0)
OUT = Path(__file__).resolve().parent.parent / "data" / "demo_data.json"

ACCOUNTS = [
    dict(id="yt_zain", platform="youtube", handle="@techtalkszain", display_name="TechTalks with Zain",
         followers=482000, top_topics=["smartphone reviews", "budget tech", "gadgets"],
         audience=dict(gender_split={"male": 78, "female": 20, "other": 2},
                       age_buckets={"13-17": 12, "18-24": 44, "25-34": 31, "35-44": 9, "45+": 4},
                       top_countries=[("Pakistan", 54), ("UAE", 14), ("Saudi Arabia", 9), ("UK", 6)]),
         posts=[("Is the Rs 60k phone worth it? Honest 30-day test", "I used this phone for 30 days so you do not have to.", ["smartphone reviews", "budget tech"]),
                ("5 gadgets under Rs 2000 that feel illegal to own", "Number three broke my brain.", ["gadgets", "budget tech"]),
                ("Why every laptop in Pakistan is overpriced", "Here is the number nobody tells you.", ["laptops", "pricing"]),
                ("I tried AI tools for a full week of work", "Day one went badly. Day five changed everything.", ["AI tools", "productivity"]),
                ("Unboxing the cheapest foldable on the market", "This costs less than your last phone repair.", ["unboxing", "smartphone reviews"])]),
    dict(id="yt_desi", platform="youtube", handle="@desieatsdaily", display_name="Desi Eats Daily",
         followers=315000, top_topics=["street food", "recipes", "food challenges"],
         audience=dict(gender_split={"male": 46, "female": 52, "other": 2},
                       age_buckets={"13-17": 8, "18-24": 29, "25-34": 38, "35-44": 18, "45+": 7},
                       top_countries=[("Pakistan", 61), ("UK", 12), ("USA", 9), ("UAE", 7)]),
         posts=[("Rs 100 street food challenge in Lahore", "Can I eat a full meal for under a hundred rupees?", ["street food", "food challenges"]),
                ("Restaurant-style chicken karahi in 20 minutes", "Stop ordering karahi, make it in 20.", ["recipes"]),
                ("Eating only at 5am food stalls", "Nobody warned me about the 5am menu.", ["street food"]),
                ("Mom rates my cooking for a whole week", "She has never lied to me about food.", ["recipes", "family"]),
                ("Cheapest vs most expensive biryani in the city", "One of these is a scam.", ["food challenges", "street food"])]),
    dict(id="ig_hira", platform="instagram", handle="@fitwithhira", display_name="Fit with Hira",
         followers=268000, top_topics=["home workouts", "healthy eating", "fitness tips"],
         audience=dict(gender_split={"male": 14, "female": 84, "other": 2},
                       age_buckets={"13-17": 7, "18-24": 39, "25-34": 40, "35-44": 11, "45+": 3},
                       top_countries=[("Pakistan", 66), ("UAE", 11), ("UK", 8), ("Canada", 5)]),
         posts=[("10-minute no-equipment fat burn", "If you have 10 minutes, you have no excuses.", ["home workouts"]),
                ("What I eat in a day (under 1500 calories)", "Eating less is not the secret. Eating this is.", ["healthy eating"]),
                ("3 mistakes ruining your abs workout", "You are doing number two right now.", ["fitness tips"]),
                ("Morning stretch routine for desk workers", "Your back will thank you by day three.", ["home workouts", "wellness"]),
                ("Gym vs home: the honest answer", "I trained both ways for 90 days.", ["fitness tips"])]),
    dict(id="ig_pindi", platform="instagram", handle="@wanderlustpindi", display_name="Wanderlust Pindi",
         followers=174000, top_topics=["travel vlogs", "hidden gems", "budget travel"],
         audience=dict(gender_split={"male": 52, "female": 46, "other": 2},
                       age_buckets={"13-17": 10, "18-24": 47, "25-34": 33, "35-44": 8, "45+": 2},
                       top_countries=[("Pakistan", 72), ("UAE", 8), ("UK", 6), ("Germany", 4)]),
         posts=[("Hunza on a Rs 15,000 budget", "Everyone said it was impossible. Here is the receipt.", ["budget travel", "travel vlogs"]),
                ("The village Google Maps forgot", "No signal, no hotel, no regrets.", ["hidden gems"]),
                ("Sunrise at Fairy Meadows", "We hiked four hours for this exact second.", ["travel vlogs"]),
                ("Packing for 7 days in one small bag", "My bag is smaller than your laptop bag.", ["budget travel", "tips"]),
                ("Train journey through the north", "The window seat is the whole trip.", ["travel vlogs"])]),
    dict(id="fb_cricket", platform="facebook", handle="cricketchaicorner", display_name="Cricket Chai Corner",
         followers=612000, top_topics=["cricket analysis", "match reactions", "debates"],
         audience=dict(gender_split={"male": 83, "female": 16, "other": 1},
                       age_buckets={"13-17": 6, "18-24": 28, "25-34": 33, "35-44": 22, "45+": 11},
                       top_countries=[("Pakistan", 77), ("UAE", 8), ("UK", 5), ("Saudi Arabia", 4)]),
         posts=[("Playing XI debate: who deserves the spot?", "Be honest, did the selectors get this right?", ["cricket analysis", "debates"]),
                ("Last over reaction, full match recap", "I am still shaking after that last over.", ["match reactions"]),
                ("Top 5 fastest spells this decade", "Number one is not who you think.", ["cricket analysis"]),
                ("Chai and stats: batting averages explained", "Averages lie. Here is how.", ["cricket analysis", "education"]),
                ("Fan poll: best captain of all time", "Comment your answer before you read the results.", ["debates"])]),
    dict(id="fb_startup", platform="facebook", handle="startupstoriespk", display_name="Startup Stories PK",
         followers=94000, top_topics=["entrepreneurship", "founder stories", "freelancing"],
         audience=dict(gender_split={"male": 64, "female": 35, "other": 1},
                       age_buckets={"13-17": 2, "18-24": 31, "25-34": 46, "35-44": 16, "45+": 5},
                       top_countries=[("Pakistan", 81), ("UAE", 6), ("UK", 4), ("USA", 3)]),
         posts=[("From a dorm room to 50 employees: founder story", "He started with one laptop and a loan from his brother.", ["founder stories"]),
                ("How I landed my first 5 freelance clients", "I sent 200 messages. Here is the one that worked.", ["freelancing"]),
                ("Startup ideas that work in small cities", "Everyone chases Karachi. Look elsewhere.", ["entrepreneurship"]),
                ("Pitch deck mistakes investors hate", "I have seen 300 decks. These mistakes repeat.", ["entrepreneurship", "funding"]),
                ("Remote work jobs that pay in dollars", "Number four needs zero experience.", ["freelancing"])]),
]

DURATION = {"youtube": (240, 900), "instagram": (15, 60), "facebook": (60, 300)}
FG_RATE = {"youtube": (0.002, 0.010), "instagram": (0.003, 0.012), "facebook": (0.001, 0.005)}
BASE_VIEWS = {"youtube": (60000, 900000), "instagram": (40000, 700000), "facebook": (30000, 500000)}


def windows_from_30d(v30):
    v7 = int(v30 * rng.uniform(0.3, 0.6))
    v36 = int(v7 * rng.uniform(0.2, 0.35))
    v24 = int(v36 * rng.uniform(0.6, 0.8))
    return {"24h": v24, "36h": v36, "7d": v7, "30d": int(v30)}


accounts_out, posts_out = [], []
for a in ACCOUNTS:
    plat = a["platform"]
    acc_posts = []
    for i, (title, hook, topics) in enumerate(a["posts"], start=1):
        v = windows_from_30d(rng.randint(*BASE_VIEWS[plat]))
        lo, hi = DURATION[plat]
        post = dict(
            id=f"{a['id']}_p{i}", account_id=a["id"], platform=plat, title=title, hook=hook,
            topics=topics, published_at=(ANCHOR - timedelta(days=rng.randint(1, 25))).isoformat(),
            duration_sec=rng.randint(lo, hi), thumbnail_url=None, views=v,
            likes=int(v["30d"] * rng.uniform(0.03, 0.09)), comments=int(v["30d"] * rng.uniform(0.002, 0.012)),
            follower_gain=int(v["30d"] * rng.uniform(*FG_RATE[plat])))
        acc_posts.append(post)
    posts_out.extend(acc_posts)

    views = {w: int(sum(p["views"][w] for p in acc_posts) * 1.4) for w in ("24h", "36h", "7d", "30d")}
    prev = {w: int(v * rng.uniform(0.7, 1.3)) for w, v in views.items()}
    fg30 = int(sum(p["follower_gain"] for p in acc_posts) * 1.3)
    fg7 = int(fg30 * 0.3); fg36 = int(fg7 * 0.25); fg24 = int(fg36 * 0.7)
    accounts_out.append(dict(
        id=a["id"], platform=plat, handle=a["handle"], display_name=a["display_name"],
        followers=a["followers"], views=views, prev_views=prev,
        follower_gain={"24h": fg24, "36h": fg36, "7d": fg7, "30d": fg30},
        top_topics=a["top_topics"],
        audience=dict(gender_split=a["audience"]["gender_split"], age_buckets=a["audience"]["age_buckets"],
                      top_countries=[dict(country=c, pct=p) for c, p in a["audience"]["top_countries"]])))

OUT.write_text(json.dumps({"accounts": accounts_out, "posts": posts_out}, indent=2), encoding="utf-8")
print(f"Wrote {len(accounts_out)} accounts, {len(posts_out)} posts -> {OUT}")
