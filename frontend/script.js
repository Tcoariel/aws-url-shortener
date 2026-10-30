
const API_URL = "http://localhost:8000";

const form = document.getElementById("urlForm");
const result = document.getElementById("result");
const shortUrl = document.getElementById("shortUrl");
const message = document.getElementById("message");
const copyButton = document.getElementById("copyButton");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const originalUrl = document.getElementById("originalUrl").value;

    message.textContent = "";
    result.hidden = true;

    try {
        const response = await fetch(`${API_URL}/shorten`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                original_url: originalUrl
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Error al acortar el enlace");
        }

        shortUrl.href = data.short_url;
        shortUrl.textContent = data.short_url;

        result.hidden = false;

    } catch (error) {
        message.textContent = error.message;
    }
});

copyButton.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(shortUrl.href);
        message.textContent = "¡Enlace copiado!";
    } catch {
        message.textContent = "No se pudo copiar el enlace";
    }
});
