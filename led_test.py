from time import sleep
import RPi.GPIO as GPIO

# unused in this script (might need rewiring as it runs from output to ground, needs input?)
button_pin = 12  

leds_top_left_pins  = [16, 20, 21]
leds_top_right_pins = [13, 19 ,26]

left_led_pins  = [7, 8, 25, 24, 23, 18, 15, 14, 4]
right_led_pins = [6, 5, 11, 9,  10, 22, 27, 17]

all_led_pins = [
    leds_top_left_pins,
    leds_top_right_pins,
    left_led_pins,
    right_led_pins,
]

GPIO.setmode(GPIO.BOARD)

# set all pins as output pins
for pin_list in all_led_pins:
    for pin_number in pin_list:
        GPIO.setup(pin_number, GPIO.OUT)

try:  
    while True:  
        # for every pin
        for pin_list in all_led_pins:
            for pin_number in pin_list:
                # turn on for 0.2 second
                GPIO.output(pin_number, 1)  
                sleep(0.5)
                GPIO.output(pin_number, 0)
                sleep(0.5)
                
except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()                 # resets all GPIO ports used by this program  