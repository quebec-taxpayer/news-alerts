/* SVG timeline: play animation when visible, detail panel on hover/focus/tap, arrow-key navigation. No libraries. */
(function () {
  var tls = document.querySelectorAll("[data-tl]");
  if (!tls.length) return;
  var wide = window.matchMedia ? window.matchMedia("(min-width: 721px)") : { matches: true };
  function lang() { return document.documentElement.classList.contains("lang-fr") ? "fr" : "en"; }
  Array.prototype.forEach.call(tls, function (tl) {
    tl.classList.add("js");
    var list = tl.querySelector("[data-tl-list]"), panel = tl.querySelector("[data-tl-panel]");
    if (list && wide.matches) list.removeAttribute("open");
    // Play once when scrolled into view (CSS skips it under prefers-reduced-motion).
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (en) { if (en.isIntersecting) { tl.classList.add("tl-run"); io.disconnect(); } });
      }, { threshold: 0.25 });
      io.observe(tl);
    } else { tl.classList.add("tl-run"); }
    function show(a) {
      var li = document.getElementById(tl.id + "-" + a.getAttribute("data-ev"));
      if (!li || !panel) return;
      var c = li.cloneNode(true); c.removeAttribute("id");
      var box = document.createElement("div"); box.className = "svg-tl-detail";
      Array.prototype.forEach.call(c.querySelectorAll("p"), function (p) { box.appendChild(p); });
      panel.innerHTML = ""; panel.appendChild(box);
      Array.prototype.forEach.call(tl.querySelectorAll(".tl-ev.is-on"), function (x) { x.classList.remove("is-on"); });
      Array.prototype.forEach.call(tl.querySelectorAll('.tl-ev[data-ev="' + a.getAttribute("data-ev") + '"]'), function (x) { x.classList.add("is-on"); });
    }
    var evs = tl.querySelectorAll("a.tl-ev");
    Array.prototype.forEach.call(evs, function (a) {
      a.addEventListener("mouseenter", function () { show(a); });
      a.addEventListener("focus", function () { show(a); });
      // Touch: first tap shows the details, second tap follows the source link.
      a.addEventListener("touchend", function (e) {
        if (!a.classList.contains("is-on")) { e.preventDefault(); show(a); }
      });
      a.addEventListener("keydown", function (e) {
        var k = e.key; if (["ArrowRight", "ArrowLeft", "Home", "End"].indexOf(k) < 0) return;
        var vis = Array.prototype.filter.call(evs, function (x) { return x.classList.contains("l-" + lang()); });
        var i = vis.indexOf(a), j = k === "ArrowRight" ? Math.min(i + 1, vis.length - 1) : k === "ArrowLeft" ? Math.max(i - 1, 0) : k === "Home" ? 0 : vis.length - 1;
        e.preventDefault(); vis[j].focus();
      });
    });
  });
})();

/* Dossier pages with a visual timeline: on phones, the detailed event list starts closed to avoid repeating the steps; always open on desktop and in print. */
(function () {
  var dd = document.querySelectorAll("[data-dossier-detail]");
  if (!dd.length || !window.matchMedia) return;
  var phone = window.matchMedia("(max-width: 720px)");
  function set() { Array.prototype.forEach.call(dd, function (d) { if (phone.matches) d.removeAttribute("open"); else d.setAttribute("open", ""); }); }
  set();
  if (phone.addEventListener) phone.addEventListener("change", set); else if (phone.addListener) phone.addListener(set);
  var was = [];
  window.addEventListener("beforeprint", function () { was = Array.prototype.map.call(dd, function (d) { return d.open; }); Array.prototype.forEach.call(dd, function (d) { d.setAttribute("open", ""); }); });
  window.addEventListener("afterprint", function () { Array.prototype.forEach.call(dd, function (d, i) { if (!was[i]) d.removeAttribute("open"); }); });
})();
