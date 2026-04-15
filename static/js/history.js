// SELECT ALL
document.getElementById("selectAll").addEventListener("change", function () {
    document.querySelectorAll(".rowCheckbox").forEach(cb => {
        cb.checked = this.checked;
    });
});

// DELETE SINGLE
function deleteSingle(id) {
    if (!confirm("Delete this record?")) return;

    fetch("/delete/" + id, { method: "POST" })
        .then(() => location.reload());
}

// DELETE ALL
function deleteAll() {
    if (!confirm("Delete ALL records?")) return;

    fetch("/delete_all", { method: "POST" })
        .then(() => location.reload());
}

function applyFilters() {
    const search = document.getElementById("searchInput").value.toLowerCase();
    const filter = document.getElementById("filterRisk").value.toLowerCase();

    const rows = document.querySelectorAll("#historyTable tbody tr");

    let visibleCount = 0;

    rows.forEach(row => {
        const riskCell = row.querySelector(".risk-badge");

        // 🔥 skip empty "no data" row
        if (!riskCell) {
            row.style.display = "none";
            return;
        }

        const text = row.innerText.toLowerCase();
        const risk = riskCell.innerText.trim().toLowerCase();

        const matchesSearch = text.includes(search);
        const matchesFilter = filter === "" || risk === filter;

        if (matchesSearch && matchesFilter) {
            row.style.display = "";
            visibleCount++;
        } else {
            row.style.display = "none";
        }
    });

    // 🔥 HANDLE EMPTY RESULT (VERY IMPORTANT)
    const tbody = document.querySelector("#historyTable tbody");

    let emptyRow = document.getElementById("noDataRow");

    if (visibleCount === 0) {
        if (!emptyRow) {
            emptyRow = document.createElement("tr");
            emptyRow.id = "noDataRow";
            emptyRow.innerHTML = `
                <td colspan="11" style="text-align:center; padding:20px;">
                    No matching records found
                </td>
            `;
            tbody.appendChild(emptyRow);
        }
    } else {
        if (emptyRow) emptyRow.remove();
    }
}