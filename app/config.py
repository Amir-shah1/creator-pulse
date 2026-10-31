import os

from dotenv import load_dotenv

load_dotenv()

# DEMO_MODE=true  -> everything runs on seeded/generated dummy data (default, safest for demos)
# DEMO_MODE=false -> YouTube accounts are fetched live (needs YOUTUBE_API_KEY);
#                    Instagram/Facebook stay demo (they need Meta app review).
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
# Gemma 4 models served by the Gemini API: gemma-4-26b-a4b-it (fast) or gemma-4-31b-it (stronger)
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")
