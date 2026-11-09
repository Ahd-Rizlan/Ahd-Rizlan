"""Shared Saturday-morning-cartoon toolkit for every SVG in the profile.

Thick ink outlines, hard offset shadows, starburst bubbles, the embedded
Bangers comic font (OFL, see fonts/Bangers-OFL.txt) and Webby, the
original spider mascot.
"""
import base64
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RED = "#E23636"
BLUE = "#00D4FF"
YELLOW = "#FFE14D"
PINK = "#FF8FA3"
INK = "#0B0B0B"
WHITE = "#FFFFFF"

THEMES = {
    "dark": {"bg": "#0F0B0E", "ray": "#22090D", "fg": WHITE, "muted": "#C9B9BE", "panel": "#1C1418",
             "city": "#1A1216", "window": RED, "dot": RED, "shadow": INK, "thread": WHITE},
    "light": {"bg": "#FFF4E8", "ray": "#FFD9D4", "fg": INK, "muted": "#4A3F45", "panel": WHITE,
              "city": "#2A2126", "window": YELLOW, "dot": RED, "shadow": INK, "thread": INK},
}

COMIC = "Bangers, Impact, 'Arial Black', sans-serif"
MONO = "'Fira Code', Consolas, monospace"

FONT_FILE = ROOT / "fonts" / "Bangers-subset.woff"
FONT_SLOT = "/*BANGERS*/"

REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"
# Cards rendered narrower than this (two-up on a phone) switch to their compact layout.
COMPACT = ("@media (max-width: 330px) { .full { display: none; } }"
           "@media (min-width: 331px) { .compact { display: none; } }")


def style(*rules):
    return "<style>" + FONT_SLOT + "\n" + "\n".join(rules) + "\n" + REDUCED + "</style>"


_subset_cache = {}


def _font_css(chars):
    """Bangers trimmed to just the characters one image uses."""
    key = "".join(sorted(chars))
    if key not in _subset_cache:
        import io
        from fontTools import subset
        from fontTools.ttLib import TTFont
        font = TTFont(FONT_FILE)
        opts = subset.Options()
        opts.flavor = "woff"
        sub = subset.Subsetter(opts)
        sub.populate(text=key)
        sub.subset(font)
        buf = io.BytesIO()
        font.flavor = "woff"
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        _subset_cache[key] = f"@font-face {{ font-family: Bangers; src: url(data:font/woff;base64,{data}) format('woff'); }}"
    return _subset_cache[key]


def save(path, svg):
    """Embed the trimmed font and write the SVG."""
    import html
    import re
    chars = set()
    for m in re.finditer(r'<text[^>]*font-family="Bangers[^>]*>(.*?)</text>', svg, re.S):
        chars |= set(html.unescape(re.sub(r"<[^>]+>", "", m.group(1))))
    css = _font_css(chars | {" "}) if chars else ""
    path.write_text(svg.replace(FONT_SLOT, css), encoding="utf-8")


def burst(cx, cy, r, points=12, fill=YELLOW, stroke=INK, sw=5, wobble=0.18, seed=1):
    """Spiky cartoon starburst."""
    pts = []
    for i in range(points * 2):
        a = math.pi * i / points - math.pi / 2
        jitter = 1 + wobble * math.sin(seed * 7.3 + i * 2.1)
        rr = (r if i % 2 == 0 else r * 0.62) * jitter
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def shadow_box(x, y, w, h, fill, r=18, off=8, sw=5, shadow=INK):
    """Rounded box with a thick outline and a hard offset shadow."""
    return (f'<rect x="{x + off}" y="{y + off}" width="{w}" height="{h}" rx="{r}" fill="{shadow}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')


