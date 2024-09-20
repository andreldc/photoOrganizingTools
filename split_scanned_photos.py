from os import listdir
from os.path import isfile, isdir, join
import cv2
import numpy as np
import imutils
from utils import resize_and_show

# Default values
DEF_MIN_SIZE = 200
DEF_ADITIONAL_CROP = 1
DEF_MEDIAN_KSIZE = 23
DEF_THRESHOLD = 240
DEF_CLOSE_KSIZE = 5
DEF_SHOW_PREVIEW = True
DEF_PREVIEW_SCALE = 30
DEF_DEBUG = False


def split_photos(
    input_image,
    min_size=DEF_MIN_SIZE,
    aditional_crop=DEF_ADITIONAL_CROP,
    median_ksize=DEF_MEDIAN_KSIZE,
    threshold=DEF_THRESHOLD,
    close_ksize=DEF_CLOSE_KSIZE,
    preview=(DEF_SHOW_PREVIEW, DEF_PREVIEW_SCALE, DEF_DEBUG),
):

    show_preview, preview_scale, debug = preview

    resize_and_show("input_image", input_image, preview_scale, show_condition=debug)

    # Converts image to grayscale
    grayscale = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    resize_and_show("grayscale", grayscale, preview_scale, show_condition=debug)

    # Removes noise
    median = cv2.medianBlur(grayscale, median_ksize)
    resize_and_show("median", median, preview_scale, show_condition=debug)

    # Get mask
    _, mask = cv2.threshold(median, threshold, median.max(), cv2.THRESH_BINARY_INV)
    resize_and_show("mask", mask, preview_scale, show_condition=debug)

    # Refines Mask
    closing = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_ksize, close_ksize)),
    )
    resize_and_show("closing", closing, preview_scale, show_condition=debug)

    # Get contours
    contours = cv2.findContours(
        closing.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = imutils.grab_contours(contours)

    split = []

    # For each contour
    for index, contour in enumerate(contours):

        # Get bounding rectangle
        x_coordinate, y_coordinate, width, height = cv2.boundingRect(contour)
        center = (width // 2, height // 2)

        # Get minarea rectangle
        _, (mar_w, mar_h), angle = cv2.minAreaRect(contour)
        mar_w = int(np.round(mar_w))
        mar_h = int(np.round(mar_h))

        # Adjusts angle
        if abs(angle) > abs(angle - 90):
            angle = angle - 90
            mar_w, mar_h = (mar_h, mar_w)

        # Discards small images
        if mar_w < min_size or mar_h < min_size:
            print("too small", index)

        else:
            # Crop image using bounding box sizes
            pre_crop = input_image[
                y_coordinate : y_coordinate + height,
                x_coordinate : x_coordinate + width,
            ]
            resize_and_show("pre_crop", pre_crop, preview_scale, show_condition=debug)

            # Rotates image
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            straight = cv2.warpAffine(
                pre_crop,
                rotation_matrix,
                (width, height),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )
            resize_and_show("straight ", straight, preview_scale, show_condition=debug)

            # Crop image using min area sizes removing dead space
            y_offset = int(np.round((height - mar_h) / 2))
            x_offset = int(np.round((width - mar_w) / 2))
            post_crop = straight[
                y_offset + aditional_crop : y_offset + mar_h - aditional_crop,
                x_offset + aditional_crop : x_offset + mar_w - aditional_crop,
            ]
            resize_and_show(
                "post_crop",
                post_crop,
                preview_scale,
                show_condition=show_preview or debug,
            )

            # Appends to result list
            split.append(post_crop)

            marked_image = np.copy(input_image)

            # Plot min area rectangle
            box = cv2.boxPoints(cv2.minAreaRect(contour))
            box = np.int0(box)
            marked_image = cv2.drawContours(marked_image, [box], 0, (0, 255, 0), 5)

            # Plot rectangle
            marked_image = cv2.rectangle(
                marked_image,
                (x_coordinate, y_coordinate),
                (x_coordinate + width, y_coordinate + height),
                (255, 0, 0),
                5,
            )

            # Plot contour
            cv2.drawContours(marked_image, [contour], -1, (0, 0, 255), 5)

            # Plot number
            ((x_coordinate, y_coordinate), _) = cv2.minEnclosingCircle(contour)
            cv2.putText(
                marked_image,
                "#{}".format(index + 1),
                (int(x_coordinate) - 45, int(y_coordinate) + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (255, 0, 0),
                5,
            )

            resize_and_show(
                "marked_image",
                marked_image,
                preview_scale,
                show_condition=show_preview or debug,
            )

            if show_preview or debug:
                cv2.waitKey(0)

    return split


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Splits file with multiple scanned photos into \
                                                  individual photos"
    )
    parser.add_argument(
        "path", help="Image path, including image name and format", type=str
    )
    parser.add_argument(
        "-m", "--minsize", help="Minimum image size", type=int, default=DEF_MIN_SIZE
    )
    parser.add_argument(
        "-ac",
        "--additionalcrop",
        help="Additional crop",
        type=int,
        default=DEF_ADITIONAL_CROP,
    )
    parser.add_argument(
        "-mk",
        "--medianksize",
        help="Median filter kernel size",
        type=int,
        default=DEF_MEDIAN_KSIZE,
    )
    parser.add_argument(
        "-t", "--threshold", help="Threshold", type=int, default=DEF_THRESHOLD
    )
    parser.add_argument(
        "-ck",
        "--closingksize",
        help="Closing operator kernel size",
        type=int,
        default=DEF_CLOSE_KSIZE,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Do not show preview images",
        action="store_const",
        const=False,
    )
    parser.add_argument(
        "-ps",
        "--previewscale",
        help="Preview scale (%)",
        type=int,
        default=DEF_PREVIEW_SCALE,
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Shows intermediate results",
        action="store_const",
        const=True,
    )

    args = parser.parse_args()
    PATH = args.path
    MIN_SIZE = args.minsize
    MIN_SIZE = args.minsize
    ADDITIONAL_CROP = args.additionalcrop
    MEDIAN_KZISE = args.medianksize
    THRESHOLD = args.threshold
    CLOSE_KSIZE = args.closingksize
    PREVIEW_SCALE = args.previewscale
    PREVIEW = not args.quiet if args.quiet is None else False
    DEBUG = args.debug

    if isdir(PATH):
        print("Listing all images from " + PATH)

        files = [file for file in listdir(PATH) if isfile(join(PATH, file))]
        images = [
            file for file in files if file.split(".")[-1] in ["jpg", "bmp", "png"]
        ]

    elif isfile(PATH) and PATH.split(".")[-1] in ["jpg", "bmp", "png"]:
        images = [PATH]

    print(str(len(images)) + " images found")

    for image in images:
        INPUT_IMAGE = cv2.imread(image)
        print("\nRotating image: " + image)

        photos = split_photos(
            INPUT_IMAGE,
            MIN_SIZE,
            ADDITIONAL_CROP,
            MEDIAN_KZISE,
            THRESHOLD,
            CLOSE_KSIZE,
            (PREVIEW, PREVIEW_SCALE, DEBUG),
        )

        for i in range(len(photos)):
            resize_and_show("{} (image {})".format(image, i), photos[i], PREVIEW_SCALE)

            save_path = (
                image.split("\\")[0]
                + "\\crop"
                + image.split(".")[-2]
                + "_"
                + str(i)
                + "."
                + image.split(".")[-1]
            )

            print(image, save_path)
            cv2.imwrite(save_path, photos[i])

        cv2.waitKey(0)
