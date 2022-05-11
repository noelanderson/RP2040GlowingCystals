
"""
LED object based on neopixels
Uses a sinewave to give the leds a breath-like pulsing effect
Pulse the brightness for a given colour, or cycle though colour wheel for a rainbow effect

The RP2040 has no built-in floating point support, so use a pre-calculated table for performance
Table is power (brighness) values between 0 & 1 based on the following formula: 0.5 + (0.5 * SIN(2PI)/ (255 * arrayPos))
Table is maxGenerations long
"""
import array
from micropython import const
import neopixel

class Leds:
    WHITE = (255,255,255)
    OFF = (0, 0, 0)
    maxGenerations = const(256)
    maxPos = const(255)
    sin_table = array.array('f',[0.50,0.51,0.52,0.54,0.55,0.56,0.57,0.59,0.60,0.61,0.62,0.63,0.65,0.66,0.67,0.68,0.69,0.70,0.71,
        0.73,0.74,0.75,0.76,0.77,0.78,0.79,0.80,0.81,0.82,0.83,0.84,0.85,0.85,0.86,0.87,0.88,0.89,0.90,0.90,0.91,0.92,0.92,0.93,0.94,
        0.94,0.95,0.95,0.96,0.96,0.97,0.97,0.98,0.98,0.98,0.99,0.99,0.99,0.99,0.99,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,
        1.00,0.99,0.99,0.99,0.99,0.98,0.98,0.98,0.97,0.97,0.97,0.96,0.96,0.95,0.94,0.94,0.93,0.93,0.92,0.91,0.91,0.90,0.89,0.88,0.88,
        0.87,0.86,0.85,0.84,0.83,0.82,0.81,0.80,0.79,0.78,0.77,0.76,0.75,0.74,0.73,0.72,0.71,0.70,0.69,0.67,0.66,0.65,0.64,0.63,0.62,
        0.60,0.59,0.58,0.57,0.56,0.54,0.53,0.52,0.51,0.49,0.48,0.47,0.46,0.44,0.43,0.42,0.41,0.40,0.38,0.37,0.36,0.35,0.34,0.33,0.31,
        0.30,0.29,0.28,0.27,0.26,0.25,0.24,0.23,0.22,0.21,0.20,0.19,0.18,0.17,0.16,0.15,0.14,0.13,0.12,0.12,0.11,0.10,0.09,0.09,0.08,
        0.07,0.07,0.06,0.06,0.05,0.04,0.04,0.03,0.03,0.03,0.02,0.02,0.02,0.01,0.01,0.01,0.01,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,
        0.00,0.00,0.00,0.01,0.01,0.01,0.01,0.01,0.02,0.02,0.02,0.03,0.03,0.04,0.04,0.05,0.05,0.06,0.06,0.07,0.08,0.08,0.09,0.10,0.10,
        0.11,0.12,0.13,0.14,0.15,0.15,0.16,0.17,0.18,0.19,0.20,0.21,0.22,0.23,0.24,0.25,0.26,0.27,0.29,0.30,0.31,0.32,0.33,0.34,0.35,
        0.37,0.38,0.39,0.40,0.41,0.43,0.44,0.45,0.46,0.48,0.49,0.50])

    @staticmethod
    def colourWheel(pos) -> tuple[int, int, int,]:
        red = blue = green = offset = 0
        if pos < 0 or pos > Leds.maxPos:
            pass
        # split wheel into 3 sectors
        elif pos < 85:
            offset = pos * 3
            red = Leds.maxPos - offset
            green = offset
            blue = 0
        elif pos < 170:
            offset = (pos - 85) * 3
            red = 0
            green = Leds.maxPos - offset
            blue = offset
        else:
            offset = (pos - 170) * 3
            red = offset
            green = 0
            blue = Leds.maxPos - offset
        return (red, green, blue)

    def __init__(self, pin, count):
        self.colour = Leds.OFF
        self.brightness = 0
        self.currentBrightnessStep = 0
        self.currentColourStep = 0
        self.pixels = neopixel.NeoPixel(pin, count)
        self.off()

    def __setPixels(self)-> None:
        #Update the hardware to match the class values
        self.pixels.brightness = self.brightness
        for i in range(len(self.pixels)):
            self.pixels[i] = self.colour

    @property
    def colourStep(self) -> int:
        return self.currentColourStep

    @colourStep.setter
    def colourStep(self, value):
        self.currentColourStep = value

    def off(self) -> None:
        self.pixels.brightness = 0
        self.colour = Leds.OFF
        self.__setPixels()

    def colourPulse(self, colour) -> None:
        self.brightness = self.sin_table[self.currentBrightnessStep]
        self.currentBrightnessStep = (self.currentBrightnessStep + 1) % self.maxGenerations
        self.colour = colour
        self.__setPixels()

    def rainbowPulse(self) -> None:
        self.brightness = self.sin_table[self.currentBrightnessStep]
        self.currentBrightnessStep = (self.currentBrightnessStep + 1) % self.maxGenerations
        # Every 10 bringness changes, also change the colour
        if self.currentBrightnessStep % 10 == 0:
            self.colour = Leds.colourWheel(self.currentColourStep)
            self.currentColourStep = (self.currentColourStep + 1) % self.maxGenerations
        self.__setPixels()
