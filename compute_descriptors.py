import cv2 as cv
import numpy as np
import os

from colored import stylize, bg
from descriptor_storage import DescriptorStorage

from utils import IMG_EXTENSIONS, VIDEO_EXTENSIONS, imread2, limit_image_dimension


N_FEATURES = 50
MAX_IMAGE_SIZE = 500


def get_image_descriptors(full_path: str) -> tuple:
    """Gets descriptor for a given image"""

    image = imread2(full_path, True)
    image = limit_image_dimension(image, MAX_IMAGE_SIZE)
    image_flip = cv.flip(image, 0)

    sift = cv.SIFT_create(nfeatures=N_FEATURES)
    try:
        _, descriptor = sift.detectAndCompute(image, None)
        _, descriptor_flip = sift.detectAndCompute(image_flip, None)
    except Exception as exception:
        print("Error getting image descriptor", exception)
        return None, None

    return descriptor, descriptor_flip


def get_video_descriptors(full_path):
    """Gets descriptor for a given video"""

    # Gets 32 frames from the video, equally spaced
    cap = cv.VideoCapture(full_path)
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    frames_to_capture = np.linspace(0, total_frames - 1, 32, dtype=int)

    frames = []
    for i in range(total_frames):
        if i in frames_to_capture:
            _, frame = cap.read()
            resized = limit_image_dimension(frame, MAX_IMAGE_SIZE)
            frames.append(resized)

    cap.release()

    combined_image = np.hstack(frames)

    sift = cv.SIFT_create(nfeatures=N_FEATURES)
    try:
        _, descriptor = sift.detectAndCompute(combined_image, None)
    except Exception as exception:
        print("Error getting descriptor for video", exception)
        return None, None

    return descriptor, None


def get_all_files(paths):
    """Gets all files in a given path"""
    all_files = []
    for path in paths:
        for dir_path, _, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dir_path, filename)
                full_path = os.path.realpath(full_path)  # follows symlinks
                all_files.append(full_path)
    return all_files


def get_all_descriptors(paths):
    """Gets descriptors for all images in a given path"""

    descriptors = DescriptorStorage.get_storage()

    for file_path in get_all_files(paths):
        # try:
        _, extension = os.path.splitext(file_path)

        print("Processing " + file_path)

        if extension.lower() in IMG_EXTENSIONS + VIDEO_EXTENSIONS:

            has_descriptor = file_path in descriptors

            # If file has descriptor, checks if it has been modified
            is_modified = has_descriptor and descriptors[file_path][
                2
            ] != os.path.getmtime(file_path)

            # If file does not have descriptor, or if it has been modified, gets descriptor
            if not has_descriptor or (has_descriptor and is_modified):
                if extension.lower() in IMG_EXTENSIONS:
                    descriptor, descriptor_flip = get_image_descriptors(file_path)
                elif extension.lower() in VIDEO_EXTENSIONS:
                    descriptor, descriptor_flip = get_video_descriptors(file_path)

                if descriptor is not None:
                    descriptors[file_path] = (
                        descriptor,
                        descriptor_flip,
                        os.path.getmtime(file_path),
                    )
                    print("    OK")
            else:
                print("    Skipping")

        else:
            print("Ignoring Format " + extension)

    DescriptorStorage.save_storage(descriptors)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Computes image descriptors")
    parser.add_argument(
        "paths",
        help="Sequence of paths to compute descriptors",
        type=str,
        nargs="+",
    )

    args = parser.parse_args()
    PATHS = args.paths

    print(stylize("Computing descriptors for files in:", bg("red")))
    for arg in PATHS:
        print(stylize("   " + arg, bg("light_red")))

    get_all_descriptors(PATHS)
