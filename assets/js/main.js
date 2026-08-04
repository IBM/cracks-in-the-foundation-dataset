document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-expand-target]").forEach((btn) => {
    const target = document.querySelector(btn.getAttribute("data-expand-target"));
    if (!target) return;
    btn.addEventListener("click", () => {
      const expanded = target.classList.toggle("expanded");
      btn.setAttribute("aria-expanded", String(expanded));
      btn.textContent = expanded ? "Read less" : "Read more";
    });
  });

  document.querySelectorAll("[data-copy-target]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const target = document.querySelector(btn.getAttribute("data-copy-target"));
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent.trim());
        const original = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(() => (btn.textContent = original), 1500);
      } catch (err) {
        console.warn("Clipboard copy failed", err);
      }
    });
  });
});
