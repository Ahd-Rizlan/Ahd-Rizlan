"""Generates the static SVG artwork for the profile README.

Run from the repo root:  python scripts/generate_assets.py
Outputs go to assets/. Everything is original artwork (halftone, webs,
glitch) in a Miles-inspired palette; no official logos or character art.
"""
from pathlib import Path
from html import escape
import textwrap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

RED = "#E23636"
BLUE = "#00D4FF"
YELLOW = "#FFE14D"
INK = "#0B0B0B"

THEMES = {
    "dark": {"bg": INK, "fg": "#FFFFFF", "muted": "#9FB3C8", "panel": "#111418",
             "border": "#FFFFFF", "web": "#FFFFFF", "bubble": "#FFFFFF", "bubble_fg": INK},
    "light": {"bg": "#F7F3EA", "fg": INK, "muted": "#4A5560", "panel": "#FFFFFF",
              "border": INK, "web": INK, "bubble": YELLOW, "bubble_fg": INK},
}

DISPLAY = "Impact, 'Arial Black', 'Helvetica Neue', sans-serif"
MONO = "'Fira Code', Consolas, 'Courier New', monospace"


def web(cx, cy, r, color, spokes=9, rings=5, start=90, sweep=90):
    """Corner spider web: radial spokes joined by sagging rings."""
    import math
    parts = []
    angles = [math.radians(start + sweep * i / (spokes - 1)) for i in range(spokes)]
    for a in angles:
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(a):.1f}" '
                     f'y2="{cy + r * math.sin(a):.1f}"/>')
    for k in range(1, rings + 1):
        rr = r * k / rings
        d = []
        for i, a in enumerate(angles):
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            if i == 0:
                d.append(f"M{x:.1f},{y:.1f}")
            else:
                mid = (angles[i - 1] + a) / 2
                sag = rr * 0.86
                qx, qy = cx + sag * math.cos(mid), cy + sag * math.sin(mid)
                d.append(f"Q{qx:.1f},{qy:.1f} {x:.1f},{y:.1f}")
        parts.append(f'<path d="{" ".join(d)}" fill="none"/>')
    return f'<g stroke="{color}" stroke-width="1.2" opacity="0.55">{"".join(parts)}</g>'


def banner(mode):
    t = THEMES[mode]
    w, h = 1200, 340
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Ahamed Rizlan, software engineer. Comic-style banner with halftone dots and spider webs.">
<style>
  .glitch-r {{ animation: gr 4s steps(1) infinite; }}
  .glitch-b {{ animation: gb 4s steps(1) infinite; }}
  .bolt {{ animation: zap 2.6s linear infinite; }}
  .bolt.b2 {{ animation-delay: .9s; }}
  .bolt.b3 {{ animation-delay: 1.7s; }}
  @keyframes gr {{ 0%,86%,100% {{ transform: translate(4px,0); }} 88% {{ transform: translate(10px,-3px); }} 92% {{ transform: translate(-6px,2px); }} }}
  @keyframes gb {{ 0%,86%,100% {{ transform: translate(-4px,0); }} 88% {{ transform: translate(-10px,3px); }} 92% {{ transform: translate(6px,-2px); }} }}
  @keyframes zap {{ 0%,70%,100% {{ opacity: 0; }} 74%,82% {{ opacity: 1; }} 78% {{ opacity: .3; }} }}
  @media (prefers-reduced-motion: reduce) {{ .glitch-r,.glitch-b,.bolt {{ animation: none; }} }}
</style>
<defs>
  <pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse">
    <circle cx="6" cy="6" r="2.4" fill="{RED}"/>
  </pattern>
  <linearGradient id="fade" x1="0" x2="1">
    <stop offset="0.35" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#fff" stop-opacity="1"/>
  </linearGradient>
  <mask id="m"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>
</defs>
<rect width="{w}" height="{h}" fill="{t["bg"]}"/>
<rect width="{w}" height="{h}" fill="url(#dots)" mask="url(#m)"/>
<polygon points="860,0 1200,0 1200,{h} 790,{h}" fill="{RED}" opacity="0.92"/>
<polygon points="860,0 1200,0 1200,{h} 790,{h}" fill="url(#dots)" opacity="0.35" style="mix-blend-mode:multiply"/>
{web(1200, 0, 300, t["web"] if mode == "light" else "#FFFFFF", start=90, sweep=90)}
<text x="1010" y="215" text-anchor="middle" font-family="{DISPLAY}" font-size="88" fill="{INK}" transform="rotate(-8 1010 200)" opacity="0.9">THWIP!</text>

