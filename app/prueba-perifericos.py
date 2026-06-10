from machine import Pin, SPI, PWM
import time
import st7789py as st7789

# Pines del display con tu conexión actual
PIN_SCK = 2
PIN_MOSI = 3
PIN_RESET = 7
PIN_DC = 6
PIN_BLK = 8

# Pines de botones
PIN_UP = 10
PIN_DOWN = 11
PIN_LEFT = 12
PIN_RIGHT = 13

# Pin del buzzer
PIN_BUZZER = 14

# Botones con resistencia pull-up interna
btn_up = Pin(PIN_UP, Pin.IN, Pin.PULL_UP)
btn_down = Pin(PIN_DOWN, Pin.IN, Pin.PULL_UP)
btn_left = Pin(PIN_LEFT, Pin.IN, Pin.PULL_UP)
btn_right = Pin(PIN_RIGHT, Pin.IN, Pin.PULL_UP)

# Buzzer pasivo
buzzer = PWM(Pin(PIN_BUZZER))
buzzer.duty_u16(0)

def beep(freq=1200, duration_ms=80, volume=12000):
    buzzer.freq(freq)
    buzzer.duty_u16(volume)
    time.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

# Luz de fondo
backlight = Pin(PIN_BLK, Pin.OUT)
backlight.value(1)

# SPI0
spi = SPI(
    0,
    baudrate=40_000_000,
    polarity=1,
    phase=1,
    sck=Pin(PIN_SCK),
    mosi=Pin(PIN_MOSI)
)

# Inicialización del display ST7789 240x240 sin CS
tft = st7789.ST7789(
    spi,
    240,
    240,
    reset=Pin(PIN_RESET, Pin.OUT),
    dc=Pin(PIN_DC, Pin.OUT),
    cs=None,
    backlight=backlight,
    rotation=0
)

# Pantalla inicial
tft.fill(st7789.BLACK)

while True:
    # Recuerda:
    # Con PULL_UP, el botón presionado lee 0
    # El botón sin presionar lee 1

    if btn_up.value() == 0:
        tft.fill(st7789.BLUE)
        print("ARRIBA - AZUL")
        beep(1000, 80)
        time.sleep_ms(200)

    elif btn_down.value() == 0:
        tft.fill(st7789.GREEN)
        print("ABAJO - VERDE")
        beep(1200, 80)
        time.sleep_ms(200)

    elif btn_right.value() == 0:
        tft.fill(st7789.WHITE)
        print("DERECHA - BLANCO")
        beep(1400, 80)
        time.sleep_ms(200)

    elif btn_left.value() == 0:
        tft.fill(st7789.RED)
        print("IZQUIERDA - ROJO")
        beep(800, 80)
        time.sleep_ms(200)

    else:
        # No hace nada cuando no presionas botones
        buzzer.duty_u16(0)
        time.sleep_ms(20)