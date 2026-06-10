from machine import Pin, SPI, PWM, ADC
import time
import random
import st7789py as st7789

# PINES DEL DISPLAY ST7789

PIN_SCK = 2
PIN_MOSI = 3
PIN_RESET = 7
PIN_DC = 6
PIN_BLK = 8

# PIN DEL POTENCIÓMETRO PARA BRILLO

PIN_POT = 26

# PINES DE BOTONES

PIN_UP = 18
PIN_DOWN = 19
PIN_LEFT = 20
PIN_RIGHT = 21

# PIN DEL BUZZER

PIN_BUZZER = 14

# BOTONES CON PULL-UP INTERNO

btn_up = Pin(PIN_UP, Pin.IN, Pin.PULL_UP)
btn_down = Pin(PIN_DOWN, Pin.IN, Pin.PULL_UP)
btn_left = Pin(PIN_LEFT, Pin.IN, Pin.PULL_UP)
btn_right = Pin(PIN_RIGHT, Pin.IN, Pin.PULL_UP)

# BUZZER PASIVO

buzzer = PWM(Pin(PIN_BUZZER))
buzzer.duty_u16(0)

def tone(freq, duration_ms, volume=12000):
    buzzer.freq(freq)
    buzzer.duty_u16(volume)
    time.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

def start_sound():
    tone(1000, 70)
    time.sleep_ms(40)
    tone(1500, 90)

def turn_sound():
    tone(900, 20, 9000)

def eat_sound():
    tone(1300, 50)
    time.sleep_ms(30)
    tone(1800, 70)

def gameover_sound():
    tone(600, 150)
    time.sleep_ms(40)
    tone(400, 180)
    time.sleep_ms(40)
    tone(250, 250)

# DISPLAY

# Primero se crea como Pin normal para que el driver pueda inicializarlo
backlight_pin = Pin(PIN_BLK, Pin.OUT)
backlight_pin.value(1)

spi = SPI(
    0,
    baudrate=40_000_000,
    polarity=1,
    phase=1,
    sck=Pin(PIN_SCK),
    mosi=Pin(PIN_MOSI)
)

tft = st7789.ST7789(
    spi,
    240,
    240,
    reset=Pin(PIN_RESET, Pin.OUT),
    dc=Pin(PIN_DC, Pin.OUT),
    cs=None,
    backlight=backlight_pin,
    rotation=1
)

# Ahora el mismo pin BLK se usa con PWM
backlight_pwm = PWM(backlight_pin)
backlight_pwm.freq(1000)

# ADC del potenciómetro
pot = ADC(Pin(PIN_POT))

# Brillo mínimo y máximo
BRIGHTNESS_MIN = 3000
BRIGHTNESS_MAX = 65535

def update_brightness():
    raw = pot.read_u16()

    duty = BRIGHTNESS_MIN + int(
        raw * (BRIGHTNESS_MAX - BRIGHTNESS_MIN) / 65535
    )

    backlight_pwm.duty_u16(duty)

W = 240
H = 240

# COLORES

BLACK = st7789.BLACK
WHITE = st7789.WHITE
RED = st7789.RED
GREEN = st7789.GREEN
BLUE = st7789.BLUE
YELLOW = st7789.YELLOW

DARK_GREEN = st7789.color565(0, 140, 0)
GRAY = st7789.color565(60, 60, 60)

# CONFIGURACIÓN DEL JUEGO

CELL = 10
HUD_H = 20

PLAY_X0 = 0
PLAY_Y0 = HUD_H
PLAY_W = W
PLAY_H = H - HUD_H

GRID_W = PLAY_W // CELL
GRID_H = PLAY_H // CELL

speed_ms = 140

# FUNCIONES DE BOTONES

def pressed(button):
    return button.value() == 0

def any_button_pressed():
    return (
        pressed(btn_up) or
        pressed(btn_down) or
        pressed(btn_left) or
        pressed(btn_right)
    )

def wait_any_button():
    while not any_button_pressed():
        update_brightness()
        time.sleep_ms(10)

    time.sleep_ms(180)

    while any_button_pressed():
        update_brightness()
        time.sleep_ms(10)

    time.sleep_ms(180)

def read_direction():
    if pressed(btn_up):
        return 0, -1

    if pressed(btn_down):
        return 0, 1

    if pressed(btn_left):
        return -1, 0

    if pressed(btn_right):
        return 1, 0

    return 0, 0

