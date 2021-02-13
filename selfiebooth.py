import os
import platform
from datetime import datetime

import pygame
import pygame.camera

# Edit /home/pi/.config/autostart/PiCube.desktop to fix autostarting

is_running_on_pi = platform.uname()[0] != 'Windows'
if is_running_on_pi:
    import RPi.GPIO as GPIO
    input_pin = 3
    output_pin = 5

    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(output_pin, GPIO.OUT)
    GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

text_color = (0, 255, 0)
countdown_length = 4
display_result_length = 4


class CameraSprite(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        pygame.sprite.Sprite.__init__(self, allsprites)

        self.will_capture = True

        pygame.camera.init()
        cameras = pygame.camera.list_cameras()
        self.webcam = pygame.camera.Camera(cameras[0])
        self.webcam.start()

        # grab first frame
        self.real_image = self.webcam.get_image()

        IMG_WIDTH = self.real_image.get_width()
        IMG_HEIGHT = self.real_image.get_height()

        print('Preparing image scaling for performance increase...')
        panel_height = WINDOW_HEIGHT * 0.8  # Height can't be more than 80%
        # how many times does original image fit in height? Width times THAT
        panel_width = IMG_WIDTH * (panel_height / IMG_HEIGHT)
        self.panel_height = int(panel_height)
        self.panel_width = int(panel_width)

        # create big img size for fast scaling
        self.image = pygame.transform.scale(
            self.real_image,
            (self.panel_width, self.panel_height),
        )

        BIG_IMG_WIDTH = self.image.get_width()
        BIG_IMG_HEIGHT = self.image.get_height()

        self.pos = (
            WINDOW_WIDTH/2 - BIG_IMG_WIDTH / 2,
            WINDOW_HEIGHT/2 - BIG_IMG_HEIGHT / 2
        )
        self.rect = (self.pos, self.image.get_size())

        print('Image scaling...')

    def get_image(self):
        return self.real_image

    def update(self):
        self.real_image = self.webcam.get_image(self.real_image)
        # draw webcam feed
        self.image = pygame.transform.scale(
            self.real_image,
            (
                self.panel_width,
                self.panel_height,
            ),
            self.image
        )
        return self.image

    def get_panel_size(self):
        IMG_WIDTH = self.image.get_width()
        IMG_HEIGHT = self.image.get_height()

        print('Preparing image scaling for performance increase...')
        panel_height = WINDOW_HEIGHT * 0.8  # Height can't be more than 80%
        # how many times does original image fit in height? Width times THAT
        panel_width = IMG_WIDTH * (panel_height / IMG_HEIGHT)
        self.panel_height = int(panel_height)
        self.panel_width = int(panel_width)
        return self.panel_width, self.panel_height


# TODO move bg image according to scale (center cutoffs)

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

    def change_font(self, font_size):
        self.font = pygame.font.Font(None, font_size)

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

    # scale to height
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

    bg.blit(
        panel,
        (
            WINDOW_WIDTH / 2 - panel.get_width() / 2,
            WINDOW_HEIGHT / 2 - panel.get_height() / 2,
        )
    )

    # header_intro_font = pygame.font.Font(None, 50)
    # header_intro_text = header_intro_font.render("Welcome to the", 1, text_color)
    # bg.blit(
    #     header_intro_text,
    #     (
    #         WINDOW_WIDTH / 2 - header_intro_text.get_width() / 2,
    #         10
    #     )
    # )

    header_main_font = pygame.font.Font(None, 120)
    header_main_text = header_main_font.render("Selfie Booth!", 1, text_color)
    bg.blit(
        header_main_text,
        (
            WINDOW_WIDTH / 2 - header_main_text.get_width() / 2,
            10
        )
    )

    bg.convert()

    return bg


def main():
    print('Starting selfie booth...')
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Selfie Booth")

    allsprites = pygame.sprite.Group()

    global WINDOW_WIDTH
    WINDOW_WIDTH = screen.get_width()
    global WINDOW_HEIGHT
    WINDOW_HEIGHT = screen.get_height()

    print('Screen resolution is (w h)', WINDOW_WIDTH, WINDOW_HEIGHT)

    print('Opening camera ...')
    webcam = CameraSprite(allsprites)

    print('Image loading succesful')

    panel_width, panel_height = webcam.get_panel_size()
    border_size = 20
    # +10 pixels on both sides to create a border
    panel = pygame.Surface(
        (panel_width + border_size, panel_height + border_size))
    panel.fill((255, 0, 0))

    print('Completing setup...')

    screen_text = ScreenText(allsprites, '', 120)
    countdown_text = ScreenText(allsprites, '', 200)

    background = get_background(panel)

    state = 'idle'

    time_button_pressed = 0
    time_pic_taken = 0

    screen.blit(background, (0, 0))

    print('Setup complete. Starting main loop.')
    print('Have a good day! :)')
    while True:
        event_list = pygame.event.get()

        # Show a countdown to the user
        if state == 'countdown':
            # wait untill countdown_length seconds have passed
            if pygame.time.get_ticks() > (time_button_pressed + (countdown_length * 1000)):
                countdown_text.change_pos((-1000, -1000))
                screen_text.change_text('Great picture?')
                screen_text.pos_to_center(0, (WINDOW_HEIGHT * 0.8) / 2)
                time_pic_taken = pygame.time.get_ticks()
                # actually save picture here

                filename = 'image_' + \
                    str(datetime.now().strftime('%Y%m%d_%H%M%S')) + '.jpg'
                fullname = os.path.join(get_main_dir(), 'images', filename)
                pygame.image.save(webcam.real_image, fullname)

                state = 'result'
            else:
                timer_text = str(int(
                    countdown_length -
                    ((pygame.time.get_ticks() - time_button_pressed) / 1000)
                ))

                if timer_text == '0':
                    timer_text = 'Smile!'

                countdown_text.change_text(timer_text)
                countdown_text.pos_to_center(0, 100)

        # Display the picture taken to the user
        elif state == 'result':
            #
            if pygame.time.get_ticks() > (time_pic_taken + (display_result_length * 1000)):
                # enough time has passed
                screen_text.change_pos((-1000, -1000))
                state = 'idle'
            else:
                pass

        # Default state: waiting for interaction
        elif state == 'idle':
            # Only receive events while idling
            for e in event_list:
                if e.type == pygame.QUIT or (e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE):
                    exit()
                if e.type == pygame.KEYUP and e.key == pygame.K_p:
                    screen_text.change_text('Get ready')
                    screen_text.pos_to_center(0, -200)
                    countdown_text.pos_to_center(0, 100)
                    time_button_pressed = pygame.time.get_ticks()
                    state = 'countdown'
            if is_running_on_pi and GPIO.input(input_pin) == 0:
                screen_text.change_text('Get ready')
                screen_text.pos_to_center(0, -200)
                countdown_text.pos_to_center(0, 100)
                time_button_pressed = pygame.time.get_ticks()
                state = 'countdown'

        # dont do this while showing result
        if state is not 'result':
            webcam.update()

        allsprites.draw(screen)
        pygame.display.update(webcam.rect)


if __name__ == "__main__":
    main()
