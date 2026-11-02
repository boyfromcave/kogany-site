# kogany-site — agent instructions

1. **Facts only, sourced.** Every version, height, branch ID, host name, amount or status on the site
   comes from the yellowback workspace (`~/projects/yellowback-workspace`): the kogany plan's execution
   status block, the vault upgrade plan, `ycash-ops/eks/testnet/networks.json`, `ycash-infra`. Never
   invent a release, date, signing key, URL or activation height. If it isn't decided, the page says so.
2. **Our own design and words.** zakura.com is a reference for *what* a node site offers
   (`docs/zakura-site-survey.md`), not a source to copy: no Zakura CSS, copy, logo or imagery.
3. **No-JS complete.** Every page reads correctly without JavaScript; `site.js` only enhances. Live data
   never overrides with guesses: missing is "unavailable", failed fetches keep the warning.
4. **Naming** (workspace rule 6): Yellowback is the system, YED the unit; first formal mention
   "Ycash Yellowback (YED)". The decision-maker is "the Yellowback lead architect"; the projects are
   "the Ycash developers'".
5. **Commits** as `boyfromcave <57612331+boyfromcave@users.noreply.github.com>` (from `~/.gitconfig`'s
   `includeIf` for this directory; no local `user.*`), pushes with the BOY_GH key (`core.sshCommand`).
   No AI attribution anywhere: no trailers, footers or links.
