import logging
import threading
import time
import RPi.GPIO as GPIO

    #############################
    ###       CONSTANTS       ###
    #############################

# Time/delays
# ---------------
bouncetime_ms = 500
turn_sig_flashtime_s = 0.5
blind_spot_flashtime_s = 0.2
callback_delay_s = 0.5

# Main light pins
# ---------------
front_light = 13
rear_light = 18
night_lights = [front_light, rear_light]
night_lights_button = 33

# Left turn sig pins
# --------------------
left_turn_front_light = 7
left_turn_rear_light = 12
left_turn_lights = [left_turn_front_light, left_turn_rear_light]
left_turn_lights_button = 35

# Right turn sig pins
# ---------------------
right_turn_front_light = 11
right_turn_rear_light = 16
right_turn_lights = [right_turn_front_light, right_turn_rear_light]
right_turn_lights_button = 37

# Blind spot pins
# -----------------
left_blind_spot_light = 15
right_blind_spot_light = 19
blind_spot_lights = [left_blind_spot_light, right_blind_spot_light]

# Light and button pins (consists of pins above)
# ----------------------
light_control_pins = night_lights + left_turn_lights + right_turn_lights + blind_spot_lights
button_pins = [night_lights_button, left_turn_lights_button, right_turn_lights_button]


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
        for pin in night_lights:
            GPIO.output(pin, GPIO.LOW)
    else:
        logging.info("Lights ON")
        for pin in night_lights:
            GPIO.output(pin, GPIO.HIGH)

    night_lights_state ^= True

    time.sleep(callback_delay_s)


# Toggle front and rear turn lights callback
def toggle_turn_lights(channel):
    global right_turn_lights_state
    global left_turn_lights_state
    global turn_sig_event

    if (channel == left_turn_lights_button):
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

    elif (channel == right_turn_lights_button):
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

    time.sleep(callback_delay_s)



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
                for pin in right_turn_lights:
                    GPIO.output(pin, GPIO.HIGH)
                time.sleep(turn_sig_flashtime_s)
                for pin in right_turn_lights:
                    GPIO.output(pin, GPIO.LOW)
                time.sleep(turn_sig_flashtime_s)

        elif (left_turn_lights_state):
            while (left_turn_lights_state):

                # Flash left LEDs
                for pin in left_turn_lights:
                    GPIO.output(pin, GPIO.HIGH)
                time.sleep(turn_sig_flashtime_s)
                for pin in left_turn_lights:
                    GPIO.output(pin, GPIO.LOW)
                time.sleep(turn_sig_flashtime_s)

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
                GPIO.output(left_blind_spot_light, GPIO.HIGH)
                time.sleep(blind_spot_flashtime_s)
               
                GPIO.output(left_blind_spot_light, GPIO.LOW)

            elif right_turn_lights_state and right_blind_spot_light_state:
                # Flash righ warningt LEDs
                GPIO.output(right_blind_spot_light, GPIO.HIGH)
                time.sleep(blind_spot_flashtime_s)
               
                GPIO.output(right_blind_spot_light, GPIO.LOW)

            # Sleep used for flashing AND not continuously polling blind spots not occupied
            time.sleep(blind_spot_flashtime_s)

        # Set light to solid ON if blind spot still occupied but turn sig off
        if left_blind_spot_light_state:
            GPIO.output(left_blind_spot_light, GPIO.HIGH)
        if right_blind_spot_light_state:
            GPIO.output(right_blind_spot_light, GPIO.HIGH)



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
    GPIO.setup(light_control_pins, GPIO.OUT)

    # Button pins set as input
    GPIO.setup(button_pins, GPIO.IN)
    # ==========================================================

    # Pin Init
    # ===========================================
    for pin in light_control_pins:
        GPIO.output(pin, GPIO.LOW)

    GPIO.add_event_detect(night_lights_button, GPIO.FALLING, callback=toggle_night_lights, bouncetime=bouncetime_ms)
    GPIO.add_event_detect(right_turn_lights_button, GPIO.FALLING, callback=toggle_turn_lights, bouncetime=bouncetime_ms)
    GPIO.add_event_detect(left_turn_lights_button, GPIO.FALLING, callback=toggle_turn_lights, bouncetime=bouncetime_ms)
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
            GPIO.output(left_blind_spot_light, GPIO.LOW)
        else:
            logging.info("Left blind  ON")
            GPIO.output(left_blind_spot_light, GPIO.HIGH)

        left_blind_spot_light_state ^= True

    elif side == "right":
        # If state has not changed, do nothing
        if right_blind_spot_light_state == occupied:
            return

        if right_blind_spot_light_state:
            logging.info("Right blind OFF")
            GPIO.output(right_blind_spot_light, GPIO.LOW)
        else:
            logging.info("Right blind  ON")
            GPIO.output(right_blind_spot_light, GPIO.HIGH)

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

