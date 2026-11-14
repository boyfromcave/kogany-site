// The Kogany website — the only script. Loaded in <head> so a stored theme applies
// before first paint. Every feature is an enhancement: pages are complete without
// JavaScript (all command variants show, status shows build-time placeholders).
(function () {
  "use strict";
  var root = document.documentElement;

  try {
    var stored = localStorage.getItem("kogany-theme");
    if (stored === "light" || stored === "dark") root.dataset.theme = stored;
  } catch (e) {}
  root.dataset.js = "";
  root.dataset.navJs = "";

  var systemDark = window.matchMedia("(prefers-color-scheme: dark)");
  function effective() {
    var t = root.dataset.theme;
    return t === "light" || t === "dark" ? t : systemDark.matches ? "dark" : "light";
  }
  function markTheme() { root.dataset.effectiveTheme = effective(); }
  markTheme();
  systemDark.addEventListener("change", markTheme);

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  function wireTheme() {
    var btn = $("[data-theme-toggle]");
    if (!btn) return;
    btn.hidden = false;
    btn.addEventListener("click", function () {
      var next = effective() === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("kogany-theme", next); } catch (e) {}
      markTheme();
    });
  }

  function wireNav() {
    var btn = $("[data-nav-toggle]"), nav = $("#site-nav");
    if (!btn || !nav) return;
    btn.hidden = false;
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function copyText(src, b) {
    if (!navigator.clipboard) return;
    var clone = src.cloneNode(true);
    $$("[hidden]", clone).forEach(function (n) { n.remove(); });
    navigator.clipboard.writeText(clone.textContent.replace(/\n{3,}/g, "\n\n").trim()).then(function () {
      b.textContent = "Copied";
      setTimeout(function () { b.textContent = "Copy"; }, 1500);
    });
  }

  function wireCopy() {
    $$("[data-copy-target]").forEach(function (b) {
      b.addEventListener("click", function () {
        var src = document.getElementById(b.getAttribute("data-copy-target"));
        if (src) copyText(src, b);
      });
    });
  }

  // Snapshot commands: one <pre> per node, tool variants marked data-only="aria2|curl".
  function wireCommands() {
    $$("[data-cmd]").forEach(function (box) {
      var fams = $$("[data-cmd-family]", box).map(function (b) { return b.dataset.cmdFamily; });
      var state = { family: fams[0], tool: "aria2" };
      function render() {
        $$("[data-cmd-family]", box).forEach(function (b) { b.setAttribute("aria-selected", b.dataset.cmdFamily === state.family); });
        $$("[data-cmd-tool]", box).forEach(function (b) { b.setAttribute("aria-selected", b.dataset.cmdTool === state.tool); });
        $$("[data-only]", box).forEach(function (el) {
          var v = el.dataset.only;
          el.hidden = (fams.indexOf(v) >= 0 && v !== state.family) ||
                      ((v === "aria2" || v === "curl") && v !== state.tool);
        });
      }
      $$("[data-cmd-family]", box).forEach(function (b) { b.addEventListener("click", function () { state.family = b.dataset.cmdFamily; render(); }); });
      $$("[data-cmd-tool]", box).forEach(function (b) { b.addEventListener("click", function () { state.tool = b.dataset.cmdTool; render(); }); });
      var copy = $("[data-copy-visible]", box);
      if (copy) copy.addEventListener("click", function () {
        var pre = $$("pre", box).filter(function (x) { return !x.hidden; })[0];
        if (pre) copyText(pre, copy);
      });
      render();
    });
  }

  // Dashboard. The feed (static/data/README.md) carries one entry per network.
  // Only status "live" clears the warning and enables the faucet and visualizer; any other
  // status (a dated snapshot) keeps the warning. Null values render as a dash, never a guess.
  function wireDashboard() {
    var box = $("[data-live]");
    if (!box) return;
    var feed = null, profile = "yb-fast";
    var tabs = $$("[data-profile]", box);
    var warn = $("[data-live-warning]", box);

    function fill() {
      tabs.forEach(function (t) { t.setAttribute("aria-selected", t.dataset.profile === profile); });
      var net = feed && feed.networks && feed.networks[profile];
      $$("[data-field]", box).forEach(function (el) {
        var key = el.dataset.field;
        if (el.dataset.orig === undefined) el.dataset.orig = el.textContent;
        if (key === "network_label") { el.textContent = profile; return; }
        if (key === "updated") {
          var g = feed && feed.generated;
          el.textContent = !g ? el.dataset.orig : feed.status === "live"
            ? "Updated " + g.replace("T", " ").replace(/:\d\dZ?$/, "") + " UTC"
            : "Testnet snapshot of " + g.replace("T", " ").replace(/:\d\dZ?$/, "") + " UTC, not a live feed";
          return;
        }
        if (!net || !(key in net)) return;
        var v = net[key];
        el.textContent = v === null || v === undefined || v === "" ? el.dataset.orig : String(v);
      });
      var stage = $("[data-stage=testnet]", box);
      if (stage && net && net.testnet_state) {
        var active = net.testnet_state === "Active";
        stage.classList.toggle("future", !active);
        var tag = $("[data-field=testnet_state]", stage);
        tag.classList.toggle("ok", active);
        tag.classList.toggle("pend", !active);
      }
      var rows = $("[data-field-rows=blocks]", box);
      if (rows && rows.dataset.orig === undefined) rows.dataset.orig = rows.innerHTML;
      if (rows && !(net && net.blocks && net.blocks.length)) rows.innerHTML = rows.dataset.orig;
      if (rows && net && net.blocks && net.blocks.length) {
        rows.innerHTML = "";
        net.blocks.slice(0, 6).forEach(function (b) {
          var tr = document.createElement("tr");
          [String(b.height), b.hash, b.time].forEach(function (v, i) {
            var td = document.createElement("td");
            td.textContent = v;
            if (i === 1) td.className = "hash";
            if (i === 2) td.className = "r";
            tr.appendChild(td);
          });
          rows.appendChild(tr);
        });
      }
      var form = $("[data-faucet-form]", box);
      if (form) {
        var on = !!(feed && feed.status === "live" && net && net.faucet_url);
        $$("input, button", form).forEach(function (el) { el.disabled = !on; });
        form.action = on ? net.faucet_url : "";
        $("[data-faucet-status]", form).textContent = on
          ? "Opens the " + profile + " faucet, which checks the address and may ask your browser for a short proof of work."
          : "Faucet offline: not deployed yet.";
      }
      var viz = $("[data-viz-link]", box);
      if (viz) {
        var vurl = feed && feed.status === "live" && net && net.viz_url;
        viz.setAttribute("aria-disabled", vurl ? "false" : "true");
        viz.href = vurl || "#";
      }
    }

    tabs.forEach(function (t) { t.addEventListener("click", function () { profile = t.dataset.profile; fill(); }); });
    var form = $("[data-faucet-form]", box);
    if (form) form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.action) return;
      var addr = form.elements.address.value.trim();
      window.open(form.action + (addr ? "?address=" + encodeURIComponent(addr) : ""), "_blank", "noopener");
    });

    fetch(box.dataset.live, { cache: "no-store" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) { feed = data; if (warn) warn.hidden = data.status === "live"; fill(); })
      .catch(function () { if (warn) warn.hidden = false; fill(); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    wireTheme(); wireNav(); wireCopy(); wireCommands(); wireDashboard();
  });
})();
