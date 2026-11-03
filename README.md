# kogany-site — kogany.net

The website for **Kogany**, the Ycash full node in Rust (a fork of Zakura) and the third node line
for the Ycash vault upgrade. Static HTML, one stylesheet, one small script, a dependency-free Python
build.

```bash
make build   # content/ + static/ → public/
make serve   # build, then serve public/ on http://localhost:8000
make check   # build and check internal links
```

The build fetches the snapshot manifests, so **rebuild after each snapshot upload** to refresh the cards and the list. The restore commands themselves read the manifest when run, so they stay correct between builds.

| Path | What |
|---|---|
| `content/*.html` | pages: an HTML fragment headed by a `title/description[/date]` comment; `content/x.html` → `/x/` |
| `content/announcements/`, `content/engineering/` | dated posts; listed on their section page (`{{ announcements }}`), announcements also in `atom.xml` |
| `static/assets/` | `site.css`, `site.js`, the flower mark (`kogany-flower-{640,160}.webp`), favicon and touch icon, Ycash logo |
| `art/` | source artwork, not published: `image_5743ea06.jpg`, the gold vault flower (its checkerboard is baked in) |
| `tools/cutout.py` | cuts the flower out of the source into the transparent web assets: `.venv/bin/python -I tools/cutout.py art/image_5743ea06.jpg static/assets` (Pillow) |
| `static/data/dashboard.json` | the vault dashboard feed (shape in `static/data/README.md`) |
| `build.py` | the layout (header, nav, footer) and the generator |
| `snapshots.json` | the snapshots page's source: bucket base, the Ycash release key, the three families (`kogany-main-pruned/`, `kogany-main/`, `main/`) and the candidate heights (the bucket cannot be listed publicly, so heights are named here; one shows once its manifest is published) |
| `snapshots_render.py` | renders the snapshot cards, restore commands and list from the published manifests at build time; rejects a manifest whose `format`, `network` or `height` does not match its place. `SNAPSHOTS_OFFLINE=1` skips the network; `SNAPSHOTS_BASE=<dir or URL>` previews from a mirror |
| `static/keys/ycash-release.pub` | the Ycash release minisign key (id `02C923A6C593AF18`), copied from ycash-infra `keys/` |
| `docs/zakura-site-survey.md` | what we learned from zakura.com's operations, and what we still need |

Facts on the site come from the workspace plans (`docs/plans/kogany/kogany-yellowback-plan.md`,
`docs/plans/yellowback-upgrade-plan.md`) and from `ycash-ops` / `ycash-infra`. See `AGENTS.md`.
