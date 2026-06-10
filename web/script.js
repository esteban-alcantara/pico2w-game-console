// Cambia esta IP por la IP real de tu Raspberry Pi Pico 2W
const IP_PICO = "192.168.1.94";
const URL_JSON = `http://${IP_PICO}/datos`;

// Elementos del HTML
const jsonSalida = document.getElementById("jsonSalida");
const estadoConexion = document.getElementById("estadoConexion");
const btnActualizar = document.getElementById("btnActualizar");

async function obtenerJsonDePico() {
    try {
        const respuesta = await fetch(URL_JSON);

        if (!respuesta.ok) {
            throw new Error("Error HTTP: " + respuesta.status);
        }

        const datos = await respuesta.json();

        // Imprime el JSON en la consola del navegador
        console.log("JSON recibido desde Pico 2W:");
        console.log(datos);

        // Muestra el JSON en la página
        jsonSalida.textContent = JSON.stringify(datos, null, 4);

        estadoConexion.textContent = "Conectado a Pico 2W";
        estadoConexion.className = "badge bg-success";
    } catch (error) {
        console.error("No se pudo obtener el JSON de la Pico 2W:");
        console.error(error);

        jsonSalida.textContent =
            "Error conectando con la Pico 2W.\n\nRevisa:\n- IP de la Pico\n- Wi-Fi\n- Código corriendo en Thonny\n- Que estén en la misma red";

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
