# wifi_server.py
import network
import time
import json
import uasyncio as asyncio
from machine import ADC

# =================================================
# CONFIGURACIÓN WiFi
# =================================================
SSID     = "INFINITUMD942"
PASSWORD = "89943675Ap"

# =================================================
# SENSOR DE TEMPERATURA INTERNA (RP2040)
# =================================================
_sensor_temp = ADC(4)

def leer_temp():
    lectura = _sensor_temp.read_u16()
    return round(27 - (lectura * 3.3 / 65535 - 0.706) / 0.001721, 2)

# =================================================
# CONEXIÓN WiFi
# =================================================
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print("WiFi ya conectado. IP:", wlan.ifconfig()[0])
        return wlan

    wlan.connect(SSID, PASSWORD)
    print("Conectando WiFi", end="")
    for _ in range(20):
        if wlan.isconnected():
            break
        print(".", end="")
        time.sleep(0.5)
    print()

    if wlan.isconnected():
        print("IP:", wlan.ifconfig()[0])
    else:
        print("Error: no se pudo conectar al WiFi")
    return wlan

# =================================================
# MANEJADOR HTTP
# =================================================
async def _handle_client(reader, writer):
    import shared_state
    try:
        req = await reader.read(1024)
        req_str = req.decode()

        if "GET /datos" in req_str:
            estado = {
                "ultima_puntuacion": shared_state.last_score,
                "juego_activo":      shared_state.current_game,
                "temperatura_c":     leer_temp(),
                "uptime_s":          time.time() - shared_state.uptime_start,
                "timestamp":         time.time(),
            }
            body = json.dumps(estado)
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Access-Control-Allow-Origin: *\r\n\r\n"
                + body
            )
        else:
            # Página de bienvenida mínima
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n\r\n"
                "Pico Game Console\n"
                "GET /datos  ->  JSON con estado y puntuacion\n"
            )

        writer.write(response.encode())
        await writer.drain()
    except Exception as e:
        print("HTTP error:", e)
    finally:
        await writer.aclose()

# =================================================
# TAREA: SERVIDOR HTTP
# =================================================
async def start_server():
    """Arranca el servidor HTTP en el puerto 80. Llamar como tarea asyncio."""
    server = await asyncio.start_server(_handle_client, "0.0.0.0", 80)
    print("Servidor HTTP escuchando en puerto 80")
    # El servidor corre indefinidamente; esta corrutina nunca retorna.
    while True:
        await asyncio.sleep(10)
