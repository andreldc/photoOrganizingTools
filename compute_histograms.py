import cv2 as cv
import numpy as np
import os

from colored import stylize, bg
from descriptor_storage import HistogramStorage
from utils import (
    IMG_EXTENSIONS,
    VIDEO_EXTENSIONS,
    imread2,
    limit_image_dimension,
    get_all_files,
    get_video_snapshots,
)


MAX_IMAGE_SIZE = 500


def get_histogram(image) -> list:

    def _do_the_magic(channel, bins):
        hist = cv.calcHist([channel], [0], None, [bins], [0, bins])
        return cv.normalize(hist, hist, alpha=0, beta=1, norm_type=cv.NORM_MINMAX)

    image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(image_hsv)

    histogram_hue = _do_the_magic(h, 180)
    histogram_saturation = _do_the_magic(s, 256)
    histogram_value = _do_the_magic(v, 256)

    final_hist = np.concatenate((histogram_hue, histogram_saturation, histogram_value))

    return final_hist.flatten().tolist()


def get_all_histograms(paths):
    histograms = HistogramStorage.get_storage()

    for file_path in get_all_files(paths):

        print(f"\nProcessing {file_path}")

        _, extension = os.path.splitext(file_path)
        if extension.lower() not in IMG_EXTENSIONS + VIDEO_EXTENSIONS:
            print(f"    Ignoring Format {extension}")
            continue

        has_histogram = file_path in histograms
        is_modified = has_histogram and histograms[file_path][1] != os.path.getmtime(
            file_path
        )
        if has_histogram and not is_modified:
            print("    Already has histogram... Skipping")
            continue

        if extension.lower() in IMG_EXTENSIONS:
            image = limit_image_dimension(imread2(file_path), MAX_IMAGE_SIZE)
        elif extension.lower() in VIDEO_EXTENSIONS:
            image = get_video_snapshots(file_path, MAX_IMAGE_SIZE)

        if image is None:
            print("    Unable to load Image or Video... Skipping")
            continue

        histograms[file_path] = (
            get_histogram(image),
            os.path.getmtime(file_path),
        )
        print("    OK ")

        # saves histograms every 100 files
        if len(histograms) % 100 == 0:
            HistogramStorage.save_storage(histograms)

    HistogramStorage.save_storage(histograms)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Computes image histograms")
    parser.add_argument(
        "paths",
        help="Sequence of paths to compute histograms",
        type=str,
        nargs="+",
    )

    args = parser.parse_args()
    PATHS = args.paths

    print(stylize("Computing histograms for files in:", bg("red")))
    for arg in PATHS:
        print(stylize("   " + arg, bg("light_red")))

    get_all_histograms(PATHS)
