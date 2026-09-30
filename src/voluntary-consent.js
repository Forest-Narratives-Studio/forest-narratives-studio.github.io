/**
 * Voluntary Consent — scroll-driven body background.
 * Scope: body.fns-vc-theme only. No libraries.
 *
 * Scroll readout = scrollY + 40% of viewport height so color shifts when a
 * section is meaningfully in view (not only when its top hits the viewport edge).
 *
 * Anchor colors are darkened section hues (~40–75% mix, still below panel luminance).
 */
(function () {
  "use strict";

  var body = document.body;
  if (!body || !body.classList.contains("fns-vc-theme")) return;

  // Dark page-chrome anchors (same gamut as panels / paper, mixed toward black).
  // Bright enough for hue to read while scrolling; still darker than each panel.
  // 1: paper cream #e8e6e1 × ~0.40 warm → #5a564c
  // 2: navy_frost #151b3f × ~0.72     → #0e1230
  // 3: lab #0e1a1c × ~0.75            → #0a1416
  // 4: burgundy #3a0f27 × ~0.55       → #200a16
  var COLORS = [
    [0x5a, 0x56, 0x4c],
    [0x0e, 0x12, 0x30],
    [0x0a, 0x14, 0x16],
    [0x20, 0x0a, 0x16],
  ];

  /** Fraction of viewport height added to scrollY for the mix readout. */
  var VIEWPORT_OFFSET = 0.4;

  var rafId = 0;

  function hex(r, g, b) {
    return (
      "#" +
      ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1)
    );
  }

  function lerpChannel(a, b, t) {
    return Math.round(a + (b - a) * t);
  }

  function lerpColor(c0, c1, t) {
    return hex(
      lerpChannel(c0[0], c1[0], t),
      lerpChannel(c0[1], c1[1], t),
      lerpChannel(c0[2], c1[2], t)
    );
  }

  function docYTop(el) {
    return el.getBoundingClientRect().top + (window.scrollY || window.pageYOffset || 0);
  }

  /**
   * Resolve the four part sections. Re-query every time so a too-early first
   * run (or a replaced main) cannot permanently disable updates.
   * @returns {HTMLElement[] | null}
   */
  function queryParts() {
    var part1 = document.querySelector(".fns-vc-part--1");
    var part2 = document.querySelector(".fns-vc-part--2");
    var part3 = document.querySelector(".fns-vc-part--3");
    var part4 = document.querySelector(".fns-vc-part--4");
    if (!part1 || !part2 || !part3 || !part4) return null;
    return [part1, part2, part3, part4];
  }

  /**
   * Four document-Y anchors (top → bottom):
   * 1–3: tops of .fns-vc-part--1…--3
   * 4: page bottom in readout space = maxScroll + 40% vh
   *    (always reachable; raw part-4 bottom / scrollHeight can sit past the readout).
   */
  function collectAnchors(parts) {
    var vh = window.innerHeight || document.documentElement.clientHeight || 0;
    var scrollHeight = Math.max(
      document.documentElement.scrollHeight,
      body.scrollHeight || 0
    );
    var maxScroll = Math.max(0, scrollHeight - vh);
    var y1 = docYTop(parts[0]);
    var y2 = docYTop(parts[1]);
    var y3 = docYTop(parts[2]);
    var y4 = maxScroll + vh * VIEWPORT_OFFSET;

    var ys = [y1, y2, y3, y4];
    // Keep strictly non-decreasing so degenerate layouts still lerp safely.
    for (var i = 1; i < ys.length; i++) {
      if (ys[i] < ys[i - 1]) ys[i] = ys[i - 1];
    }
    return ys;
  }

  function applyBg(color) {
    // Keep sky / global body background-image from showing through chrome.
    body.style.backgroundImage = "none";
    body.style.setProperty("--vc-page-bg", color);
    body.style.backgroundColor = color;
  }

  function update() {
    rafId = 0;
    var parts = queryParts();
    if (!parts) return;

    var ys = collectAnchors(parts);
    var vh = window.innerHeight || document.documentElement.clientHeight || 0;
    var scrollY = window.scrollY || window.pageYOffset || 0;
    var pos = scrollY + vh * VIEWPORT_OFFSET;

    if (pos <= ys[0]) {
      applyBg(hex(COLORS[0][0], COLORS[0][1], COLORS[0][2]));
      return;
    }
    if (pos >= ys[ys.length - 1]) {
      var last = COLORS[COLORS.length - 1];
      applyBg(hex(last[0], last[1], last[2]));
      return;
    }

    for (var i = 0; i < ys.length - 1; i++) {
      var y0 = ys[i];
      var y1 = ys[i + 1];
      if (pos > y1) continue;
      var span = y1 - y0;
      var t = span <= 0 ? 1 : Math.min(1, Math.max(0, (pos - y0) / span));
      applyBg(lerpColor(COLORS[i], COLORS[i + 1], t));
      return;
    }
  }

  function scheduleUpdate() {
    if (rafId) return;
    rafId = window.requestAnimationFrame(update);
  }

  function onResize() {
    scheduleUpdate();
  }

  // Initial paint + late layout (fonts / images can shift part tops).
  update();
  scheduleUpdate();
  window.addEventListener("load", scheduleUpdate);

  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", onResize, { passive: true });
  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", onResize, { passive: true });
    window.visualViewport.addEventListener("scroll", scheduleUpdate, { passive: true });
  }
})();
