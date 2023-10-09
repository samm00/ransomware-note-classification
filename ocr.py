import cv2
import pytesseract
import numpy as np
import os

for path, subdirs, files in os.walk('RansomNoteFiles/ransomwhere_notes'):
    for name in files:
        if name.endswith("png") or name.endswith("PNG") or name.endswith("jpg"):

            img = cv2.imread('RansomNoteFiles/ransomwhere_notes/' + name)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            gray, img_bin = cv2.threshold(gray,128,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            gray = cv2.bitwise_not(img_bin)

            kernel = np.ones((2, 1), np.uint8)
            img = cv2.erode(gray, kernel, iterations=1)
            img = cv2.dilate(img, kernel, iterations=1)
            output = pytesseract.image_to_string(img)
            open("RansomNoteFiles/ransomwhere_notes/" + name[:-3] + 'txt', 'w').write(output)