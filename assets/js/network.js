/* Network page: force-directed bubble map of people/organizations co-mentioned in published stories.
   Data: _data/network.json (built by _tools/network.py), served at assets/data/network.json.
   A link = two names mentioned in the same story. Edges are never labelled with anything else. */
(function () {
  "use strict";
  var BLUE = "#0b3d91", RED = "#c8102e";
  var mapEl = document.getElementById("net-map");
  if (!mapEl || !window.d3) return;
  var BASE = mapEl.getAttribute("data-base") || "/";
  var FR_M = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];
  var EN_M = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]; }); }
  function bi(en, fr) { return '<span class="l-en" lang="en">' + en + '</span><span class="l-sep" aria-hidden="true"> / </span><span class="l-fr" lang="fr">' + fr + "</span>"; }
  function lang() { return document.documentElement.classList.contains("lang-fr") ? "fr" : "en"; }
  function dates(d) { var p = d.split("-"), m = +p[1] - 1, day = +p[2]; return bi(EN_M[m] + " " + day + ", " + p[0], day + " " + FR_M[m] + " " + p[0]); }
  function nStories(n) { return bi(n + (n === 1 ? " story" : " stories"), n + (n === 1 ? " article" : " articles")); }
  function fold(s) { return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[’']/g, "'").toLowerCase(); }
  function postUrl(d) { return BASE + d.replace(/-/g, "/") + "/digest/"; }

  fetch(mapEl.getAttribute("data-src")).then(function (r) { return r.json(); }).then(init).catch(function (e) {
    mapEl.innerHTML = "<p>" + bi("Could not load the network data.", "Impossible de charger les données du réseau.") + "</p>";
    if (window.console) console.warn(e);
  });

  function init(data) {
    var nodes = data.nodes.map(function (n) { return Object.assign({}, n); });
    var byId = {}; nodes.forEach(function (n) { byId[n.id] = n; n.nb = []; });
    var links = data.edges.map(function (e) { return Object.assign({}, e); });
    var edgeKey = {};
    links.forEach(function (l) {
      byId[l.source].nb.push({ id: l.target, link: l }); byId[l.target].nb.push({ id: l.source, link: l });
      edgeKey[l.source + "|" + l.target] = l; edgeKey[l.target + "|" + l.source] = l;
    });
    nodes.forEach(function (n) { n.nb.sort(function (a, b) { return b.link.weight - a.link.weight || byId[a.id].name.localeCompare(byId[b.id].name); }); });
    var maxM = d3.max(nodes, function (n) { return n.mentions; }) || 1;
    var r = d3.scaleSqrt().domain([1, maxM]).range([6, 30]);
    

    var days = Object.keys(data.days).sort();
    document.getElementById("net-stats").innerHTML = bi(
      nodes.length + " names, " + links.length + " links, from " + data.story_count + " stories (" + days[0] + " to " + days[days.length - 1] + ").",
      nodes.length + " noms, " + links.length + " liens, tirés de " + data.story_count + " articles (du " + days[0] + " au " + days[days.length - 1] + ").");

    var W = mapEl.clientWidth || 720, H = W < 520 ? Math.round(Math.max(420, W * 1.25)) : Math.round(Math.min(640, W * 0.82));
    var svg = d3.select(mapEl).append("svg").attr("class", "net-svg").attr("viewBox", [0, 0, W, H]).attr("width", "100%").attr("height", H)
      .attr("role", "group").attr("aria-label", "Network map / Carte du réseau");
    var g = svg.append("g");
    var gl = g.append("g").attr("class", "net-links");
    var gn = g.append("g").attr("class", "net-nodes");

    var sim = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(function (d) { return d.id; }).distance(function (l) { return 34 + r(l.source.mentions || 1) * 0.6; }).strength(function (l) { return Math.min(1, 0.25 + 0.15 * l.weight); }))
      .force("charge", d3.forceManyBody().strength(function (d) { return -55 - r(d.mentions) * 6; }))
      .force("collide", d3.forceCollide(function (d) { return r(d.mentions) + 3; }))
      .force("x", d3.forceX(W / 2).strength(0.07)).force("y", d3.forceY(H / 2).strength(W < 520 ? 0.06 : 0.09))
      .stop();
    for (var i = 0; i < 400; i++) sim.tick();

    var link = gl.selectAll("g").data(links).join("g").attr("class", "net-link");
    link.append("line").attr("class", "vis").attr("stroke-width", function (l) { return 1 + Math.min(4, (l.weight - 1) * 1.2); });
    link.append("line").attr("class", "hit");
    link.append("title").text(function (l) { return l.source.name + " — " + l.target.name + " (" + l.weight + ")"; });
    link.on("click", function (ev, l) { ev.stopPropagation(); showPair(l.source.id, l.target.id, true); });

    var node = gn.selectAll("g").data(nodes).join("g").attr("class", function (d) { return "net-node " + (d.type === "person" ? "per" : "org"); })
      .attr("tabindex", 0).attr("role", "button");
    node.append("circle").attr("class", "hit").attr("r", function (d) { return r(d.mentions) + 7; });
    node.append("circle").attr("class", "vis").attr("r", function (d) { return r(d.mentions); }).attr("fill", function (d) { return d.type === "person" ? RED : BLUE; });
    nodes.forEach(function (d) {
      var ac = (d.aliases || []).filter(function (a) { return /^[A-ZÉ][A-ZÉ0-9-]{1,6}$/.test(a); })[0];
      d.short = d.name.length > 18 && ac ? ac : d.name;
    });
    node.append("text").attr("class", "lbl").attr("dy", function (d) { return r(d.mentions) + 13; }).text(function (d) { return d.short; });
    
    function setAria() {
      var fr = lang() === "fr";
      node.attr("aria-label", function (d) {
        var t = d.type === "person" ? (fr ? "personne" : "person") : (fr ? "organisation" : "organization");
        var c = fr ? d.mentions + (d.mentions > 1 ? " articles" : " article") : d.mentions + (d.mentions > 1 ? " stories" : " story");
        return d.name + ", " + t + ", " + c;
      });
    }
    setAria();
    new MutationObserver(setAria).observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });

    var dragged = false;
    node.call(d3.drag()
      .on("start", function (ev, d) { dragged = false; if (!ev.active) sim.alphaTarget(0.2).restart(); d.fx = d.x; d.fy = d.y; })
      .on("drag", function (ev, d) { dragged = true; d.fx = ev.x; d.fy = ev.y; })
      .on("end", function (ev, d) { if (!ev.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));
    node.on("click", function (ev, d) { ev.stopPropagation(); if (dragged) { dragged = false; return; } select(d.id, true); });
    node.on("keydown", function (ev, d) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); select(d.id, true); } });
    sim.on("tick", draw); sim.on("end", function () { cullLabels((W < 520 ? 12.5 : 12) / lastK); });
    function draw() {
      link.selectAll("line").attr("x1", function (l) { return l.source.x; }).attr("y1", function (l) { return l.source.y; })
        .attr("x2", function (l) { return l.target.x; }).attr("y2", function (l) { return l.target.y; });
      node.attr("transform", function (d) { return "translate(" + d.x + "," + d.y + ")"; });
    }
    draw();

    var lbl = node.select("text.lbl"), lastK = 0;
    var zoom = d3.zoom().scaleExtent([0.3, 8]).on("zoom", function (ev) {
      g.attr("transform", ev.transform);
      var k = ev.transform.k; if (Math.abs(k - lastK) < 1e-3) return; lastK = k;
      var fs = (W < 520 ? 12.5 : 12) / k;  /* labels keep a readable on-screen size at any zoom */
      lbl.style("font-size", fs + "px").style("stroke-width", (3 / k) + "px").attr("dy", function (d) { return r(d.mentions) + fs * 1.1; });
      cullLabels(fs);
    });
    /* Show labels for the bigger bubbles only, skipping any label that would overlap one already shown. */
    var byMent = nodes.slice().sort(function (a, b) { return b.mentions - a.mentions; });
    function cullLabels(fs) {
      var boxes = [], minM = W < 520 ? 3 : 2, show = {};
      byMent.forEach(function (d) {
        if (d.mentions < minM) return;
        var w = d.short.length * fs * 0.58, h = fs * 1.2, x = d.x - w / 2, y = d.y + r(d.mentions) + fs * 0.1;
        var cr = r(d.mentions);
        for (var i = 0; i < boxes.length; i++) { var b = boxes[i]; if (x < b[2] && x + w > b[0] && y < b[3] && y + h > b[1]) return; }
        boxes.push([x, y, x + w, y + h]); boxes.push([d.x - cr, d.y - cr, d.x + cr, d.y + cr]); show[d.id] = 1;
      });
      node.classed("big", function (d) { return !!show[d.id]; });
    }
    svg.call(zoom).on("dblclick.zoom", null);
    function fitTransform() {
      var x0 = d3.min(nodes, function (d) { return d.x - r(d.mentions); }), x1 = d3.max(nodes, function (d) { return d.x + r(d.mentions); });
      var y0 = d3.min(nodes, function (d) { return d.y - r(d.mentions); }), y1 = d3.max(nodes, function (d) { return d.y + r(d.mentions) + 16; });
      var k = Math.min(2, 0.94 / Math.max((x1 - x0) / W, (y1 - y0) / H));
      return d3.zoomIdentity.translate(W / 2, H / 2).scale(k).translate(-(x0 + x1) / 2, -(y0 + y1) / 2);
    }
    svg.call(zoom.transform, fitTransform());
    document.querySelectorAll("[data-zoom]").forEach(function (b) {
      b.addEventListener("click", function () {
        var z = b.getAttribute("data-zoom");
        if (z === "in") svg.transition().duration(250).call(zoom.scaleBy, 1.4);
        else if (z === "out") svg.transition().duration(250).call(zoom.scaleBy, 1 / 1.4);
        else svg.transition().duration(300).call(zoom.transform, fitTransform());
      });
    });
    svg.on("click", function () { clearSel(); closePanel(false); });

    /* ---------- highlight ---------- */
    var current = null;
    function highlight(ids, edge) {
      var set = {}; ids.forEach(function (i) { set[i] = 1; });
      if (!edge && ids.length === 1) byId[ids[0]].nb.forEach(function (x) { set[x.id] = 1; });
      svg.classed("has-sel", true);
      node.classed("dim", function (d) { return !set[d.id]; }).classed("sel", function (d) { return ids.indexOf(d.id) >= 0; }).classed("nbr", function (d) { return !!set[d.id]; });
      link.classed("hl", function (l) {
        if (edge) return l === edge;
        return l.source.id === ids[0] || l.target.id === ids[0];
      }).classed("dim", function (l) { return edge ? l !== edge : !(l.source.id === ids[0] || l.target.id === ids[0]); });
      gn.selectAll(".net-node.sel").raise();
    }
    function clearSel() { current = null; svg.classed("has-sel", false); node.classed("dim sel nbr", false); link.classed("hl dim", false); }
    function centerOn(d) {
      var t = d3.zoomTransform(svg.node()), k = Math.max(t.k, 1.2);
      svg.transition().duration(400).call(zoom.transform, d3.zoomIdentity.translate(W / 2, H / 2).scale(k).translate(-d.x, -d.y));
    }

    /* ---------- panel ---------- */
    var panel = document.getElementById("net-panel"), body = document.getElementById("net-panel-body");
    var back = document.getElementById("net-back"), closeBtn = document.getElementById("net-close");
    var returnFocus = null, lastEntity = null, dossiers = [];
    try { dossiers = JSON.parse((document.getElementById("net-dossiers") || {}).textContent || "[]"); } catch (e) { dossiers = []; }
    function storyList(list) {
      var s = list.slice().sort(function (a, b) { return b.date.localeCompare(a.date) || a.headline.localeCompare(b.headline); });
      return '<ul class="net-stories">' + s.map(function (st) {
        return '<li><span class="net-date"><a href="' + esc(postUrl(st.date)) + '">' + dates(st.date) + "</a></span> " +
          '<a class="net-hl" href="' + esc(st.url) + '" target="_blank" rel="noopener">' + esc(st.headline) + "</a></li>";
      }).join("") + "</ul>";
    }
    function typeLbl(d) { return d.type === "person" ? bi("Person", "Personne") : bi("Organization", "Organisation"); }
    function openPanel() {
      if (panel.hidden) returnFocus = document.activeElement;
      panel.hidden = false; document.body.classList.add("net-open");
      var h = document.getElementById("net-panel-title"); if (h) h.focus({ preventScroll: true });
      panel.scrollTop = 0;
    }
    function closePanel(restore) {
      if (panel.hidden) return;
      panel.hidden = true; document.body.classList.remove("net-open"); clearSel();
      if (restore !== false && returnFocus && returnFocus.focus) returnFocus.focus();
    }
    function select(id, center) {
      var d = byId[id]; if (!d) return;
      current = id; lastEntity = id; highlight([id]);
      if (center) centerOn(d);
      back.hidden = true;
      var html = '<p class="net-kind"><span class="net-dot ' + (d.type === "person" ? "per" : "org") + '" aria-hidden="true"></span>' + typeLbl(d) + "</p>" +
        '<h2 id="net-panel-title" tabindex="-1">' + esc(d.name) + "</h2>";
      if (d.aliases && d.aliases.length) html += '<p class="net-alias">' + bi("Also: ", "Aussi : ") + esc(d.aliases.join(", ")) + "</p>";
      html += '<h3>' + bi("Stories naming " + esc(d.name), "Articles qui nomment " + esc(d.name)) + " (" + d.stories.length + ")</h3>" + storyList(d.stories);
      var ds = dossiers.filter(function (x) { return x.entities.indexOf(id) >= 0; });
      if (ds.length) html += "<h3>" + bi("Appears in these dossiers", "Figure dans ces dossiers") + " (" + ds.length + ")</h3>" +
        '<ul class="net-dossiers">' + ds.map(function (x) {
          return '<li><a href="' + esc(BASE + "chronology/" + x.id + "/") + '">' + bi(esc(x.en), esc(x.fr)) + "</a></li>";
        }).join("") + "</ul>";
      html += '<h3>' + bi("Named in the same stories as", "Nommé dans les mêmes articles que") + " (" + d.nb.length + ")</h3>";
      if (!d.nb.length) html += "<p>" + bi("No other name in these stories.", "Aucun autre nom dans ces articles.") + "</p>";
      else html += '<p class="net-hint">' + bi("Select a name to see the stories where both appear.", "Choisissez un nom pour voir les articles où les deux apparaissent.") + "</p>" +
        '<ul class="net-nb">' + d.nb.map(function (x) {
          var o = byId[x.id];
          return '<li><button type="button" class="net-nbbtn" data-pair="' + esc(x.id) + '"><span class="net-dot ' + (o.type === "person" ? "per" : "org") + '" aria-hidden="true"></span>' +
            '<span class="net-nbname">' + esc(o.name) + '</span> <span class="net-count">' + nStories(x.link.weight) + "</span></button></li>";
        }).join("") + "</ul>";
      body.innerHTML = html; openPanel();
    }
    function showPair(a, b, fromEdge) {
      var A = byId[a], B = byId[b], l = edgeKey[a + "|" + b]; if (!l) return;
      highlight([a, b], l);
      var html = '<p class="net-kind">' + bi("Shared stories", "Articles communs") + "</p>" +
        '<h2 id="net-panel-title" tabindex="-1">' + esc(A.name) + ' <span class="net-amp">&amp;</span> ' + esc(B.name) + "</h2>" +
        '<p class="net-note">' + bi("Both names appear in these stories. This does not imply any relationship, wrongdoing or involvement.",
          "Les deux noms apparaissent dans ces articles. Cela n’implique aucune relation, faute ou implication.") + "</p>" +
        "<h3>" + bi("Stories naming both", "Articles qui nomment les deux") + " (" + l.stories.length + ")</h3>" + storyList(l.stories) +
        '<p class="net-jump">' + bi("Open: ", "Ouvrir : ") + '<button type="button" class="net-btn net-link-btn" data-ent="' + esc(a) + '">' + esc(A.name) + "</button> " +
        '<button type="button" class="net-btn net-link-btn" data-ent="' + esc(b) + '">' + esc(B.name) + "</button></p>";
      body.innerHTML = html; openPanel();
      back.hidden = !!fromEdge; back.setAttribute("data-ent", fromEdge ? "" : a);
    }
    body.addEventListener("click", function (ev) {
      var t = ev.target.closest("[data-pair],[data-ent]"); if (!t) return;
      if (t.hasAttribute("data-pair")) showPair(current || lastEntity, t.getAttribute("data-pair"), false);
      else select(t.getAttribute("data-ent"), true);
    });
    back.addEventListener("click", function () { var e = back.getAttribute("data-ent"); if (e) select(e, false); });
    closeBtn.addEventListener("click", function () { closePanel(true); });
    document.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && !panel.hidden) closePanel(true); });

    /* ---------- list + search ---------- */
    var listEl = document.getElementById("net-list");
    listEl.innerHTML = nodes.map(function (d) {
      return '<li><button type="button" class="net-nbbtn" data-sel="' + esc(d.id) + '"><span class="net-dot ' + (d.type === "person" ? "per" : "org") + '" aria-hidden="true"></span>' +
        '<span class="net-nbname">' + esc(d.name) + '</span> <span class="net-count">(' + d.mentions + ")</span></button></li>";
    }).join("");
    listEl.addEventListener("click", function (ev) { var t = ev.target.closest("[data-sel]"); if (t) select(t.getAttribute("data-sel"), true); });

    var q = document.getElementById("net-q"), res = document.getElementById("net-results");
    nodes.forEach(function (d) { d._k = fold([d.name].concat(d.aliases || []).join(" | ")); });
    function search() {
      var v = fold(q.value.trim());
      if (v.length < 2) { res.hidden = true; res.innerHTML = ""; return; }
      var m = nodes.filter(function (d) { return d._k.indexOf(v) >= 0; }).slice(0, 8);
      res.innerHTML = m.length ? m.map(function (d) {
        return '<li><button type="button" class="net-nbbtn" data-sel="' + esc(d.id) + '"><span class="net-dot ' + (d.type === "person" ? "per" : "org") + '" aria-hidden="true"></span>' +
          '<span class="net-nbname">' + esc(d.name) + '</span> <span class="net-count">(' + d.mentions + ")</span></button></li>";
      }).join("") : "<li class=\"net-none\">" + bi("No match.", "Aucun résultat.") + "</li>";
      res.hidden = false;
    }
    q.addEventListener("input", search);
    q.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter") { ev.preventDefault(); var f = res.querySelector("[data-sel]"); if (f) { select(f.getAttribute("data-sel"), true); res.hidden = true; } }
      if (ev.key === "ArrowDown") { var b = res.querySelector("button"); if (b) { ev.preventDefault(); b.focus(); } }
    });
    res.addEventListener("click", function (ev) { var t = ev.target.closest("[data-sel]"); if (t) { select(t.getAttribute("data-sel"), true); res.hidden = true; } });
    res.addEventListener("keydown", function (ev) {
      var bs = Array.prototype.slice.call(res.querySelectorAll("button")), i = bs.indexOf(document.activeElement);
      if (ev.key === "ArrowDown" && i < bs.length - 1) { ev.preventDefault(); bs[i + 1].focus(); }
      if (ev.key === "ArrowUp") { ev.preventDefault(); if (i > 0) bs[i - 1].focus(); else q.focus(); }
    });
    function fromHash() { var h = decodeURIComponent(location.hash.slice(1)); if (h && byId[h]) select(h, true); }
    window.addEventListener("hashchange", fromHash); fromHash();
    window.qgmNetwork = { select: select, showPair: showPair, close: closePanel, nodes: nodes, links: links };
  }
})();
