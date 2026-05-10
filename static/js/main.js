// ── Date display ─────────────────────────────────────────────────────
(function () {
  const el = document.getElementById("js-date");
  if (!el) return;
  const d = new Date();
  const opts = { weekday: "short", year: "numeric", month: "short", day: "numeric" };
  el.textContent = d.toLocaleDateString("en-GB", opts);
})();
