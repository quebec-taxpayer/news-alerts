/* Visual timeline (special reports): gentle reveal on scroll, count-up of the summary numbers, and
   "click a dot on the axis to open that event". Everything is already visible and usable without this file.
   Honors prefers-reduced-motion (no animation, no count-up). */
(function () {
  if (window.qgmVtLoaded) return; /* several includes on one page each load this file: run once */
  window.qgmVtLoaded = true;
  var roots = document.querySelectorAll("[data-vt]");
  if (!roots.length) return;
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var io = !still && "IntersectionObserver" in window;
  function countUp(el) {
    var n = parseInt(el.getAttribute("data-n"), 10);
    if (isNaN(n) || n < 2) return;
    var t0 = null, dur = 700;
    function step(t) { if (!t0) t0 = t; var p = Math.min(1, (t - t0) / dur); el.textContent = Math.round(n * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(step); }
    el.textContent = "0"; requestAnimationFrame(step);
  }
  Array.prototype.forEach.call(roots, function (root) {
    var pins = root.querySelectorAll("[data-vt-open]");
    function mark(id) {
      Array.prototype.forEach.call(pins, function (p) { p.classList.toggle("is-active", p.getAttribute("data-vt-open") === id); });
      Array.prototype.forEach.call(root.querySelectorAll(".vt-item"), function (li) { li.classList.toggle("is-active", li.id === id); });
    }
    Array.prototype.forEach.call(pins, function (p) {
      p.addEventListener("click", function () {
        var id = p.getAttribute("data-vt-open"), li = document.getElementById(id);
        if (!li) return;
        var d = li.querySelector("details"); if (d) d.open = true;
        mark(id);
        li.scrollIntoView({ block: "nearest", behavior: still ? "auto" : "smooth" });
        var s = li.querySelector("summary"); if (s) s.focus({ preventScroll: true });
      });
    });
    Array.prototype.forEach.call(root.querySelectorAll(".vt-item details"), function (d) {
      d.addEventListener("toggle", function () { if (d.open) mark(d.parentNode.id); });
    });
    if (!io) return;
    root.classList.add("vt-anim");
    var els = Array.prototype.slice.call(root.querySelectorAll(".vt-stat, .vt-axis, .vt-item, .vb-anim"));
    function reveal(el) {
      if (el.classList.contains("is-in")) return;
      el.classList.add("is-in"); obs.unobserve(el);
      var num = el.classList.contains("vt-stat") && el.querySelector("[data-n]"); if (num) countUp(num);
    }
    /* reveal what enters the viewport, plus anything above it the reader skipped past (anchor jump, fast scroll) */
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting && en.boundingClientRect.top > 0) return;
        var k = els.indexOf(en.target);
        for (var j = 0; j <= k; j++) reveal(els[j]);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.15 });
    els.forEach(function (el) { obs.observe(el); });
  });
  window.addEventListener("beforeprint", function () {
    Array.prototype.forEach.call(document.querySelectorAll(".vt-item details, details.vt-table"), function (d) { d.open = true; });
  });
})();
