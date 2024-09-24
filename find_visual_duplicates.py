import os
import cv2 as cv
from colored import stylize
import colored
import pickle
import enhanced_imshow
import utils
import json


def compare_descriptors(paths):
    """Compares files to find duplicates"""

    all_descriptors = {}

    # Merges all descriptors into one dict
    for path in paths:

        path = path.replace('"', "")

        for dir_path, subdirs, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dir_path, filename)

                try:
                    full_path = os.path.realpath(full_path)  # follows symlinks

                    if filename == "descriptors.pkl":

                        try:
                            with open(full_path, "rb") as pickle_reader:
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

    duplicatesss = {}

    for i in range(len(all_descriptors)):

        path_a, desc_a = all_descriptors.popitem()

        a1, a2, _ = desc_a
        # print(len(a1), len(a2))

        found = []

        for path_b in all_descriptors:

            b1, b2, _ = all_descriptors[path_b]

            bfm = cv.BFMatcher(cv.NORM_L2)
            bfm2 = cv.BFMatcher(cv.NORM_L2)

            matches = bfm.knnMatch(a1, b1, k=2)
            matches2 = bfm2.knnMatch(a1, b2, k=2)

            # print(path_b, len(a1), len(a2), len(b1), len(b2), len(matches), len(matches2))

            similarity_ratio = 0.10

            good = []
            if len(b1) > 1:
                for m, n in matches:
                    if m.distance < similarity_ratio * n.distance:
                        good.append([m])

            good2 = []
            if len(b2) > 1:
                for m, n in matches2:
                    if m.distance < similarity_ratio * n.distance:
                        good2.append([m])

            # print(path_a + "\n" + path_b + " " + str(len(matches)) +" "+ str(len(matches2)) +" "+ str(len(good))+ " "+str(len(good2)))
            # if (len(good) + len(good2))/(len(matches)+len(matches2)) > .1:
            if len(good) / len(matches) > 0.1 or len(good2) / len(matches2) > 0.1:
                print(
                    path_a + "\n" + path_b + "\n",
                    len(matches),
                    len(matches2),
                    len(good),
                    len(good2),
                    len(good) / len(matches),
                    len(good2) / len(matches2),
                )
                print("")

                img_props = {}

                img_props["path"] = path_b

                found.append(path_b)

                img1 = utils.imread2(path_a)
                img2 = utils.imread2(path_b)

                shape1 = img1.shape
                shape2 = img2.shape
                shape = (img2.shape[1], img2.shape[0])

                im2_rsz = cv.resize(img2, (shape))

                if shape1[0] / shape1[1] >= 1 and shape2[0] / shape2[1] <= 1:
                    im2_rsz = cv.rotate(im2_rsz, cv.ROTATE_90_CLOCKWISE)

                # cv.imshow("A", utils.limit_image_dimension(img1, 500))
                # cv.imshow("B", utils.limit_image_dimension(img2, 500))
                # cv.waitKey(2000)
                # cv.destroyAllWindows()

                enhanced_imshow.enhanced_imshow(
                    "Duplicate!", utils.stack_1_by_2(img1, im2_rsz)
                )

                cv.waitKey(0)

            # except Exception as exception:
            #     print("Erro", path_a, path_b)
            #     print("Erro", exception)

            if len(found) > 0:
                duplicatesss[path_a] = found

    # saves duplicatesss to json file
    with open("./duplicates.json", "w", encoding="utf8") as json_file:
        json.dump(duplicatesss, json_file, ensure_ascii=False)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Finds duplicate files and moves/deletes then if \
                                     needed"
    )
    parser.add_argument(
        "paths",
        help="Sequence of paths to search for duplicate files",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "-m", "--move", help="Define path to move files", type=str, default=None
    )
    parser.add_argument(
        "-c", "--copy", help="Define path to copy files", type=str, default=None
    )
    parser.add_argument(
        "-d",
        "--delete",
        help="Delete duplicate files",
        action="store_const",
        const=True,
    )
    parser.add_argument(
        "-y",
        "--yestoall",
        help="Automatically confirms file move/deletion",
        action="store_const",
        const=True,
    )

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
