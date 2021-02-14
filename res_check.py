# run this to find all posible resolutions of a camera
# https://www.learnpythonwithrune.org/find-all-possible-webcam-resolutions-with-opencv-in-python/

import pandas as pd
import cv2

url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
table = pd.read_html(url)[0]
table.columns = table.columns.droplevel()

cap = cv2.VideoCapture(0)
resolutions = {}

for index, row in table[["W", "H"]].iterrows():
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, row["W"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, row["H"])
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    resolutions[str(width)+"x"+str(height)] = "OK"

res_list = list(dict.fromkeys(resolutions))

new_res_list = []

for res in res_list:
    temp = res.split('x')
    new_res_list.append(
        (
            int(float(temp[0])), 
            int(float(temp[1]))
        )
    )

for res in new_res_list:
    print (res)