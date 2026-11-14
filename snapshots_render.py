"""The snapshots page, rendered at build time from the published manifests.

The bucket cannot be listed publicly, so snapshots.json names the candidate heights; each one is
shown only once its manifest is published. A manifest is used only if its format, network, height
and storage mode match where it was found (ycash-infra bundles/state/FORMAT.md). Nothing is
inferred: a missing value renders as a placeholder.

SNAPSHOTS_BASE overrides the base URL (or names a local directory with the same layout, for
previewing); SNAPSHOTS_OFFLINE=1 skips the network and renders the placeholders.
"""

import html
import json
import os
import sys
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from pathlib import Path

RETENTION = 34560   # the infrastructure's pruned bundles (FORMAT.md kogany-state/2, decision 8)


def fetch_json(url):
    """(document, upload date or None), or (None, None) if it is not there."""
    if not url.startswith(("http://", "https://")):
        p = Path(url)
        return (json.loads(p.read_text()), None) if p.is_file() else (None, None)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "kogany-site-build"})
        with urllib.request.urlopen(req, timeout=15) as r:
            lm = r.headers.get("Last-Modified")
            return json.loads(r.read()), (parsedate_to_datetime(lm).date().isoformat() if lm else None)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None, None


def valid(fam, m, height=None):
    if m is None:
        return False
    mode = m.get("storage_mode") or "archive"
    ok = (isinstance(m, dict) and m.get("format") in fam["formats"] and m.get("network") == "main"
          and isinstance(m.get("height"), int) and isinstance(m.get("tarball"), str)
          and isinstance(m.get("sha256"), str) and len(m["sha256"]) == 64
          and (height is None or m["height"] == height)
          and (fam["storage_mode"] is None or mode == fam["storage_mode"])
          and (fam.get("flavour") is None or m.get("flavour") == fam["flavour"]))
    if not ok:
        print(f"snapshots: ignoring a {fam['id']} manifest that does not match its place", file=sys.stderr)
    return ok


def collect(cfg):
    base = os.environ.get("SNAPSHOTS_BASE", cfg["base"]).rstrip("/")
    out = {"base": cfg["base"].rstrip("/"), "families": {}}
    offline = os.environ.get("SNAPSHOTS_OFFLINE") == "1"
    for fam in cfg["families"]:
        entry = {"latest": None, "all": []}
        if not offline:
            m, date = fetch_json(f"{base}/{fam['latest']}")
            if valid(fam, m):
                entry["latest"] = dict(m, published=date)
            for h in cfg["heights"]:
                if fam["id"] not in h.get("families", [fam["id"]]):
                    continue
                m, date = fetch_json(f"{base}/{fam['dir']}/{h['height']}/manifest.json")
                if valid(fam, m, h["height"]):
                    entry["all"].append(dict(m, published=date, label=h["label"]))
            if entry["latest"] is None and entry["all"]:
                entry["latest"] = max(entry["all"], key=lambda x: x["height"])
        out["families"][fam["id"]] = entry
    return out


def gib(n):
    return f"{n / 2**30:.1f} GiB" if isinstance(n, int) else None


def e(v):
    return html.escape(str(v)) if v not in (None, "") else "—"


def node_version(fam, m):
    """koganyd's release tag (the part in parentheses), or ycashd's version."""
    v = m.get("version")
    if not isinstance(v, str):
        return None
    if fam["node"] == "kogany":
        tag = v[v.find("(") + 1:v.find(")")] if "(" in v and ")" in v else v.split(",")[0]
        return f"koganyd {tag}"
    return f"ycashd {v}"


def retention(m):
    low = m.get("lowest_retained_height")
    if (m.get("storage_mode") or "archive") == "archive":
        return "Full history"
    if isinstance(low, int):
        return f"transactions from block {low:,}" if low else "every transaction so far"
    return None


def card(cfg, data, fam, m, base, group):
    """One snapshot: title, one line, a facts row, the restore steps, one note, then the rest
    folded into "More about this snapshot"."""
    fid = fam["id"]
    tag = f' <span class="tag gold">{e(fam["tag"])}</span>' if fam.get("tag") else ""
    more = [("Contains", fam.get("contains"))]
    if m:
        height = f"Block {m['height']:,}"
        url = f"{base}/{fam['dir']}/{m['height']}/{m['tarball']}"
        facts = [gib(m.get("bytes")), m.get("format"), node_version(fam, m), m.get("published")]
        facts = "".join(f"<li>{e(x)}</li>" for x in facts if x) + f'<li><a href="{url}">Direct download</a></li>'
        if fam["node"] == "kogany":
            more += [("Retention", retention(m))]
            if m.get("agrees_with"):
                more.append(("Matches ycashd", "same block"))
        more.append(("Manifest", f'<a href="{base}/{fam["dir"]}/{m["height"]}/manifest.json">manifest.json</a> · '
                                  f'<a href="{base}/{fam["dir"]}/{m["height"]}/SHA256SUMS">SHA256SUMS</a>'))
        sha = (f'<div class="sha"><span class="label">SHA256 <button class="copy-btn" type="button" '
               f'data-copy-target="sha-{fid}">Copy</button></span><code id="sha-{fid}">{e(m["sha256"])}</code></div>')
    else:
        height = "Block —"
        facts = "<li>not published yet</li>"
        sha = ""
    dl = "".join(f"<dt>{k}</dt><dd>{v if k == 'Manifest' else e(v)}</dd>" for k, v in more if v)
    extra = f'<p>{e(fam["more"])}</p>' if fam.get("more") else ""
    note = f'<p class="snap-note">{e(fam["note"])}</p>' if fam.get("note") else ""
    rec = " recommended" if fam.get("tag") == "Recommended" else ""
    return (f'<article class="snap snap-{e(group["id"])}{rec}" id="snap-{fid}">'
            f'<header class="snap-top"><h3>{e(fam["title"])}{tag}</h3><p class="height">{height}</p></header>'
            f'<p class="desc">{e(fam["desc"])}</p><ul class="snap-facts">{facts}</ul>{note}'
            f'{restore(cfg, data, fam, group)}'
            f'<details class="snap-more"><summary>More about this snapshot</summary>{extra}'
            f'<dl class="meta">{dl}</dl>{sha}</details></article>')


