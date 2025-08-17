import os

import cv2 as cv
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener


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
    ".heic",
    ".nef",
]
VIDEO_EXTENSIONS = [
    ".avi",
    ".mp4",
    ".mov",
    ".mkv",
    ".flv",
    ".wmv",
    ".webm",
    ".3gp",
]


def imread2(path: str, grayscale: bool = False, max_size: int | None = None):
    """
    Reads an image from the given path.
    Optionally converts to grayscale and limits image size.

    Args:
        path (str): Path to the image file.
        grayscale (bool): If True, converts image to grayscale.
        max_size (int, optional): Maximum dimension for resizing.

    Returns:
        np.ndarray: Loaded image, or None if loading fails.
    """
    image = None
    try:
        ext = os.path.splitext(path)[1].lower()

        if ext == ".heic":
            register_heif_opener()
            image = Image.open(path)
            image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
        else:
            with open(path, "rb") as stream:
                bytes_data = bytearray(stream.read())
            numpyarray = np.asarray(bytes_data, dtype=np.uint8)
            image = cv.imdecode(numpyarray, cv.IMREAD_UNCHANGED)

        if image is None:
            print(f"Failed to load image: {path}")
            return None

        if max_size is not None:
            try:
                image = limit_image_dimension(image, max_size)
            except Exception as e:
                print("Error resizing image", e)
                return None

        if grayscale:
            image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        return image
    except Exception as e:
        print(f"Error reading image {path}: {e}")
        return None


def change_range(vector, old_min, old_max, new_min, new_max):
    """
    Changes the range of values in a vector from [old_min, old_max] to [new_min, new_max].

    Args:
        vector (np.ndarray): Input vector.
        old_min (float): Old minimum value.
        old_max (float): Old maximum value.
        new_min (float): New minimum value.
        new_max (float): New maximum value.

    Returns:
        np.ndarray: Vector with new range.
    """

    if vector.min() != vector.max() and old_max != old_min:
        new_vector = ((vector - old_min) / (old_max - old_min)) * (
            new_max - new_min
        ) + new_min
    else:
        new_vector = vector

    return new_vector


def normalize(vector, new_min=0, new_max=255):
    """
    Normalizes a vector to a new range [new_min, new_max].

    Args:
        vector (np.ndarray): Input vector.
        new_min (float): New minimum value.
        new_max (float): New maximum value.

    Returns:
        np.ndarray: Normalized vector.
    """

    old_min = vector.min()
    old_max = vector.max()

    return change_range(vector, old_min, old_max, new_min, new_max)


def convert_to_image(vector):
    """
    Converts a vector to an 8-bit image by normalizing and rounding.

    Args:
        vector (np.ndarray): Input vector.

    Returns:
        np.ndarray: 8-bit image.
    """

    return np.rint(normalize(vector, 0, 255)).astype("uint8")


def resize_and_show(
    name, img, scale_percent, preview_event=None, event_params=None, show_condition=True
):
    """
    Resizes and displays an image using OpenCV. Optionally sets a mouse callback.

    Args:
        name (str): Window name.
        img (np.ndarray): Image to display.
        scale_percent (float): Scale percentage.
        preview_event (callable, optional): Mouse callback function.
        event_params (any, optional): Parameters for callback.
        show_condition (bool): If True, shows the image.
    """

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
    Stacks two numpy arrays either horizontally or vertically.

    Args:
        image_1 (np.ndarray): First image.
        image_2 (np.ndarray): Second image.
        convert_image (bool): If True, converts images to 8-bit.
        orientation (str): 'Horizontal' or 'Vertical'.

    Returns:
        np.ndarray: Stacked image.
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
    """
    Limits the dimensions of an image to a maximum size.

    Args:
        image (np.ndarray): Input image.
        max (int): Maximum dimension size.

    Returns:
        np.ndarray: Resized image.
    """

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


def get_all_files(paths):
    """
    Gets all files from the given list of directory paths.

    Args:
        paths (list): List of directory paths.

    Returns:
        list: List of file paths.
    """

    all_files = []
    for path in paths:
        for dir_path, _, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dir_path, filename)
                full_path = os.path.realpath(full_path)  # follows symlinks
                all_files.append(full_path)
    print(f"Found {len(all_files)} files")
    return all_files


def get_video_snapshots(full_path, snapshots_count=32, max_image_size=500):
    """
    Captures snapshots from a video file at evenly spaced intervals.

    Args:
        full_path (str): Path to video file.
        snapshots_count (int): Number of snapshots to capture.
        max_image_size (int): Maximum size for each snapshot.

    Returns:
        np.ndarray: Stacked snapshots image.
    """

    try:
        cap = cv.VideoCapture(full_path)
        total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        frames_to_capture = np.linspace(0, total_frames - 1, snapshots_count, dtype=int)

        frames = []
        for i in range(total_frames):
            if i in frames_to_capture:
                _, frame = cap.read()
                resized = limit_image_dimension(frame, max_image_size)
                frames.append(resized)
        cap.release()

        return np.hstack(frames)
    except Exception as e:
        print("Error processing video", e)
        return


def plot_histogram(hist):
    """
    Plots a single histogram using matplotlib.

    Args:
        hist (np.ndarray): Histogram data.
    """

    from matplotlib import pyplot as plt

    hist = np.array(hist).ravel()
    plt.plot(hist, color="k")
    plt.xlim([0, 256])
    plt.show()


def plot_histograms(hist_a, hist_b):
    """
    Plots two histograms on the same plot using matplotlib.

    Args:
        hist_a (np.ndarray): First histogram data.
        hist_b (np.ndarray): Second histogram data.
    """

    from matplotlib import pyplot as plt

    hist_a = np.array(hist_a).ravel()
    hist_b = np.array(hist_b).ravel()
    plt.plot(hist_a, color="k")
    plt.plot(hist_b, color="r")
    plt.xlim([0, 256])
    plt.show()
