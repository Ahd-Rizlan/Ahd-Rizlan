"""Generates the static cartoon SVG artwork for the profile README.

Run from the repo root:  python scripts/generate_assets.py
Outputs go to assets/. Everything is original artwork; the mascot is
Webby, an original spider, not any official character.
"""
import base64
import math
import textwrap
from html import escape

from cartoon import (BLUE, COMIC, INK, MONO, RED, ROOT, THEMES, WHITE, YELLOW, burst, comic_text,
                     mascot, mini_spider, pill, shadow_box, style)

OUT = ROOT / "assets"
BODY = "'Trebuchet MS', Verdana, sans-serif"


def sunburst(cx, cy, color, n=22, r=1200):
    wedges = []
    for i in range(0, n * 2, 2):
        a1, a2 = math.pi * i / n, math.pi * (i + 1) / n
        wedges.append(f'<polygon points="{cx},{cy} {cx + r * math.cos(a1):.0f},{cy + r * math.sin(a1):.0f} '
                      f'{cx + r * math.cos(a2):.0f},{cy + r * math.sin(a2):.0f}"/>')
    return f'<g fill="{color}" class="spin" style="transform-origin:{cx}px {cy}px">{"".join(wedges)}</g>'


def skyline(t, w, base):
    """Rounded cartoon buildings along the bottom edge."""
    out, x, i = [], -10, 0
    heights = [70, 110, 85, 140, 95, 60, 125, 80, 150, 90, 115, 70, 135, 100]
    while x < w:
        bw = 70 + (i * 37) % 40
        bh = heights[i % len(heights)]
        y = base - bh
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh + 20}" rx="10" fill="{t["city"]}" stroke="{INK}" stroke-width="4"/>')
        for wy in range(y + 16, base - 10, 26):
            for wx in range(x + 12, x + bw - 16, 22):
                if (wx * 7 + wy * 3 + i) % 5 < 2:
                    out.append(f'<rect x="{wx}" y="{wy}" width="10" height="12" rx="2" fill="{t["window"]}" class="win" '
                               f'style="animation-delay:{(wx + wy) % 7 * 0.6:.1f}s"/>')
        x += bw - 4
        i += 1
    return "".join(out)


def sparkle(x, y, s, delay):
    return (f'<path class="twinkle" style="animation-delay:{delay}s;transform-origin:{x}px {y}px" '
            f'd="M{x},{y - s} Q{x + s * .15},{y - s * .15} {x + s},{y} Q{x + s * .15},{y + s * .15} {x},{y + s} '
            f'Q{x - s * .15},{y + s * .15} {x - s},{y} Q{x - s * .15},{y - s * .15} {x},{y - s} z" '
            f'fill="{YELLOW}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')


