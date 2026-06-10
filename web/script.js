// Cambia esta IP por la IP real de tu Raspberry Pi Pico 2W
const IP_PICO = "192.168.1.94";
const URL_JSON = `http://${IP_PICO}/datos`;

// Elementos del HTML
const estadoConexion = document.getElementById("estadoConexion");
const btnActualizar = document.getElementById("btnActualizar");

async function obtenerJsonDePico() {
    try {
        const respuesta = await fetch(URL_JSON);

        if (!respuesta.ok) throw new Error("Error HTTP: " + respuesta.status);

        const datos = await respuesta.json();
        console.log("JSON recibido desde Pico 2W:", datos);

        // Sistema
        const fecha = new Date(datos.timestamp * 1000);
        document.getElementById("sistemaSalida").textContent =
            `Temperatura: ${datos.temperatura_c} °C\n` +
            `Uptime: ${datos.uptime_s} s\n` +
            `Timestamp: ${fecha.toLocaleString()}`;

        // Juegos
        document.getElementById("snakeScore").textContent =
            datos.ultimo_juego === "snake" ? datos.ultima_puntuacion : 0;
        document.getElementById("blocksScore").textContent =
            datos.ultimo_juego === "blocks" ? datos.ultima_puntuacion : 0;

        // Mostrar solo la pestaña del último juego
        const tabs = bootstrap.Tab.getOrCreateInstance;
        if (datos.ultimo_juego === "snake") {
            bootstrap.Tab.getOrCreateInstance(
                document.getElementById("snake-tab"),
            ).show();
        } else if (datos.ultimo_juego === "blocks") {
            bootstrap.Tab.getOrCreateInstance(
                document.getElementById("blocks-tab"),
            ).show();
        } else {
            bootstrap.Tab.getOrCreateInstance(
                document.getElementById("sistema-tab"),
            ).show();
        }

        estadoConexion.textContent = "Conectado a Pico 2W";
        estadoConexion.className = "badge bg-success";
    } catch (error) {
        console.error("No se pudo obtener el JSON de la Pico 2W:", error);
        document.getElementById("sistemaSalida").textContent =
            "Error conectando con la Pico 2W.\nRevisa la IP, Wi-Fi y que el código esté corriendo.";
        estadoConexion.textContent = "Sin conexión";
        estadoConexion.className = "badge bg-danger";
    }
}

// Botón para actualizar manualmente
btnActualizar.addEventListener("click", obtenerJsonDePico);

// Primera lectura inmediata
obtenerJsonDePico();

// Consulta automática cada 5 segundos
setInterval(obtenerJsonDePico, 5000);
