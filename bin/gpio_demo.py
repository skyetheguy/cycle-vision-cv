import logging
import threading
import time
import RPi.GPIO as GPIO

    #############################
    ###       CONSTANTS       ###
    #############################

# Time/delays
# ---------------
BOUNCETIME_MS = 500
TURN_SIG_FLASHTIME_S = 0.5
BLIND_SPOT_FLASHTIME_S = 0.2
CALLBACK_DELAY_S = 0.5

# Main light pins
# ---------------
FRONT_LIGHT = 13
REAR_LIGHT = 18
NIGHT_LIGHTS = [FRONT_LIGHT, REAR_LIGHT]
NIGHT_LIGHTS_BUTTON = 33

# Left turn sig pins
# --------------------
LEFT_TURN_FRONT_LIGHT = 7
LEFT_TURN_REAR_LIGHT = 12
LEFT_TURN_LIGHTS = [LEFT_TURN_FRONT_LIGHT, LEFT_TURN_REAR_LIGHT]
LEFT_TURN_LIGHTS_BUTTON = 35

# Right turn sig pins
# ---------------------
RIGHT_TURN_FRONT_LIGHT = 11
RIGHT_TURN_REAR_LIGHT = 16
RIGHT_TURN_LIGHTS = [RIGHT_TURN_FRONT_LIGHT, RIGHT_TURN_REAR_LIGHT]
RIGHT_TURN_LIGHTS_BUTTON = 37

# Blind spot pins
# -----------------
LEFT_BLIND_SPOT_LIGHT = 15
RIGHT_BLIND_SPOT_LIGHT = 19
BLIND_SPOT_LIGHTS = [LEFT_BLIND_SPOT_LIGHT, RIGHT_BLIND_SPOT_LIGHT]

# Light and button pins (consists of pins above)
# ----------------------
LIGHT_CONTROL_PINS = NIGHT_LIGHTS + LEFT_TURN_LIGHTS + RIGHT_TURN_LIGHTS + BLIND_SPOT_LIGHTS
BUTTON_PINS = [NIGHT_LIGHTS_BUTTON, LEFT_TURN_LIGHTS_BUTTON, RIGHT_TURN_LIGHTS_BUTTON]


    #############################
    ###        GLOBALS        ###
    #############################

# Events
turn_sig_event = threading.Event()      # Happens when turn sig turned on, used by turn sig thread
blind_spot_event = threading.Event()    # Happens when turn sig turned on, used by blind spot thread

# Light states (True = ON, False = Off)
night_lights_state = False
left_turn_lights_state = False
right_turn_lights_state = False
left_blind_spot_light_state = False
right_blind_spot_light_state = False


    #############################
    ###       INTERRUPTS      ###
    #############################

# Toggle front and rear light callback
def toggle_night_lights(channel):
    global night_lights_state

    if night_lights_state:
        logging.info("Lights OFF")
        for pin in NIGHT_LIGHTS:
            GPIO.output(pin, GPIO.LOW)
    else:
        logging.info("Lights ON")
        for pin in NIGHT_LIGHTS:
            GPIO.output(pin, GPIO.HIGH)

    night_lights_state ^= True

    time.sleep(CALLBACK_DELAY_S)


# Toggle front and rear turn lights callback
def toggle_turn_lights(channel):
    global right_turn_lights_state
    global left_turn_lights_state
    global turn_sig_event

    if (channel == LEFT_TURN_LIGHTS_BUTTON):
        # Ensure both lights arent on at the same time
        if right_turn_lights_state:
            logging.info("Right turn sig OFF, Left ON")
            right_turn_lights_state = False

        if left_turn_lights_state:
            logging.info("Left turn sig OFF")

            left_turn_lights_state = False
        else:
            logging.info("Left turn sig ON")

            left_turn_lights_state = True
            turn_sig_event.set()
            blind_spot_event.set()

    elif (channel == RIGHT_TURN_LIGHTS_BUTTON):
        # Ensure both lights arent on at the same time
        if left_turn_lights_state:
            logging.info("Left turn sig OFF, Right ON")
            left_turn_lights_state = False

        if right_turn_lights_state:
            logging.info("Right turn sig OFF")

            right_turn_lights_state = False
        else:
            logging.info("Right turn sig ON")

            right_turn_lights_state = True
            turn_sig_event.set()
            blind_spot_event.set()

    time.sleep(CALLBACK_DELAY_S)



    #############################
    ###        THREADS        ###
    #############################

# Thread for flashing turn signal lights
def flash_turn_sigs():
    global right_turn_lights_state
    global turn_sig_event

    while True:
        turn_sig_event.wait()
        turn_sig_event.clear()

        if (right_turn_lights_state):
            while (right_turn_lights_state):

                # Flash right LEDs
                for pin in RIGHT_TURN_LIGHTS:
                    GPIO.output(pin, GPIO.HIGH)
                time.sleep(TURN_SIG_FLASHTIME_S)
                for pin in RIGHT_TURN_LIGHTS:
                    GPIO.output(pin, GPIO.LOW)
                time.sleep(TURN_SIG_FLASHTIME_S)

        elif (left_turn_lights_state):
            while (left_turn_lights_state):

                # Flash left LEDs
                for pin in LEFT_TURN_LIGHTS:
                    GPIO.output(pin, GPIO.HIGH)
                time.sleep(TURN_SIG_FLASHTIME_S)
                for pin in LEFT_TURN_LIGHTS:
                    GPIO.output(pin, GPIO.LOW)
                time.sleep(TURN_SIG_FLASHTIME_S)

