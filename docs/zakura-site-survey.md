# What zakura.com taught us — survey, 2026-11-01

A read of zakura.com (a static site, generated, one CSS file and one small script) to learn which
operational services a node project publishes and how. **Kogany's site copies the information
architecture and the operational patterns, not Zakura's design, wording or logo**: those belong to
the Zakura team, and an imitation of their site would misrepresent who runs ours.

## Their page map, and ours

| zakura.com | What it does | kogany.net | Our backing service today |
|---|---|---|---|
| `/` | hero, latest-release badge, four feature cards | `/` | — |
| `/nu7/` (nav item tagged "Dashboard") | upgrade rollout dashboard: selected network, live chain figures, rule parameters per height, join config, faucet and snapshot controls | `/vault/` (rollout, waves) + `/testnet/` (networks, faucet) | ycash-ops `eks/testnet/networks.json`; ycash-infra `charts/ycash-testnet` status page (not deployed) |
| `/download/` | install via cargo / installer script / binaries / Docker; signed checksums + CI attestations; official-channel list | `/download/` | ycash6 tag-driven release workflow; Kogany has none until K-19(a) |
| `/snapshots/` | live cards from JSON manifests (pruned, archive, third-party), copyable restore commands, roles daily/monthly/historical | `/snapshots/` | ycash-infra `bundles/state` (`ycash-state/1`, two-implementation agreement), snapshotter CronJob (not yet run live) |
| `/zcashd/` | compatibility mode for software that expects the old node | `/yewd/` | `yew/yewd` (plan §3b, S0–S5) |
| `/announcements/` + Atom feed | release notes per version | `/announcements/` + `atom.xml` | — |
| `/engineering/` | technical write-ups | `/engineering/` | — |
| `/about/` | team | `/about/` | — |
| `/ironwood/` | a protocol programme with audits, history, migration | (none yet) | the vault upgrade plan's audits could go under `/vault/` later |

## Operational patterns worth adopting

1. **A Markdown twin of each page** (`index.html.md`, linked as `rel=alternate type=text/markdown`),
   with a "notes for language models" section: never quote a version, URL, height or key from memory;
   if the page doesn't list it, it doesn't exist. *Not built yet; next step.*
2. **Machine-readable manifests are canonical** (snapshots JSON with `height, date, size, url, sha256,
   db_format_version, <node>_version, roles`); the page renders from them, and the no-JS page bakes the
   last good copy. Our `ycash-state/1` FORMAT.md should define the equivalent manifest.
3. **The dashboard never moves backwards**: once it has shown public testnet it never falls back to
   staging data; stale or failed fetches keep dated data and show a warning; missing values read
   "unavailable", never inferred. `static/assets/site.js` `wireLive` follows this.
4. **Activation is a height; dates are estimates.** State it on every upgrade page.
5. **Faucet scoped to the selected network**, with per-network amounts and accepted address types,
   bounded polling, and requests never resent automatically. Ours has its own page per network
   (ycash-infra `images/faucet`), so the site links to it rather than embedding a form.
6. **Release verification in three parts**: a signed `SHA256SUMS.txt` (minisign), checksums, and GitHub
   artifact attestations; an explicit list of the only official channels; unsigned Docker images said to be
   unsigned. Kogany's release workflow should produce all three from the first tag.
7. **An installer script** pinned to the release, with checksums and image tags. A candidate for when
   Kogany ships.
8. **No-JS first, tiny JS**: the theme override is applied before first paint; the nav toggle and theme
   toggle ship `hidden` so no-JS visitors never see dead controls; tabbed command blocks show all panels
   without JS.

## Open items for us

- Decide the signing tool and publish the key with the first release (minisign is what Zakura uses).
- Define the snapshot manifest schema in `ycash-infra/bundles/state/FORMAT.md` and point `/snapshots/` at it.
- Have the testnet status service emit `static/data/README.md`'s shape (`status: live` only when fresh).
- Generate the Markdown twins from the same content.
- Domain: kogany.net (not yet registered/pointed, as far as this repo knows), hosting (static: GitHub Pages
  or the ycash-infra gateway).
