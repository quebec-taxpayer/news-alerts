/* Special Reports index: "Trier par / Sort by" control. The server-rendered order (newest first, first-publication
   rules in _includes/report-order.html) is the default and what readers without JS get; the control stays hidden
   without JS. JS only re-orders the existing cards of the "More to explore" grid; the featured (newest) report stays
   in its block above. Theme grouping uses _data/report_map.json (same themes as /reports-map/). The choice is kept
   for the browser tab only (sessionStorage); a fresh visit always starts with newest first. No libraries. */
(function () {
  var box = document.querySelector("[data-report-sort]"), sel = document.getElementById("report-sort-select"),
      grid = document.getElementById("report-sort-grid");
  if (!box || !sel || !grid) return;
  var themes = []; try { themes = JSON.parse(document.getElementById("report-sort-themes").textContent) || []; } catch (e) {}
  var cards = Array.prototype.slice.call(grid.querySelectorAll(".report-card"));
  var featured = document.querySelector(".report-card.featured");
  var status = document.querySelector("[data-sort-status]"), desc = document.querySelector("[data-sort-desc]");
  var KEY = "altviews-report-sort", h = document.documentElement;
  var DESC = {
    newest: ["Du plus récent au plus ancien.", "Newest first."],
    oldest: ["Du plus ancien au plus récent.", "Oldest first."],
    title: ["Par titre, de A à Z.", "By title, A to Z."],
    theme: ["Par thème, du plus récent au plus ancien dans chaque thème.", "By theme, newest first within each theme."]
  };
  var FEAT = [" Le rapport à la une, le plus récent, reste ci-dessus.", " The featured report, the newest, stays above."];
  function lang() { return h.lang === "en" ? "en" : "fr"; }
  function li() { return lang() === "en" ? 1 : 0; }
  function themeIndex(id) { for (var i = 0; i < themes.length; i++) if (themes[i].id === id) return i; return themes.length; }
  function byDate(dir) {
    return function (a, b) {
      var da = a.getAttribute("data-date") || "", db = b.getAttribute("data-date") || "";
      if (!da !== !db) return da ? -1 : 1;            /* undated last, as on the server */
      if (da !== db) return dir * (da < db ? -1 : 1);
      var ua = a.getAttribute("data-url"), ub = b.getAttribute("data-url");
      return ua < ub ? -1 : ua > ub ? 1 : 0;          /* same day: canonical URL ascending, as on the server */
    };
  }
  function byTitle(a, b) {
    var k = "data-title-" + lang(), c = (window.Intl && Intl.Collator) ? new Intl.Collator(lang(), { sensitivity: "base", ignorePunctuation: true, numeric: true }) : null;
    var x = a.getAttribute(k) || "", y = b.getAttribute(k) || "";
    return c ? c.compare(x, y) : x.localeCompare(y);
  }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function bi(fr, en) { return '<span class="l-fr" lang="fr">' + esc(fr) + '</span><span class="l-en" lang="en">' + esc(en) + "</span>"; }
  function render(mode, announce) {
    Array.prototype.forEach.call(grid.querySelectorAll(".sort-group, .sort-featured-note"), function (n) { n.parentNode.removeChild(n); });
    var list = cards.slice();
    if (mode === "oldest") list.sort(byDate(1));
    else if (mode === "title") list.sort(byTitle);
    else if (mode === "theme") list.sort(function (a, b) { return (themeIndex(a.getAttribute("data-theme")) - themeIndex(b.getAttribute("data-theme"))) || byDate(-1)(a, b); });
    else list.sort(byDate(-1));
    if (mode === "theme") {
      var ft = featured && featured.getAttribute("data-theme"), groups = {};
      list.forEach(function (c) { var t = c.getAttribute("data-theme"); (groups[t] = groups[t] || []).push(c); });
      if (ft && !groups[ft]) groups[ft] = [];
      var ids = Object.keys(groups).sort(function (a, b) { return themeIndex(a) - themeIndex(b); });
      ids.forEach(function (id) {
        var t = themes[themeIndex(id)] || { fr: id, en: id };
        var head = el("div", "sort-group", bi(t.fr, t.en)); head.setAttribute("role", "heading"); head.setAttribute("aria-level", "3");
        grid.appendChild(head);
        if (id === ft) {
          var tf = featured.getAttribute("data-title-fr"), te = featured.getAttribute("data-title-en"), u = featured.getAttribute("data-url");
          grid.appendChild(el("p", "sort-featured-note", '<span class="l-fr" lang="fr">À la une ci-dessus : <a href="' + esc(u) + '">' + esc(tf) + '</a></span><span class="l-en" lang="en">Featured above: <a href="' + esc(u) + '">' + esc(te) + "</a></span>"));
        }
        groups[id].forEach(function (c) { grid.appendChild(c); });
      });
    } else {
      list.forEach(function (c) { grid.appendChild(c); });
    }
    grid.setAttribute("data-mode", mode);
    if (desc) desc.innerHTML = bi(DESC[mode][0] + (featured && mode !== "newest" ? FEAT[0] : ""), DESC[mode][1] + (featured && mode !== "newest" ? FEAT[1] : ""));
    if (announce) {
      grid.classList.remove("sort-anim"); void grid.offsetWidth; grid.classList.add("sort-anim");
      var o = sel.options[sel.selectedIndex];
      if (status) status.textContent = (lang() === "en" ? "Reports sorted: " : "Rapports triés : ") + o.getAttribute("data-" + lang()) + ".";
    }
  }
  function labels() { Array.prototype.forEach.call(sel.options, function (o) { o.textContent = o.getAttribute("data-" + lang()); }); }
  var mode = "newest";
  try { var saved = sessionStorage.getItem(KEY); if (saved && DESC[saved]) mode = saved; } catch (e) {}
  sel.value = mode; labels(); box.hidden = false;
  if (mode !== "newest") render(mode, false);
  sel.addEventListener("change", function () {
    var m = DESC[sel.value] ? sel.value : "newest";
    try { if (m === "newest") sessionStorage.removeItem(KEY); else sessionStorage.setItem(KEY, m); } catch (e) {}
    render(m, true);
  });
  Array.prototype.forEach.call(document.querySelectorAll("[data-set-lang]"), function (b) {
    b.addEventListener("click", function () { setTimeout(function () { labels(); if (sel.value === "title") render("title", false); }, 0); });
  });
})();
