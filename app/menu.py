from hardware import tft, update_brightness, pressed, wait_any_button
from hardware import menu_sound, select_sound
import time

MENU_GAMES = ["SNAKE", "DODGE GAME"]

def draw_main_menu(selected):
    tft.fill(0)  # Limpia pantalla
    tft.rect(10, 10, 220, 220, 0x001F)  # Marco azul

    # Opciones
    for i, game in enumerate(MENU_GAMES):
        y = 130 + i*35
        if i == selected:
            tft.fill_rect(40, y-5, 160, 25, 0x001F)
        # Opcional: dibujar bloques decorativos según juego

def main_menu():
    selected = 0
    draw_main_menu(selected)
    last_move = time.ticks_ms()

    while True:
        update_brightness()
        now = time.ticks_ms()
        if time.ticks_diff(now, last_move) > 220:
            if pressed(btn_up):
                selected = (selected -1) % len(MENU_GAMES)
                menu_sound()
                draw_main_menu(selected)
                last_move = now
            elif pressed(btn_down):
                selected = (selected +1) % len(MENU_GAMES)
                menu_sound()
                draw_main_menu(selected)
                last_move = now

        if pressed(btn_right):
            select_sound()
            return selected

        time.sleep_ms(20)