import logging
import threading
import time
import RPi.GPIO as GPIO

# state_1 = False
# state_changed_event = threading.Event()
# led_pin = 12
# but_pin = 18

front_light = 13
rear_light = 18
night_lights = [front_light, rear_light]
night_lights_state = False
night_lights_button = 33

left_turn_front_light = None
left_turn_rear_light = None
left_turn_lights = [left_turn_front_light, left_turn_rear_light]
left_turn_lights_state = False
left_turn_lights_button = None

right_turn_front_light = None
right_turn_rear_light = None
right_turn_lights = [right_turn_front_light, right_turn_rear_light]
right_turn_lights_state = False
right_turn_lights_button = None

left_blind_spot_light = None
left_blind_spot_light_state = False
right_blind_spot_light = None
right_blind_spot_light_state = False
blind_spot_lights = [left_blind_spot_light, right_blind_spot_light]

# light_control_pins = night_lights + left_turn_lights + right_turn_lights + blind_spot_lights
# button_pins = [night_lights_button, left_turn_lights_button, right_turn_lights_button]

light_control_pins = night_lights
button_pins = [night_lights_button]

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


# Toggle right front and rear turn lights callback
def toggle_right_turn_lights(channel):
    global right_turn_lights_state

    if right_turn_lights_state:
        logging.info("Right turn sig OFF")

        right_turn_lights_state ^= True
    else:
        logging.info("Right turn sig ON")

        right_turn_lights_state ^= True
        while (right_turn_lights_state):
            # Flash lights
            for pin in right_turn_lights:
                GPIO.output(pin, GPIO.HIGH)
            time.sleep(1)
            for pin in right_turn_lights:
                GPIO.output(pin, GPIO.LOW)
            time.sleep(1)


# Toggle left front and rear turn lights callback
def toggle_left_turn_lights(channel):
    global left_turn_lights_state

    if left_turn_lights_state:
        logging.info("left turn sig OFF")

        left_turn_lights_state ^= True
    else:
        logging.info("left turn sig ON")

        left_turn_lights_state ^= True
        while (left_turn_lights_state):
            # Flash lights
            for pin in left_turn_lights:
                GPIO.output(pin, GPIO.HIGH)
            time.sleep(1)
            for pin in left_turn_lights:
                GPIO.output(pin, GPIO.LOW)
            time.sleep(1)

def init():
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

    GPIO.add_event_detect(night_lights_button, GPIO.FALLING, callback=toggle_night_lights, bouncetime=100)
    # GPIO.add_event_detect(left_turn_lights_button, GPIO.FALLING, callback=toggle_right_turn_lights, bouncetime=100)
    # GPIO.add_event_detect(right_turn_lights_button, GPIO.FALLING, callback=toggle_left_turn_lights, bouncetime=100)
    # ===========================================


# # Test thread function
# def thread_function(name):
#     # logging.info("Thread %s: starting", name)

#     while(True):
#         state_changed_event.wait()
#         state_changed_event.clear()

#         if(state_1):
#             GPIO.output(led_pin, GPIO.HIGH)
#         else:
#             GPIO.output(led_pin, GPIO.LOW)
    
#     # logging.info("Thread %s: finishing", name)

# # Test interrupt callback
# def interrupt_callback(channel):
#     global state_1

#     print("Changed state")
#     state_1 ^= True
#     print(state_1)
#     state_changed_event.set()



def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    # # Pin Setup
    # # ==========================================================
    # GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
    # GPIO.setup(led_pin, GPIO.OUT)  # LED pins set as output
    # GPIO.setup(but_pin, GPIO.IN)  # button pin set as input
    # # ==========================================================

    # # Pin Init
    # # ==========================================================
    # GPIO.output(led_pin, GPIO.LOW)
    # GPIO.add_event_detect(but_pin, GPIO.FALLING, callback=interrupt_callback, bouncetime=100)
    # # ==========================================================

    # # Set state to "Nothing"
    # state_changed_event.clear()

    init()

    try:
        logging.info("Starting test")
        # thread = threading.Thread(target=thread_function, args=(1,))
        # logging.info("Main    : before running thread")
        # thread.start()
        # logging.info("Main    : wait for the thread to finish")
        
        while(1):
            print("Doing nothing")
            time.sleep(2)

        # thread.join()
        # logging.info("Main    : all done")

    finally:
        GPIO.cleanup()



if __name__ == '__main__':
    main()

