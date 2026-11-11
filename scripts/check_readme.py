#!/usr/bin/env python3
"""
Guard rails for the profile README. Run after render_readme_cards.py.

Checks, all fatal:
  * the repo cards in README.md are in the pinned order, and that order matches
    the REPOS list in render_readme_cards.py;
  * every ./cards/*.svg referenced by the README exists;
  * data/tests.json is internally consistent (total == sum of rows, statuses valid);
  * the exact professional title is present in the hero card;
  * "Avi" appears only in the layout-credit comment;
  * no live number is hardcoded in the scripts (665 contributions, 15 repos,
    10 stars are read from data/profile_stats.json at render time).

    python scripts/check_readme.py
"""
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):   # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
TITLE = "Backend Engineer \u2014 Java 21 \u00b7 Spring Boot 3"
PINNED = [
    "logibridge-backend",
    "url-shortener-system",
    "bloodbridge-api",
    "calorie-tracker-backend",
    "attendance-management-api",
    "ecommerce-backend",
]

failures = []


def check(ok, message):
    if ok:
        print(f"ok   {message}")
    else:
        print(f"FAIL {message}")
        failures.append(message)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


readme = read(os.path.join(ROOT, "README.md"))

# 1. card order in the README
cards = re.findall(r'<img src="\./cards/repo-([a-z0-9-]+)\.svg"', readme)
check(cards == PINNED, f"README repo-card order == pinned order ({cards})")

# 2. the render script agrees
script = read(os.path.join(HERE, "render_readme_cards.py"))
repos_block = re.search(r"^REPOS = \[(.*?)^\]", script, re.S | re.M)
script_order = re.findall(r'\("([a-z0-9-]+)",', repos_block.group(1)) if repos_block else []
check(script_order == PINNED, f"render script REPOS order == pinned order ({script_order})")

# 3. every referenced image exists
images = re.findall(r'src="\./(cards/[^"]+\.svg)"', readme)
missing = [p for p in images if not os.path.exists(os.path.join(ROOT, p))]
check(bool(images) and not missing, f"all {len(images)} README card images exist (missing: {missing})")

# 4. test data is self-consistent (the README now shows the card only, and the
#    tests tile links to data/tests.json)
tests = json.loads(read(os.path.join(ROOT, "data", "tests.json")))
check(
    sum(int(p["tests"]) for p in tests["projects"]) == int(tests["total"]),
    "data/tests.json total == sum of its rows",
)
check(
    all(p.get("status") in ("verified", "reported", "disputed") for p in tests["projects"]),
    "every test entry has a verified/reported/disputed status",
)

# 5. exact title in the hero card (the only place the profile shows it now)
hero = read(os.path.join(ROOT, "cards", "hero.svg"))
check(TITLE in hero, "exact professional title in hero card")

# 6. no Avi except the credit comment
avi_lines = [i + 1 for i, line in enumerate(readme.splitlines()) if "Avi" in line]
check(all(i <= 7 for i in avi_lines), f"'Avi' only in the layout-credit comment (lines {avi_lines})")

# 7. no hardcoded live numbers in the generators
for path in ("render_readme_cards.py", "fetch_contributions.py", "fetch_profile_stats.py"):
    body = read(os.path.join(HERE, path))
    for literal in ("665", "\"stars\": 10", "'stars': 10"):
        check(literal not in body, f"{path} does not hardcode {literal!r}")

# 8. no unsupported glyphs in card text
for name in sorted(os.listdir(os.path.join(ROOT, "cards"))):
    body = read(os.path.join(ROOT, "cards", name))
    for bad in ("\u2605", "\u2022"):
        check(bad not in body, f"cards/{name} free of {bad.encode('unicode_escape').decode()}")

print()
if failures:
    print(f"{len(failures)} check(s) failed")
    sys.exit(1)
print("all README checks passed")
