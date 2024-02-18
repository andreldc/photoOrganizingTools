import os
import shutil
import re
from datetime import datetime
import argparse
def split_files_by_month(directory):
    files = os.listdir(directory)

    # Commom photo and video extensions
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mov', '.avi', '.mp4']
    months_br = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    for file in files:
        if file.endswith(tuple(extensions)):
            file_name, file_extension = os.path.splitext(file)

            # Regular expression to match date in the following formats:
            # IMG-20230310-WA3424.jpg
            # 20231229_152041
            # VID_20231023_172603.mp4
            # 20230511_163955000_iOS.png
            match = re.search(r'(\d{4})(\d{2})(\d{2})', file)

            if match:
                month = match.group(2)
                try:
                    month_directory = os.path.join(directory, f"{month} - {months_br[int(month) - 1]}")
                    os.makedirs(month_directory, exist_ok=True)

                    file_path = os.path.join(directory, file)
                    new_file_path = os.path.join(month_directory, file)

                    shutil.move(file_path, new_file_path)

                    print(f"Moved {file} to {month_directory}")
                except ValueError:
                    print(f"Invalid date format in file {file}")
            else:
                print(f"No date found in file {file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split files by month.')
    parser.add_argument('directory', type=str, help='Directory path')

    args = parser.parse_args()

    split_files_by_month(args.directory)
