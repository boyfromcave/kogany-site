// kogany.net — the only script. Loaded in <head> so a stored theme applies
// before first paint. Every feature is an enhancement: the pages are complete
// without JavaScript (tab panels all show, status falls back to build-time data).
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
  function text(el, value) { if (el) el.textContent = value == null || value === "" ? "unavailable" : String(value); }

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

  function wireCopy() {
    $$("pre[data-copy]").forEach(function (pre) {
      var wrap = document.createElement("div");
      wrap.className = "copyable";
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);
      var b = document.createElement("button");
      b.type = "button"; b.className = "copy-btn"; b.textContent = "copy";
      b.addEventListener("click", function () {
        navigator.clipboard.writeText(pre.innerText.trim()).then(function () {
          b.textContent = "copied";
          setTimeout(function () { b.textContent = "copy"; }, 1500);
        });
      });
      wrap.appendChild(b);
    });
  }

  function wireTabs() {
    $$(".tabs").forEach(function (box) {
      var tabs = $$('[role="tab"]', box);
      function select(tab) {
        tabs.forEach(function (t) {
          var on = t === tab;
          t.setAttribute("aria-selected", on ? "true" : "false");
          t.tabIndex = on ? 0 : -1;
          document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
        });
      }
      tabs.forEach(function (t) { t.addEventListener("click", function () { select(t); }); });
      if (tabs.length) select(tabs[0]);
    });
  }

  // Live status. A page opts in with data-live="<json url>". The JSON's shape is
  // documented in static/data/README.md. A failed or stale fetch keeps the
  // build-time values and shows the dated-data warning; it never invents values.
  function wireLive() {
    $$("[data-live]").forEach(function (box) {
      var url = box.getAttribute("data-live");
      var warn = $("[data-live-warning]", box);
      fetch(url, { cache: "no-store" })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (data) {
          if (data.status !== "live") throw new Error("not live");
          (data.networks || []).forEach(function (n) {
            var card = $('[data-network="' + n.id + '"]', box);
            if (!card) return;
            $$("[data-field]", card).forEach(function (el) { text(el, n[el.getAttribute("data-field")]); });
            var dot = $(".dot", card);
            if (dot) dot.className = "dot " + (n.state === "up" ? "ok" : n.state === "degraded" ? "warn" : "");
            var faucet = $("[data-faucet]", card);
            if (faucet && n.faucet_url) { faucet.href = n.faucet_url; faucet.hidden = false; }
          });
          if (warn) warn.hidden = true;
        })
        .catch(function () { if (warn) warn.hidden = false; });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    wireTheme(); wireNav(); wireCopy(); wireTabs(); wireLive();
  });
})();
