import logging
import threading
import time
import RPi.GPIO as GPIO

state_1 = False
state_changed_event = threading.Event()
led_pin = 12
but_pin = 18

# Test thread function
def thread_function(name):
    # logging.info("Thread %s: starting", name)

    while(True):
        state_changed_event.wait()
        state_changed_event.clear()

        if(state_1):
            GPIO.output(led_pin, GPIO.HIGH)
        else:
            GPIO.output(led_pin, GPIO.LOW)
    
    # logging.info("Thread %s: finishing", name)

# Test interrupt callback
def interrupt_callback(channel):
    global state_1

    print("Changed state")
    state_1 ^= True
    print(state_1)
    state_changed_event.set()



def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    # Pin Setup
    # ==========================================================
    GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
    GPIO.setup(led_pin, GPIO.OUT)  # LED pins set as output
    GPIO.setup(but_pin, GPIO.IN)  # button pin set as input
    # ==========================================================

    # Pin Init
    # ==========================================================
    GPIO.output(led_pin, GPIO.LOW)
    GPIO.add_event_detect(but_pin, GPIO.FALLING, callback=interrupt_callback, bouncetime=100)
    # ==========================================================

    # Set state to "Nothing"
    state_changed_event.clear()

    try:
        logging.info("Main    : before creating thread")
        thread = threading.Thread(target=thread_function, args=(1,))
        logging.info("Main    : before running thread")
        thread.start()
        logging.info("Main    : wait for the thread to finish")
        
        while(1):
            print("Doing nothing")
            time.sleep(2)

        thread.join()
        logging.info("Main    : all done")

    finally:
        GPIO.cleanup()



if __name__ == '__main__':
    main()

