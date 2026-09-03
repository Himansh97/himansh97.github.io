#!/usr/bin/env python3
"""Render the link-preview cards.

Pasting the site into LinkedIn, Slack or an email produced a bare grey box,
because there was no og:image anywhere. LinkedIn is the actual distribution
channel for a job search, which made this the highest-leverage missing thing
on the site and also the cheapest.

Cards are drawn as SVG and rasterised by headless Chrome, which is already a
dependency of nothing -- it is just installed. No Pillow, no ImageMagick, no
node_modules. Same evidence-first treatment as the pages: a name, one line,
and the figures that back it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "assets" / "og"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 1200x630 is the size LinkedIn, Slack and Twitter all crop from.
W, H = 1200, 630

PAPER = "#FAFAF8"
INK = "#16161A"
SOFT = "#55554F"
FAINT = "#6E6D66"
RULE = "#CFCEC4"
RED = "#D92906"

CARDS = {
    "og-home.png": {
        "eyebrow": "HIMANSHU SRIVASTAVA",
        "line1": "I build systems that know",
        "line2": "what they can’t prove.",
        "accent": "And stop.",
        "sub": "Data and analytics engineering · mortgage and financial services · Dallas, TX",
        "facts": [("4", "PyPI releases"), ("39,130", "records read"), ("457", "backend tests"), ("0", "auto-submits")],
    },
    "og-custody.png": {
        "eyebrow": "CUSTODY",
        "line1": "Prove what your AI did",
        "line2": "to a loan.",
        "accent": "Including when it was wrong.",
        "sub": "A signed chain of evidence for AI decisions in mortgage lending",
        "facts": [("4", "releases"), ("92", "tests"), ("11", "test files"), ("1", "dependency")],
    },
    "og-register.png": {
        "eyebrow": "REGISTER SIGNAL",
        "line1": "Three public registers.",
        "line2": "39,130 records.",
        "accent": "One says nothing.",
        "sub": "Dated, named reasons to contact a pharmaceutical company",
        "facts": [("3", "registers"), ("39,130", "records"), ("6,899", "triggers"), ("0", "from Tanzania")],
    },
    "og-careeros.png": {
        "eyebrow": "CAREEROS",
        "line1": "A job search that cannot",
        "line2": "say anything I have not done.",
        "accent": "By construction.",
        "sub": "Evidence-constrained resume tailoring, with a containment gate in front",
        "facts": [("457", "backend tests"), ("88", "endpoints"), ("281", "commits"), ("9", "job boards")],
    },
    "og-optionora.png": {
        "eyebrow": "OPTIONORA",
        "line1": "Seven strategies measured.",
        "line2": "None of them proven.",
        "accent": "Published anyway.",
        "sub": "A decision layer that reports its own uncertainty instead of a number",
        "facts": [("801", "tests"), ("82", "test files"), ("7", "strategies"), ("0", "proven")],
    },
}
CARDS["og-default.png"] = CARDS["og-home.png"]


def svg(card: dict) -> str:
    facts = []
    for i, (value, label) in enumerate(card["facts"]):
        x = 88 + i * 268
        facts.append(
            f'<text x="{x}" y="540" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'font-size="40" font-weight="700" fill="{INK}">{value}</text>'
            f'<text x="{x}" y="568" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
            f'font-size="15" letter-spacing="1.6" fill="{FAINT}">{label.upper()}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{PAPER}"/>
  <rect x="0" y="0" width="{W}" height="8" fill="{INK}"/>
  <text x="88" y="112" font-family="ui-monospace,SFMono-Regular,Menlo,monospace"
        font-size="17" letter-spacing="5" fill="{SOFT}">{card['eyebrow']}</text>
  <text x="88" y="228" font-family="Helvetica Neue,Helvetica,Arial,sans-serif"
        font-size="66" font-weight="700" letter-spacing="-2" fill="{INK}">{card['line1']}</text>
  <text x="88" y="304" font-family="Helvetica Neue,Helvetica,Arial,sans-serif"
        font-size="66" font-weight="700" letter-spacing="-2" fill="{INK}">{card['line2']}</text>
  <text x="88" y="380" font-family="Helvetica Neue,Helvetica,Arial,sans-serif"
        font-size="66" font-weight="700" letter-spacing="-2" fill="{RED}">{card['accent']}</text>
  <text x="88" y="440" font-family="Helvetica Neue,Helvetica,Arial,sans-serif"
        font-size="23" fill="{SOFT}">{card['sub']}</text>
  <line x1="88" y1="486" x2="{W-88}" y2="486" stroke="{RULE}" stroke-width="1"/>
  {''.join(facts)}
</svg>"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "_card.html"
    made = []
    for name, card in CARDS.items():
        tmp.write_text(
            f'<body style="margin:0">{svg(card)}</body>'
        )
        target = OUT / name
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             f"--window-size={W},{H}", f"--screenshot={target}", f"file://{tmp}"],
            capture_output=True, check=True,
        )
        if not target.exists():
            print(f"  FAIL {name}", file=sys.stderr)
            return 1
        made.append((name, target.stat().st_size))
    tmp.unlink(missing_ok=True)
    for name, size in made:
        print(f"  {name:22} {size//1024:3} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
