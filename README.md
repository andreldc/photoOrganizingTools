# Photo Organizing Tools - by Andreldc

A collection of scripts that I use to organize my photos.

## Requirements & Installation

1. Install Python 3.8 from - https://www.python.org/downloads/

2. Create virtual Env:
            
        python3 -m venv env

3. Enable virtual Env (Windows PowerShell):
  
        ./env/Scripts/activate

4. Install dependencies:
        
        pip install -r requirements.txt



## Tools:
   
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
    


