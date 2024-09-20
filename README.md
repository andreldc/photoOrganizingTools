# Photo Organizing Tools - by Andreldc

A collection of scripts that I use to organize my photos.

## Requirements & Installation

1. Install Python 3.8 from - <https://www.python.org/downloads/>

2. Install `pipenv`:

        pip install pipenv

3. Create and activate virtual environment:

        pipenv install
        pipenv shell

4. Install dependencies:

        pipenv install --dev

## Tools

1. Scanned photos splitter:

    Splits batch scanned photos into single photos.

        split_scanned_photos.py 

        args:
        [-m MINSIZE] 
        [-ac ADDITIONALCROP] 
        [-mk MEDIANKSIZE] 
        [-t THRESHOLD] 
        [-ck CLOSINGKSIZE] 
        [-q] 
        [-ps PREVIEWSCALE] 
        [-d] 
        path

2. Duplicate files finder:

    Finds duplicate files, allowing its automatic deletion.

        find_duplicates.py 
        
        args:
        [-m MOVE] 
        [-c COPY] 
        [-d] 
        [-y] 
        paths 
        [paths ...]
