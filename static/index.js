document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/robots")
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("robot-table-body");
            data.forEach(robot => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${robot.id}</td>
                    <td>${robot.name}</td>
                    <td>${robot.model}</td>
                `;

                tbody.appendChild(row);
            });
        })
        .catch(err => {
            console.error("Failed to fetch robots:", err);
        });
});