def restore(cfg, data, fam, group):
    """The restore steps for one family, with the aria2/curl switch."""
    return (f'<div class="code snap-restore" data-cmd><div class="code-bar"><span class="file">Restore steps</span>'
            '<span class="seg-sep"></span><div class="seg" role="tablist" aria-label="Download tool">'
            '<button type="button" role="tab" aria-selected="false" data-cmd-tool="curl">curl</button>'
            '<button type="button" role="tab" aria-selected="true" data-cmd-tool="aria2">aria2</button></div>'
            '<span class="spacer"></span><button class="copy-btn" type="button" data-copy-visible>Copy</button></div>'
            f'{commands(cfg, data, fam)}</div>')


def commands(cfg, data, fam):
    """The restore steps. They read the height, tarball and checksum from the manifest when run,
    so they never go stale between site builds; the current height is shown as a comment."""
    fid = fam["id"]
    m = data["families"][fid]["latest"]
    base, key = data["base"], cfg["key"]["public"]
    now = f"currently {m['height']:,}" if m else "not published yet"
    c = lambda t: f'<span class="c">{t}</span>'
    k = lambda t: f'<span class="k">{t}</span>'
    s = lambda t: f'<span class="s">{t}</span>'
    n = iter(range(1, 10))
    lines = [c(f"# {next(n)} · stop the node first, if it is already running"), ""]
    if fam["node"] == "kogany":
        lines += [c("# Kogany's config file and state directory (macOS or Linux)"),
                  f'{k("if")} [ "$({k("uname")})" = Darwin ]; {k("then")}',
                  f'  CONF=$HOME/Library/Preferences/kogany.toml; CACHE=$HOME/Library/Caches/kogany',
                  f'{k("else")}',
                  '  CONF=${XDG_CONFIG_HOME:-$HOME/.config}/kogany.toml; CACHE=${XDG_CACHE_HOME:-$HOME/.cache}/kogany',
                  f'{k("fi")}', ""]
    if fid == "pruned":
        lines += [c(f"# {next(n)} · run in pruned storage mode (one-way; this replaces any existing kogany.toml)"),
                  f'{k("mkdir")} -p "$({k("dirname")} "$CONF")"',
                  f'{k("cat")} &gt; "$CONF" &lt;&lt;{s(chr(39) + "EOF" + chr(39))}',
                  "[state.storage_mode.pruned]",
                  f"tx_retention = {RETENTION}",
                  "EOF", ""]
    lines += [c(f"# {next(n)} · the latest manifest names the height; fetch that height's files"),
              f'B={s(base + "/" + fam["dir"])}',
              f'H=$({k("curl")} -fsS $B/{s(fam["latest"].split("/", 1)[1])} | {k("jq")} -r .height)   {c("# " + now)}',
              f'{k("curl")} -fsS --remote-name-all $B/$H/{{{",".join(fam["files"])}}}',
              f'T=$({k("jq")} -r .tarball manifest.json)',
              f'<span data-only="aria2">{k("aria2c")} -x16 -s16 --continue=true --checksum=sha-256=$({k("jq")} -r .sha256 manifest.json) $B/$H/$T</span>'
              f'<span data-only="curl">{k("curl")} -fL -C - -O $B/$H/$T</span>', "",
              c(f"# {next(n)} · check the Ycash release key's signature, then every file against it"),
              f'{k("minisign")} -Vm SHA256SUMS -P {s(key)}',
              f'{k("shasum")} -a 256 -c SHA256SUMS', ""]
    if fam["node"] == "kogany":
        lines += [c(f"# {next(n)} · replace the state"),
                  f'{k("rm")} -rf "$CACHE/state" "$CACHE/non_finalized_state"',
                  f'{k("mkdir")} -p "$CACHE" && {k("tar")} -xzf $T -C "$CACHE"',
                  f'{k("cat")} "$CACHE/state/v30/mainnet/version"   {c("# must be 30.2.0")}', "",
                  c(f"# {next(n)} · start — the node resumes from block $H, not genesis"),
                  f'{k("koganyd")} start']
    else:
        lines += [c(f"# {next(n)} · restore into a datadir with no blocks/ or chainstate/"),
                  f'{k("mkdir")} -p ~/.ycash && {k("tar")} -xzf $T -C ~/.ycash --strip-components=1', ""]
        if fam.get("conf"):
            flags = "\\n".join(fam["conf"]) + "\\n"
            lines += [c(f"# {next(n)} · this datadir holds the indexes: the node must run with these flags"),
                      f'{k("printf")} {s(chr(39) + flags + chr(39))} &gt;&gt; ~/.ycash/ycash.conf', ""]
        lines += [c(f"# {next(n)} · start, then compare block $H with the manifest's blockhash"),
                  f'{k("ycashd")} -datadir=$HOME/.ycash -daemon',
                  f'{k("ycash-cli")} -datadir=$HOME/.ycash getblockhash $H; {k("jq")} -r .blockhash manifest.json']
    return f'<pre id="cmd-{fid}">' + "\n".join(lines) + "</pre>"


