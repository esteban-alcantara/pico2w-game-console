import uasyncio as asyncio
import json
from machine import Pin, ADC
import network
import time

# ── Configuración WiFi ──────────────────────────────────────────
SSID = "INFINITUMD942"
PASSWORD = "89943675Ap"

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
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
        print("Error: no se pudo conectar")

# ── Pines y estado ──────────────────────────────────────────────
PIN_UP = 18
PIN_DOWN = 19
btn_up = Pin(PIN_UP, Pin.IN, Pin.PULL_UP)
btn_down = Pin(PIN_DOWN, Pin.IN, Pin.PULL_UP)
conteos = {"UP": 0, "DOWN": 0}
last_up, last_down = 1, 1
sensor_temp = ADC(4)

def leer_temp():
    lectura = sensor_temp.read_u16()
    return round(27 - (lectura * 3.3 / 65535 - 0.706) / 0.001721, 2)

# ── Tareas async ────────────────────────────────────────────────
async def leer_botones():
    global last_up, last_down
    while True:
        up_val = btn_up.value()
        down_val = btn_down.value()
        if up_val == 0 and last_up == 1:
            conteos["UP"] += 1
            print("UP presionado →", conteos["UP"])
        if down_val == 0 and last_down == 1:
            conteos["DOWN"] += 1
            print("DOWN presionado →", conteos["DOWN"])
        last_up, last_down = up_val, down_val
        await asyncio.sleep_ms(20)

async def handle_client(reader, writer):
    try:
        req = await reader.read(1024)
        req = req.decode()
        if "GET /datos" in req:
            estado = {
                "conteos": conteos.copy(),
                "temperatura": leer_temp(),
                "timestamp": time.time()
            }
            cuerpo = json.dumps(estado)
            respuesta = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Access-Control-Allow-Origin: *\r\n\r\n" + cuerpo
            )
        else:
            respuesta = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nServidor Pico funcionando"
        writer.write(respuesta.encode())
        await writer.drain()
    finally:
        await writer.aclose()

async def main():
    conectar_wifi()
    asyncio.create_task(leer_botones())


    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Servidor HTTP escuchando en puerto 80")

    while True:
        await asyncio.sleep(1)

asyncio.run(main())
