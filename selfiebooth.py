import os
import platform
from datetime import datetime
import time

import pygame
import pygame.camera

# https://rgbcolorcode.com/
text_color = (0, 136, 204)
border_color = (0, 136, 204)
countdown_length = 4 * 1000
display_result_length = 4 * 1000

# These can easily be found out by using the res_check.py script
possible_resolutions = [
    (160, 120),
    (176, 144),
    (544, 288),
    (320, 176),
    (320, 240),
    (432, 240),
    (352, 288),
    (640, 360),
    (800, 448),
    (640, 480),
    (864, 480),
    (800, 600),  # [-7] or [11]
    (960, 544),
    (1024, 576),
    (960, 720),
    (1184, 656),
    (1280, 720),
    (1280, 960),  # [-1] or [17]
]

# Beware of choosing higher resolutions as this might slow the script down
# If a laggy system is okay for you, go ahead. If you want a more responsive system keep it lower
camera_resolution = possible_resolutions[-1]

# Edit /home/pi/.config/autostart/PiCube.desktop to fix autostarting
is_running_on_pi = platform.uname()[0] != 'Windows'
if is_running_on_pi:
    import RPi.GPIO as GPIO
    button_pin = 32

    leds_top_left_pins  = [36, 38, 40]
    leds_top_right_pins = [33, 35, 37]
    leds_top_max_index = len(leds_top_left_pins) - 1

    left_led_pins  = [31, 29, 23, 21, 19, 15, 13, 11]
    left_led_max_index = len(left_led_pins) - 1
    
    right_led_pins = [26, 24, 22, 18, 16, 12, 10, 8, 7]
    right_led_max_index = len(right_led_pins) - 1

    max_indexi = [leds_top_max_index, left_led_max_index, right_led_max_index]

    all_led_pins = [
        leds_top_left_pins,
        leds_top_right_pins,
        left_led_pins,
        right_led_pins,
    ]

    GPIO.setmode(GPIO.BOARD)

    print('Setting pin numbers...')
    # set all pins as output pins
    for pin_list in all_led_pins:
        for pin_number in pin_list:
            GPIO.setup(pin_number, GPIO.OUT)


