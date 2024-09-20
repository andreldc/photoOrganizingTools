from datetime import datetime

import os
import shutil
from colored import stylize
import colored

MONTHS_BR = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]


def create_folders(paths):
    for path in paths:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)

                mtime = datetime.fromtimestamp(os.path.getmtime(full_path))

                month_folder = (
                    str(str(mtime.month)).zfill(2) + " - " + MONTHS_BR[mtime.month - 1]
                )
                destiny_folder = os.path.join(dirpath, month_folder)

                origin_path = os.path.join(dirpath, filename)
                destiny_path = os.path.join(destiny_folder, filename)

                print(dirpath, month_folder)
                print(filename)
                print(mtime)
                print(origin_path, "to", destiny_path)
                print("---")

                os.makedirs(destiny_folder, exist_ok=True)
                shutil.move(origin_path, destiny_path)


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

    duplicate_set = create_folders(PATHS)

    # full_paths = list(map(lambda p: os.path.abspath(p), PATHS))

    # # For each duplicate set
    # for duplicate_list in duplicate_set:

    #     # sorted_list = sort_by_paths(duplicate_list, PATHS)

    #     solve_duplicates(sorted_list, MOVE_PATH, COPY_PATH, DELETE_DUPLICATES, AUTO_CONFIRM)
    #     print("")

    # print(stylize("     " + str(len(duplicate_set)) + " duplicates found!     ",
    #       colored.bg("green")))
