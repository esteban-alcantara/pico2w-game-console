from machine import Pin, SPI, PWM, ADC
import time
import random
import st7789py as st7789

# =============================
# PINES DEL DISPLAY ST7789
# =============================
PIN_SCK = 2
PIN_MOSI = 3
PIN_RESET = 7
PIN_DC = 6
PIN_BLK = 8

# POTENCIOMETRO BRILLO
PIN_POT = 26

# BOTONES
PIN_UP = 18
PIN_DOWN = 19
PIN_LEFT = 20
PIN_RIGHT = 21
PIN_MENU = 16  # Botón para seleccionar juego

# BUZZER
PIN_BUZZER = 14

# =============================
# CONFIGURACIÓN HARDWARE
# =============================
# Botones con pull-up
btn_up = Pin(PIN_UP, Pin.IN, Pin.PULL_UP)
btn_down = Pin(PIN_DOWN, Pin.IN, Pin.PULL_UP)
btn_left = Pin(PIN_LEFT, Pin.IN, Pin.PULL_UP)
btn_right = Pin(PIN_RIGHT, Pin.IN, Pin.PULL_UP)
btn_menu = Pin(PIN_MENU, Pin.IN, Pin.PULL_UP)

# Buzzer
buzzer = PWM(Pin(PIN_BUZZER))
buzzer.duty_u16(0)

def tone(freq, duration_ms, volume=12000):
    buzzer.freq(freq)
    buzzer.duty_u16(volume)
    time.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

# Sonidos
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

# Display
backlight_pin = Pin(PIN_BLK, Pin.OUT)
backlight_pin.value(1)

spi = SPI(0, baudrate=40_000_000, polarity=1, phase=1, sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI))
tft = st7789.ST7789(spi, 240, 240, reset=Pin(PIN_RESET, Pin.OUT), dc=Pin(PIN_DC, Pin.OUT),
                     cs=None, backlight=backlight_pin, rotation=1)

# PWM de backlight
backlight_pwm = PWM(backlight_pin)
backlight_pwm.freq(1000)
pot = ADC(Pin(PIN_POT))
BRIGHTNESS_MIN = 3000
BRIGHTNESS_MAX = 65535

def update_brightness():
    raw = pot.read_u16()
    duty = BRIGHTNESS_MIN + int(raw * (BRIGHTNESS_MAX - BRIGHTNESS_MIN) / 65535)
    backlight_pwm.duty_u16(duty)

# =============================
# COLORES Y CONFIG
# =============================
W = 240
H = 240

BLACK = st7789.BLACK
WHITE = st7789.WHITE
RED = st7789.RED
GREEN = st7789.GREEN
BLUE = st7789.BLUE
YELLOW = st7789.YELLOW
DARK_GREEN = st7789.color565(0, 140, 0)
GRAY = st7789.color565(60, 60, 60)

# =============================
# FUNCIONES DE BOTONES
# =============================
def pressed(button):
    return button.value() == 0

