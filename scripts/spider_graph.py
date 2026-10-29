"""Draws the contribution graph with a spider swinging across it.

Needs GITHUB_TOKEN (and optionally GITHUB_USER) in the environment.
Writes dist/spider-dark.svg and dist/spider-light.svg.
"""
import json
import os
import urllib.request
from pathlib import Path

USER = os.environ.get("GITHUB_USER", "Ahd-Rizlan")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = Path(os.environ.get("OUT_DIR", "dist"))

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
  totalContributions weeks{contributionDays{contributionCount weekday}}}}}}"""

from cartoon import BLUE, INK, THEMES as BASE, comic_text, mini_spider, shadow_box, style

THEMES = {
    "dark": {**BASE["dark"], "empty": "#2E2760", "levels": ["#7A2A3A", "#B0303A", "#E23636", "#FF6B6B"]},
    "light": {**BASE["light"], "empty": "#F1E8CF", "levels": ["#F7C1C1", "#F09595", "#E24B4A", "#A32D2D"]},
}
CELL, GAP, LEFT, TOP = 14, 4, 40, 112
DURATION = 14  # seconds per swing across the whole graph


def fetch():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def level(count, peak):
    if count == 0:
        return -1
    return min(3, int(4 * count / (peak + 1)))


def swing_path(cols, width):
    """A chain of arcs: the spider dips into the graph and swings back up."""
    step = 6
    x0 = LEFT - 10
    d = [f"M{x0},{TOP - 40}"]
    x = x0
    while x < width - LEFT - step * (CELL + GAP):
        nx = x + step * (CELL + GAP)
        cx = (x + nx) / 2
        d.append(f"Q{cx:.0f},{TOP + 7 * (CELL + GAP) + 30} {nx:.0f},{TOP - 40}")
        x = nx
    return " ".join(d)


def render(mode, total, weeks):
    t = THEMES[mode]
    cols = len(weeks)
    width = LEFT * 2 + cols * (CELL + GAP) + 16
    height = TOP + 7 * (CELL + GAP) + 50
    peak = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=0)
    path = swing_path(cols, width)
    cells = []
    for ci, w in enumerate(weeks):
        x = LEFT + ci * (CELL + GAP)
        delay = DURATION * (x - LEFT + 10) / width
        for d in w["contributionDays"]:
            y = TOP + d["weekday"] * (CELL + GAP)
            lv = level(d["contributionCount"], peak)
            fill = t["empty"] if lv < 0 else t["levels"][lv]
            zap = f' class="z" style="--c:{fill};animation-delay:{delay:.2f}s"' if lv >= 0 else ""
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="4" fill="{fill}" stroke="{INK}" stroke-width="1.5"{zap}/>')
    css = style(
        f".z {{ animation: zap {DURATION}s linear infinite; }}",
        f"@keyframes zap {{ 0%, 2% {{ fill: {BLUE}; }} 5%, 100% {{ fill: var(--c); }} }}",
        f".web {{ stroke-dasharray: 6000; stroke-dashoffset: 6000; animation: shoot {DURATION}s linear infinite; }}",
        "@keyframes shoot { to { stroke-dashoffset: 0; } }",
        "@media (prefers-reduced-motion: reduce) { #rider { display: none; } }",
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} contributions in the last year, with a cartoon spider swinging across the graph">
{css}
<defs><clipPath id="f"><rect x="6" y="6" width="{width - 22}" height="{height - 22}" rx="24"/></clipPath></defs>
{shadow_box(6, 6, width - 22, height - 22, t["panel"], r=24, off=9, sw=5)}
<g clip-path="url(#f)">
{comic_text(LEFT, 52, f"{total:,} CONTRIBUTIONS IN THE LAST YEAR", 30, t["fg"] if mode == "light" else "#FFE14D", shadow=INK, off=3, sw=6)}
{"".join(cells)}
<path class="web" d="{path}" fill="none" stroke="{t["thread"]}" stroke-width="2.5" stroke-linecap="round" opacity="0.6"/>
<g id="rider"><g transform="scale(0.9)">{mini_spider()}</g><animateMotion dur="{DURATION}s" repeatCount="indefinite" path="{path}"/></g>
</g>
<rect x="6" y="6" width="{width - 22}" height="{height - 22}" rx="24" fill="none" stroke="{INK}" stroke-width="5"/>
</svg>'''


def main():
    total, weeks = fetch()
    OUT.mkdir(parents=True, exist_ok=True)
    for mode in THEMES:
        (OUT / f"spider-{mode}.svg").write_text(render(mode, total, weeks), encoding="utf-8")
    print(f"{total} contributions, wrote {OUT}/spider-*.svg")


if __name__ == "__main__":
    main()
