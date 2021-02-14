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

# https://rgbcolorcode.com/
text_color = (0, 136, 204)
border_color = (0, 136, 204)
countdown_length = 4 * 1000
display_result_length = 4 * 1000


class CameraSprite(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        pygame.sprite.Sprite.__init__(self, allsprites)

        # flag to not update screen while in 'result' state
        self.will_capture = True

        pygame.camera.init()
        cameras = pygame.camera.list_cameras()
        self.webcam = pygame.camera.Camera(cameras[0], (1280, 960))
        self.webcam.start()

        # grab first frame
        self.image = self.webcam.get_image()

        self.IMG_WIDTH, self.IMG_HEIGHT = self.image.get_size()

        self.pos = (
            WINDOW_WIDTH/2 - self.IMG_WIDTH / 2,
            WINDOW_HEIGHT/2 - self.IMG_HEIGHT / 2
        )
        self.rect = (self.pos, self.image.get_size())

    def update(self):
        self.image = self.webcam.get_image(self.image)
        return self.image

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

    panel = webcam.get_panel()

    screen_text = ScreenText(allsprites, 'PLACEHOLDER', 120)
    countdown_text = ScreenText(allsprites, 'PLACEHOLDER', 200)

    background = get_background(panel)

    state = 'idle'

    btn_time = pygame.time.get_ticks()
    pic_time = pygame.time.get_ticks()

    screen.blit(background, (0, 0))

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
            new_pic_time = pygame.time.get_ticks()
            # actually save picture here

            filename = 'image_' + \
                str(datetime.now().strftime('%Y%m%d_%H%M%S')) + '.jpg'
            fullname = os.path.join(get_main_dir(), 'images', filename)
            pygame.image.save(webcam.image, fullname)
        elif new_state == 'idle':
            screen_text.change_pos((-1000, -1000))
        else:
            print('Undefined state encountered!', new_state)
            exit()

        return new_state, new_btn_time, new_pic_time

    print('Setup complete. Starting main loop.')
    while True:
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
            webcam.update()

        allsprites.draw(screen)
        pygame.display.update(webcam.rect)


if __name__ == "__main__":
    main()
