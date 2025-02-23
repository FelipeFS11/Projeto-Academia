document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            alert.classList.add("hide");
            setTimeout(() => alert.remove(), 500); // Remove do DOM após a transição
        });
    }, 3000); // Esconde após 3 segundos
});