<text x="60" y="66" font-family="{MONO}" font-size="16" fill="{BLUE}" letter-spacing="3">EARTH-1610 // FULL-STACK DIVISION</text>

<g font-family="{DISPLAY}" font-size="96" letter-spacing="2">
  <text class="glitch-b" x="56" y="170" fill="{BLUE}">AHAMED RIZLAN</text>
  <text class="glitch-r" x="56" y="170" fill="{RED}">AHAMED RIZLAN</text>
  <text x="56" y="170" fill="{t["fg"]}">AHAMED RIZLAN</text>
</g>

<g stroke="{BLUE}" stroke-width="3" fill="none" stroke-linejoin="round">
  <polyline class="bolt" points="640,30 662,48 650,54 674,76"/>
  <polyline class="bolt b2" points="700,96 724,112 712,120 740,140"/>
  <polyline class="bolt b3" points="620,186 646,198 634,206 664,222"/>
</g>

<text x="60" y="212" font-family="{MONO}" font-size="20" fill="{t["muted"]}">Software engineer · Java · React · Angular · Automation</text>

<g transform="rotate(-2 300 272)">
  <path d="M60,240 h620 a8,8 0 0 1 8,8 v40 a8,8 0 0 1 -8,8 h-540 l-26,22 l4,-22 h-58 a8,8 0 0 1 -8,-8 v-40 a8,8 0 0 1 8,-8 z" fill="{t["bubble"]}" stroke="{INK}" stroke-width="3"/>
  <text x="80" y="276" font-family="{DISPLAY}" font-size="22" fill="{t["bubble_fg"]}" letter-spacing="1">JUST A DEV SWINGING BETWEEN JAVA AND JAVASCRIPT.</text>
</g>
<rect x="0" y="{h - 8}" width="{w}" height="8" fill="{BLUE}"/>
<rect x="0" y="0" width="{w}" height="{h}" fill="none" stroke="{t["border"]}" stroke-width="6"/>
</svg>'''


def caption(text, tilt=-1.5):
    w = 18 * len(text) + 48
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="58" viewBox="0 0 {w} 58" role="img" aria-label="{escape(text.title())}">
<g transform="rotate({tilt} {w / 2} 29)">
  <rect x="6" y="8" width="{w - 12}" height="40" fill="{YELLOW}" stroke="{INK}" stroke-width="3"/>
  <rect x="12" y="14" width="{w - 12}" height="40" fill="none" stroke="{RED}" stroke-width="2" opacity="0.8"/>
  <text x="{w / 2}" y="37" text-anchor="middle" font-family="{DISPLAY}" font-size="22" letter-spacing="1.5" fill="{INK}">{escape(text)}</text>
</g>
</svg>'''


def divider(mode):
    t = THEMES[mode]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="48" viewBox="0 0 1200 48" role="img" aria-label="Web line divider">
