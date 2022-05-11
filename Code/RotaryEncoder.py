"""
Simple rotary encoder with pushbutton device
Tracks pushbutton state, rotary position (modulo 255) and adjusted position (relative to given start point)
"""
import digitalio
import rotaryio

class RotaryEncoder:
    buttonClicked = False    # Tracks when the encoder button was pressed and released
    startPosition = 0
    lastPosition = 0

    def __init__(self, APin, BPin, switchPin):
        self.encoder = rotaryio.IncrementalEncoder(APin, BPin)
        self.encoderSwitch = digitalio.DigitalInOut(switchPin)
        self.encoderSwitch.direction = digitalio.Direction.INPUT
        self.encoderSwitch.pull = digitalio.Pull.UP
        self.startPosition = int(0)

    def deinit(self):
        self.encoder.deinit()
        self.encoderSwitch.deinit()

    @property
    def adjustedPosition(self) -> int:
        adjustment = self.lastPosition - self.encoder.position
        pos = self.startPosition + adjustment
        if adjustment != 0:
            self.lastPosition = self.encoder.position
            self.startPosition = pos
        return pos % 255

    @adjustedPosition.setter
    def adjustedPosition(self, value):
        self.startPosition = value
        self.lastPosition = self.encoder.position

    @property
    def position(self) -> int:
        self.lastPosition = self.encoder.position
        return self.encoder.position % 255

    @property
    def button(self) -> bool:
        return not self.encoderSwitch.value

    @property
    def isClicked(self) -> bool:
        clicked = False
        push = self.button
        if push == True and self.buttonClicked == False:
            self.buttonClicked = True
        elif push == False and self.buttonClicked == True:
            self.buttonClicked = False
            clicked = True
        return clicked