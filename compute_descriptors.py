import os
import cv2 as cv
from colored import stylize
import colored
import pickle
import utils

N_FEATURES = 50
MAX_IMAGE_SIZE = 500
IMG_EXTENSION = [
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


def get_descriptor(full_path):
    """Gets descriptor for a given image"""

    image = utils.imread2(full_path, True)
    image = utils.limit_image_dimension(image, MAX_IMAGE_SIZE)

    image_flip = cv.flip(image, 0)

    try:
        sift = cv.SIFT_create(nfeatures=N_FEATURES)
        _, descriptor = sift.detectAndCompute(image, None)
        _, descriptor_flip = sift.detectAndCompute(image_flip, None)

    except Exception as exception:
        print("Error getting descriptor", exception)
        return None, None

    return descriptor, descriptor_flip


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


class DescriptorStorage:
    pickle_filename = os.path.join("d:\\descriptors.pkl")

    @staticmethod
    def get_storage():
        """Gets descriptor storage"""
        try:
            with open(DescriptorStorage.pickle_filename, "rb") as pickle_reader:
                descriptors = pickle.load(pickle_reader)
        except Exception as exception:
            descriptors = {}

        return descriptors

    @staticmethod
    def save_storage(descriptors):
        """Saves descriptor storage"""
        with open(DescriptorStorage.pickle_filename, "wb") as pickle_writer:
            pickle.dump(descriptors, pickle_writer)


def get_all_descriptors(paths):
    """Gets descriptors for all images in a given path"""

    descriptors = DescriptorStorage.get_storage()

    for file_path in get_all_files(paths):
        try:
            _, extension = os.path.splitext(file_path)

            print("Processing " + file_path)

            if extension.lower() in IMG_EXTENSION:

                has_descriptor = file_path in descriptors

                # If file has descriptor, checks if it has been modified
                is_modified = has_descriptor and descriptors[file_path][
                    2
                ] != os.path.getmtime(file_path)

                # If file does not have descriptor, or if it has been modified, gets descriptor
                if not has_descriptor or (has_descriptor and is_modified):
                    descriptor, descriptor_flip = get_descriptor(file_path)

                    if descriptor is not None:
                        descriptors[file_path] = (
                            descriptor,
                            descriptor_flip,
                            os.path.getmtime(file_path),
                        )
                        print("OK    - " + file_path)
                else:
                    print("Skip  - " + file_path)
            else:
                print("Ignoring Format " + extension)

        except (OSError,):
            continue

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

    print(stylize("Searching duplicate files in:", colored.bg("red")))
    for arg in PATHS:
        print(stylize("   " + arg, colored.bg("light_red")))

    # duplicate_set =
    get_all_descriptors(PATHS)

    full_paths = list(map(lambda p: os.path.abspath(p), PATHS))
