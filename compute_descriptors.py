import os

import cv2 as cv
from colored import bg, stylize

from storage.descriptor_storage import DescriptorStorage
from utils import (
    IMG_EXTENSIONS,
    VIDEO_EXTENSIONS,
    get_all_files,
    get_video_snapshots,
    imread2,
)

N_FEATURES = 3000
MAX_IMAGE_SIZE = 1280
THRESHOLD = 0.03


def get_descriptors(image) -> list | None:
    """
    Extracts and returns the strongest descriptors for a given image,
    sorted by keypoint strength.
    Returns None if no descriptors are found.
    """
    sift = cv.SIFT_create(nfeatures=N_FEATURES)

    try:
        keypoints, descriptors = sift.detectAndCompute(image, None)

        if descriptors is None or len(descriptors) == 0:
            print("No descriptors found.")
            return None

        descriptors = [
            desc for desc, kp in zip(descriptors, keypoints) if kp.response > THRESHOLD
        ]

        sorted_descriptors = sorted(
            zip(keypoints, descriptors), key=lambda x: x[0].response, reverse=True
        )

        strong_descriptors = [desc for _, desc in sorted_descriptors]

    except Exception as exception:
        print(f"Error getting image descriptors: {exception}")
        return None

    print(f"Number of descriptors returned: {len(strong_descriptors)}")
    return strong_descriptors


def get_all_descriptors(paths: list[str]) -> None:
    """Gets descriptors for all images in a given path."""

    descriptors = DescriptorStorage.get_storage()
    processed_count = 0

    for file_path in get_all_files(paths):

        print(f"Processing #{processed_count + 1}: {file_path}")

        # Get file extension
        _, extension = os.path.splitext(file_path)
        if extension.lower() not in IMG_EXTENSIONS + VIDEO_EXTENSIONS:
            print("Ignoring Format " + extension)

        has_descriptor = file_path in descriptors

        # If file already has a descriptor, checks if it has been modified
        is_modified = has_descriptor and descriptors[file_path][1] != os.path.getmtime(
            file_path
        )

        # If file already has a descriptor and it has not been modified, skips processing
        if has_descriptor and not is_modified:
            print("    Skipping ")
            continue

        # Read image/video
        image = None
        if extension.lower() in IMG_EXTENSIONS:
            image = imread2(file_path, max_size=MAX_IMAGE_SIZE)

        elif extension.lower() in VIDEO_EXTENSIONS:
            image = get_video_snapshots(file_path)

        if image is None:
            print("    Failed to read image")
            continue

        # Get descriptors
        descriptor = get_descriptors(image)
        if descriptor is None:
            print("    No descriptors extracted")
            continue

        descriptors[file_path] = (descriptor, os.path.getmtime(file_path))
        print("    OK ", len(descriptor))

        processed_count += 1
        if processed_count % 20 == 0:
            print("    Saving intermediate results...")
            DescriptorStorage.save_storage(descriptors)

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
