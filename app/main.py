from hardware import update_brightness, clear_screen
import time
import menu
import snake_game
# import dodge_game  # descomentar cuando esté listo

while True:
    update_brightness()
    selected = menu.main_menu()

    if selected == 0:
        snake_game.run()
    # elif selected == 1:
    #     dodge_game.run()

    # Pausa antes de regresar al menú
    clear_screen()
    time.sleep_ms(500)
