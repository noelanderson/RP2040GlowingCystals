import alarm
import board
import time
from micropython import const

from HallEffectSensor import HallEffectSensor
from RotaryEncoder import RotaryEncoder
from Leds import Leds

"""
Simple state machine class
 Defines states
 Keeps track of state changes
 tick() called on every iteration of main program loop.  Sleeps for 20 milliseconds.
  goes into low power state after 10 minutes of no user activity.
 State actions performed in main loop as an if/elif/else chain
"""
class SystemState:
    LOW_POWER = const(0)
    START_UP = const(1)
    WHITE_PULSING = const(2)
    RAINBOW_PULSING = const(3)
    SELECTED_COLOUR_PULSING = const(4)
    STATE_NAMES = ["Low Power", "Start Up", "White Pulsing", "Rainbow Pulsing", "Selected Colour pulsing"]
    TEN_MINUTES = const(30000)
    ONE_MINUTE = const(3000)

    state = None
    timeoutCount = 0

    @staticmethod
    def nameFromState(state) -> str:
        name = "Unknown"
        if state in range(0, 5, 1):
            name = SystemState.STATE_NAMES[state]
        return name

    def __init__(self, state):
        print ("state: ", SystemState.nameFromState(self.state), " -> ", SystemState.nameFromState(state))
        self.state = state
        self.timeoutCount = 0

    @property
    def current(self) -> int:
        return self.state

    def tick(self):
        self.timeoutCount = (self.timeoutCount + 1) % SystemState.TEN_MINUTES
        if self.timeoutCount == 0: # Timed out, so go into low power mode
            self.change(SystemState.LOW_POWER)
        time.sleep(0.02)

    def change(self, newState):
        if newState != self.state:
            print ("state: ", SystemState.nameFromState(self.state), " -> ", SystemState.nameFromState(newState))
            self.state = newState
            self.timeoutCount = 0 # Reset our timeout as we have user activity


"""
Set up Board (adafruit RP2040 Feather)
 D4    output - neopixel leds
 D11   input - rotary encoder A
 D10   input - rotary encoder B
 D12   input - rotary encoder switch 
 D24   input - moon Hall Effect sensor
 D25   input - sun Hall Effect sensor
"""
if alarm.wake_alarm != None:
    if isinstance(alarm.wake_alarm, alarm.pin.PinAlarm):
        print("wake from deep sleep")
        # startState = alarm.sleep_memory[0]
        # enc = alarm.sleep_memory[1]

# Neopixel output
leds = Leds(board.D4, 2)

# Rotary Encoder
encoder =  RotaryEncoder(board.D11, board.D10, board.D12)

# Hall Effect Sensors
moon = HallEffectSensor(board.D24)
sun = HallEffectSensor(board.D25)

# Control state
state = SystemState(SystemState.START_UP)
colour = Leds.WHITE


##############################################
# Main Loop
while True:
    # Run State Machine
    state.tick()
    if state.current == SystemState.START_UP:
        if moon.isAligned:
            state.change(SystemState.WHITE_PULSING)

    elif state.current == SystemState.WHITE_PULSING:
        leds.colourPulse(Leds.WHITE)
        if sun.isAligned:
            state.change(SystemState.RAINBOW_PULSING)
        if not moon.isAligned:
            state.change(SystemState.LOW_POWER)

    elif state.current == SystemState.RAINBOW_PULSING:
        leds.rainbowPulse()
        encoder.adjustedPosition = leds.colourStep  # keep in sync
        if not sun.isAligned:
            state.change(SystemState.WHITE_PULSING)
        if not moon.isAligned:
            state.change(SystemState.LOW_POWER)
        if encoder.isClicked:
            state.change(SystemState.SELECTED_COLOUR_PULSING)

    elif state.current == SystemState.SELECTED_COLOUR_PULSING:
        newColour = Leds.colourWheel(encoder.adjustedPosition)
        if newColour != colour:
            leds.colourStep = encoder.adjustedPosition # keep in sync
            colour = newColour
        leds.colourPulse(colour)
        if not sun.isAligned:
            state.change(SystemState.WHITE_PULSING)
        if not moon.isAligned:
            state.change(SystemState.LOW_POWER)
        if encoder.isClicked:
            state.change(SystemState.RAINBOW_PULSING)

    else: # State.LOW_POWER
        # Deinit our existing device configuration
        leds.off()
        encoder.deinit()
        moon.deinit()
        sun.deinit()

        # Reuse our inputs as alarm triggers
        encoderPinAlarm = alarm.pin.PinAlarm(pin=board.D12, value=False, pull=True, edge = True)
        encoderAPinAlarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True, edge = True)
        encoderBPinAlarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True, edge = True)
        moonPinAlarm = alarm.pin.PinAlarm(pin=board.D24, value=False, pull=True, edge = True)
        pin_alarm_sun = alarm.pin.PinAlarm(pin=board.D25, value=False, pull=True, edge = True)

        # Exit the program, and then deep sleep until one of the controls is moved to create a PIN alarm.
        alarm.exit_and_deep_sleep_until_alarms(encoderPinAlarm, encoderAPinAlarm, encoderBPinAlarm, moonPinAlarm, pin_alarm_sun)