def any_button_pressed():
    return (
        pressed(btn_up) or
        pressed(btn_down) or
        pressed(btn_left) or
        pressed(btn_right) or
        pressed(btn_menu)
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

# =============================
# DIBUJO
# =============================
CELL = 10
HUD_H = 20
PLAY_X0 = 0
PLAY_Y0 = HUD_H
PLAY_W = W
PLAY_H = H - HUD_H
GRID_W = PLAY_W // CELL
GRID_H = PLAY_H // CELL

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
        tft.fill_rect(i*8, 7, 6, 8, YELLOW)

# =============================
# SNAKE
# =============================
def spawn_food(snake_set):
    while True:
        food = (random.randrange(0, GRID_W), random.randrange(0, GRID_H))
        if food not in snake_set:
            return food

def snake_game():
    score = 0
    speed_ms = 140
    head = (GRID_W//2, GRID_H//2)
    snake = [head, (head[0]-1, head[1]), (head[0]-2, head[1])]
    snake_set = set(snake)
    dx, dy = 1, 0
    pending_dx, pending_dy = dx, dy
    food = spawn_food(snake_set)
    clear_screen(BLACK)
    draw_hud(score)
    for i, segment in enumerate(snake):
        draw_cell(segment, GREEN if i==0 else DARK_GREEN)
    draw_cell(food, RED)
    last_step = time.ticks_ms()

    while True:
        update_brightness()
        ndx, ndy = read_direction()
        if ndx != 0 or ndy != 0:
            if not (ndx == -dx and ndy == -dy):
                if (ndx, ndy) != (pending_dx, pending_dy):
                    turn_sound()
                pending_dx, pending_dy = ndx, ndy

        now = time.ticks_ms()
        if time.ticks_diff(now, last_step) < speed_ms:
            time.sleep_ms(5)
            continue
        last_step = now
        dx, dy = pending_dx, pending_dy
        hx, hy = snake[0]
        new_head = (hx+dx, hy+dy)
        if new_head[0]<0 or new_head[0]>=GRID_W or new_head[1]<0 or new_head[1]>=GRID_H or (new_head in snake_set and new_head!=snake[-1]):
            gameover_sound()
            clear_screen(RED)
            time.sleep_ms(500)
            return
        snake.insert(0, new_head)
        snake_set.add(new_head)
        draw_cell(new_head, GREEN)
        if len(snake)>1:
            draw_cell(snake[1], DARK_GREEN)
        if new_head == food:
            eat_sound()
            score += 1
            if score % 3 == 0 and speed_ms>60:
                speed_ms -= 10
            draw_hud(score)
            food = spawn_food(snake_set)
            draw_cell(food, RED)
        else:
            removed = snake.pop()
            snake_set.remove(removed)
            draw_cell(removed, BLACK)

# =============================
# SPEED RACE 1974 (versión simplificada)
# =============================
def speed_race_game():
    car_x = W//2
    car_y = H-30
    obstacle_y = 0
    obstacle_x = random.randrange(0, W-10, 10)
    speed = 5
    score = 0
    clear_screen(BLACK)
    tft.fill_rect(car_x, car_y, 10, 20, GREEN)
    last_step = time.ticks_ms()
    while True:
        update_brightness()
        ndx, _ = read_direction()
        car_x += ndx*10
        if car_x<0: car_x=0
        if car_x>W-10: car_x=W-10
        # mover obstáculo
        obstacle_y += speed
        if obstacle_y>H:
            obstacle_y=0
            obstacle_x=random.randrange(0, W-10, 10)
            score += 1
            start_sound()
        # checar colisión
        if (obstacle_y+10 >= car_y and obstacle_y<=car_y+20) and (obstacle_x+10 >= car_x and obstacle_x <= car_x+10):
            gameover_sound()
            clear_screen(RED)
            time.sleep_ms(500)
            return
        # dibujar
        clear_screen(BLACK)
        tft.fill_rect(car_x, car_y, 10, 20, GREEN)
        tft.fill_rect(obstacle_x, obstacle_y, 10, 10, RED)
        tft.text(str(score), 5, 0, WHITE)
        time.sleep_ms(50)

# =============================
# MENÚ DE SELECCIÓN
# =============================
games = ["Snake", "Speed Race"]
selected = 0

def draw_menu():
    clear_screen(BLACK)
    tft.text("Selecciona juego:", 10, 10, WHITE)
    for i, g in enumerate(games):
        color = YELLOW if i==selected else WHITE
        tft.text(g, 20, 40 + i*30, color)

# =============================
# LOOP PRINCIPAL
# =============================
while True:
    update_brightness()
    # Menú
    selected = 0
    while True:
        draw_menu()
        update_brightness()
        if pressed(btn_up):
            selected = (selected - 1) % len(games)
            turn_sound()
            time.sleep_ms(180)
        if pressed(btn_down):
            selected = (selected + 1) % len(games)
            turn_sound()
            time.sleep_ms(180)
        if pressed(btn_menu):
            start_sound()
            time.sleep_ms(200)
            break
        time.sleep_ms(50)

    # Ejecutar juego
    if games[selected] == "Snake":
        snake_game()
    else:
        speed_race_game()
        
