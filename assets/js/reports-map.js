/* Map of our reports: draws links between report boxes when themes sit side by side (>= 640px).
   Without JS (or on narrow screens) the board stays a grouped list and every link is written out in the cards.
   Hover or keyboard focus on a report highlights its links. No libraries. */
(function () {
  var board = document.querySelector("[data-rmap]"), dataEl = document.getElementById("rmap-links");
  if (!board || !dataEl) return;
  var links; try { links = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var svg = board.querySelector(".rmap-lines"), NS = "http://www.w3.org/2000/svg";
  var nodes = {}; Array.prototype.forEach.call(board.querySelectorAll(".rmap-node"), function (n) { nodes[n.getAttribute("data-node")] = n; });
  var drawn = false, mq = window.matchMedia("(min-width: 640px)");
  function box(n, b) { var r = n.getBoundingClientRect(); return { l: r.left - b.left, r: r.right - b.left, t: r.top - b.top, b: r.bottom - b.top, cy: (r.top + r.bottom) / 2 - b.top }; }
  function arrow(x, y, dir) { var s = 6; return " M" + (x - dir * s) + "," + (y - s) + " L" + x + "," + y + " L" + (x - dir * s) + "," + (y + s); }
  function draw() {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (!mq.matches) { board.classList.remove("has-lines"); return; }
    board.classList.add("has-lines");
    var b = board.getBoundingClientRect(), slot = {};
    links.forEach(function (l) {
      var A = nodes[l.from], B = nodes[l.to]; if (!A || !B) return;
      var a = box(A, b), c = box(B, b), d;
      if (Math.abs(a.l - c.l) < 4) { /* same column: bow out to the right */
        var k = (slot[a.l] = (slot[a.l] || 0) + 1), bow = 16 + 10 * k, x = a.r;
        d = "M" + x + "," + a.cy + " C" + (x + bow) + "," + a.cy + " " + (x + bow) + "," + c.cy + " " + x + "," + c.cy + arrow(x, c.cy, -1);
        if (l.both) d += arrow(x, a.cy, -1);
      } else {
        var ltr = a.l < c.l, x1 = ltr ? a.r : a.l, x2 = ltr ? c.l : c.r, mid = (x1 + x2) / 2;
        d = "M" + x1 + "," + a.cy + " C" + mid + "," + a.cy + " " + mid + "," + c.cy + " " + x2 + "," + c.cy + arrow(x2, c.cy, ltr ? 1 : -1);
        if (l.both) d += arrow(x1, a.cy, ltr ? -1 : 1);
      }
      var p = document.createElementNS(NS, "path");
      p.setAttribute("d", d); p.setAttribute("class", l.kind === "subject" ? "subject" : "link");
      p.setAttribute("data-from", l.from); p.setAttribute("data-to", l.to);
      svg.appendChild(p);
      if (!drawn) { var len = Math.ceil(p.getTotalLength ? p.getTotalLength() : 600); p.style.setProperty("--len", len); p.classList.add("draw"); }
    });
    drawn = true;
  }
  function focus(url) {
    board.classList.toggle("is-focus", !!url);
    Object.keys(nodes).forEach(function (k) { nodes[k].classList.remove("on", "cur"); });
    Array.prototype.forEach.call(svg.querySelectorAll("path"), function (p) {
      var on = url && (p.getAttribute("data-from") === url || p.getAttribute("data-to") === url);
      p.classList.toggle("on", !!on);
      if (on) { nodes[p.getAttribute("data-from")].classList.add("on"); nodes[p.getAttribute("data-to")].classList.add("on"); }
    });
    if (url) nodes[url].classList.add("on", "cur");
  }
  Object.keys(nodes).forEach(function (k) {
    var n = nodes[k];
    n.addEventListener("mouseenter", function () { focus(k); }); n.addEventListener("mouseleave", function () { focus(null); });
    n.addEventListener("focus", function () { focus(k); }); n.addEventListener("blur", function () { focus(null); });
  });
  var t; function later() { clearTimeout(t); t = setTimeout(draw, 120); }
  window.addEventListener("resize", later);
  Array.prototype.forEach.call(document.querySelectorAll("[data-set-lang]"), function (btn) { btn.addEventListener("click", function () { setTimeout(draw, 30); }); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw); else draw();
  draw();
})();
