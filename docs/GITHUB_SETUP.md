# Publishing to GitHub (team of three)

## 1. One person creates the repo
1. On github.com click **New repository**. Name: `creator-pulse`. Visibility: **Public** (hackathon tracks need an open-source repo).
2. Do NOT tick "Add README", ".gitignore" or "license" (we already have them).

## 2. Push the code (same person)
```bash
cd creator-pulse
git init
git add .
git commit -m "Initial scaffold"
git branch -M main
git remote add origin https://github.com/<username>/creator-pulse.git
git push -u origin main
```

## 3. Add teammates
Repo -> **Settings -> Collaborators -> Add people** (enter their GitHub usernames). They accept the email invite.

## 4. Teammates clone
```bash
git clone https://github.com/<username>/creator-pulse.git
cd creator-pulse
```

## 5. Daily flow
```bash
git checkout main && git pull
git checkout -b feature/my-task
# ... work ...
git add . && git commit -m "Describe the change"
git push -u origin feature/my-task
```
Then open a Pull Request on GitHub, get a review, and merge.

## Tips
- Optional: Settings -> Branches -> require a PR before merging into `main`.
- Add the topic `hacktoberfest` to the repo (the gear icon beside "About") and the tracks you target.
- If `git push` asks for a password, use a Personal Access Token or sign in via GitHub Desktop / `gh auth login`.
