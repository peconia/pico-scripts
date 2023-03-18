import array, time
from machine import Pin
import rp2
import random

# Configure the number of WS2812 LEDs, pins and brightness.
NUM_LEDS = 8
PIN_NUM = 21


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 1]
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on Pin(16).
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])


def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i, c in enumerate(ar):
        brightness = random.random()
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g << 16) + (r << 8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)


def pixels_set(i, color):
    ar[i] = (color[1] << 16) + (color[0] << 8) + color[2]


def pixels_fill(color):
    for i in range(len(ar)):
        if random.randint(0, 2) == 1:
            pixels_set(i, color)
        time.sleep(random.uniform(0.02, 0.15))
        pixels_show()


ORANGE = (252, 177, 3)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
DARK_ORANGE = (252, 107, 3)
DARK_RED = (135, 41, 7)
LIGHT_YELLOW = (252, 252, 3)
PURPLE = (252, 211, 3)
WHITE = (255, 255, 255)
COLORS = (DARK_ORANGE, RED, YELLOW, ORANGE, DARK_RED, LIGHT_YELLOW, PURPLE, WHITE)

while True:
    for color in COLORS:
        pixels_fill(color)
        time.sleep(0.02)