class CameraSprite(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        # include this sprite in updated sprites
        pygame.sprite.Sprite.__init__(self, allsprites)

        self.pic_save_directory = os.path.join(get_main_dir(), 'images')

        # flags to not update screen while in 'result' state
        self.will_capture = True
        self.will_save = False

        # Initialize pygame camera object (from any available camera device)
        pygame.camera.init()
        
        # I thought about make a catch for if no camera was found.
        # This didn't work how i'd like and if non is found it just throws a segmentation  fault
        cameras = pygame.camera.list_cameras()
        
        # Set camera variables and start the device
        self.webcam = pygame.camera.Camera(cameras[0], camera_resolution)
        self.webcam.start()
        
        # grab first frame
        self.image = self.webcam.get_image()

        # Get size, save and calculate position on window based of this
        self.IMG_WIDTH, self.IMG_HEIGHT = self.image.get_size()
        self.pos = (
            WINDOW_WIDTH/2 - self.IMG_WIDTH / 2,
            WINDOW_HEIGHT/2 - self.IMG_HEIGHT / 2
        )
        self.rect = (self.pos, self.image.get_size())

    # Every sprite update another screengrab is done
    def update(self):
        self.image = self.webcam.get_image(self.image)

    def save_image(self):
        filename = 'image_' + \
            str(datetime.now().strftime('%Y%m%d_%H%M%S')) + '.jpg'
        fullname = os.path.join(self.pic_save_directory, filename)
        pygame.image.save(self.image, fullname)

        self.will_save = False  # reset flag so no save will be done on next scriptloop

    def get_panel(self, border_size=40):
        panel = pygame.Surface((
            self.IMG_WIDTH + border_size,
            self.IMG_HEIGHT + border_size
        ))
        panel.fill(border_color)

        return panel


class ScreenText(pygame.sprite.Sprite):
    def __init__(self, allsprites, text, initial_font_size):
        pygame.sprite.Sprite.__init__(self, allsprites)

        self.text = text

        self.font = pygame.font.Font(None, initial_font_size)
        self.image = self.font.render(self.text, 1, text_color)
        self.pos = (-1000, -1000)  # Set the location of the text
        self.rect = (self.pos, self.image.get_size())

    def update(self):
        pass

    def change_text(self, new_text):
        self.text = new_text
        self.image = self.font.render(self.text, 1, text_color)
        self.rect = (self.pos, self.image.get_size())

    def change_pos(self, new_pos):
        self.pos = (new_pos)
        self.rect = (self.pos, self.image.get_size())

    def pos_to_center(self, offset_h=0, offset_v=0):
        self.pos = (
            WINDOW_WIDTH / 2 - self.image.get_width() / 2 + offset_h,
            WINDOW_HEIGHT / 2 - self.image.get_height() / 2 + offset_v
        )
        self.rect = (self.pos, self.image.get_size())


def get_main_dir():
    return os.path.split(os.path.abspath(__file__))[0]


def get_background(panel):

    fullname = os.path.join(get_main_dir(), 'background.png')
    try:
        bg_image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        exit()
    bg_image = bg_image.convert()

    bg = bg_image

    # TODO this is currently floating left and/or top, rather have it centered?
    # other solution would be to take an bg image which doesn't get affected by warping

    # Below is almost equal to CSS's object-fit: contain
    # if the aspect ratio is narrower than the screen
    if (bg.get_width() * (WINDOW_HEIGHT / bg.get_height())) <= WINDOW_WIDTH:
        # scale to width and lose some content top and bottom
        bg_w = WINDOW_WIDTH
        bg_h = bg.get_height() * (WINDOW_WIDTH / bg.get_width())
    # else if it's wider than the screen
    else:
        # scale to height and lose some content left and right
        bg_h = WINDOW_HEIGHT
        bg_w = bg.get_width() * (WINDOW_HEIGHT / bg.get_height())

    bg_w = int(bg_w)
    bg_h = int(bg_h)

    bg = pygame.transform.scale(
        bg,
        (bg_w, bg_h),
    )

    # include the webcam border in the background for optimalisation, these pixels don't need regular updating
    # It is currently simply centered. If changed consider that the camera_sprite also needs adjusting
    bg.blit(
        panel,
        (
            WINDOW_WIDTH / 2 - panel.get_width() / 2,
            WINDOW_HEIGHT / 2 - panel.get_height() / 2,
        )
    )

    # I excluded this for now, as it might be pretty obvious from the instalation as a whole
    # also, sometimes this overlapped with the camera so this is a bit safer
    # header_main_font = pygame.font.Font(None, 120)
    # header_main_text = header_main_font.render("Selfie Booth!", 1, text_color)
    # bg.blit(
    #     header_main_text,
    #     (
    #         WINDOW_WIDTH / 2 - header_main_text.get_width() / 2,
    #         10
    #     )
    # )

    bg.convert()

    return bg


def update_all_leds(led_state):
    # if its not yet time to update return unchanged state
    if pygame.time.get_ticks() - led_state[0] > 2000:
        return led_state

    leds_indexi = led_state[1]

    # loop through led indixi
    # use range as it also applies to max_indixi
    for i in range(3):
        # turn on last/current led
        GPIO.output(leds_indexi[i], 1)

        # update led index
        if leds_indexi[i] < max_indexi[i]:
            leds_indexi[i] += 1
        else:
            leds_indexi[i] = 0

        # turn off the next led
        GPIO.output(leds_indexi[i], 0)

    return [pygame.time.get_ticks(), leds_indexi]


def main():
    print('Starting selfie booth...')

    if is_running_on_pi:
        print('Turning on all leds...')
        for pin_list in all_led_pins:
            for pin_number in pin_list:
                GPIO.output(pin_number, 1)


    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # set to fullscreen
    pygame.display.set_caption("Selfie Booth")

    # Create sprites group
    allsprites = pygame.sprite.Group()

    # get and save screen size globally
    global WINDOW_WIDTH
    WINDOW_WIDTH = screen.get_width()
    global WINDOW_HEIGHT
    WINDOW_HEIGHT = screen.get_height()

    print('Screen resolution is (w h)', WINDOW_WIDTH, WINDOW_HEIGHT)

    # Create the camera sprite, every tick/update this updates
    print('Opening camera ...')
    camera_sprite = CameraSprite(allsprites)

    # panel is the surface the camera_sprite is blit on to seem like its a border
    panel = camera_sprite.get_panel()

    screen_text = ScreenText(allsprites, '', 120)
    countdown_text = ScreenText(allsprites, '', 200)

    background = get_background(panel)

    state = 'idle'

    btn_time = pygame.time.get_ticks()
    pic_time = pygame.time.get_ticks()

    last_led_update_time = pygame.time.get_ticks()
    leds_indexi = [0, 0, 0]

    led_state = [last_led_update_time, leds_indexi]

    screen.blit(background, (0, 0))

    # define state switcher function (only used in main)
    def switch_state(new_state, new_btn_time, new_pic_time):
        if new_state == 'countdown':
            screen_text.change_text('Get ready')
            screen_text.pos_to_center(0, -200)
            countdown_text.pos_to_center(0, 100)
            new_btn_time = pygame.time.get_ticks()
        elif new_state == 'result':
            countdown_text.change_pos((-1000, -1000))
            screen_text.change_text('Great picture?')
            screen_text.pos_to_center(
                0, (WINDOW_HEIGHT * 0.7) / 2)  # 70% from top
            camera_sprite.will_save = True
            new_pic_time = pygame.time.get_ticks()
        elif new_state == 'idle':
            countdown_text.change_pos((-1000, -1000))
            screen_text.change_pos((-1000, -1000))
        else:
            print('Undefined state encountered!', new_state)
            exit()

        return new_state, new_btn_time, new_pic_time

    py_clock = pygame.time.Clock()

    print('Setup complete. Starting main loop.')
    while True:
        # Limit to 60fps to save pi from throtling on high temps
        py_clock.tick(60)

        if is_running_on_pi:
            led_state = update_all_leds(led_state)

        event_list = pygame.event.get()

        # Show a countdown to the user
        if state == 'countdown':
            # wait untill countdown_length seconds have passed
            if pygame.time.get_ticks() > (btn_time + countdown_length):

                state, btn_time, pic_time = switch_state(
                    'result', btn_time, pic_time)
            else:
                timer_text = str(
                    int(
                        (countdown_length - (pygame.time.get_ticks() - btn_time)) / 1000
                    )
                )
                if timer_text == '0':
                    timer_text = 'Smile!'
                countdown_text.change_text(timer_text)
                countdown_text.pos_to_center(0, 100)

        # Display the picture taken to the user
        elif state == 'result':
            # if enough time has passed
            if pygame.time.get_ticks() > (pic_time + display_result_length):
                state, btn_time, pic_time = switch_state(
                    'idle', btn_time, pic_time)

        # Default state: waiting for interaction
        elif state == 'idle':
            # Only receive events while idling
            for e in event_list:
                if e.type == pygame.QUIT or (e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE):
                    exit()
                if e.type == pygame.KEYUP and e.key == pygame.K_p:
                    state, btn_time, pic_time = switch_state(
                        'countdown', btn_time, pic_time)
            if is_running_on_pi and GPIO.input(input_pin) == 0:
                state, btn_time, pic_time = switch_state(
                    'countdown', btn_time, pic_time)

        # dont do this while showing result
        if state is not 'result':
            camera_sprite.update()

        allsprites.draw(screen)
        pygame.display.update(camera_sprite.rect)

        # do this after a screen render to clean up text changes before halting
        if camera_sprite.will_save:
            now = datetime.now()  # see print below
            camera_sprite.save_image()

            # This print is included to see monitor performance 
            print('Taking picture took:', datetime.now() - now)


if __name__ == "__main__":
    main()
