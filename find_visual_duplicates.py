import json

import colored
import cv2 as cv
import numpy as np
from colored import stylize

import enhanced_imshow
import utils
from storage.descriptor_storage import DescriptorStorage

SIMILARITY_RATIO = 0.10


def descriptor_matches(desc_a, desc_b):
    desc_a = np.array(desc_a, dtype=np.float32)
    desc_b = np.array(desc_b, dtype=np.float32)

    bfm = cv.BFMatcher(cv.NORM_L2)
    matches = bfm.knnMatch(desc_a, desc_b, k=2)

    good = []
    if len(desc_b) > 1:
        for m, n in matches:
            if m.distance < SIMILARITY_RATIO * n.distance:
                good.append([m])

    return len(good) / len(matches) > 0.1


def compare_descriptors():
    """Compares files to find duplicates"""

    descriptors = DescriptorStorage.get_storage()
    duplicates = {}

    print(
        stylize(f"    {len(descriptors)} files found", colored.bg("light_red")),
    )

    for _ in range(len(descriptors)):

        path_a, desc_a = descriptors.popitem()
        desc_a1, mtime_a = desc_a
        print(stylize(f"         Processing {path_a}", colored.bg("black")))

        found = []
        for path_b in descriptors:

            desc_b1, mtime_b = descriptors[path_b]

            comp_a = descriptor_matches(desc_a1, desc_b1)

            if comp_a:
                found.append(path_b)
                img1 = utils.imread2(path_a)
                img2 = utils.imread2(path_b)
                enhanced_imshow.enhanced_imshow(
                    "Duplicate!", utils.stack_1_by_2(img1, img2)
                )
                cv.waitKey(0)

            if len(found) > 0:
                duplicates[path_a] = found

    # saves duplicates to json file
    with open("./duplicates.json", "w", encoding="utf8") as json_file:
        json.dump(duplicates, json_file, ensure_ascii=False)


if __name__ == "__main__":
    compare_descriptors()
