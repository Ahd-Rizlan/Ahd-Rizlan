"""Draws the "power levels" stats card and top-languages card.

Self-hosted replacement for public stats services, which go down often.
Needs GITHUB_TOKEN (and optionally GITHUB_USER). Writes dist/stats-*.svg
and dist/langs-*.svg.
"""
import json
import os
import urllib.request
from html import escape
from pathlib import Path

USER = os.environ.get("GITHUB_USER", "Ahd-Rizlan")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = Path(os.environ.get("OUT_DIR", "dist"))

QUERY = """query($login:String!){user(login:$login){
  contributionsCollection{totalCommitContributions totalPullRequestContributions
    totalIssueContributions restrictedContributionsCount}
  followers{totalCount}
  repositories(first:100, ownerAffiliations:OWNER, isFork:false){totalCount nodes{
    stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}){
      edges{size node{name color}}}}}}}"""

RED, BLUE, YELLOW, INK = "#E23636", "#00D4FF", "#FFE14D", "#0B0B0B"
THEMES = {
    "dark": {"bg": INK, "fg": "#FFFFFF", "muted": "#9FB3C8", "border": "#FFFFFF", "track": "#222831", "blue": BLUE},
    "light": {"bg": "#F7F3EA", "fg": INK, "muted": "#4A5560", "border": INK, "track": "#E2DCCD", "blue": "#0096B4"},
}
DISPLAY = "Impact, 'Arial Black', sans-serif"
MONO = "'Fira Code', Consolas, monospace"
SKIP_LANGS = {"Jupyter Notebook", "ShaderLab", "HLSL", "Mathematica", "PLpgSQL"}


def fetch():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]


def header(t, title, w):
    return (f'<rect x="3" y="3" width="{w - 6}" height="194" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="4"/>'
            f'<rect x="20" y="18" width="{14 * len(title) + 24}" height="28" fill="{YELLOW}" stroke="{INK}" stroke-width="2"/>'
            f'<text x="32" y="39" font-family="{DISPLAY}" font-size="18" letter-spacing="1" fill="{INK}">{escape(title)}</text>')


def stats_svg(mode, u):
    t = THEMES[mode]
    c = u["contributionsCollection"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    rows = [("Commits (this year)", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
            ("Pull requests", c["totalPullRequestContributions"]),
            ("Issues", c["totalIssueContributions"]),
            ("Repositories", u["repositories"]["totalCount"]),
            ("Stars earned", stars)]
    body = []
    for i, (label, val) in enumerate(rows):
        y = 74 + i * 25
        col = RED if i % 2 == 0 else t["blue"]
        body.append(f'<rect x="24" y="{y - 11}" width="6" height="14" fill="{col}"/>'
                    f'<text x="40" y="{y + 1}" font-family="{MONO}" font-size="14" fill="{t["muted"]}">{label}</text>'
                    f'<text x="300" y="{y + 1}" text-anchor="end" font-family="{DISPLAY}" font-size="18" fill="{t["fg"]}">{val:,}</text>')
    total = sum(v for _, v in rows[:3])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="200" viewBox="0 0 440 200" role="img" aria-label="GitHub stats: {", ".join(f"{l} {v}" for l, v in rows)}">
{header(t, "THE STATS", 440)}
{"".join(body)}
<circle cx="370" cy="112" r="44" fill="none" stroke="{t["track"]}" stroke-width="8"/>
<circle cx="370" cy="112" r="44" fill="none" stroke="{RED}" stroke-width="8" stroke-dasharray="210 277" transform="rotate(-90 370 112)"/>
<text x="370" y="120" text-anchor="middle" font-family="{DISPLAY}" font-size="26" fill="{t["fg"]}">{total:,}</text>
<text x="370" y="174" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{t["muted"]}">contributions</text>
</svg>'''


def langs_svg(mode, u):
    t = THEMES[mode]
    sizes = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name not in SKIP_LANGS:
                sizes[name] = sizes.get(name, 0) + e["size"]
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    palette = [RED, t["blue"], YELLOW, "#FF7A7A", "#7FE8FF", t["muted"]]
    bar, x = [], 24
    for i, (_, v) in enumerate(top):
        w = 392 * v / total
        bar.append(f'<rect x="{x:.1f}" y="62" width="{w:.1f}" height="12" fill="{palette[i]}"/>')
        x += w
    legend = []
    for i, (name, v) in enumerate(top):
        cx, cy = 24 + (i % 2) * 200, 102 + (i // 2) * 28
        legend.append(f'<rect x="{cx}" y="{cy - 10}" width="12" height="12" fill="{palette[i]}" stroke="{INK}" stroke-width="1"/>'
                      f'<text x="{cx + 20}" y="{cy + 1}" font-family="{MONO}" font-size="14" fill="{t["fg"]}">{escape(name)}'
                      f' <tspan fill="{t["muted"]}">{100 * v / total:.1f}%</tspan></text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="200" viewBox="0 0 440 200" role="img" aria-label="Top languages: {", ".join(n for n, _ in top)}">
{header(t, "TOP LANGUAGES", 440)}
{"".join(bar)}
{"".join(legend)}
</svg>'''


def main():
    u = fetch()
    OUT.mkdir(parents=True, exist_ok=True)
    for mode in THEMES:
        (OUT / f"stats-{mode}.svg").write_text(stats_svg(mode, u), encoding="utf-8")
        (OUT / f"langs-{mode}.svg").write_text(langs_svg(mode, u), encoding="utf-8")
    print(f"wrote {OUT}/stats-*.svg and {OUT}/langs-*.svg")


if __name__ == "__main__":
    main()
