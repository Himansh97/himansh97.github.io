# himansh97.github.io

Portfolio for Himanshu Srivastava. Hand-written HTML, one build step that stamps
the shared head, nav and footer, and no framework.

**One external request:** the three typefaces come from Google Fonts. The README
used to say "nothing loaded from a CDN", which stopped being true the moment the
webfonts went in. The trade was deliberate: the previous stack fell back to Arial
on Windows and Linux, so most visitors saw none of the intended typography. On a
site whose argument is that claims should be checkable, leaving the old sentence
in place would have been the worst kind of small lie.

## Build

```bash
python3 build.py     # src/ fragments -> the pages, and fails on a missing head
python3 make_og.py   # re-render the six link-preview cards
```

`build.py` refuses to ship a page missing a doctype, `lang`, a meta description,
an `og:image`, a favicon, a nav, a way home, **or a figure with no provenance
stamp**. That last check is the site's own rule applied to itself: every number
on a page names the command that produced it.

## Layout

| Path | What it is |
| --- | --- |
| `src/*.html` | Body fragments. The only files worth editing. |
| `assets/site.css` | Tokens, type scale, chrome. The only place colours and sizes are set. |
| `assets/home.css` | Home-page layout: the claim/proof split. |
| `assets/case.css` | Case-page layout, shared by the prose case studies. |
| `work/*.html` | Built output. Do not edit. |
| `*.html` at root | Redirect stubs for URLs that were public before the pages moved. |

## The design

The left column states a claim in a human voice and is set in a serif. The right
column shows the artifact behind it and is set in mono, with the command that
produced the figure underneath. The two voices are the argument: a claim is
written by a person, a figure is emitted by a machine, and neither should be
mistaken for the other.

Every figure traces to a record — a `pytest --collect-only`, a `git rev-list`, a
hashed register snapshot — not to an estimate. The evidence file those records
describe is private and stays out of this repo.
