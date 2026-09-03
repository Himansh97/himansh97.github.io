#!/usr/bin/env python3
"""Stamp the shared head, nav and footer onto every page.

The site was seven hand-written files that each carried their own copy of the
chrome, and the copies had drifted: three different palettes, three different
conventions for "go home", two pages with no links at all, and not one
`<!doctype>` between them. Every one of those is a defect that only exists
because the chrome was written seven times.

So it is written once, here. A page in `src/` is a body fragment plus a
metadata entry in PAGES below; this produces the finished HTML. No
dependencies, no node_modules, no install step -- `python3 build.py` and push.

Deliberately not a static-site generator. The whole site is nine pages of
hand-written HTML whose value is the writing, and a framework would add a
build toolchain to solve a problem that is really "the header was copied".
"""

from __future__ import annotations

import html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
SITE = "https://himansh97.github.io"


@dataclass
class Page:
    """One page: where it comes from, where it goes, and what the head says."""

    src: str
    out: str
    title: str
    description: str
    # Extra <style>/<script> the page needs that the shared sheet should not
    # carry. Kept in the fragment itself; this is only the og image name.
    og: str = "og-default.png"
    nav_label: str = ""
    in_nav: bool = True
    extra_head: str = ""
    body_class: str = ""
    scripts: list[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"{SITE}/{self.out}" if self.out != "index.html" else f"{SITE}/"

    @property
    def href(self) -> str:
        """Root-relative, so one nav string works from any directory depth."""
        return "/" if self.out == "index.html" else f"/{self.out}"


PAGES: list[Page] = [
    Page(
        src="index.html",
        out="index.html",
        title="Himanshu Srivastava - Data and Analytics Engineering",
        description=(
            "Data and analytics engineer in Dallas. Mortgage GL reconciliation, "
            "Ginnie Mae pool delivery, and the evidence controls that make "
            "automated output checkable. Live demos, published code."
        ),
        og="og-home.png",
        nav_label="Home",
        in_nav=False,
        extra_head='<link rel="stylesheet" href="/assets/home.css">\n',
    ),
    Page(
        src="custody.html",
        out="work/custody.html",
        title="Custody - Himanshu Srivastava",
        description=(
            "A signed chain of evidence for AI decisions in mortgage lending. "
            "Published to PyPI, 92 tests, and a demo in your browser that lets "
            "you break the chain and watch verification fail."
        ),
        og="og-custody.png",
        nav_label="Custody",
    ),
    Page(
        src="register-signal.html",
        out="work/register-signal.html",
        title="Register Signal - Himanshu Srivastava",
        description=(
            "Reads three national medicines registers, 39,130 records, and "
            "produces dated reasons to contact a pharmaceutical company. "
            "One register returns nothing, on purpose."
        ),
        og="og-register.png",
        nav_label="Register Signal",
        extra_head='<link rel="stylesheet" href="/assets/case.css">\n',
    ),
    Page(
        src="careeros.html",
        out="work/careeros.html",
        title="CareerOS - Himanshu Srivastava",
        description=(
            "A job search that cannot say anything I have not done. FastAPI and "
            "Next.js, 457 backend tests, and a containment gate that discards "
            "generated prose introducing unsupported claims."
        ),
        og="og-careeros.png",
        nav_label="CareerOS",
        extra_head='<link rel="stylesheet" href="/assets/case.css">\n',
    ),
    Page(
        src="optionora.html",
        out="work/optionora.html",
        title="Optionora - Himanshu Srivastava",
        description=(
            "A decision-readiness layer for short-dated options traders that "
            "publishes its own uncertainty. Seven strategies measured, none of "
            "them proven."
        ),
        og="og-optionora.png",
        nav_label="Optionora",
    ),
    Page(
        src="containment-gate.html",
        out="work/containment-gate.html",
        title="The containment gate - Himanshu Srivastava",
        description=(
            "A resume writer that cannot overstate its author. Try to make it "
            "claim something the evidence does not support, and watch it refuse."
        ),
        og="og-careeros.png",
        in_nav=False,
    ),
    Page(
        src="pipeline-hero.html",
        out="work/pipeline-hero.html",
        title="Ten thousand postings - Himanshu Srivastava",
        description=(
            "10,034 job postings went in, ten came out, and nothing sent itself. "
            "One run of the CareerOS discovery pipeline, drawn."
        ),
        og="og-careeros.png",
        in_nav=False,
    ),
]

NAV = [p for p in PAGES if p.in_nav]

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Himanshu Srivastava">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/assets/og/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{site}/assets/og/{og}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
{extra_head}</head>
<body{body_class}>
<a class="skip" href="#main">Skip to content</a>
<nav class="sitenav" aria-label="Primary">
  <div class="wrap">
    <a class="home" href="/">HIMANSHU SRIVASTAVA</a>
    <ul>
{navitems}
    </ul>
  </div>
</nav>
{body}
<footer class="sitefoot">
  <div class="wrap">
    <p>Open to data, analytics and engineering roles in the United States.
       The fastest way to reach me is email, and I answer everything.</p>
    <p><a href="mailto:hsrivast22@gmail.com">hsrivast22@gmail.com</a>
       &nbsp;/&nbsp; <a href="https://www.linkedin.com/in/himanshu-data-engineer/" rel="noopener">LinkedIn</a>
       &nbsp;/&nbsp; <a href="https://github.com/Himansh97" rel="noopener">GitHub</a></p>
    <p>Every figure on this site comes from a command that was run, not an estimate.</p>
  </div>
</footer>
{scripts}</body>
</html>
"""


# Pages that used to live at the repo root. These URLs are already public --
# https://himansh97.github.io/custody.html is the homepage field on the custody
# repository, so deleting it would 404 the link GitHub shows on that repo -- and
# a moved page that 404s is worse than one that never existed.
REDIRECTS = {
    "custody.html": "/work/custody.html",
    "careeros.html": "/work/careeros.html",
    "optionora.html": "/work/optionora.html",
    "containment-gate.html": "/work/containment-gate.html",
    "pipeline-hero.html": "/work/pipeline-hero.html",
    "custody-ledger.html": "/work/custody.html#demo",
}

STUB = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved - Himanshu Srivastava</title>
<link rel="canonical" href="{site}{target}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<div class="wrap" style="padding-top:18vh">
<p>This page moved. <a href="{target}">Continue</a>.</p>
</div>
<script>location.replace("{target}");</script>
</body>
</html>
"""


def write_redirects() -> None:
    for old, target in REDIRECTS.items():
        (ROOT / old).write_text(STUB.format(site=SITE, target=target))
    print(f"  {len(REDIRECTS)} redirect stubs at the old root URLs")


def nav_items(current: Page) -> str:
    out = []
    for p in NAV:
        mark = ' aria-current="page"' if p.out == current.out else ""
        out.append(f'      <li><a href="{p.href}"{mark}>{html.escape(p.nav_label)}</a></li>')
    return "\n".join(out)


def build(page: Page) -> str:
    fragment = (SRC / page.src).read_text()
    scripts = "".join(f'<script src="{s}"></script>\n' for s in page.scripts)
    return SHELL.format(
        title=html.escape(page.title),
        # og:title drops the trailing name, which the site_name already carries.
        og_title=html.escape(page.title.split(" - ")[0]),
        description=html.escape(page.description),
        url=page.url,
        site=SITE,
        og=page.og,
        extra_head=page.extra_head,
        body_class=f' class="{page.body_class}"' if page.body_class else "",
        navitems=nav_items(page),
        body=fragment.rstrip("\n"),
        scripts=scripts,
    )


def check(path: Path, text: str) -> list[str]:
    """The defects this build exists to prevent, asserted rather than assumed."""
    problems = []
    if not text.startswith("<!doctype html>"):
        problems.append("no doctype")
    if '<html lang="en">' not in text:
        problems.append("no lang")
    if 'name="description"' not in text:
        problems.append("no meta description")
    if 'property="og:image"' not in text:
        problems.append("no og:image")
    if 'rel="icon"' not in text:
        problems.append("no favicon")
    if 'class="sitenav"' not in text:
        problems.append("no nav")
    if 'href="/"' not in text:
        problems.append("no way home")
    for ch, name in (("—", "em dash"), ("–", "en dash")):
        pass  # prose keeps its punctuation here; this is a site, not a resume
    return problems


def main() -> int:
    if not SRC.exists():
        print(f"error: {SRC} does not exist", file=sys.stderr)
        return 1

    failed = False
    for page in PAGES:
        if not (SRC / page.src).exists():
            print(f"  SKIP  {page.src} (no fragment yet)")
            continue
        out = ROOT / page.out
        out.parent.mkdir(parents=True, exist_ok=True)
        text = build(page)
        out.write_text(text)
        problems = check(out, text)
        failed |= bool(problems)
        status = "FAIL " + ", ".join(problems) if problems else "ok"
        print(f"  {page.out:34} {len(text)//1024:3} KB  {status}")

    write_redirects()
    (ROOT / ".nojekyll").write_text("")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
