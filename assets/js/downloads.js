document.addEventListener("DOMContentLoaded", async () => {
  const downloadsStat = document.querySelector("#downloads-stat");
  if (!downloadsStat) return;

  try {
    const response = await fetch("assets/data/downloads.json", {
      cache: "no-store",
    });
    if (!response.ok) return;

    const data = await response.json();
    const totalDownloads = Number(data.total_downloads);
    const last30Downloads = Number(data.last_30_days_downloads);
    const updatedAt = new Date(data.updated_at);

    if (
      !Number.isSafeInteger(totalDownloads) ||
      totalDownloads < 0 ||
      !Number.isSafeInteger(last30Downloads) ||
      last30Downloads < 0 ||
      Number.isNaN(updatedAt.getTime())
    ) {
      return;
    }

    downloadsStat.querySelector("[data-stat='total-downloads']").textContent =
      totalDownloads.toLocaleString();
    downloadsStat.querySelector("[data-stat='last30-downloads']").textContent =
      `${last30Downloads.toLocaleString()} in the last 30 days`;
    downloadsStat.querySelector("[data-stat='downloads-updated']").textContent =
      `Updated ${updatedAt.toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      })}`;
    downloadsStat.hidden = false;
  } catch {
    // Keep the optional counter hidden when its generated data is unavailable.
  }
});