def comic_text(x, y, text, size, fill, anchor="start", stroke=INK, sw=None, shadow=None, off=None, extra=""):
    """Comic lettering: ink outline behind the fill, optional offset shadow copy."""
    sw = sw if sw is not None else max(3, size // 9)
    off = off if off is not None else max(3, size // 16)
    base = (f'font-family="{COMIC}" font-size="{size}" text-anchor="{anchor}" letter-spacing="{size / 30:.1f}" '
            f'stroke-linejoin="round" paint-order="stroke"')
    out = ""
    if shadow:
        out += f'<text x="{x + off}" y="{y + off}" {base} fill="{shadow}" stroke="{stroke}" stroke-width="{sw}">{text}</text>'
    out += f'<text x="{x}" y="{y}" {base} fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}>{text}</text>'
    return out


ODOMETER_CSS = (".odo { animation: roll 1.6s cubic-bezier(.2, .8, .2, 1) backwards; }",
                "@keyframes roll { from { transform: translateY(0); } }")


def odometer(x, y, value, size, fill, uid, anchor="end", delay=0.0, stroke=None):
    """A number whose digits roll up from 0 when the image loads.

    Each digit is a 0-9 strip behind a clip; its resting transform shows the
    real digit, so with reduced motion the final number simply appears.
    Needs ODOMETER_CSS in the image's style().
    """
    text = f"{value:,}"
    dw, cw, lh = size * 0.5, size * 0.26, size * 1.15
    width = sum(cw if ch == "," else dw for ch in text)
    x0 = x - width if anchor == "end" else x - width / 2 if anchor == "middle" else x
    st = (f' stroke="{stroke}" stroke-width="{size // 7}" paint-order="stroke" stroke-linejoin="round"'
          if stroke else "")
    out = [f'<defs><clipPath id="odo{uid}"><rect x="{x0 - 6:.1f}" y="{y - size * 0.92:.1f}" '
           f'width="{width + 12:.1f}" height="{size * 1.18:.1f}"/></clipPath></defs><g clip-path="url(#odo{uid})">']
    cx, k = x0, 0
    for ch in text:
        if ch == ",":
            out.append(f'<text x="{cx + cw / 2:.1f}" y="{y}" text-anchor="middle" font-family="{COMIC}" '
                       f'font-size="{size}" fill="{fill}"{st}>,</text>')
            cx += cw
            continue
        shift = int(ch) * lh
        strip = "".join(f'<text x="{cx + dw / 2:.1f}" y="{y + n * lh:.1f}" text-anchor="middle" font-family="{COMIC}" '
                        f'font-size="{size}" fill="{fill}"{st}>{n}</text>' for n in range(10))
        out.append(f'<g class="odo" style="transform: translateY(-{shift:.1f}px); animation-delay: {delay + k * 0.09:.2f}s">'
                   f'{strip}</g>')
        cx += dw
        k += 1
    out.append("</g>")
    return "".join(out)


def pill(x, y, text, fill, fg=INK, size=16, off=4):
    w = size * 0.62 * len(text) + 26
    h = size + 16
    return (shadow_box(x, y, w, h, fill, r=h / 2, off=off, sw=3) +
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + size * 0.36:.1f}" text-anchor="middle" font-family="{COMIC}" '
            f'font-size="{size}" letter-spacing="1" fill="{fg}">{text}</text>'), w


HOODIE = "#2B2B33"


def sneaker(x, y, flip=1):
    """Red high-top on a leg tip."""
    s = flip
    return (f'<g transform="translate({x} {y}) scale({s} 1)">'
            f'<path d="M-8,-14 L4,-14 L6,-2 Q20,0 22,8 L22,12 L-10,12 Z" fill="{RED}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            f'<rect x="-11" y="10" width="35" height="7" rx="3" fill="{WHITE}" stroke="{INK}" stroke-width="3.5"/>'
            f'<path d="M-4,-8 L4,-6 M-3,-2 L6,0" stroke="{WHITE}" stroke-width="2.5" stroke-linecap="round"/></g>')


def mascot(thread=WHITE, thread_len=600):
    """Webby: an original cute spider in streetwear.

    Hoodie, blue headphones, red high-tops and a spray can. Drawn around
    (0, 0), body radius ~48. Includes the web thread going up.
    """
    legs = []
    for side in (-1, 1):
        for i, (ay, ky, fy) in enumerate([(-18, -46, -22), (-2, -20, 6), (14, 10, 40), (28, 46, 70)]):
            sx = side * 34
            kx = side * (72 + i * 4)
            fx = side * (92 - i * 6)
            legs.append(f'<path d="M{sx},{ay} Q{kx},{ky} {fx},{fy}"/>')
    return f'''<g>
  <line x1="0" y1="-44" x2="0" y2="{-thread_len}" stroke="{thread}" stroke-width="3"/>
  <g fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round">{"".join(legs)}</g>
  {sneaker(-80, 60, -1)}{sneaker(80, 60, 1)}
  <g transform="translate(96 -30) rotate(18)">
    <rect x="-10" y="-22" width="20" height="40" rx="5" fill="{BLUE}" stroke="{INK}" stroke-width="4"/>
    <rect x="-10" y="-8" width="20" height="9" fill="{YELLOW}" stroke="{INK}" stroke-width="3"/>
    <rect x="-5" y="-32" width="10" height="10" rx="2" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>
    <g fill="{RED}" class="mist"><circle cx="10" cy="-44" r="4"/><circle cx="20" cy="-52" r="3"/><circle cx="4" cy="-56" r="2.5"/><circle cx="24" cy="-40" r="2"/></g>
  </g>
  <path d="M-56,20 Q-62,-62 0,-70 Q62,-62 56,20 Q40,64 0,64 Q-40,64 -56,20 Z" fill="{INK}" transform="translate(6 6)"/>
  <path d="M-56,20 Q-62,-62 0,-70 Q62,-62 56,20 Q40,64 0,64 Q-40,64 -56,20 Z" fill="{HOODIE}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
  <ellipse cx="0" cy="4" rx="44" ry="44" fill="{RED}" stroke="{INK}" stroke-width="5"/>
  <path d="M-30,40 Q0,52 30,40 L26,64 L-26,64 Z" fill="{HOODIE}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
  <g stroke="{RED}" stroke-width="4" stroke-linecap="round"><path d="M-14,44 L-16,74"/><path d="M14,44 L16,74"/></g>
  <circle cx="-16" cy="76" r="4" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/><circle cx="16" cy="76" r="4" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>
  <ellipse cx="-16" cy="-22" rx="12" ry="7" fill="{WHITE}" opacity="0.35" transform="rotate(-25 -16 -22)"/>
  <path d="M-58,4 Q-58,-72 0,-72 Q58,-72 58,4" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>
  <path d="M-58,4 Q-58,-72 0,-72 Q58,-72 58,4" fill="none" stroke="{BLUE}" stroke-width="8" stroke-linecap="round"/>
  <rect x="-70" y="-14" width="22" height="34" rx="10" fill="{BLUE}" stroke="{INK}" stroke-width="5"/>
  <rect x="48" y="-14" width="22" height="34" rx="10" fill="{BLUE}" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="-17" cy="-4" rx="15" ry="19" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>
  <ellipse cx="17" cy="-4" rx="15" ry="19" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>
  <circle cx="-13" cy="-1" r="8" fill="{INK}"/><circle cx="21" cy="-1" r="8" fill="{INK}"/>
  <circle cx="-10" cy="-5" r="3" fill="{WHITE}"/><circle cx="24" cy="-5" r="3" fill="{WHITE}"/>
  <ellipse cx="-30" cy="22" rx="8" ry="5" fill="{PINK}" opacity="0.8"/>
  <ellipse cx="30" cy="22" rx="8" ry="5" fill="{PINK}" opacity="0.8"/>
  <path d="M-10,24 Q0,36 10,24" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>
</g>'''


def mini_spider():
    """Small version of Webby for tight spots (the contribution graph)."""
    return f'''<g transform="scale(0.32)">
  <g fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round">
    <path d="M-34,-10 Q-80,-40 -96,-6"/><path d="M-34,10 Q-84,6 -96,40"/>
    <path d="M34,-10 Q80,-40 96,-6"/><path d="M34,10 Q84,6 96,40"/>
  </g>
  <ellipse cx="0" cy="4" rx="50" ry="48" fill="{RED}" stroke="{INK}" stroke-width="8"/>
  <path d="M-58,4 Q-58,-72 0,-72 Q58,-72 58,4" fill="none" stroke="{BLUE}" stroke-width="12" stroke-linecap="round"/>
  <ellipse cx="-17" cy="-4" rx="15" ry="19" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="17" cy="-4" rx="15" ry="19" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>
  <circle cx="-13" cy="-1" r="9" fill="{INK}"/><circle cx="21" cy="-1" r="9" fill="{INK}"/>
</g>'''
