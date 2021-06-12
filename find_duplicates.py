# Based on https://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them
from collections import defaultdict
import hashlib
import os
import sys
import shutil
from colored import stylize
import colored

def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk

def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    """Gets hash for a given file"""
    hashobj = hash()
    file_object = open(filename, 'rb')

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed

def check_for_duplicates(paths):
    """Compares files to find duplicates"""
    hashes_by_size = defaultdict(list)
    hashes_on_1k = defaultdict(list)
    hashes_full = {}
    duplicates = defaultdict(list)

    for path in paths:
        for dirpath, _, filenames in os.walk(path):
            # get all files that have the same size - they are the collision candidates
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                try:
                    # if the target is a symlink (soft one), this will
                    # dereference it - change the value to the actual target file
                    full_path = os.path.realpath(full_path)
                    file_size = os.path.getsize(full_path)
                    hashes_by_size[file_size].append(full_path)
                except (OSError,):
                    continue

    # For all files with the same file size, get their hash on the 1st 1024 bytes only
    for size_in_bytes, files in hashes_by_size.items():
        if len(files) < 2:
            continue

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
                hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
            except (OSError,):
                continue

    # For all files with the hash on the 1st 1024 bytes, get their hash on the full file
    for __, files_list in hashes_on_1k.items():
        if len(files_list) < 2:
            continue

        for filename in files_list:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
                duplicate = hashes_full.get(full_hash)
                if duplicate:

                    if not filename in duplicates[full_hash]:
                        duplicates[full_hash].append(filename)

                    if not duplicate in duplicates[full_hash]:
                        duplicates[full_hash].append(duplicate)
                else:
                    hashes_full[full_hash] = filename
            except (OSError,):
                continue

    # Returns only duplicates list, discarding hashes
    return [duplicate for (_, duplicate) in duplicates.items()]

def sort_by_paths(duplicates, paths):
    """Sorts a given list of duplicates by path, defining wich file will be kept"""
    sorted_files = []

    for path in paths:

        # Gets set of files contained in each path
        full_path = os.path.abspath(path)
        files_in_path = [file for file in duplicates if file.find(full_path) != -1]

        # Sort them by path specificity
        files_in_path = sorted(files_in_path, key=lambda t: t.count('\\'), reverse=True)
        sorted_files.append(files_in_path)

    # Joins all paths sublists and returns
    return [item for sublist in sorted_files for item in sublist]

def manual_confirm(file):
    """Confirms file deletion and removes input message"""
    result = input("Confirm deletion of " + file + "? (y/n): ") == 'y'
    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line
    return result

def solve_duplicates(duplicates, move_path=None, copy_path=None, delete_duplicates=False,
                     auto_confirm=False):
    """ Allows removing, copying and moving duplicated files, always keeping the first file
    on ghe list"""

    count = 1
    for file in duplicates:

        if count == 1:
            # Always keep first file
            print(
                stylize(count, colored.fg("white")),
                stylize(file, colored.fg("green"))
                )

        else:
            # If the user wants to delete duplicates
            if delete_duplicates:

                delete_success = False
                if auto_confirm or manual_confirm(file):
                    try:
                        os.remove(file)
                        delete_success = True
                    except (OSError,):
                        continue

                print(
                        stylize(count, colored.fg("white")),
                        stylize(file, colored.fg("red" if delete_success else "blue")),
                        "has been deleted!" if delete_success else "kept!"
                        )

            # If the user wants to move duplicates
            elif move_path is not None:

                move_path = os.path.abspath(move_path)

                # Gets target path
                for full_path in full_paths:
                    if file.find(full_path) != -1:
                        target_path = file.replace("\\".join(full_path.split("\\")[:-1]), move_path)

                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.move(file, target_path)

                print(
                        stylize(count, colored.fg("white")),
                        stylize(file, colored.fg("red")),
                        "moved to",
                        stylize(target_path, colored.fg("blue")),
                        )
            # If the user wants to copy duplicates
            elif copy_path is not None:

                copy_path = os.path.abspath(copy_path)

                # Gets target path
                for full_path in full_paths:
                    if file.find(full_path) != -1:
                        target_path = file.replace("\\".join(full_path.split("\\")[:-1]), copy_path)

                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy(file, target_path)

                print(
                        stylize(count, colored.fg("white")),
                        stylize(file, colored.fg("red")),
                        "copied to",
                        stylize(target_path, colored.fg("blue")),
                        )
            # Otherwise, just print duplicates names
            else:
                print(
                        stylize(count, colored.fg("white")),
                        stylize(file, colored.fg("blue")),
                        "is duplicate"
                        )

        count += 1


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

    duplicate_set = check_for_duplicates(PATHS)

    full_paths = list(map(lambda p: os.path.abspath(p), PATHS))

    # For each duplicate set
    for duplicate_list in duplicate_set:

        sorted_list = sort_by_paths(duplicate_list, PATHS)

        solve_duplicates(sorted_list, MOVE_PATH, COPY_PATH, DELETE_DUPLICATES, AUTO_CONFIRM)
        print("")

    print(stylize("     " + str(len(duplicate_set)) + " duplicates found!     ", 
          colored.bg("green")))
