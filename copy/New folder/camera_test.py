import GUI_function
import cv2
index = 0
width = 1920
height = 1080
resolution = 255
image = GUI_function.OCR_camera_capture(index, width, height, resolution)
cv2.imwrite('scan.jpg', image)