# Thread for flashing turn signal lights
def flash_blind_spot():
    global left_turn_lights_state
    global right_turn_lights_state
    global left_blind_spot_light_state
    global right_blind_spot_light_state
    global blind_spot_event

    while True:
        blind_spot_event.wait()
        blind_spot_event.clear()

        # While one of the turn signals are on, continously check blind spots and flash lights if occupied
        while left_turn_lights_state or right_turn_lights_state:
            if left_turn_lights_state and left_blind_spot_light_state:
                # Flash left warning LEDs
                GPIO.output(LEFT_BLIND_SPOT_LIGHT, GPIO.HIGH)
                time.sleep(BLIND_SPOT_FLASHTIME_S)
               
                GPIO.output(LEFT_BLIND_SPOT_LIGHT, GPIO.LOW)

            elif right_turn_lights_state and right_blind_spot_light_state:
                # Flash righ warningt LEDs
                GPIO.output(RIGHT_BLIND_SPOT_LIGHT, GPIO.HIGH)
                time.sleep(BLIND_SPOT_FLASHTIME_S)
               
                GPIO.output(RIGHT_BLIND_SPOT_LIGHT, GPIO.LOW)

            # Sleep used for flashing AND not continuously polling blind spots not occupied
            time.sleep(BLIND_SPOT_FLASHTIME_S)

        # Set light to solid ON if blind spot still occupied but turn sig off
        if left_blind_spot_light_state:
            GPIO.output(LEFT_BLIND_SPOT_LIGHT, GPIO.HIGH)
        if right_blind_spot_light_state:
            GPIO.output(RIGHT_BLIND_SPOT_LIGHT, GPIO.HIGH)



    #############################
    ###        PUBLIC         ###
    #############################

# * init
# *
# * @desc Sets up GPIOs, hardware interrupts for button presses and starts threads for flashing lights
def init():
    global turn_sig_event

    # Pin Setup
    # ==========================================================
    # BOARD pin-numbering scheme
    GPIO.setmode(GPIO.BOARD)

    # LED pins set as output
    GPIO.setup(LIGHT_CONTROL_PINS, GPIO.OUT)

    # Button pins set as input
    GPIO.setup(BUTTON_PINS, GPIO.IN)
    # ==========================================================

    # Pin Init
    # ===========================================
    for pin in LIGHT_CONTROL_PINS:
        GPIO.output(pin, GPIO.LOW)

    GPIO.add_event_detect(NIGHT_LIGHTS_BUTTON, GPIO.FALLING, callback=toggle_night_lights, bouncetime=BOUNCETIME_MS)
    GPIO.add_event_detect(RIGHT_TURN_LIGHTS_BUTTON, GPIO.FALLING, callback=toggle_turn_lights, bouncetime=BOUNCETIME_MS)
    GPIO.add_event_detect(LEFT_TURN_LIGHTS_BUTTON, GPIO.FALLING, callback=toggle_turn_lights, bouncetime=BOUNCETIME_MS)
    # ===========================================

    # Settup threads
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    turn_sig_event.clear()

    turn_sig_thread = threading.Thread(target=flash_turn_sigs, args=())
    turn_sig_thread.start()


    blind_spot_event.clear()

    blind_spot_thread = threading.Thread(target=flash_blind_spot, args=())
    blind_spot_thread.start()
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# * update_blind_spot
# *
# * @desc Updates the blind spot occupied state for either side of the bike
# * @param side - either "left" or "right"
# * @param occupied - True or False
def update_blind_spot(side, occupied):
    global left_blind_spot_light_state
    global right_blind_spot_light_state

    if side == "left":
        # If state has not changed, do nothing
        if left_blind_spot_light_state == occupied:
            return

        if left_blind_spot_light_state:
            logging.info("Left blind OFF")
            GPIO.output(LEFT_BLIND_SPOT_LIGHT, GPIO.LOW)
        else:
            logging.info("Left blind  ON")
            GPIO.output(LEFT_BLIND_SPOT_LIGHT, GPIO.HIGH)

        left_blind_spot_light_state ^= True

    elif side == "right":
        # If state has not changed, do nothing
        if right_blind_spot_light_state == occupied:
            return

        if right_blind_spot_light_state:
            logging.info("Right blind OFF")
            GPIO.output(RIGHT_BLIND_SPOT_LIGHT, GPIO.LOW)
        else:
            logging.info("Right blind  ON")
            GPIO.output(RIGHT_BLIND_SPOT_LIGHT, GPIO.HIGH)

        right_blind_spot_light_state ^= True

    

def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    init()

    try:
        logging.info("Starting test")

        while(1):
            print("Doing nothing")
            time.sleep(5)

    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()

