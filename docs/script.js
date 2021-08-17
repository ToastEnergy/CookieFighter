var currentMode = "light"

if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    mode();
}

function mode() {
    if (currentMode === "light") {
        document.getElementById("css").href = "css/dark.css";
        document.getElementById("logo").src = "https://cdn.toastenergy.xyz/CookieFighter/logo3.gif"
        document.getElementById("mode").innerText = "Light Mode"
        currentMode = "dark";
    } else if (currentMode === "dark") {
        document.getElementById("logo").src = "https://cdn.toastenergy.xyz/CookieFighter/logo2.png"
        document.getElementById("css").href = "css/light.css";
        document.getElementById("mode").innerText = "Dark Mode"
        currentMode = "light";
    }
}
