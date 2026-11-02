# kogany-site — kogany.net

The website for **Kogany**, the Ycash full node in Rust (a fork of Zakura) and the third node line
for the Ycash vault upgrade. Static HTML, one stylesheet, one small script, a dependency-free Python
build.

```bash
make build   # content/ + static/ → public/
make serve   # build, then serve public/ on http://localhost:8000
make check   # build and check internal links
```

| Path | What |
|---|---|
| `content/*.html` | pages: an HTML fragment headed by a `title/description[/date]` comment; `content/x.html` → `/x/` |
| `content/announcements/`, `content/engineering/` | dated posts; listed on their section page (`{{ announcements }}`), announcements also in `atom.xml` |
| `static/assets/` | `site.css`, `site.js`, the Kogany mark, favicon, Ycash logo |
| `static/data/dashboard.json` | the vault dashboard feed (shape in `static/data/README.md`) |
| `build.py` | the layout (header, nav, footer) and the generator |
| `docs/zakura-site-survey.md` | what we learned from zakura.com's operations, and what we still need |

Facts on the site come from the workspace plans (`docs/plans/kogany/kogany-yellowback-plan.md`,
`docs/plans/yellowback-upgrade-plan.md`) and from `ycash-ops` / `ycash-infra`. See `AGENTS.md`.
