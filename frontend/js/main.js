/**
 * TRUVEX Main Client Script
 * Owner: Arunav / Anany
 * Status: Phase 1 Skeleton
 */

document.addEventListener("DOMContentLoaded", async () => {
  console.log("TRUVEX Trust Infrastructure initialized.");

  // Check backend health dynamically
  const healthBadge = document.getElementById("health-indicator");
  if (healthBadge) {
    try {
      const resp = await fetch("/api/health");
      if (resp.ok) {
        const data = await resp.json();
        healthBadge.textContent = `Backend Online (${data.app} v${data.version})`;
        healthBadge.style.color = "var(--accent-emerald)";
      } else {
        healthBadge.textContent = "Backend Offline";
        healthBadge.style.color = "var(--accent-rose)";
      }
    } catch (e) {
      healthBadge.textContent = "Connecting...";
      healthBadge.style.color = "var(--text-muted)";
    }
  }

  // Format Trust ID input (e.g., TRX-XXXX-XXXX)
  const trustInput = document.getElementById("trust-id-input");
  if (trustInput) {
    trustInput.addEventListener("input", (e) => {
      let val = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
      if (val.length > 3 && !val.startsWith("TRX")) {
        val = "TRX" + val;
      }
      e.target.value = val;
    });
  }
});
