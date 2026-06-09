import network
import socket
import time
import json

# =========================
# CONFIGURACIÓN WIFI
# =========================
SSID = "INFINITUMD942"
PASSWORD = "89943675Ap"

contador = 0


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Conectando al WiFi...")
        wlan.connect(SSID, PASSWORD)

        tiempo_inicio = time.time()

        while not wlan.isconnected():
            if time.time() - tiempo_inicio > 20:
                print("No se pudo conectar al WiFi")
                return None

            print("Esperando conexión...")
            time.sleep(1)

    ip = wlan.ifconfig()[0]
    print("Conectado correctamente")
    print("IP de la Pico 2W:", ip)

    return ip


def crear_json_prueba():
    global contador

    contador += 1

    datos = {
        "dispositivo": "Raspberry Pi Pico 2W",
        "proyecto": "Consola ST7789",
        "juego": "Prueba JSON",
        "jugador": "Esteban",
        "puntaje": contador * 100,
        "estado": "activo",
        "contador_envios": contador,
        "timestamp": time.time()
    }

    return datos


def iniciar_servidor():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    servidor = socket.socket()
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(addr)
    servidor.listen(1)

    print("Servidor HTTP iniciado en puerto 80")
    print("Ruta JSON: /datos")

    while True:
        cliente, direccion = servidor.accept()
        print("Cliente conectado desde:", direccion)

        request = cliente.recv(1024).decode("utf-8")
        print("Petición recibida:")
        print(request)

        if "GET /datos" in request:
            datos = crear_json_prueba()
            cuerpo = json.dumps(datos)

            respuesta = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                "Access-Control-Allow-Headers: Content-Type\r\n"
                "Connection: close\r\n"
                "\r\n"
                + cuerpo
            )

        else:
            cuerpo = "Servidor Pico 2W funcionando. Usa /datos para obtener JSON."

            respuesta = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Connection: close\r\n"
                "\r\n"
                + cuerpo
            )

        cliente.send(respuesta.encode("utf-8"))
        cliente.close()


ip = conectar_wifi()

if ip:
    iniciar_servidor()
else:
    print("No se inició el servidor porque no hubo conexión WiFi.")
