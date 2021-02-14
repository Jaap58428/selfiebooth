# Based of https://makersportal.com/blog/2019/4/21/image-processing-using-raspberry-pi-and-python

# import pygame.camera
import cv2
import numpy as np
import matplotlib.pyplot as plt

# pygame.camera.init()
# cameras = pygame.camera.list_cameras()
# webcam = pygame.camera.Camera(cameras[0])
# webcam.start()

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(width, height)

rval, frame = cap.read()
# print(rval)

# print(frame)

# img = webcam.get_image()

# cam_res = img.get_size()

# print(webcam.query_image())

# h = 1024 # change this to anything < 2592 (anything over 2000 will likely get a memory error when plotting
# cam_res = (int(h),int(0.75*h)) # keeping the natural 3/4 resolution of the camera
# we need to round to the nearest 16th and 32nd (requirement for picamera)
# cam_res = (int(16*np.floor(cam_res[0]/16)),int(32*np.floor(cam_res[1]/32)))
# camera initialization
# cam = PiCamera()
# cam.resolution = (cam_res[1],cam_res[0])
# data = np.empty((cam_res[0],cam_res[1],3),dtype=np.uint8) # preallocate image
# print(webcam.get_raw())
# print(data)
while True:
    
    ret, frame = cap.read()
    # cv2.resize(frame, )
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


while False:
    try:
        cam.capture(data,'rgb') # capture RGB image
        plt.imshow(data) # plot image
        # clear data to save memory and prevent overloading of CPU
        data = np.empty((cam_res[0],cam_res[1],3),dtype=np.uint8)
        plt.show() # show the image
        # press enter when ready to take another photo
        input("Click to save a different plot")
    # pressing CTRL+C exits the loop
    except KeyboardInterrupt:
        break