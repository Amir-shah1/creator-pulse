# Deploy on DigitalOcean App Platform

1. Push the repo to GitHub (see `GITHUB_SETUP.md`).
2. DigitalOcean -> **Create -> App Platform** -> choose your GitHub repo and branch `main`.
3. It detects the `Dockerfile`. Set the HTTP port to **8080**.
4. Add environment variables (mark keys as **Encrypted**):
   - `DEMO_MODE` = `true`
   - `GEMINI_API_KEY` = your key from https://aistudio.google.com/apikey
   - `GEMMA_MODEL` = `gemma-4-26b-a4b-it`
5. Deploy, open the app URL and check `/health`: `"ai_live": true` means Gemma is connected.

Alternative (Droplet): install Docker, then
`docker build -t creator-pulse . && docker run -d -p 80:8080 --env-file .env creator-pulse`

Note: the account list is kept in memory, so added accounts reset on restart. That is fine for a demo.
