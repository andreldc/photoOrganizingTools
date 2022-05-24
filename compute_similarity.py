import os
import numpy as np
import cv2 as cv
from colored import stylize
import colored
import pickle
import enhanced_imshow
import utils
import json

GOOD_RATIO = 0.75

def compare_descriptors(paths):
    """Compares files to find duplicates"""

    all_descriptors = {}

    # Merges all descriptors into one dict
    for path in paths:

        path = path.replace("\"", "")

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

    similarities = {}

    for i in range(len(all_descriptors)):

        path_a, desc_a  = all_descriptors.popitem()
        a1, _, _ = desc_a

        for path_b in all_descriptors:

            b1, b2, _ = all_descriptors[path_b]

            matches1 = cv.BFMatcher(cv.NORM_L2).knnMatch(a1, b1, k=2)
            matches2 = cv.BFMatcher(cv.NORM_L2).knnMatch(a1, b2, k=2)

            matchesA = sorted(cv.BFMatcher(cv.NORM_L2, crossCheck=True).match(a1, b1), key = lambda x:x.distance)
            matchesB = sorted(cv.BFMatcher(cv.NORM_L2, crossCheck=True).match(a1, b2), key = lambda x:x.distance)            

            good1 = []
            good2 = []

            if len(b1) > 1:
                for m, n in matches1:
                    if m.distance < GOOD_RATIO * n.distance:
                        good1.append([m])

            if len(b2) > 1:
                for m, n in matches2:
                    if m.distance < GOOD_RATIO * n.distance:
                        good2.append([m])

       

            score =  len(good1) + len(good2) + abs(len(good1) - len(good2))
            score2 =  len(matchesA) + len(matchesB) + abs(len(matchesA) - len(matchesB))
            # if pct1 > 0.25 or pct2 > 0.25:
            if score > 60 and score2 > 90: # VALORES BONS PARA 100 DESCRITORES

                print("{:2.0f} {:2.0f} {:2.0f} {:2.0f} | {:2.0f} {:2.0f} {:2.0f} {:2.0f}".format(len(good1), len(good2), abs(len(good1) - len(good2)), score, len(matchesA), len(matchesB), abs(len(good1) - len(good2)), score2))
                # dict2 = {}
                # dict2[path_b] = pct
                # similarities[path_a] = dict2
                # print(" Confirmation: {:10.0f} {:10.0f}".format(len(matchesA), len(matchesB)))
                
                img1 = utils.imread2(path_a)
                img2 = utils.imread2(path_b)

                cv.imshow("A", utils.limit_image_dimension(img1, 500))
                cv.imshow("B", utils.limit_image_dimension(img2, 500))
                cv.waitKey(1000)
    #             # cv.destroyAllWindows()



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
