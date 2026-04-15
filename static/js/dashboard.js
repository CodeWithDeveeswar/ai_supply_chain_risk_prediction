// ================= ALERT TABLE =================
function loadAlerts() {
    const table = document.getElementById("alertTable");
    if (!table) return;

    table.innerHTML = "";

    if (!window.alerts || window.alerts.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center; padding:15px;">
                    No high risk data
                </td>
            </tr>
        `;
        return;
    }

    window.alerts.forEach(row => {
        const tr = document.createElement("tr");

        const supplier = row[0];
        const region = row[1];
        const delay = row[2];
        const weather = row[3];
        const risk = row[4];

        tr.innerHTML = `
            <td>${supplier}</td>
            <td>${getRegion(region)}</td>
            <td>${delay}</td>
            <td>${getWeather(weather)}</td>
            <td>
                <span class="risk-badge risk-${risk.toLowerCase()}">
                    ${risk}
                </span>
            </td>
        `;

        table.appendChild(tr);
    });
}


// ================= HELPERS =================
function getRegion(r) {
    return ["Asia", "Europe", "North America", "South America", "Africa"][r] || "Unknown";
}

function getWeather(w) {
    return ["Clear", "Rain", "Storm", "Fog", "Snow"][w] || "Unknown";
}


// ================= AUTO REFRESH =================
function refreshDashboard() {
    fetch("/dashboard-data")   // 🔥 NEW API ROUTE REQUIRED
        .then(res => res.json())
        .then(data => {

            // ===== UPDATE KPIs =====
            document.getElementById("totalPredictions").innerText = data.total_predictions;
            document.getElementById("totalSuppliers").innerText = data.total_suppliers;
            document.getElementById("highRisk").innerText = data.high_risk;
            document.getElementById("mediumRisk").innerText = data.medium_risk;
            document.getElementById("lowRisk").innerText = data.low_risk;
            document.getElementById("avgDelay").innerText = data.avg_delay + " days";
            document.getElementById("totalValue").innerText = "$" + data.total_value;
            document.getElementById("avgFuel").innerText = "$" + data.avg_fuel;

            // ===== UPDATE ALERTS =====
            window.alerts = data.alerts;
            loadAlerts();

            // ⚠️ IMPORTANT:
            // If you want charts auto-update → destroy & recreate charts
            // (optional - only if needed)

        })
        .catch(err => console.error("Dashboard refresh error:", err));
}


// ================= INIT =================
document.addEventListener("DOMContentLoaded", () => {
    loadAlerts();

    // 🔥 AUTO REFRESH EVERY 10 SECONDS
    setInterval(refreshDashboard, 10000);
});