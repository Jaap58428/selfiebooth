from datetime import datetime
import os, pygame
import pygame.camera

text_color = (0,255,0)
countdown_length = 4

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
        self.image = self.font.render(self.text, 1, text_color)
        self.rect = (self.pos, self.image.get_size())

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
            pygame.display.get_window_size()[0] / 2 - self.image.get_width() / 2 + offset_h,
            pygame.display.get_window_size()[1] / 2 - self.image.get_height() / 2 + offset_v
        )
        self.rect = (self.pos, self.image.get_size())


def get_picture():
    camera_resolution = '1280x720'
    filename = 'image_' + str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
    # example: fswebcam -r 1280x720 --na-banner image_2021-02-10_14:57:54
    command = 'fswebcam -r {s_resolution} --na-banner {s_filename}'.format(s_resolution = camera_resolution, s_filename = filename)
    # os.system(command)
    


def is_running_on_rpi():
    return platform.uname()[0] != 'Windows'


def get_main_dir():
    return os.path.split(os.path.abspath(__file__))[0]


# loads image resources, takes a filename as arg
# when colorkey has argument -1 the background will be made transparant based of topleft pixel
def load_image(name, colorkey=None):
    fullname = os.path.join(get_main_dir(), name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image


def get_background(panel):

    fullname = os.path.join(get_main_dir(), 'inside_temp.png')
    try:
        bg_image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    bg_image = bg_image.convert()

    bg = bg_image

    # scale to height
    screen_width, screen_height = pygame.display.get_window_size()
    # if the aspect ratio is narrower than the screen
    if (bg.get_width() * (screen_height / bg.get_height())) <= screen_width:
        # scale to width and lose some content top and bottom
        bg_w = screen_width
        bg_h = bg.get_height() * (screen_width / bg.get_width())
    # else if it's wider than the screen
    else:
        #scale to height and lose some content left and right
        bg_h = screen_height
        bg_w = bg.get_width() * (screen_height / bg.get_height())

    bg_w = int(bg_w)
    bg_h = int(bg_h)
    
    bg = pygame.transform.scale(
        bg,
        (bg_w, bg_h),
    )

    bg.blit(
        panel,
        (
            pygame.display.get_window_size()[0] / 2 - panel.get_width() / 2,
            pygame.display.get_window_size()[1] / 2 - panel.get_height() / 2,
        )
    )

    header_intro_font = pygame.font.Font(None, 50)
    header_intro_text = header_intro_font.render("Welcome to the", 1, text_color)
    bg.blit(
        header_intro_text, 
        (
            pygame.display.get_window_size()[0] / 2 - header_intro_text.get_width() / 2,
            # (pygame.display.get_window_size()[1] / 100) * 5 # 20% height
            10
        )
    )

    header_main_font = pygame.font.Font(None, 120)
    header_main_text = header_main_font.render("Selfie Booth!", 1, text_color)
    bg.blit(
        header_main_text, 
        (
            pygame.display.get_window_size()[0] / 2 - header_main_text.get_width() / 2,
            # (pygame.display.get_window_size()[1] / 100) * 5 + 40 # 20% height
            50
        )
    )

    # header_main_font = pygame.font.Font(None, 120)
    # header_main_text = header_main_font.render("Selfie Booth!", 1, text_color)
    # bg.blit(
    #     header_main_text, 
    #     (
    #         pygame.display.get_window_size()[0] / 2 - header_main_text.get_width() / 2,
    #         # (pygame.display.get_window_size()[1] / 100) * 5 + 40 # 20% height
    #         50
    #     )
    # )

    bg.convert()

    return bg


def resize_img(img, width, height, big_img):
    new_img = pygame.transform.scale(
        img,
        (width, height),
        big_img
    )

    return new_img

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Selfie Booth")

    allsprites = pygame.sprite.Group()

    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    pygame.camera.init()
    cameras = pygame.camera.list_cameras()
    webcam = pygame.camera.Camera(cameras[0])
    webcam.start()

    # grab first frame
    img = webcam.get_image()

    IMG_WIDTH = img.get_width()
    IMG_HEIGHT = img.get_height()

    # TODO make a panel (about 75% of screen size) to display the camera field in
    # this way we prevent warping of the original aspect ratio

    """
        final image cant be bigger than 80% of screen height
        
    """
    panel_height = SCREEN_HEIGHT * 0.8 # Height can't be more than 80%
    # how many times does original image fit in height? Width times THAT
    panel_width = IMG_WIDTH * (panel_height / IMG_HEIGHT)
    panel_height = int(panel_height)
    panel_width = int(panel_width)

    border_size = 20
    panel = pygame.Surface((panel_width + border_size, panel_height + border_size)) # +10 pixels on both sides to create a border
    panel.fill((255,0,0))

    # create big img size for fast scaling
    big_img = pygame.transform.scale(
        img,
        (panel_width, panel_height),
    )
    BIG_IMG_WIDTH = big_img.get_width()
    BIG_IMG_HEIGHT = big_img.get_height()

    screen_text = ScreenText(allsprites, '', 120)
    countdown_text = ScreenText(allsprites, '', 200)

    background = get_background(panel)

    state = 'idle'

    time_button_pressed = 0

    running = True
    while running:
        # clear screen
        screen.blit(background, (0,0))

        event_list = pygame.event.get()
        
        # Show a countdown to the user
        if state == 'countdown':
            # wait untill countdown_length seconds have passed
            if pygame.time.get_ticks() > (time_button_pressed + (countdown_length * 1000)):
                print('picture now!')
                screen_text.change_pos((-1000, -1000))
                countdown_text.change_pos((-1000, -1000))
                state = 'result'
            else: 
                timer_text = str(int(
                    countdown_length - ((pygame.time.get_ticks() - time_button_pressed) / 1000)
                ))

                if timer_text == '0':
                    timer_text = 'Smile!'

                countdown_text.change_text(timer_text)
                countdown_text.pos_to_center(0, 100)
                
                

        # Display the picture taken to the user
        elif state == 'result':
            # TODO
            print('display result for XX seconds')
            state = 'idle'

        # Default state: waiting for interaction
        elif state == 'idle': 
            # Only receive events while idling
            for e in event_list:
                if e.type == pygame.QUIT :
                    sys.exit()
                if e.type == pygame.KEYUP and e.key == pygame.K_p:
                    screen_text.change_text('Get ready')
                    screen_text.pos_to_center(0, -200)
                    countdown_text.pos_to_center(0, 100)
                    time_button_pressed = pygame.time.get_ticks()
                    state = 'countdown'

        

        # grab next frame    
        img = webcam.get_image()
        resized_img = resize_img(img, panel_width, panel_height, big_img)

        # draw webcam feed
        screen.blit(
            resized_img, 
            (
                SCREEN_WIDTH/2 - BIG_IMG_WIDTH / 2, 
                SCREEN_HEIGHT/2 - BIG_IMG_HEIGHT / 2
            )
        )
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    main()
