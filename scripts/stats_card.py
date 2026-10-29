"""Draws the cartoon stats card and top-languages card.

Self-hosted replacement for public stats services, which go down often.
Needs GITHUB_TOKEN (and optionally GITHUB_USER). Writes dist/stats-*.svg
and dist/langs-*.svg.
"""
import json
import os
import urllib.request
from html import escape
from pathlib import Path

from cartoon import save, BLUE, COMIC, INK, MONO, PINK, RED, THEMES, WHITE, YELLOW, burst, comic_text, shadow_box, style

USER = os.environ.get("GITHUB_USER", "Ahd-Rizlan")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = Path(os.environ.get("OUT_DIR", "dist"))

QUERY = """query($login:String!){user(login:$login){
  contributionsCollection{totalCommitContributions totalPullRequestContributions
    totalIssueContributions restrictedContributionsCount}
  repositories(first:100, ownerAffiliations:OWNER, isFork:false){totalCount nodes{
    stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}){
      edges{size node{name}}}}}}}"""

SKIP_LANGS = {"Jupyter Notebook", "ShaderLab", "HLSL", "Mathematica", "PLpgSQL"}
W, H = 460, 260


def fetch():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]


def frame(t, title, head):
    return (f'<defs><clipPath id="c"><rect x="6" y="6" width="{W - 22}" height="{H - 22}" rx="22"/></clipPath></defs>'
            + shadow_box(6, 6, W - 22, H - 22, t["panel"], r=22, off=9, sw=5)
            + f'<g clip-path="url(#c)"><rect x="6" y="6" width="{W - 22}" height="60" fill="{head}"/></g>'
            f'<line x1="6" y1="66" x2="{W - 16}" y2="66" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="6" y="6" width="{W - 22}" height="{H - 22}" rx="22" fill="none" stroke="{INK}" stroke-width="5"/>'
            + comic_text(28, 52, title, 34, WHITE, shadow=INK, off=4, sw=7))


def stats_svg(mode, u):
    t = THEMES[mode]
    c = u["contributionsCollection"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    rows = [("Commits this year", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
            ("Pull requests", c["totalPullRequestContributions"]),
            ("Issues", c["totalIssueContributions"]),
            ("Repositories", u["repositories"]["totalCount"]),
            ("Stars earned", stars)]
    body = []
    for i, (label, val) in enumerate(rows):
        y = 98 + i * 28
        col = [RED, BLUE, YELLOW][i % 3]
        body.append(f'<circle cx="34" cy="{y - 6}" r="7" fill="{col}" stroke="{INK}" stroke-width="3"/>'
                    f'<text x="50" y="{y}" font-family="{MONO}" font-size="14" fill="{t["muted"]}">{label}</text>'
                    f'<text x="268" y="{y + 1}" text-anchor="end" font-family="{COMIC}" font-size="24" letter-spacing="1" fill="{t["fg"]}">{val:,}</text>')
    total = sum(v for _, v in rows[:3])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub stats: {", ".join(f"{l} {v}" for l, v in rows)}">
{style()}
{frame(t, "THE STATS", RED)}
{"".join(body)}
<g>{burst(362, 156, 82, points=14, fill=YELLOW, sw=5, seed=3)}</g>
{comic_text(362, 164, f"{total:,}", 38, RED, anchor="middle", sw=6, off=0)}
<text x="362" y="188" text-anchor="middle" font-family="{COMIC}" font-size="15" letter-spacing="1" fill="{INK}">THIS YEAR</text>
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
    palette = [RED, BLUE, YELLOW, PINK, WHITE, "#9B7BFF"]
    bar, x = [], 28
    for i, (_, v) in enumerate(top):
        w = 396 * v / total
        bar.append(f'<rect x="{x:.1f}" y="88" width="{w:.1f}" height="24" fill="{palette[i]}"/>')
        x += w
    legend = []
    for i, (name, v) in enumerate(top):
        cx, cy = 34 + (i % 2) * 206, 146 + (i // 2) * 30
        legend.append(f'<circle cx="{cx}" cy="{cy - 6}" r="8" fill="{palette[i]}" stroke="{INK}" stroke-width="3"/>'
                      f'<text x="{cx + 16}" y="{cy}" font-family="{COMIC}" font-size="20" letter-spacing="1" fill="{t["fg"]}">{escape(name.upper())}'
                      f' <tspan font-family="{MONO}" font-size="13" fill="{t["muted"]}">{100 * v / total:.1f}%</tspan></text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Top languages: {", ".join(n for n, _ in top)}">
{style()}
{frame(t, "TOP LANGUAGES", BLUE)}
<defs><clipPath id="bar"><rect x="28" y="88" width="396" height="24" rx="12"/></clipPath></defs>
<rect x="32" y="92" width="396" height="24" rx="12" fill="{INK}"/>
<g clip-path="url(#bar)">{"".join(bar)}</g>
<rect x="28" y="88" width="396" height="24" rx="12" fill="none" stroke="{INK}" stroke-width="4"/>
{"".join(legend)}
</svg>'''


def main():
    u = fetch()
    OUT.mkdir(parents=True, exist_ok=True)
    for mode in THEMES:
        save(OUT / f"stats-{mode}.svg", stats_svg(mode, u))
        save(OUT / f"langs-{mode}.svg", langs_svg(mode, u))
    print(f"wrote {OUT}/stats-*.svg and {OUT}/langs-*.svg")


if __name__ == "__main__":
    main()
