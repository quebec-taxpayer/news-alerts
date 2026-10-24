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