def listing(fam, entries, base):
    rows = []
    for m in sorted(entries, key=lambda x: x["height"], reverse=True):
        url = f"{base}/{fam['dir']}/{m['height']}/manifest.json"
        meta = " · ".join(x for x in (m.get("published"), gib(m.get("bytes")),
                                      m.get("state_format") and f"v{m['state_format']}" or m.get("version")) if x)
        rows.append(f'<div class="snap-row"><div><b>Block {m["height"]:,}</b><span>{e(m["label"])}</span>'
                    f'<span>{e(meta)}</span></div><a class="copy-btn" href="{url}">Manifest</a></div>')
    if not rows:
        rows.append('<div class="snap-row empty"><div><b>Block —</b><span>none published yet</span></div></div>')
    return f'<div><h4>{e(fam["title"])}</h4>' + "".join(rows) + "</div>"


def shown(fam, entry):
    """A family marked hide_until_published shows nothing until its first manifest is published."""
    return not fam.get("hide_until_published") or bool(entry["latest"] or entry["all"])


def render(root):
    cfg = json.loads((root / "snapshots.json").read_text())
    data = collect(cfg)
    base = data["base"]
    tabs, panels = [], []
    for i, g in enumerate(cfg["groups"]):
        gf = [f for f in cfg["families"] if f["group"] == g["id"]]
        live = [f for f in gf if shown(f, data["families"][f["id"]])]
        cards = "".join(card(cfg, data, f, data["families"][f["id"]]["latest"], base, g) for f in live if f.get("card"))
        coming = "".join(f'<p class="snap-coming">{e(f["coming"])}</p>' for f in gf if f not in live and f.get("coming"))
        heights = "".join(listing(f, data["families"][f["id"]]["all"], base) for f in live)
        notes = "".join(f"<p>{e(n)}</p>" for n in g.get("notes", []))
        aliases = "".join(f'<span id="{e(a)}" class="snap-alias"></span>' for a in g.get("aliases", []))
        sel = "true" if i == 0 else "false"
        tabs.append(f'<button type="button" role="tab" id="tab-{e(g["id"])}" aria-controls="{e(g["id"])}" '
                    f'aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">'
                    f'<b>{e(g["tab"])}</b><span>{e(g["sub"])}</span></button>')
        panels.append(f'<section class="snap-panel snap-panel-{e(g["id"])}" id="{e(g["id"])}" data-tab-panel'
                      f'{" data-tab-alias=" + chr(34) + " ".join(g["aliases"]) + chr(34) if g.get("aliases") else ""}>'
                      f'{aliases}<header class="snap-panel-head"><h2>{e(g["heading"])}</h2>'
                      f'<p>{e(g["lead"])}</p></header>'
                      f'<div class="snap-cards">{cards}</div>{coming}'
                      f'<div class="snap-notes">{notes}</div>'
                      f'<details class="snap-heights"><summary>All published heights</summary>'
                      f'<div class="all-snaps snap-lists">{heights}</div></details></section>')
    published = any(data["families"][f["id"]]["latest"] for f in cfg["families"])
    notice = "" if published else (
        '<div class="notice column"><p><strong>The first mainnet snapshots are being uploaded.</strong> '
        'Until a manifest is published, its values show as a dash.</p></div>')
    print("snapshots: latest", {f["id"]: (data["families"][f["id"]]["latest"] or {}).get("height") for f in cfg["families"]},
          "listed", {k: len(v["all"]) for k, v in data["families"].items()})
    return {
        "{{ snapshot_notice }}": notice,
        "{{ snapshot_tabs }}": "".join(tabs),
        "{{ snapshot_panels }}": "".join(panels),
        "{{ key_public }}": cfg["key"]["public"],
        "{{ key_id }}": cfg["key"]["id"],
        "{{ key_file }}": cfg["key"]["file"],
    }
