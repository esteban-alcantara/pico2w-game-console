import _thread
import uasyncio as asyncio
import time
import shared_state
import wifi_server
from hardware import update_brightness, clear_screen
import menu
import snake_game
# import dodge_game  

# NÚCLEO 1: servidor WiFi (corre en segundo núcleo)
def wifi_core():
    """Corre el event loop de asyncio con el servidor HTTP en el núcleo 1."""
    async def _server():
        server = await asyncio.start_server(wifi_server._handle_client, "0.0.0.0", 80)
        print("Servidor HTTP listo en puerto 80")
        while True:
            await asyncio.sleep(1)
    asyncio.run(_server())

# NÚCLEO 0: juego (loop principal)
def main():
    shared_state.uptime_start = time.time()

    wifi_server.conectar_wifi()

    _thread.start_new_thread(wifi_core, ())
    time.sleep(1)  # Se le da tiempo al servidor para iniciar

    # Loop del juego en el núcleo principal
    while True:
        update_brightness()
        selected = menu.main_menu()

        if selected == 0:
            snake_game.run()
        # elif selected == 1:
        #     dodge_game.run()

        clear_screen()
        time.sleep_ms(500)

main()
