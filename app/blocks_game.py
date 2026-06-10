# blocks_game.py
import time
import random
from hardware import tft, update_brightness, wait_any_button
from hardware import pressed, btn_left, btn_right
from hardware import gameover_sound, eat_sound, tone, start_sound, menu_pressed_flag

# Pantalla
W = 240
H = 240

# Jugador
PLAYER_W = 36
PLAYER_H = 12

# Obstáculo
OBSTACLE_SIZE = 14

# Colores
GREEN = 0x07E0
RED = 0xF800
BLACK = 0x0000
YELLOW = 0xFFE0
PURPLE = 0xF81F

# Puntaje y vidas
def draw_hud(score, lives):
    tft.fill_rect(0, 0, W, 20, BLACK)
    tft.fill_rect(0, 0, W, 3, PURPLE)
    # Score con bloques amarillos
    for i in range(score):
        if i < 15:
            tft.fill_rect(5 + i*8, 8, 6, 8, YELLOW)
    # Vidas con bloques rojos
    for i in range(lives):
        tft.fill_rect(200 + i*12, 8, 8, 8, RED)

# Pantalla de inicio
def draw_start_screen():
    tft.fill(BLACK)
    tft.rect(20, 20, 200, 200, PURPLE)
    # jugador
    tft.fill_rect(W//2 - PLAYER_W//2, H-25, PLAYER_W, PLAYER_H, GREEN)
    # obstáculos de ejemplo
    tft.fill_rect(70, 70, OBSTACLE_SIZE, OBSTACLE_SIZE, RED)
    tft.fill_rect(150, 100, OBSTACLE_SIZE, OBSTACLE_SIZE, RED)
    tft.fill_rect(115, 50, OBSTACLE_SIZE, OBSTACLE_SIZE, RED)
    # texto con bloques 
    print("BLOCKS")
    print("LEFT/RIGHT: mover")
    print("Evita los bloques rojos")
    print("Presiona cualquier boton para iniciar")

# Pantalla de game over
def draw_gameover(score):
    tft.fill(BLACK)
    tft.rect(30, 40, 180, 160, RED)
    tft.fill_rect(70, 80, 100, 30, RED)
    tft.fill_rect(60, 140, 120, 12, YELLOW)
    print("BLOCKS GAME OVER")
    print("Score:", score)
    print("Presiona cualquier boton para volver al menu")

# ==========================
# FUNCION PRINCIPAL
# ==========================
def run():
    draw_start_screen()
    wait_any_button()
    start_sound()

    # jugador inicial
    player_x = W//2 - PLAYER_W//2
    player_y = H - 25
    old_player_x = player_x

    # obstáculo inicial
    obstacle_x = random.randrange(0, W - OBSTACLE_SIZE)
    obstacle_y = 25
    old_obstacle_x = obstacle_x
    old_obstacle_y = obstacle_y

    score = 0
    lives = 3
    fall_speed = 4

    draw_hud(score, lives)
    tft.fill_rect(player_x, player_y, PLAYER_W, PLAYER_H, GREEN)
    tft.fill_rect(obstacle_x, obstacle_y, OBSTACLE_SIZE, OBSTACLE_SIZE, RED)

    while True:
        update_brightness()

        # salir al menu si se presiona el botón de interrupción
        if menu_pressed_flag:
            from hardware import menu_pressed_flag
            menu_pressed_flag = False
            return

        # mover jugador
        if pressed(btn_left):
            player_x -= 6
        if pressed(btn_right):
            player_x += 6
        player_x = max(0, min(W-PLAYER_W, player_x))

        # mover obstáculo
        obstacle_y += fall_speed

        # borrar posiciones anteriores
        tft.fill_rect(old_player_x, player_y, PLAYER_W, PLAYER_H, BLACK)
        tft.fill_rect(old_obstacle_x, old_obstacle_y, OBSTACLE_SIZE, OBSTACLE_SIZE, BLACK)

        # detectar colisión
        collision = (
            obstacle_x < player_x + PLAYER_W and
            obstacle_x + OBSTACLE_SIZE > player_x and
            obstacle_y < player_y + PLAYER_H and
            obstacle_y + OBSTACLE_SIZE > player_y
        )

        if collision:
            tone(300, 120)
            lives -= 1
            # reset obstáculo
            obstacle_x = random.randrange(0, W - OBSTACLE_SIZE)
            obstacle_y = 25
            draw_hud(score, lives)
            if lives <= 0:
                gameover_sound()
                draw_gameover(score)
                wait_any_button()
                return

        # si obstáculo llega abajo sin tocar al jugador
        if obstacle_y > H:
            score += 1
            if score % 5 == 0:
                fall_speed += 1
            obstacle_x = random.randrange(0, W - OBSTACLE_SIZE)
            obstacle_y = 25
            eat_sound()
            draw_hud(score, lives)

        # dibujar nuevas posiciones
        tft.fill_rect(player_x, player_y, PLAYER_W, PLAYER_H, GREEN)
        tft.fill_rect(obstacle_x, obstacle_y, OBSTACLE_SIZE, OBSTACLE_SIZE, RED)

        old_player_x = player_x
        old_obstacle_x = obstacle_x
        old_obstacle_y = obstacle_y

        time.sleep_ms(35)
