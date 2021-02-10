from datetime import datetime
import os, pygame
import pygame.camera


class ScreenText(pygame.sprite.Sprite):
    def __init__(self, allsprites, text):
        pygame.sprite.Sprite.__init__(self, allsprites)

        self.text = text

        self.font = pygame.font.Font(None, 36)
        self.image = self.font.render(self.text, 1, (255, 255, 255))
        self.pos = (100, 100)  # Set the location of the text
        self.rect = (self.pos, self.image.get_size())

    def update(self):
        self.image = self.font.render(self.text, 1, (255, 255, 255))

    def change_text(self, new_text):
        self.text = new_text


def get_picture():
    camera_resolution = '1280x720'
    filename = 'image_' + str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
    # example: fswebcam -r 1280x720 --na-banner image_2021-02-10_14:57:54
    command = 'fswebcam -r {s_resolution} --na-banner {s_filename}'.format(s_resolution = camera_resolution, s_filename = filename)
    return command


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Selfie Booth")

    allsprites = pygame.sprite.Group()

    SCREEN_HEIGHT = screen.get_height()
    SCREEN_WIDTH = screen.get_width()
    
    pygame.camera.init()
    cameras = pygame.camera.list_cameras()
    webcam = pygame.camera.Camera(cameras[0])
    webcam.start()

    # grab first frame
    img = webcam.get_image()

    IMG_WIDTH = img.get_width()
    IMG_HEIGHT = img.get_height()

    screen_text = ScreenText(allsprites, 'testtesttest')

    running = True
    while running:
        for e in pygame.event.get() :
            if e.type == pygame.QUIT :
                sys.exit()

        temp_string = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        screen_text.change_text(str(temp_string))

        # draw webcam feed
        # screen.blit(img, (
        #     SCREEN_WIDTH/2 - IMG_WIDTH / 2,
        #     SCREEN_HEIGHT/2 - IMG_HEIGHT / 2)
        # )
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.update()
        # grab next frame    
        img = webcam.get_image()


    # os.system(command)
    # get_picture()
    


if __name__ == "__main__":
    main()
