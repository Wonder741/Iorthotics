import GUI_function
import cv2

width = 1920
height = 1080
image = GUI_function.capture_image(width, height, 255)
cv2.imwrite('scan.jpg', image)
image = GUI_function.OCR_camera_capture(1, width, height)
cv2.imwrite('scan1.jpg', image)