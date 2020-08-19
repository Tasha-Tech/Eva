import cv2
import numpy as np
import os
import getopt, sys

os.system("sudo modprobe bcm2835-v4l2")
os.system('sudo modprobe uvcvideo')

window_name = 'Camera'
cv2.namedWindow(window_name)

print("Version 2")

path = '/media/pi/3565-3431/'
wait_ms = 100
elapsed = 0
rate_ms = 1000 * 1

opts, args = getopt.getopt(sys.argv,"r")
for opt, arg in opts:
    if opt == '-r':
        rate_ms = arg * 1000
        print("The rate is set to {} sec.".format(int(rate_ms / 1000)))

'''
f = open("{}last_image".format(path), "r")
last_image = int(f.readline())
f.close()
print("Last image {:05d}".format(last_image))
'''

cap = cv2.VideoCapture(0)

def set_resolution(x=640, y=480):
    cap.set(3,x)
    cap.set(4,y)

def write_image(image):
    global last_image
    #cv2.imwrite('sample_out_2.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR)) 
    cv2.imwrite("{}{:05d}.jpg".format(path, last_image), image)

    last_image += 1
    f = open("{}last_image".format(path), "w")
    f.write("{}".format(last_image))
    f.close()

set_resolution(x=854, y=480)

while True:
    ret, image = cap.read()
    cv2.imshow(window_name, image)
    k = cv2.waitKey(wait_ms) & 0xFF
    if k == 27:
        break
    elapsed += wait_ms
    if elapsed >= rate_ms:
        #write_image(image)
        elapsed = 0
        
cap.release()
cv2.destroyAllWindows()
    
