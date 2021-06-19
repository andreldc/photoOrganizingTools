import cv2
import numpy as np
from utils import resize_and_show
from os import listdir
from os.path import isfile, isdir, join

def interactive_rotate(input_image, save_path=None):

    transformed = np.copy(input_image)

    while True:
        resize_and_show("Rotating Image", transformed, 20)
        key = cv2.waitKeyEx(0)
        # print(key)

        if key == 2555904: # right_arrow
            print("Rotating 90º clockwise")
            transformed = cv2.rotate(transformed, cv2.ROTATE_90_CLOCKWISE)
        elif key == 2424832: # left_arrow
            print("Rotating 90º counter-clockwise")
            transformed = cv2.rotate(transformed, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif key == 104: # h
            print("Horizontal flip")
            transformed = cv2.flip(transformed, 1)
        elif key == 118: # v
            print("Vertical flip")
            transformed = cv2.flip(transformed, 0)
        elif key == 115: # s
            if save_path:
                print("Saving image: "+ save_path)
                cv2.imwrite(save_path, transformed)
                break
            else:
                save_path = input('Enter save path with image name and format.')
                cv2.imwrite(save_path, transformed)
                break
        elif key == 13: # enter
            print("Returning rotated image")
            return transformed
        elif key == 27: # esc
            print("Returning original image")
            return input_image
        elif key == -1: # quit_button
            break
        else:
            print("Invalid Key. Press 'esc' to finish")

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Interactively rotates images")
    parser.add_argument("path", help="Image path, including image name and format")

    args = parser.parse_args()
    PATH = args.path

    if isdir(PATH):
        print("Listing all images from " + PATH)

        files = [file for file in listdir(PATH) if isfile(join(PATH, file))]
        images = [file for file in files if file.split(".")[-1] in ["jpg","bmp","png"]]

    elif isfile(PATH) and PATH.split(".")[-1] in ["jpg","bmp","png"]:
        images = [PATH]

    print(str(len(images)) + " images found")

    for image in images:
        INPUT_IMAGE = cv2.imread(image)
        print("\nRotating image: " + image)
        interactive_rotate(INPUT_IMAGE, image)
