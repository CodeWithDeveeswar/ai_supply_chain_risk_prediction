function exportToExcel() {
    window.location.href = "/export_excel";
}

function exportDashboardImage() {

    const dashboard = document.querySelector(".dashboard");
    if (!dashboard) return;

    // force dark background
    dashboard.style.background = "#0f172a";

    html2canvas(dashboard, {
        scale: 2,
        useCORS: true,
        backgroundColor: "#0f172a"
    }).then(canvas => {

        // 🔥 UNIQUE FILE NAME
        const now = new Date();
        const timestamp = now.toISOString().replace(/[:.]/g, "-");
        const filename = `dashboard_report_${timestamp}.png`;

        const imageData = canvas.toDataURL("image/png");

        // =========================
        // 1. DOWNLOAD (BROWSER)
        // =========================
        const link = document.createElement("a");
        link.download = filename;
        link.href = imageData;
        link.click();

        // =========================
        // 2. SAVE TO DOWNLOADS (BACKEND)
        // =========================
        fetch("/save-dashboard-image", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                image: imageData,
                filename: filename
            })
        })
        .then(res => res.json())
        .then(data => {
            console.log("Saved to Downloads:", data);
        })
        .catch(err => {
            console.error("Save failed:", err);
        });

    }).catch(err => {
        console.error("Image export failed:", err);
    });
}