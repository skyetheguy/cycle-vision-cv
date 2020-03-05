import logging
import threading
import time
import RPi.GPIO as GPIO

    #############################
    ###       CONSTANTS       ###
    #############################

bouncetime_ms = 500
flashtime_s = 0.5
callback_delay_s = 0.5

front_light = 13
rear_light = 18
night_lights = [front_light, rear_light]

night_lights_button = 33

left_turn_front_light = 7
left_turn_rear_light = 12
left_turn_lights = [left_turn_front_light, left_turn_rear_light]
left_turn_lights_button = 35

right_turn_front_light = 11
right_turn_rear_light = 16
right_turn_lights = [right_turn_front_light, right_turn_rear_light]
right_turn_lights_button = 37

left_blind_spot_light = None
right_blind_spot_light = None
blind_spot_lights = [left_blind_spot_light, right_blind_spot_light]

# light_control_pins = night_lights + left_turn_lights + right_turn_lights + blind_spot_lights
# button_pins = [night_lights_button, left_turn_lights_button, right_turn_lights_button]

light_control_pins = night_lights + right_turn_lights + left_turn_lights
button_pins = [night_lights_button, right_turn_lights_button, left_turn_lights_button]


    #############################
    ###        GLOBALS        ###
    #############################

# Events
turn_sig_event = threading.Event()

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

    time.sleep(callback_delay_s)



    #############################
    ###        THREADS        ###
    #############################

# Test thread function
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
                time.sleep(flashtime_s)
                for pin in right_turn_lights:
                    GPIO.output(pin, GPIO.LOW)
                time.sleep(flashtime_s)

        elif (left_turn_lights_state):
            while (left_turn_lights_state):

                # Flash left LEDs
                for pin in left_turn_lights:
                    GPIO.output(pin, GPIO.HIGH)
                time.sleep(flashtime_s)
                for pin in left_turn_lights:
                    GPIO.output(pin, GPIO.LOW)
                time.sleep(flashtime_s)


    #############################
    ###        PUBLIC         ###
    #############################

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
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    

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