# =================================================
# FUNCIONES DE DIBUJO
# =================================================

def clear_screen(color=BLACK):
    tft.fill(color)

def draw_cell(cell, color):
    x = PLAY_X0 + cell[0] * CELL
    y = PLAY_Y0 + cell[1] * CELL
    tft.fill_rect(x, y, CELL, CELL, color)

def draw_hud(score):
    tft.fill_rect(0, 0, W, HUD_H, BLACK)
    tft.fill_rect(0, 0, W, 3, BLUE)

    max_blocks = W // 8

    blocks = score
    if blocks > max_blocks:
        blocks = max_blocks

    for i in range(blocks):
        x = i * 8
        tft.fill_rect(x, 7, 6, 8, YELLOW)

def draw_start_screen():
    clear_screen(BLACK)

    tft.rect(20, 20, 200, 200, BLUE)

    tft.fill_rect(70, 90, 20, 20, GREEN)
    tft.fill_rect(90, 90, 20, 20, DARK_GREEN)
    tft.fill_rect(110, 90, 20, 20, DARK_GREEN)
    tft.fill_rect(130, 90, 20, 20, DARK_GREEN)

    tft.fill_rect(160, 90, 20, 20, RED)

    tft.fill_rect(95, 145, 50, 12, WHITE)
    tft.fill_rect(80, 165, 80, 12, YELLOW)

    print("PICO SNAKE")
    print("Mueve el potenciometro para cambiar el brillo")
    print("Presiona cualquier boton para iniciar")

def draw_gameover_screen():
    clear_screen(BLACK)

    tft.rect(30, 40, 180, 160, RED)
    tft.fill_rect(60, 80, 120, 40, RED)

    tft.fill_rect(85, 145, 15, 15, WHITE)
    tft.fill_rect(140, 145, 15, 15, WHITE)
    tft.fill_rect(95, 175, 50, 8, WHITE)

    print("GAME OVER")
    print("Presiona cualquier boton para reiniciar")

def spawn_food(snake_set):
    while True:
        food = (
            random.randrange(0, GRID_W),
            random.randrange(0, GRID_H)
        )

        if food not in snake_set:
            return food


# JUEGO

def game():
    global speed_ms

    score = 0
    speed_ms = 140

    head = (GRID_W // 2, GRID_H // 2)

    snake = [
        head,
        (head[0] - 1, head[1]),
        (head[0] - 2, head[1])
    ]

    snake_set = set(snake)

    dx = 1
    dy = 0

    pending_dx = dx
    pending_dy = dy

    food = spawn_food(snake_set)

    clear_screen(BLACK)
    draw_hud(score)

    tft.rect(0, HUD_H, W, H - HUD_H, WHITE)

    for i, segment in enumerate(snake):
        if i == 0:
            draw_cell(segment, GREEN)
        else:
            draw_cell(segment, DARK_GREEN)

    draw_cell(food, RED)

    last_step = time.ticks_ms()

    while True:
        # Actualizar brillo constantemente
        update_brightness()

        ndx, ndy = read_direction()

        if ndx != 0 or ndy != 0:
            if not (ndx == -dx and ndy == -dy):
                if (ndx, ndy) != (pending_dx, pending_dy):
                    turn_sound()

                pending_dx = ndx
                pending_dy = ndy

        now = time.ticks_ms()

        if time.ticks_diff(now, last_step) < speed_ms:
            time.sleep_ms(5)
            continue

        last_step = now

        dx = pending_dx
        dy = pending_dy

        hx, hy = snake[0]
        new_head = (hx + dx, hy + dy)

        if (
            new_head[0] < 0 or
            new_head[0] >= GRID_W or
            new_head[1] < 0 or
            new_head[1] >= GRID_H
        ):
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

            if score % 3 == 0 and speed_ms > 60:
                speed_ms -= 10

            draw_hud(score)

            food = spawn_food(snake_set)
            draw_cell(food, RED)

        else:
            removed_tail = snake.pop()
            snake_set.remove(removed_tail)
            draw_cell(removed_tail, BLACK)

# LOOP PRINCIPAL

while True:
    update_brightness()

    draw_start_screen()
    wait_any_button()

    start_sound()

    game()