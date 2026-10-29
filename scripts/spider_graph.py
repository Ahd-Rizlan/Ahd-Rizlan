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

THEMES = {
    "dark": {"empty": "#161B22", "levels": ["#4A1216", "#8C1D23", "#C42A30", "#E23636"],
             "text": "#9FB3C8", "web": "#FFFFFF"},
    "light": {"empty": "#EBE6DA", "levels": ["#F7C1C1", "#F09595", "#E24B4A", "#A32D2D"],
              "text": "#4A5560", "web": "#0B0B0B"},
}
BLUE = "#00D4FF"
CELL, GAP, LEFT, TOP = 13, 4, 20, 70
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
    while x < width:
        nx = x + step * (CELL + GAP)
        cx = (x + nx) / 2
        d.append(f"Q{cx:.0f},{TOP + 7 * (CELL + GAP) + 30} {nx:.0f},{TOP - 40}")
        x = nx
    return " ".join(d)


SPIDER = f'''<g id="spider">
  <g stroke="#0B0B0B" stroke-width="2" fill="none" stroke-linecap="round">
    <path d="M-4,-2 l-9,-7 l-4,6"/><path d="M-4,1 l-11,-1 l-4,7"/>
    <path d="M-4,3 l-9,6 l-2,7"/><path d="M-3,5 l-6,9 l1,6"/>
    <path d="M4,-2 l9,-7 l4,6"/><path d="M4,1 l11,-1 l4,7"/>
    <path d="M4,3 l9,6 l2,7"/><path d="M3,5 l6,9 l-1,6"/>
  </g>
  <ellipse cx="0" cy="2" rx="7" ry="9" fill="#E23636" stroke="#0B0B0B" stroke-width="2"/>
  <path d="M-4,0 l3,2 l-4,1 z M4,0 l-3,2 l4,1 z" fill="#FFFFFF"/>
  <path d="M0,-6 v16 M-6,3 h12" stroke="#0B0B0B" stroke-width="1.2"/>
</g>'''


def render(mode, total, weeks):
    t = THEMES[mode]
    cols = len(weeks)
    width = LEFT * 2 + cols * (CELL + GAP)
    height = TOP + 7 * (CELL + GAP) + 40
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
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{fill}"{zap}/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} contributions in the last year, with a spider swinging across the graph">
<style>
  .z {{ animation: zap {DURATION}s linear infinite; }}
  @keyframes zap {{ 0%, 2% {{ fill: {BLUE}; }} 5%, 100% {{ fill: var(--c); }} }}
  .web {{ stroke-dasharray: 6000; stroke-dashoffset: 6000; animation: shoot {DURATION}s linear infinite; }}
  @keyframes shoot {{ to {{ stroke-dashoffset: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .z, .web {{ animation: none; }} #rider {{ display: none; }} }}
</style>
<text x="{LEFT}" y="{height - 12}" font-family="'Fira Code', Consolas, monospace" font-size="14" fill="{t["text"]}">{total} contributions in the last year</text>
{"".join(cells)}
<path class="web" d="{path}" fill="none" stroke="{t["web"]}" stroke-width="1" opacity="0.35"/>
<g id="rider">{SPIDER}<animateMotion dur="{DURATION}s" repeatCount="indefinite" path="{path}"/></g>
</svg>'''


def main():
    total, weeks = fetch()
    OUT.mkdir(parents=True, exist_ok=True)
    for mode in THEMES:
        (OUT / f"spider-{mode}.svg").write_text(render(mode, total, weeks), encoding="utf-8")
    print(f"{total} contributions, wrote {OUT}/spider-*.svg")


if __name__ == "__main__":
    main()
