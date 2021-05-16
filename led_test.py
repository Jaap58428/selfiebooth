from time import sleep
import RPi.GPIO as GPIO

# unused in this script (might need rewiring as it runs from output to ground, needs input?)
button_pin = 32

leds_top_left_pins  = [36, 38, 40]
leds_top_right_pins = [33, 35, 37]

left_led_pins  = [31, 29, 23, 21, 19, 15, 13, 11]
right_led_pins = [26, 24, 22, 18, 16, 12, 10, 8, 7]

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
        print('Setting pin number: ' + str(pin_number))
        GPIO.setup(pin_number, GPIO.OUT)

print('Now all leds should blink after each other for 0.2 seconds...')
try:  
    while True:  
        # for every pin after each other
        for pin_list in all_led_pins:
            for pin_number in pin_list:
                # turn on for 0.2 second
                GPIO.output(pin_number, 1)  
                sleep(0.2)
                GPIO.output(pin_number, 0)
        
        # turn on all pins
        for pin_list in all_led_pins:
            for pin_number in pin_list:
                GPIO.output(pin_number, 1)

        sleep(0.5)

        for pin_list in all_led_pins:
            for pin_number in pin_list:
                GPIO.output(pin_number, 0)

        sleep(0.5)        
        # turn on all pins
        for pin_list in all_led_pins:
            for pin_number in pin_list:
                GPIO.output(pin_number, 1)

        sleep(0.5)

        for pin_list in all_led_pins:
            for pin_number in pin_list:
                GPIO.output(pin_number, 0)

        sleep(0.5)
                
except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()                 # resets all GPIO ports used by this program  