<style>.shot {{ stroke-dasharray: 560; stroke-dashoffset: 560; animation: shoot 5s ease-out infinite; }}
@keyframes shoot {{ 0% {{ stroke-dashoffset: 560; }} 30%,100% {{ stroke-dashoffset: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .shot {{ animation: none; stroke-dashoffset: 0; }} }}</style>
<path class="shot" d="M0,24 Q300,40 560,24" stroke="{t["web"]}" stroke-width="1.5" fill="none" opacity="0.6"/>
<path class="shot" d="M1200,24 Q900,40 640,24" stroke="{t["web"]}" stroke-width="1.5" fill="none" opacity="0.6"/>
<polygon points="600,4 610,16 626,12 618,24 630,34 612,32 600,44 590,32 572,34 582,24 574,12 590,16" fill="{RED}" stroke="{INK}" stroke-width="2"/>
<circle cx="600" cy="24" r="4" fill="{BLUE}"/>
</svg>'''


def card(mode, issue, title, desc, tags, status=None):
    t = THEMES[mode]
    lines = textwrap.wrap(desc, 46)[:3]
    desc_svg = "".join(
        f'<text x="24" y="{106 + i * 22}" font-family="{MONO}" font-size="14" fill="{t["muted"]}">{escape(l)}</text>'
        for i, l in enumerate(lines))
    tag_svg, x = [], 24
    for i, tag in enumerate(tags):
        col = RED if i % 2 == 0 else BLUE
        tw = 9 * len(tag) + 20
        tag_svg.append(f'<rect x="{x}" y="176" width="{tw}" height="24" rx="4" fill="none" stroke="{col}" stroke-width="1.5"/>'
                       f'<text x="{x + tw / 2}" y="193" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{col}">{escape(tag)}</text>')
        x += tw + 8
    stamp = ""
    if status:
        stamp = (f'<g transform="rotate(-8 330 34)"><rect x="262" y="16" width="136" height="34" fill="none" stroke="{RED}" stroke-width="3"/>'
                 f'<text x="330" y="40" text-anchor="middle" font-family="{DISPLAY}" font-size="20" fill="{RED}" letter-spacing="2">{escape(status)}</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="220" viewBox="0 0 420 220" role="img" aria-label="Issue {issue}: {escape(title)}. {escape(desc)}">
<defs><pattern id="d" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="1.8" fill="{RED}"/></pattern></defs>
<rect x="3" y="3" width="414" height="214" fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="4"/>
<polygon points="330,3 417,3 417,90" fill="url(#d)" opacity="0.7"/>
<rect x="24" y="22" width="118" height="26" fill="{YELLOW}" stroke="{INK}" stroke-width="2"/>
<text x="83" y="41" text-anchor="middle" font-family="{DISPLAY}" font-size="16" fill="{INK}" letter-spacing="1">ISSUE #{issue}</text>
<text x="24" y="82" font-family="{DISPLAY}" font-size="30" fill="{t["fg"]}" letter-spacing="1">{escape(title.upper())}</text>
{desc_svg}
{"".join(tag_svg)}
{stamp}
</svg>'''


MISSIONS = [
    ("01", "Ember", "My current main build. Fresh repo, the story is still being written.", ["JavaScript"], None),
    ("02", "Web Automations", "Test automation framework for a banking web application.", ["Java", "Selenium"], None),
    ("03", "Ticketing Sim", "Real-time event ticketing simulation with producers and consumers.", ["Angular", "TypeScript"], None),
    ("04", "Game AI", "Unity game AI coursework: agent behaviours, steering and shaders.", ["C#", "Unity", "HLSL"], None),
    ("05", "Machine Learning", "Notebooks and experiments: models, data wrangling and evaluation.", ["Python", "Jupyter"], None),
    ("06", "Property Finder", "Responsive single-page property search app with filters and favourites.", ["React", "JavaScript"], None),
    ("07", "InfluencerHub", "Platform connecting brands with influencers. Live demo available.", ["JavaScript", "Vercel"], "CLASSIFIED"),
    ("08", "Nive E-commerce", "Full e-commerce storefront with a Postgres backend.", ["Next.js", "Postgres"], "CLASSIFIED"),
]

CAPTIONS = {
    "about": "MEANWHILE, IN THE TERMINAL...",
    "stack": "SPIDER-SENSE STACK",
    "stats": "POWER LEVELS",
    "missions": "PINNED MISSIONS",
    "classified": "CLASSIFIED FILES",
    "web": "THE WEB I'VE SPUN",
    "contact": "SIGNAL THE SPIDER",
}


def main():
    (OUT / "cards").mkdir(parents=True, exist_ok=True)
    (OUT / "captions").mkdir(parents=True, exist_ok=True)
    for mode in THEMES:
        (OUT / f"banner-{mode}.svg").write_text(banner(mode), encoding="utf-8")
        (OUT / f"divider-{mode}.svg").write_text(divider(mode), encoding="utf-8")
        for issue, title, desc, tags, status in MISSIONS:
            (OUT / "cards" / f"{issue}-{mode}.svg").write_text(card(mode, issue, title, desc, tags, status), encoding="utf-8")
    for i, (key, text) in enumerate(CAPTIONS.items()):
        (OUT / "captions" / f"{key}.svg").write_text(caption(text, -1.5 if i % 2 else 1.2), encoding="utf-8")
    print(f"Wrote assets to {OUT}")


if __name__ == "__main__":
    main()
