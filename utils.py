import cv2 as cv
import numpy as np

IMG_EXTENSIONS = [
    ".jpeg",
    ".jpg",
    ".jpe",
    ".bmp",
    ".jp2",
    ".png",
    ".pbm",
    ".pgm",
    ".ppm",
    ".sr",
    ".ras",
    ".tiff",
    ".tif",
]
VIDEO_EXTENSIONS = [".avi", ".mp4", ".mov", ".mkv", ".flv", ".wmv", ".webm"]


def imread2(path, grayscale=False):
    stream = open(path, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    image = cv.imdecode(numpyarray, cv.IMREAD_UNCHANGED)

    if grayscale:
        return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    return image


def change_range(vector, old_min, old_max, new_min, new_max):
    if vector.min() != vector.max() and old_max != old_min:
        new_vector = ((vector - old_min) / (old_max - old_min)) * (
            new_max - new_min
        ) + new_min
    else:
        new_vector = vector

    return new_vector


def normalize(vector, new_min=0, new_max=255):
    old_min = vector.min()
    old_max = vector.max()

    return change_range(vector, old_min, old_max, new_min, new_max)


def convert_to_image(vector):
    return np.rint(normalize(vector, 0, 255)).astype("uint8")


def resize_and_show(
    name, img, scale_percent, preview_event=None, event_params=None, show_condition=True
):
    if show_condition:
        cv.imshow(
            name,
            cv.resize(
                img,
                (
                    int(img.shape[1] * scale_percent / 100),
                    int(img.shape[0] * scale_percent / 100),
                ),
            ),
        )
        if preview_event is not None:
            cv.setMouseCallback(name, preview_event, param=event_params)


def stack_1_by_2(image_1, image_2, convert_image=False, orientation="Horizontal"):
    """
    Stacks 2 np.arrays vertically or horizontally
    """
    if convert_image:
        image_1 = convert_to_image(image_1)
        image_2 = convert_to_image(image_2)

    if orientation == "Horizontal":
        out = np.hstack((image_1, image_2))
    elif orientation == "Vertical":
        out = np.vstack((image_1, image_2))
    else:
        out = np.hstack((image_1, image_2))

    return out


def limit_image_dimension(image, max=1280):
    """Limits image dimension to 1280x1280"""

    # 8K = 7680x4320
    # 4K = 3840x2160
    # FullHD = 1920x1080
    # HD = 1280x720
    # SD = 640x480
    # 480p = 480x360
    # 360p = 360x240
    # 240p = 240x180
    # 180p = 180x135
    # 135p = 135x90
    # 90p = 90x60
    # 60p = 60x45

    shape = image.shape
    if shape[0] > max or shape[1] > max:
        if shape[0] > shape[1]:
            image = cv.resize(image, (max, int(shape[0] * max / shape[1])))
        else:
            image = cv.resize(image, (int(shape[1] * max / shape[0]), max))

    return image
