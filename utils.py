import cv2
import numpy as np

def change_range(vector, old_min, old_max, new_min, new_max):
    if(vector.min() != vector.max() and old_max != old_min):
        new_vector = ((vector-old_min)/(old_max-old_min))*(new_max-new_min) + new_min
    else:
        new_vector = vector

    return new_vector

def normalize(vector, new_min=0, new_max=255):
    old_min = vector.min()
    old_max = vector.max()

    return change_range(vector, old_min, old_max, new_min, new_max)

def convert_to_image(vector):
    return np.rint(normalize(vector, 0, 255)).astype("uint8")

def resize_and_show(name, img, scale_percent, preview_event=None, event_params=None, show_condition=True):
    if show_condition:
        cv2.imshow(name, cv2.resize(img, (int(img.shape[1] * scale_percent / 100), int(img.shape[0] * scale_percent / 100))))
        if preview_event is not None:
            cv2.setMouseCallback(name, preview_event, param=event_params)

       
