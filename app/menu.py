from hardware import tft, update_brightness, pressed, wait_any_button
from hardware import btn_up, btn_down
from hardware import menu_sound, select_sound
from hardware import btn_right
import time

MENU_GAMES = ["SNAKE", "DODGE GAME"]

# Tamaño del "pixel" de la letra
BLOCK = 6
GAP = 1  # espacio entre rectángulos
LETTER_SPACING = 4

LETTER_COLOR = 0xFFFF  # blanco

def draw_M(x, y):
    # Dos líneas verticales
    tft.fill_rect(x, y, BLOCK, BLOCK*5, LETTER_COLOR)
    tft.fill_rect(x+BLOCK*4, y, BLOCK, BLOCK*5, LETTER_COLOR)
    # Diagonal central
    tft.fill_rect(x+BLOCK, y, BLOCK, BLOCK, LETTER_COLOR)
    tft.fill_rect(x+BLOCK*2, y+BLOCK, BLOCK, BLOCK, LETTER_COLOR)
    tft.fill_rect(x+BLOCK*3, y, BLOCK, BLOCK, LETTER_COLOR)

def draw_E(x, y):
    # Vertical
    tft.fill_rect(x, y, BLOCK, BLOCK*5, LETTER_COLOR)
    # Horizontales
    tft.fill_rect(x+BLOCK, y, BLOCK*3, BLOCK, LETTER_COLOR)       # top
    tft.fill_rect(x+BLOCK, y+2*BLOCK, BLOCK*2, BLOCK, LETTER_COLOR) # middle
    tft.fill_rect(x+BLOCK, y+4*BLOCK, BLOCK*3, BLOCK, LETTER_COLOR) # bottom

def draw_N(x, y):
    # Dos verticales
    tft.fill_rect(x, y, BLOCK, BLOCK*5, LETTER_COLOR)
    tft.fill_rect(x+BLOCK*4, y, BLOCK, BLOCK*5, LETTER_COLOR)
    # Diagonal
    tft.fill_rect(x+BLOCK, y+BLOCK, BLOCK, BLOCK, LETTER_COLOR)
    tft.fill_rect(x+BLOCK*2, y+2*BLOCK, BLOCK, BLOCK, LETTER_COLOR)
    tft.fill_rect(x+BLOCK*3, y+3*BLOCK, BLOCK, BLOCK, LETTER_COLOR)

def draw_U(x, y):
    # Dos verticales
    tft.fill_rect(x, y, BLOCK, BLOCK*4, LETTER_COLOR)
    tft.fill_rect(x+BLOCK*4, y, BLOCK, BLOCK*4, LETTER_COLOR)
    # Base
    tft.fill_rect(x+BLOCK, y+4*BLOCK, BLOCK*3, BLOCK, LETTER_COLOR)

def draw_menu_text():
    TITLE_X = 40
    TITLE_Y = 50
    BLOCK = 6
    LETTER_SPACING = 4

    # Coordenadas base
    x = TITLE_X + 10
    y = TITLE_Y + 5

    draw_M(x, y)
    x += BLOCK*5 + LETTER_SPACING
    draw_E(x, y)
    x += BLOCK*5 + LETTER_SPACING
    draw_N(x, y)
    x += BLOCK*5 + LETTER_SPACING
    draw_U(x, y)



def draw_menu_title():
    # Rectángulo base para el título
    TITLE_X = 40
    TITLE_Y = 50
    TITLE_W = 160
    TITLE_H = 30
    TITLE_COLOR = 0x07FF  # cian brillante

    tft.fill_rect(TITLE_X, TITLE_Y, TITLE_W, TITLE_H, TITLE_COLOR)

def draw_main_menu(selected):
    tft.fill(0)  # Limpia pantalla
    tft.rect(10, 10, 220, 220, 0x001F)  # Marco azul
    
    draw_menu_title()
    draw_menu_text()   # letras blancas "MENU"

    # Opciones
    for i, game in enumerate(MENU_GAMES):
        y = 130 + i*35
        if i == selected:
            tft.fill_rect(40, y-5, 160, 25, 0x001F)

def main_menu():
    selected = 0
    draw_main_menu(selected)
    last_move = time.ticks_ms()

    while True:
        update_brightness()
        now = time.ticks_ms()
        if time.ticks_diff(now, last_move) > 220:
            if pressed(btn_up):
                selected = (selected - 1) % len(MENU_GAMES)
                menu_sound()
                draw_main_menu(selected)
                last_move = now
            elif pressed(btn_down):
                selected = (selected + 1) % len(MENU_GAMES)
                menu_sound()
                draw_main_menu(selected)
                last_move = now

        if pressed(btn_right):
            select_sound()
            return selected

        time.sleep_ms(20)
