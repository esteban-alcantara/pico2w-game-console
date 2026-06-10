from machine import Pin, SPI, PWM, ADC
import time
import st7789py as st7789
import random

# =================================================
# PINES
# =================================================
PIN_SCK = 2
PIN_MOSI = 3
PIN_RESET = 7
PIN_DC = 6
PIN_BLK = 8

PIN_POT = 26
PIN_UP = 18
PIN_DOWN = 19
PIN_LEFT = 20
PIN_RIGHT = 21
PIN_BUZZER = 14
PIN_MENU = 16

# =================================================
# DISPLAY
# =================================================
backlight_pin = Pin(PIN_BLK, Pin.OUT)
backlight_pin.value(1)

spi = SPI(0, baudrate=40_000_000, polarity=1, phase=1, sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI))

tft = st7789.ST7789(spi, 240, 240, reset=Pin(PIN_RESET, Pin.OUT),
                    dc=Pin(PIN_DC, Pin.OUT), cs=None, backlight=backlight_pin, rotation=1)

backlight_pwm = PWM(backlight_pin)
backlight_pwm.freq(1000)

pot = ADC(Pin(PIN_POT))

# =================================================
# BRILLO
# =================================================
BRIGHTNESS_MIN = 3000
BRIGHTNESS_MAX = 65535

def update_brightness():
    raw = pot.read_u16()
    duty = BRIGHTNESS_MIN + int(raw * (BRIGHTNESS_MAX - BRIGHTNESS_MIN) / 65535)
    backlight_pwm.duty_u16(duty)

# =================================================
# BOTONES
# =================================================
btn_up = Pin(PIN_UP, Pin.IN, Pin.PULL_UP)
btn_down = Pin(PIN_DOWN, Pin.IN, Pin.PULL_UP)
btn_left = Pin(PIN_LEFT, Pin.IN, Pin.PULL_UP)
btn_right = Pin(PIN_RIGHT, Pin.IN, Pin.PULL_UP)
btn_menu = Pin(PIN_MENU, Pin.IN, Pin.PULL_UP)

def pressed(button):
    return button.value() == 0

def any_button_pressed():
    return pressed(btn_up) or pressed(btn_down) or pressed(btn_left) or pressed(btn_right)

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

# Bandera global que indica si se presionó
menu_pressed_flag = False

# Función de interrupción
def menu_isr(pin):
    global menu_pressed_flag
    menu_pressed_flag = True

# Configurar interrupción para flanco descendente (cuando se presiona)
btn_menu.irq(trigger=Pin.IRQ_FALLING, handler=menu_isr)

# =================================================
# BUZZER
# =================================================
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

def menu_sound():
    tone(1200, 40, 8000)

def select_sound():
    tone(1600, 70, 10000)