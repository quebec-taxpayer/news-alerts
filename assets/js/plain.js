/* Plain-language helpers: glossary tooltips (first use per page, tap/click, keyboard) and What's next date sorting. */
(function () {
  "use strict";
  var BASE = (document.currentScript && document.currentScript.getAttribute("data-base")) || "";
  function lang() { return document.documentElement.classList.contains("lang-fr") ? "fr" : "en"; }

  /* ---------- What's next: move past dates under "Past" (today in Quebec time) ---------- */
  function todayQC() {
    try { return new Intl.DateTimeFormat("en-CA", { timeZone: "America/Toronto", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date()); }
    catch (e) { var d = new Date(); return d.toISOString().slice(0, 10); }
  }
  function upcoming() {
    var today = todayQC();
    var boxes = document.querySelectorAll("[data-upcoming]");
    for (var i = 0; i < boxes.length; i++) {
      var box = boxes[i], fut = box.querySelector(".up-future"), past = box.querySelector(".up-past"), pul = past.querySelector("ul");
      var lis = fut.querySelectorAll("li[data-date]"), moved = 0;
      for (var j = 0; j < lis.length; j++) {
        var d = lis[j].getAttribute("data-date"), end = d.length === 4 ? d + "-12-31" : d;
        if (end < today) { lis[j].classList.add("up-is-past"); pul.insertBefore(lis[j], pul.firstChild); moved++; }
      }
      if (moved) past.hidden = false;
      if (!fut.querySelector("li")) box.querySelector(".up-none").hidden = false;
    }
  }

  /* ---------- Glossary tooltips ---------- */
  var dataEl = document.getElementById("gl-data");
  var TERMS = [];
  try { TERMS = dataEl ? JSON.parse(dataEl.textContent) : []; } catch (e) { TERMS = []; }
  var SCOPE = ".tl-text, .story .summary, .callout.why p, .tldr dd span, .wk-text";
  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/[’']/g, "['’]"); }
  function build(lg) {
    var list = [];
    TERMS.forEach(function (t) { (t["match_" + lg] || []).forEach(function (m) { list.push({ t: t, m: m }); }); });
    list.sort(function (a, b) { return b.m.length - a.m.length; });
    return list.map(function (x) {
      var cs = x.m === x.m.toUpperCase();  // acronyms are case-sensitive
      return { t: x.t, re: new RegExp("(^|[^\\p{L}\\p{N}])(" + esc(x.m) + ")(?![\\p{L}\\p{N}])", cs ? "u" : "iu") };
    });
  }
  var tip, openBtn = null, n = 0;
  function closeTip() {
    if (!tip || tip.hidden) return;
    tip.hidden = true;
    if (openBtn) { openBtn.setAttribute("aria-expanded", "false"); openBtn.removeAttribute("aria-describedby"); }
    openBtn = null;
  }
  function openTip(btn) {
    var t = TERMS.filter(function (x) { return x.id === btn.getAttribute("data-term"); })[0]; if (!t) return;
    if (openBtn === btn && !tip.hidden) { closeTip(); return; }
    closeTip();
    var lg = btn.closest("[lang]") ? btn.closest("[lang]").getAttribute("lang") : lang();
    if (lg !== "fr") lg = "en";
    tip.innerHTML = "";
    var h = document.createElement("strong"); h.textContent = t["term_" + lg]; tip.appendChild(h);
    var p = document.createElement("span"); p.className = "gl-def"; p.textContent = t["def_" + lg]; tip.appendChild(p);
    var a = document.createElement("a"); a.href = BASE + "/glossary/#" + t.id; a.textContent = lg === "fr" ? "Voir le lexique →" : "See the glossary →"; tip.appendChild(a);
    var c = document.createElement("button"); c.type = "button"; c.className = "gl-close"; c.setAttribute("aria-label", lg === "fr" ? "Fermer" : "Close"); c.textContent = "×";
    c.addEventListener("click", function () { var b = openBtn; closeTip(); if (b) b.focus(); }); tip.appendChild(c);
    tip.setAttribute("lang", lg);
    tip.hidden = false; openBtn = btn;
    btn.setAttribute("aria-expanded", "true"); btn.setAttribute("aria-describedby", "gl-tip");
    var r = btn.getBoundingClientRect(), w = Math.min(340, document.documentElement.clientWidth - 24);
    tip.style.width = w + "px";
    var left = Math.max(12, Math.min(r.left + window.scrollX, window.scrollX + document.documentElement.clientWidth - w - 12));
    tip.style.left = left + "px"; tip.style.top = (r.bottom + window.scrollY + 6) + "px";
  }
  function mark() {
    if (!TERMS.length) return;
    var els = document.querySelectorAll(SCOPE); if (!els.length) return;
    var R = { en: build("en"), fr: build("fr") }, done = { en: {}, fr: {} };
    for (var i = 0; i < els.length; i++) {
      var el = els[i], lg = (el.closest("[lang]") || document.documentElement).getAttribute("lang") === "fr" ? "fr" : "en";
      var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null), nodes = [], nd;
      while ((nd = walker.nextNode())) if (!nd.parentNode.closest("a, button, .gl-term")) nodes.push(nd);
      nodes.forEach(function (node) {
        var changed = true;
        while (changed) {
          changed = false;
          for (var k = 0; k < R[lg].length; k++) {
            var r = R[lg][k]; if (done[lg][r.t.id]) continue;
            var m = r.re.exec(node.nodeValue); if (!m) continue;
            var start = m.index + m[1].length, word = m[2];
            var after = node.splitText(start); var rest = after.splitText(word.length);
            var b = document.createElement("button");
            b.type = "button"; b.className = "gl-term"; b.setAttribute("data-term", r.t.id); b.setAttribute("aria-expanded", "false");
            b.setAttribute("aria-controls", "gl-tip"); b.id = "gl-b" + (++n); b.textContent = word;
            after.parentNode.replaceChild(b, after);
            done[lg][r.t.id] = true; node = rest; changed = true; break;
          }
        }
      });
    }
    if (!n) return;
    tip = document.createElement("div"); tip.id = "gl-tip"; tip.className = "gl-tip"; tip.hidden = true;
    document.body.appendChild(tip);
    document.addEventListener("click", function (e) {
      var b = e.target.closest && e.target.closest(".gl-term");
      if (b) { e.preventDefault(); openTip(b); return; }
      if (!tip.contains(e.target)) closeTip();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && openBtn) { var b = openBtn; closeTip(); b.focus(); } });
    window.addEventListener("resize", closeTip);
    var ls = document.querySelectorAll("[data-set-lang]"); for (var j = 0; j < ls.length; j++) ls[j].addEventListener("click", closeTip);
  }
  function init() { upcoming(); mark(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
