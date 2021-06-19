import cv2
import numpy as np

scale_percent = 20


def rescale_and_show(name, image):
    rescaled = cv2.resize(image, (int(image.shape[1] * scale_percent / 100),
                          int(image.shape[0] * scale_percent / 100)))
    cv2.imshow(name, rescaled)


def mouse_event(event, x, y, flags, param):

    name, image = param

    if event == cv2.EVENT_MOUSEWHEEL:

        global scale_percent

        if flags > 0:
            scale_percent += 2
        elif flags < 0:
            scale_percent -= 2

        if scale_percent < 0:
            scale_percent = 0

    rescale_and_show(name, image)


def enhanced_imshow(name, image):

    rescale_and_show(name, image)
    cv2.setMouseCallback(name, mouse_event, param=(name, image))
    cv2.moveWindow(name, 0, 0)


if __name__ == "__main__":

    image = cv2.imread("./photo1.jpg")

    enhanced_imshow("test", image)
    cv2.waitKey(0)