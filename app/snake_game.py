# snake_game.py
import random
import time
import hardware
from hardware import tft, update_brightness, wait_any_button
from hardware import read_direction, GREEN, DARK_GREEN, RED, WHITE, BLUE
from hardware import gameover_sound, eat_sound, turn_sound, start_sound

CELL = 10
HUD_H = 20
W = 240
H = 240
PLAY_X0 = 0
PLAY_Y0 = HUD_H
PLAY_W = W
PLAY_H = H - HUD_H
GRID_W = PLAY_W // CELL
GRID_H = PLAY_H // CELL

def draw_hud(score):
    tft.fill_rect(0, 0, W, HUD_H, 0)  # negro
    tft.fill_rect(0, 0, W, 3, BLUE)
    max_blocks = W // 8
    blocks = min(score, max_blocks)
    for i in range(blocks):
        tft.fill_rect(i*8, 7, 6, 8, 0xFFE0)  # amarillo

def draw_snake_start_screen():
    tft.fill(0)
    tft.rect(20, 20, 200, 200, BLUE)
    tft.fill_rect(70, 90, 20, 20, GREEN)
    tft.fill_rect(90, 90, 20, 20, DARK_GREEN)
    tft.fill_rect(110, 90, 20, 20, DARK_GREEN)
    tft.fill_rect(130, 90, 20, 20, DARK_GREEN)
    tft.fill_rect(160, 90, 20, 20, RED)
    tft.fill_rect(95, 145, 50, 12, WHITE)
    tft.fill_rect(80, 165, 80, 12, 0xFFE0)
    print("PICO SNAKE")
    print("Presiona cualquier boton para iniciar")

def draw_cell(cell, color):
    x = PLAY_X0 + cell[0]*CELL
    y = PLAY_Y0 + cell[1]*CELL
    tft.fill_rect(x, y, CELL, CELL, color)

def spawn_food(snake_set):
    while True:
        food = (random.randrange(GRID_W), random.randrange(GRID_H))
        if food not in snake_set:
            return food

def draw_gameover_screen():
    tft.fill(0)
    tft.rect(30, 40, 180, 160, RED)
    tft.fill_rect(60, 80, 120, 40, RED)
    tft.fill_rect(85, 145, 15, 15, WHITE)
    tft.fill_rect(140, 145, 15, 15, WHITE)
    tft.fill_rect(95, 175, 50, 8, WHITE)
    print("GAME OVER")
    print("Presiona cualquier boton para volver al menu")

# =========================
# FUNCION PRINCIPAL
# =========================
def run():
    draw_snake_start_screen()
    wait_any_button()
    start_sound()

    score = 0
    hardware.speed_ms = 140

    head = (GRID_W//2, GRID_H//2)
    snake = [head, (head[0]-1, head[1]), (head[0]-2, head[1])]
    snake_set = set(snake)

    dx, dy = 1, 0
    pending_dx, pending_dy = dx, dy

    food = spawn_food(snake_set)

    tft.fill(0)
    draw_hud(score)
    tft.rect(0, HUD_H, W, H-HUD_H, WHITE)

    for i, segment in enumerate(snake):
        draw_cell(segment, GREEN if i == 0 else DARK_GREEN)
    draw_cell(food, RED)

    last_step = time.ticks_ms()

    while True:
        update_brightness()

        # Verificar botón menú via flag de hardware
        if hardware.menu_pressed_flag:
            hardware.menu_pressed_flag = False
            return

        ndx, ndy = read_direction()
        if ndx != 0 or ndy != 0:
            if not (ndx == -dx and ndy == -dy):
                if (ndx, ndy) != (pending_dx, pending_dy):
                    turn_sound()
                pending_dx, pending_dy = ndx, ndy

        now = time.ticks_ms()
        if time.ticks_diff(now, last_step) < hardware.speed_ms:
            time.sleep_ms(5)
            continue
        last_step = now

        dx, dy = pending_dx, pending_dy
        hx, hy = snake[0]
        new_head = (hx+dx, hy+dy)

        if new_head[0] < 0 or new_head[0] >= GRID_W or new_head[1] < 0 or new_head[1] >= GRID_H:
            gameover_sound()
            draw_gameover_screen()
            wait_any_button()
            return

        tail = snake[-1]
        eating = new_head == food

        if new_head in snake_set and not (new_head == tail and not eating):
            gameover_sound()
            draw_gameover_screen()
            wait_any_button()
            return

        snake.insert(0, new_head)
        snake_set.add(new_head)
        draw_cell(new_head, GREEN)
        if len(snake) > 1:
            draw_cell(snake[1], DARK_GREEN)

        if eating:
            eat_sound()
            score += 1
            if score % 3 == 0 and hardware.speed_ms > 60:
                hardware.speed_ms -= 10
            draw_hud(score)
            food = spawn_food(snake_set)
            draw_cell(food, RED)
        else:
            removed_tail = snake.pop()
            snake_set.remove(removed_tail)
            draw_cell(removed_tail, 0)  # negro