def drips(color, base, xs):
    """Spray-paint drips hanging off a line of lettering."""
    out = []
    for i, x in enumerate(xs):
        ln = 22 + (i * 17) % 26
        out.append(f'<path class="drip" style="animation-delay:{i * .5:.1f}s" d="M{x - 6},{base - 8} L{x - 5},{base + ln} '
                   f'a6,6 0 0 0 12,0 L{x + 6},{base - 8} Z" fill="{color}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
    return "".join(out)


def graffiti():
    """Tags sprayed on the buildings."""
    tags = [(770, 402, "BK", BLUE, -8, 30), (836, 396, "1610", YELLOW, 6, 24), (912, 404, "THWIP", RED, -5, 26),
            (34, 404, "W!", YELLOW, -10, 28), (1130, 400, "NYC", BLUE, 7, 22)]
    out = []
    for x, y, text, col, rot, size in tags:
        out.append(f'<g transform="rotate({rot} {x} {y})">{comic_text(x, y, text, size, col, anchor="middle", sw=5, off=0)}</g>')
    splats = [(800, 372, 5, RED), (880, 368, 3, BLUE), (950, 376, 4, YELLOW), (60, 372, 4, BLUE)]
    out += [f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in splats]
    return "".join(out)


def banner(mode):
    t = THEMES[mode]
    w, h = 1200, 420
    css = style(
        ".spin { animation: spin 60s linear infinite; }",
        "@keyframes spin { to { transform: rotate(360deg); } }",
        ".bob { animation: bob 2.6s ease-in-out infinite alternate; }",
        "@keyframes bob { from { transform: translate(1010px, 205px) rotate(-3deg); } to { transform: translate(1010px, 235px) rotate(3deg); } }",
        ".wobble { animation: wobble 3s ease-in-out infinite alternate; transform-origin: 320px 250px; }",
        "@keyframes wobble { from { transform: rotate(-4deg); } to { transform: rotate(-2deg) scale(1.02); } }",
        ".pow { animation: pow 1.6s ease-in-out infinite; }",
        "@keyframes pow { 0%,100% { transform: scale(1) rotate(-8deg); } 50% { transform: scale(1.12) rotate(4deg); } }",
        ".twinkle { animation: tw 1.8s ease-in-out infinite; }",
        "@keyframes tw { 0%,100% { transform: scale(.4); opacity: .3; } 50% { transform: scale(1); opacity: 1; } }",
        ".win { animation: win 4.2s steps(1) infinite; }",
        "@keyframes win { 0%,70% { opacity: 1; } 71%,100% { opacity: .25; } }",
        ".gb { animation: gb 3.2s steps(1) infinite; } .gr { animation: gr 3.2s steps(1) infinite; }",
        "@keyframes gb { 0%,84%,100% { transform: translate(-7px,-3px); } 86% { transform: translate(-16px,4px); } 90% { transform: translate(6px,-6px); } }",
        "@keyframes gr { 0%,84%,100% { transform: translate(7px,3px); } 86% { transform: translate(14px,-4px); } 90% { transform: translate(-6px,6px); } }",
        ".drip { animation: drip 3.5s ease-in infinite; transform-box: fill-box; transform-origin: top; }",
        "@keyframes drip { 0% { transform: scaleY(.3); } 60%,100% { transform: scaleY(1); } }",
        ".mist { animation: mist 1.2s ease-out infinite; }",
        "@keyframes mist { 0% { opacity: 1; transform: translate(0,0); } 100% { opacity: 0; transform: translate(10px,-14px); } }",
        ".bubble { animation: pop 2.6s ease-in-out infinite alternate; transform-origin: 770px 120px; }",
        "@keyframes pop { from { transform: scale(.96) rotate(2deg); } to { transform: scale(1.03) rotate(-1deg); } }",
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Cartoon banner: Ahamed Rizlan, software engineer from Sri Lanka. A cute spider in a hoodie, headphones and red sneakers hangs from a web holding a spray can and says Thwip, deployed. Graffiti tags cover the buildings.">
{css}
<defs>
  <clipPath id="frame"><rect x="6" y="6" width="{w - 12}" height="{h - 12}" rx="28"/></clipPath>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r="3" fill="{t["dot"]}" opacity="0.35"/></pattern>
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{t["bg"]}"/>
  {sunburst(470, 240, t["ray"])}
  <rect x="0" y="0" width="260" height="{h}" fill="url(#dots)"/>
  <rect x="940" y="0" width="260" height="{h}" fill="url(#dots)"/>
  {skyline(t, w, h)}
  {graffiti()}
  <g class="wobble">
    <g class="gb">{comic_text(84, 214, "AHAMED", 156, BLUE, sw=0, off=0)}{comic_text(150, 336, "RIZLAN", 156, BLUE, sw=0, off=0)}</g>
    <g class="gr">{comic_text(84, 214, "AHAMED", 156, RED, sw=0, off=0)}{comic_text(150, 336, "RIZLAN", 156, YELLOW, sw=0, off=0)}</g>
    {comic_text(84, 214, "AHAMED", 156, YELLOW, shadow=INK, off=8, sw=12)}
    {comic_text(150, 336, "RIZLAN", 156, RED, shadow=INK, off=8, sw=12)}
    {drips(RED, 336, [176, 232, 300, 352, 418])}
  </g>
  <g transform="translate(96 88)"><g class="pow">
    {burst(0, 0, 64, points=12, fill=YELLOW, sw=6)}
    {comic_text(0, 12, "POW!", 36, RED, anchor="middle", sw=6, off=0)}
  </g></g>
  {pill(96, 352, "SOFTWARE ENGINEER · SRI LANKA · JAVA · REACT", BLUE, size=24)[0]}
  <g class="bubble">
    <path d="M640,56 Q640,34 662,34 L878,34 Q900,34 900,56 L900,126 Q900,148 878,148 L840,148 L930,196 L790,148 L662,148 Q640,148 640,126 Z" fill="{INK}" transform="translate(7 7)"/>
    <path d="M640,56 Q640,34 662,34 L878,34 Q900,34 900,56 L900,126 Q900,148 878,148 L840,148 L930,196 L790,148 L662,148 Q640,148 640,126 Z" fill="{WHITE}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
    <text x="770" y="86" text-anchor="middle" font-family="{COMIC}" font-size="34" letter-spacing="1.5" fill="{RED}">THWIP!</text>
    <text x="770" y="126" text-anchor="middle" font-family="{COMIC}" font-size="30" letter-spacing="1.5" fill="{INK}">DEPLOYED.</text>
  </g>
  <g class="bob">{mascot(t["thread"])}</g>
  <g stroke="{t["fg"]}" stroke-width="4" stroke-linecap="round" fill="none" opacity="0.7">
    <path d="M1100,170 q14,10 0,24"/><path d="M1118,160 q20,20 0,44"/>
    <path d="M920,250 q-14,10 0,24"/>
  </g>
  {sparkle(560, 70, 16, 0)}{sparkle(1150, 330, 14, .6)}{sparkle(40, 260, 12, 1.1)}{sparkle(620, 300, 12, .3)}
</g>
<rect x="6" y="6" width="{w - 12}" height="{h - 12}" rx="28" fill="none" stroke="{INK}" stroke-width="8"/>
</svg>'''


def caption(text, color=YELLOW, seed=1):
    w = int(15.5 * len(text) + 96)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="74" viewBox="0 0 {w} 74" role="img" aria-label="{escape(text.title())}">
{style()}
<g transform="rotate({-1.5 if seed % 2 else 1.2} {w / 2} 37)">
  {shadow_box(30, 12, w - 46, 46, color, r=23, off=6, sw=4)}
  <text x="{(w + 30) / 2:.0f}" y="45" text-anchor="middle" font-family="{COMIC}" font-size="28" letter-spacing="1.5" fill="{INK}">{escape(text)}</text>
  {burst(32, 35, 26, points=9, fill=RED if seed % 2 else BLUE, sw=4, seed=seed)}
</g>
</svg>'''


def divider(mode):
    t = THEMES[mode]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="96" viewBox="0 0 1200 96" role="img" aria-label="Divider: a little spider bobbing on a web line">
{style(".bob { animation: bob 1.8s ease-in-out infinite alternate; }",
       "@keyframes bob { from { transform: translate(600px, 42px); } to { transform: translate(600px, 58px); } }")}
<path d="M0,14 Q300,40 600,14 Q900,40 1200,14" fill="none" stroke="{t["thread"]}" stroke-width="3" stroke-dasharray="2 8" stroke-linecap="round" opacity="0.8"/>
<g class="bob"><line x1="0" y1="-14" x2="0" y2="-70" stroke="{t["thread"]}" stroke-width="2.5"/><g transform="scale(1.5)">{mini_spider()}</g></g>
</svg>'''


def card(mode, issue, title, desc, tags, status=None):
    t = THEMES[mode]
    head = RED if int(issue) % 2 else BLUE
    lines = textwrap.wrap(desc, 44)[:3]
    desc_svg = "".join(
        f'<text x="28" y="{116 + i * 22}" font-family="{MONO}" font-size="14" fill="{t["muted"]}">{escape(l)}</text>'
        for i, l in enumerate(lines))
    tag_svg, x = [], 26
    for i, tag in enumerate(tags):
        p, pw = pill(x, 178, escape(tag.upper()), [YELLOW, WHITE, BLUE][i % 3], size=15, off=3)
        tag_svg.append(p)
        x += pw + 12
    stamp = ""
    if status:
        stamp = (f'<g transform="rotate(-10 330 168)"><rect x="250" y="146" width="160" height="44" rx="8" fill="none" stroke="{RED}" stroke-width="4"/>'
                 f'<text x="330" y="179" text-anchor="middle" font-family="{COMIC}" font-size="28" letter-spacing="2" fill="{RED}">{escape(status)}</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="250" viewBox="0 0 440 250" role="img" aria-label="Issue {issue}: {escape(title)}. {escape(desc)}">
{style()}
<defs><clipPath id="c"><rect x="6" y="6" width="420" height="226" rx="22"/></clipPath></defs>
{shadow_box(6, 6, 420, 226, t["panel"], r=22, off=9, sw=5)}
<g clip-path="url(#c)"><rect x="6" y="6" width="420" height="68" fill="{head}"/></g>
<line x1="6" y1="74" x2="426" y2="74" stroke="{INK}" stroke-width="5"/>
<rect x="6" y="6" width="420" height="226" rx="22" fill="none" stroke="{INK}" stroke-width="5"/>
{comic_text(28, 56, escape(title.upper()), 36, WHITE, shadow=INK, off=4, sw=7)}
{burst(384, 42, 40, points=10, wobble=0.1, fill=YELLOW, sw=4, seed=int(issue))}
<text x="384" y="50" text-anchor="middle" font-family="{COMIC}" font-size="21" fill="{INK}">#{issue}</text>
{desc_svg}
{"".join(tag_svg)}
{stamp}
</svg>'''


def avatar_uri(name):
    data = (OUT / "avatars" / f"{name}.png").read_bytes()
    mime = "image/png" if data[1:4] == b"PNG" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def team_card(mode, slug, title, role, desc, tags, current=False):
    """Organization card: logo in a round comic frame, NOW! burst for the current job."""
    t = THEMES[mode]
    head = YELLOW if current else t["city"]
    title_fill = RED if current else WHITE
    lines = textwrap.wrap(desc, 44)[:3]
    desc_svg = "".join(
        f'<text x="28" y="{136 + i * 22}" font-family="{MONO}" font-size="14" fill="{t["muted"]}">{escape(l)}</text>'
        for i, l in enumerate(lines))
    tag_svg, x = [], 26
    for i, tag in enumerate(tags):
        p, pw = pill(x, 198, escape(tag.upper()), [YELLOW, WHITE, BLUE][i % 3], size=15, off=3)
        tag_svg.append(p)
        x += pw + 12
    badge = (f'<g class="pulse">{burst(384, 46, 44, points=12, fill=RED, sw=4, wobble=0.1)}'
             f'<text x="384" y="56" text-anchor="middle" font-family="{COMIC}" font-size="26" letter-spacing="1" fill="{WHITE}" '
             f'stroke="{INK}" stroke-width="4" paint-order="stroke">NOW!</text></g>') if current else ""
    css = style(".pulse { animation: pulse 1.4s ease-in-out infinite; transform-origin: 384px 46px; }",
                "@keyframes pulse { 50% { transform: scale(1.12) rotate(6deg); } }") if current else style()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="270" viewBox="0 0 440 270" role="img" aria-label="{escape(title)}: {escape(role)}. {escape(desc)}">
{css}
<defs>
  <clipPath id="c"><rect x="6" y="6" width="420" height="246" rx="22"/></clipPath>
  <clipPath id="logo"><circle cx="62" cy="62" r="34"/></clipPath>
</defs>
{shadow_box(6, 6, 420, 246, t["panel"], r=22, off=9, sw=5)}
<g clip-path="url(#c)"><rect x="6" y="6" width="420" height="86" fill="{head}"/></g>
<line x1="6" y1="92" x2="426" y2="92" stroke="{INK}" stroke-width="5"/>
<rect x="6" y="6" width="420" height="246" rx="22" fill="none" stroke="{INK}" stroke-width="5"/>
<circle cx="66" cy="66" r="38" fill="{INK}"/>
<circle cx="62" cy="62" r="38" fill="{WHITE}"/>
<image href="{avatar_uri(slug)}" x="28" y="28" width="68" height="68" clip-path="url(#logo)" preserveAspectRatio="xMidYMid slice"/>
<circle cx="62" cy="62" r="36" fill="none" stroke="{INK}" stroke-width="5"/>
{comic_text(114, 58, escape(title.upper()), 34, title_fill, shadow=INK, off=4, sw=7)}
<text x="116" y="80" font-family="{COMIC}" font-size="17" letter-spacing="1" fill="{INK if current else BLUE}">{escape(role.upper())}</text>
{desc_svg}
{"".join(tag_svg)}
{badge}
</svg>'''


TEAMS = [
    ("Pacto-Code", "Pacto Code", "Org admin",
     "Dev studio work: portfolios, digital vCards and sites for Blinksky Productions.", ["TypeScript", "React"], False),
    ("SGDP-group", "SGDP Group", "Org admin",
     "FocusFrame: gaze tracking, an AI focus agent, a smart desk clock and a mobile app.", ["Python", "Java", "C"], False),
    ("AssuraSolutions", "Assura Solutions", "Member",
     "Client builds: logistics platforms and e-commerce storefronts.", ["TypeScript", "Next.js"], False),
]


def fact_panel(mode, n, question, answer, color):
    """Comic panel: question in a caption box, Webby answering in a speech bubble."""
    t = THEMES[mode]
    lines = textwrap.wrap(answer, 27)[:6]
    top = 150 - len(lines) * 11
    text = "".join(
        f'<text x="290" y="{top + i * 22}" text-anchor="middle" font-family="{BODY}" '
        f'font-size="15" font-weight="bold" fill="{INK}">{escape(l)}</text>'
        for i, l in enumerate(lines))
    bubble = "M176,74 Q176,58 192,58 L404,58 Q420,58 420,74 L420,226 Q420,242 404,242 L192,242 Q176,242 176,226 L176,170 L148,184 L176,146 Z"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="270" viewBox="0 0 440 270" role="img" aria-label="{escape(question)} {escape(answer)}">
{style(".bob { animation: bob 2.4s ease-in-out infinite alternate; }",
       f"@keyframes bob {{ from {{ transform: translate(80px, 170px) scale(.62) rotate(-4deg); }} to {{ transform: translate(80px, 180px) scale(.62) rotate(4deg); }} }}")}
<defs>
  <clipPath id="c"><rect x="6" y="6" width="420" height="246" rx="22"/></clipPath>
  <pattern id="d" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="6" cy="6" r="2" fill="{RED}" opacity="0.3"/></pattern>
</defs>
{shadow_box(6, 6, 420, 246, t["panel"], r=22, off=9, sw=5)}
<g clip-path="url(#c)">
  <rect x="6" y="6" width="420" height="246" fill="url(#d)"/>
  <g class="bob">{mascot(t["thread"], thread_len=300)}</g>
</g>
<rect x="6" y="6" width="420" height="246" rx="22" fill="none" stroke="{INK}" stroke-width="5"/>
<g transform="rotate(-2 120 30)">{shadow_box(18, 14, 26 + 12.5 * len(question), 38, color, r=8, off=4, sw=4)}
<text x="{31 + 6.25 * len(question):.0f}" y="41" text-anchor="middle" font-family="{COMIC}" font-size="23" letter-spacing="1" fill="{INK}">{escape(question.upper())}</text></g>
<path d="{bubble}" fill="{INK}" transform="translate(6 6)"/>
<path d="{bubble}" fill="{WHITE}" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>
{text}
<text x="404" y="18" text-anchor="end" font-family="{COMIC}" font-size="16" fill="{t["muted"]}">#{n}</text>
</svg>'''


FACTS = [
    ("Favourite language?", "Can't pick just one. Every language is a new universe, and each one hands me a new superpower.", YELLOW),
    ("Proudest project?", "The one fighting back right now. Every project throws a new villain at me, and I swing out with fresh ideas and sharper skills.", BLUE),
    ("Currently learning?", "Everything the world is willing to teach me. The syllabus never ends, and that's the fun part.", RED),
    ("Off the keyboard?", "Smashing boundaries on the cricket pitch, or lost in a playlist with the volume all the way up.", YELLOW),
    ("Fave Spider-Verse moment?", "Miles deciding he's gonna do his own thing. That's exactly the energy I bring to every line of code.", BLUE),
]


MISSIONS = [
    ("01", "Ember", "My current main build. Fresh repo, the story is still being written.", ["JavaScript"], None),
    ("02", "Web Automations", "Test automation framework for a banking web application.", ["Java", "Selenium"], None),
    ("03", "Ticketing Sim", "Real-time event ticketing simulation with producers and consumers.", ["Angular", "TypeScript"], None),
    ("04", "Game AI", "Unity game AI coursework: agent behaviours, steering and shaders.", ["C#", "Unity", "HLSL"], None),
    ("05", "Machine Learning", "Notebooks and experiments: models, data wrangling and evaluation.", ["Python", "Jupyter"], None),
    ("06", "Property Finder", "Responsive single-page property search app with filters and favourites.", ["React", "JavaScript"], None),
    ("07", "InfluencerHub", "Platform connecting brands with influencers. Live demo available.", ["JavaScript", "Vercel"], "TOP SECRET"),
    ("08", "Nive Store", "Full e-commerce storefront with a Postgres backend.", ["Next.js", "Postgres"], "TOP SECRET"),
]

CAPTIONS = {
    "about": "MEANWHILE, IN THE TERMINAL...",
    "stack": "SPIDER-SENSE STACK",
    "stats": "POWER LEVELS",
    "missions": "PINNED MISSIONS",
    "classified": "CLASSIFIED FILES",
    "teams": "TEAM-UPS",
    "web": "THE WEB I'VE SPUN",
    "facts": "ENTER THE SPIDER-VERSE",
    "contact": "SIGNAL THE SPIDER",
}


def main():
    (OUT / "cards").mkdir(parents=True, exist_ok=True)
    (OUT / "captions").mkdir(parents=True, exist_ok=True)
    (OUT / "teams").mkdir(parents=True, exist_ok=True)
    (OUT / "facts").mkdir(parents=True, exist_ok=True)
    for mode in THEMES:
        (OUT / f"banner-{mode}.svg").write_text(banner(mode), encoding="utf-8")
        (OUT / f"divider-{mode}.svg").write_text(divider(mode), encoding="utf-8")
        for issue, title, desc, tags, status in MISSIONS:
            (OUT / "cards" / f"{issue}-{mode}.svg").write_text(card(mode, issue, title, desc, tags, status), encoding="utf-8")
        for n, (question, answer, color) in enumerate(FACTS, 1):
            (OUT / "facts" / f"{n:02}-{mode}.svg").write_text(fact_panel(mode, f"{n:02}", question, answer, color), encoding="utf-8")
        for slug, title, role, desc, tags, current in TEAMS:
            (OUT / "teams" / f"{slug}-{mode}.svg").write_text(team_card(mode, slug, title, role, desc, tags, current), encoding="utf-8")
    for i, (key, text) in enumerate(CAPTIONS.items()):
        (OUT / "captions" / f"{key}.svg").write_text(caption(text, seed=i + 1), encoding="utf-8")
    print(f"Wrote assets to {OUT}")


if __name__ == "__main__":
    main()
