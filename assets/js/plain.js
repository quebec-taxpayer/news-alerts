/* Plain-language helpers: pop-up term definitions (first mention per page; hover, tap, keyboard) and What's next date sorting. */
(function () {
  "use strict";
  var BASE = (document.currentScript && document.currentScript.getAttribute("data-base")) || "";
  function lang() { return document.documentElement.classList.contains("lang-fr") ? "fr" : "en"; }

  /* ---------- What's next: label today's items, hide (homepage) or move under "Past" (dossiers) passed ones; today in Quebec time ---------- */
  function todayQC() {
    try { return new Intl.DateTimeFormat("en-CA", { timeZone: "America/Toronto", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date()); }
    catch (e) { var d = new Date(); return d.toISOString().slice(0, 10); }
  }
  function upcoming() {
    var today = todayQC();
    var boxes = document.querySelectorAll("[data-upcoming]");
    for (var i = 0; i < boxes.length; i++) {
      var box = boxes[i], fut = box.querySelector(".up-future"), past = box.querySelector(".up-past"), pul = past ? past.querySelector("ul") : null;
      var hide = box.hasAttribute("data-hide-past");
      var lis = fut.querySelectorAll("li[data-date]"), moved = 0;
      for (var j = 0; j < lis.length; j++) {
        var d = lis[j].getAttribute("data-date"), end = d.length === 4 ? d + "-12-31" : d;
        if (end < today) {
          if (hide || !pul) { lis[j].parentNode.removeChild(lis[j]); }
          else { lis[j].classList.add("up-is-past"); pul.insertBefore(lis[j], pul.firstChild); moved++; }
        } else if (d === today) {
          var w = lis[j].querySelector(".up-when"), t = lis[j].querySelector(".up-today");
          if (w && t) { w.hidden = true; t.hidden = false; lis[j].classList.add("up-is-today"); }
        }
      }
      if (moved && past) past.hidden = false;
      if (!fut.querySelector("li")) box.querySelector(".up-none").hidden = false;
    }
  }
  /* A link to a collapsed homepage story (#n-…) opens its <details>. */
  function openTarget() {
    var id = decodeURIComponent((location.hash || "").slice(1)); if (!id) return;
    var el = document.getElementById(id); if (!el) return;
    var dt = el.querySelector("details"); if (dt && !dt.open) dt.open = true;
  }
  window.addEventListener("hashchange", openTarget);

  /* ---------- Pop-up term definitions (data: _data/glossary.json, emitted as #gl-data) ----------
     The first mention of each term per page and per language is wrapped in a <button class="gl-term">.
     Hover (mouse), tap/click, or keyboard focus shows the definition; Enter toggles, Esc / tap outside closes.
     Never inside links, buttons, headings, nav, code, SVG, form controls or labels. With JS off: plain text. */
  var dataEl = document.getElementById("gl-data");
  var TERMS = [];
  try { TERMS = dataEl ? JSON.parse(dataEl.textContent) : []; } catch (e) { TERMS = []; }
  var SCOPE = "main";
  var SKIP = "a, button, h1, h2, h3, h4, h5, h6, nav, header, footer, code, pre, kbd, samp, script, style, noscript, svg, summary, label, input, textarea, select, option, .gl-term, .gl-tip, .callout-label, .post-meta, .day-meta, .tags, .crumb, .latest-label, [data-no-gl]";
  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/[’']/g, "['’]").replace(/[\s\u00a0]+/g, "[\\s\\u00a0]+").replace(/-/g, "[-\\u2011]"); }
  // A plain plural (-s, and -x in French) of a listed form also matches, e.g. "Crown corporations".
  function build(lg) {
    var list = [];
    TERMS.forEach(function (t) { (t["match_" + lg] || []).forEach(function (m) { if (m) list.push({ t: t, m: m }); }); });
    list.sort(function (a, b) { return b.m.length - a.m.length; });
    return list.map(function (x) {
      return { t: x.t, re: new RegExp("(^|[^\\p{L}\\p{N}])(" + esc(x.m) + "(?:s|x)?)(?![\\p{L}\\p{N}])", "iu") };
    });
  }
  function nodeLang(el) { var c = el.closest("[lang]") || document.documentElement; return c.getAttribute("lang") === "fr" ? "fr" : "en"; }
  var tip, openBtn = null, pinned = false, n = 0, hideTimer = null;
  function closeTip() {
    clearTimeout(hideTimer);
    if (!tip || tip.hidden) { openBtn = null; pinned = false; return; }
    tip.hidden = true;
    if (openBtn) { openBtn.setAttribute("aria-expanded", "false"); openBtn.removeAttribute("aria-describedby"); }
    openBtn = null; pinned = false;
  }
  function place(btn) {
    var vw = document.documentElement.clientWidth || window.innerWidth, vh = window.innerHeight;
    var w = Math.min(340, vw - 24);
    tip.style.width = w + "px"; tip.style.maxWidth = (vw - 24) + "px";
    var r = btn.getBoundingClientRect();
    var left = Math.max(12, Math.min(r.left, vw - w - 12));
    tip.style.left = (left + window.scrollX) + "px";
    var top = r.bottom + 6, h = tip.offsetHeight;
    if (top + h > vh - 8 && r.top - h - 6 > 8) top = r.top - h - 6;  // flip above when there is no room below
    tip.style.top = (top + window.scrollY) + "px";
  }
  function openTip(btn, pin) {
    clearTimeout(hideTimer);
    var t = TERMS.filter(function (x) { return x.id === btn.getAttribute("data-term"); })[0]; if (!t) return;
    if (openBtn === btn && !tip.hidden) { if (pin) pinned = true; return; }
    closeTip();
    var lg = nodeLang(btn);
    tip.innerHTML = "";
    var h = document.createElement("strong"); h.textContent = t["term_" + lg]; tip.appendChild(h);
    var p = document.createElement("span"); p.className = "gl-def"; p.textContent = t["def_" + lg]; tip.appendChild(p);
    var src = t["source_" + lg];
    if (src) { var a = document.createElement("a"); a.href = src; a.rel = "noopener"; a.target = "_blank"; a.textContent = lg === "fr" ? "Source officielle" : "Official source"; tip.appendChild(a); }
    var c = document.createElement("button"); c.type = "button"; c.className = "gl-close"; c.setAttribute("aria-label", lg === "fr" ? "Fermer" : "Close"); c.textContent = "×";
    c.addEventListener("click", function () { var b = openBtn; closeTip(); if (b) b.focus(); }); tip.appendChild(c);
    tip.setAttribute("lang", lg);
    tip.hidden = false; openBtn = btn; pinned = !!pin;
    btn.setAttribute("aria-expanded", "true"); btn.setAttribute("aria-describedby", "gl-tip");
    place(btn);
  }
  function laterClose() { clearTimeout(hideTimer); hideTimer = setTimeout(function () { if (!pinned) closeTip(); }, 250); }
  function mark() {
    if (!TERMS.length) return;
    var roots = document.querySelectorAll(SCOPE); if (!roots.length) return;
    var R = { en: build("en"), fr: build("fr") }, done = { en: {}, fr: {} };
    for (var i = 0; i < roots.length; i++) {
      if (roots[i].closest("[data-no-gl]")) continue;
      var walker = document.createTreeWalker(roots[i], NodeFilter.SHOW_TEXT, null), nodes = [], nd;
      while ((nd = walker.nextNode())) if (nd.nodeValue.trim() && !nd.parentNode.closest(SKIP)) nodes.push(nd);
      nodes.forEach(function (node) {
        var lg = nodeLang(node.parentNode), changed = true;
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
    tip = document.createElement("div"); tip.id = "gl-tip"; tip.className = "gl-tip"; tip.setAttribute("role", "tooltip"); tip.hidden = true;
    document.body.appendChild(tip);
    document.addEventListener("click", function (e) {
      var b = e.target.closest && e.target.closest(".gl-term");
      if (b) { e.preventDefault(); if (openBtn === b && pinned) { closeTip(); } else { openTip(b, true); } return; }
      if (!tip.contains(e.target)) closeTip();
    });
    document.addEventListener("pointerover", function (e) {
      if (e.pointerType !== "mouse") return;  // hover only for a real mouse; touch uses tap
      var b = e.target.closest && e.target.closest(".gl-term");
      if (b) { if (!pinned || openBtn === b) openTip(b, false); }
      else if (tip.contains(e.target)) clearTimeout(hideTimer);
    });
    document.addEventListener("pointerout", function (e) {
      if (e.pointerType !== "mouse" || pinned || !openBtn) return;
      var to = e.relatedTarget;
      if (to && (to === openBtn || openBtn.contains(to) || tip.contains(to))) return;
      if ((e.target.closest && e.target.closest(".gl-term")) || tip.contains(e.target)) laterClose();
    });
    document.addEventListener("focusin", function (e) {
      var b = e.target.closest && e.target.closest(".gl-term");
      if (!b) return;
      var kb = true; try { kb = b.matches(":focus-visible"); } catch (x) {}
      if (kb && openBtn !== b) openTip(b, false);
    });
    document.addEventListener("focusout", function (e) {
      if (!openBtn || pinned) return;
      var to = e.relatedTarget;
      if (to && (to === openBtn || tip.contains(to))) return;
      if (e.target === openBtn || tip.contains(e.target)) closeTip();
    });
    document.addEventListener("keydown", function (e) {
      if ((e.key === "Escape" || e.key === "Esc") && openBtn) { var b = openBtn; closeTip(); b.focus(); }
    });
    window.addEventListener("resize", closeTip);
    var ls = document.querySelectorAll("[data-set-lang]"); for (var j = 0; j < ls.length; j++) ls[j].addEventListener("click", closeTip);
  }
  function init() { upcoming(); openTarget(); mark(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
