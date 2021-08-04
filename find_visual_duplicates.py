import os
import numpy as np
import cv2 as cv
from colored import stylize
import colored
import pickle
import enhanced_imshow
import utils

def imread2(path, grayscale=False):
    stream = open(path, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    image = cv.imdecode(numpyarray, cv.IMREAD_UNCHANGED)

    if grayscale:
        return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    return image


def compare_descriptors(paths):
    """Compares files to find duplicates"""

    all_descriptors = {}

    # Merges all descriptors into one dict
    for path in paths:
        for dir_path, subdirs, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dir_path, filename)

                try:
                    full_path = os.path.realpath(full_path) # follows symlinks

                    if filename == "descriptors.pkl":

                        try:
                            with open(full_path, 'rb') as pickle_reader:
                                descriptors = pickle.load(pickle_reader)
                        except Exception as exception:
                            descriptors = {}         

                        # Updates file paths                        
                        for descriptor_path in descriptors.keys():
                            image_path = os.path.join(dir_path, descriptor_path)
                            all_descriptors[image_path] = descriptors[descriptor_path]

                except (OSError,):
                    continue


    print(len(all_descriptors))

    for i in range(len(all_descriptors)):
        print(i)

        path_a, desc_a  = all_descriptors.popitem()
        a1, a2, _ = desc_a
        print(a1.shape, a1.dtype)
        for path_b in all_descriptors:

            b1, b2, _ = all_descriptors[path_b]
            bfm = cv.BFMatcher(cv.NORM_L2)
            bfm2 = cv.BFMatcher(cv.NORM_L2)

            matches = bfm.knnMatch(a1, b1, k=2)
            matches2 = bfm2.knnMatch(a1, b2, k=2)

            good = []
            for m, n in matches:
                if m.distance < 0.25*n.distance:
                    good.append([m])

            good2 = []
            for m, n in matches2:
                if m.distance < 0.25*n.distance:
                    good2.append([m])

            print(path_a + "\n" + path_b + " " + str(len(matches)) +" "+ str(len(matches2)) +" "+ str(len(good))+ " "+str(len(good2)))
            if (len(good) + len(good2))/(len(matches)+len(matches2)) > .2:

                enhanced_imshow.enhanced_imshow("Duplicate!", utils.stack_1_by_2(imread2(path_a), imread2(path_b)))

                cv.waitKey(0)   



if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Finds duplicate files and moves/deletes then if \
                                     needed")
    parser.add_argument("paths", help="Sequence of paths to search for duplicate files", type=str,
                        nargs='+')
    parser.add_argument("-m", "--move", help="Define path to move files", type=str,
                        default=None)
    parser.add_argument("-c", "--copy", help="Define path to copy files", type=str,
                        default=None)
    parser.add_argument("-d", "--delete", help="Delete duplicate files", action='store_const',
                        const=True)
    parser.add_argument("-y", "--yestoall", help="Automatically confirms file move/deletion",
                        action='store_const', const=True)

    args = parser.parse_args()
    PATHS = args.paths
    MOVE_PATH = args.move
    COPY_PATH = args.copy
    DELETE_DUPLICATES = args.delete if args.delete is not None else False
    AUTO_CONFIRM = args.yestoall if args.yestoall is not None else False

    print(stylize(" Searching duplicate files in:", colored.bg("red")))
    for arg in PATHS:
        print(stylize("   " + arg, colored.bg("light_red")))

    # duplicate_set =
    compare_descriptors(PATHS)

    full_paths = list(map(lambda p: os.path.abspath(p), PATHS))




    # print(stylize("     " + str(len(duplicate_set)) + " duplicates found!     ",
    #       colored.bg("green")))
