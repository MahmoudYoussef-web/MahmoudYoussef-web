#!/usr/bin/env python3
"""
Fetch the public profile numbers from the GitHub REST API and write
data/profile_stats.json -- the single source used by both the README cards and
the README text, so a number can never disagree with itself.

Numbers:
  public_repos  user.public_repos            (public repositories, forks included)
  owned_repos   len(repos where not fork)    (what "my repos" means on the cards)
  stars         sum(stargazers_count) over own public non-fork repos
  followers / following

Auth: set GITHUB_TOKEN (CI does). Unauthenticated calls are limited to 60/hour
per IP, which GitHub-hosted runners share, so a token is strongly preferred.

Run by .github/workflows/update-profile-art.yml after fetch_contributions.py.
"""
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request

USER = os.environ.get("GH_PROFILE_USER", "MahmoudYoussef-web")
TOKEN = (os.environ.get("GITHUB_TOKEN") or "").strip()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "profile_stats.json")

API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "profile-readme-bot/1.0",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def api(path, retries=4):
    """GET a GitHub API path, retrying transient failures with backoff."""
    url = path if path.startswith("http") else API + path
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last = exc
            # 403/429 are usually rate limits; 5xx are GitHub having a bad day.
            if exc.code in (403, 429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"GitHub API request failed after {retries} attempts: {url}: {last}")


def all_repos():
    """Every public repo owned by the user, following pagination."""
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError(f"unexpected repos payload: {batch!r}")
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def main():
    user = api(f"/users/{USER}")
    repos = all_repos()
    own = [r for r in repos if not r.get("fork")]

    stars = sum(int(r.get("stargazers_count") or 0) for r in own)
    data = {
        "username": user.get("login") or USER,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "public_repos": int(user.get("public_repos") or 0),
        "owned_repos": len(own),
        "stars": stars,
        "followers": int(user.get("followers") or 0),
        "following": int(user.get("following") or 0),
        "repos": [
            {
                "name": r.get("name"),
                "stars": int(r.get("stargazers_count") or 0),
                "fork": bool(r.get("fork")),
                "language": r.get("language"),
                "archived": bool(r.get("archived")),
            }
            for r in sorted(own, key=lambda r: (-int(r.get("stargazers_count") or 0), r.get("name") or ""))
        ],
    }

    # Sanity gate: never publish an empty/zeroed payload as if it were real.
    if data["public_repos"] <= 0 or not data["repos"]:
        print(f"refusing to write empty profile stats: {data['public_repos']} repos", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(
        f"wrote {OUT}: {data['public_repos']} public repos, "
        f"{data['owned_repos']} owned, {data['stars']} stars, "
        f"{data['followers']} followers, {data['following']} following"
    )


if __name__ == "__main__":
    main()
