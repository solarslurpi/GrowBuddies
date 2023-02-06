import zipfile
import re
from colorama import init as colorama_init, Fore, Style
#_______________________________________________________
def check_zipfile(zip_file):
    """
    check_zipfile is part of the Dr GrowBuddy pipeline.  A prior data pre-processing
    step is to transfer the images from the original dataset into a zip file structured
    similar to the following:
    datasets/
    |-- class_name_1/
    |   |-- image001.jpg
    |   |-- image002.jpg
    |-- class_name_2/
        |-- image003.jpg
        |-- image004.jpg

    Where class_name_x are the names of the image category classes and imagexxx.jpg are 
    the images in the dataset.  This function checks that the zip file is structured
    correctly and returns the names of the directories and the number of images in each 
    directory.
    """
    colorama_init()
    with zipfile.ZipFile(zip_file) as archive:
        names = archive.namelist()
        directories = set()
        print(f"{Fore.YELLOW}directories: {directories}{Style.RESET_ALL}")
        for name in names:
            if not name.endswith(".jpg"):
                raise ValueError(f"{Fore.RED}Error {name} does not end in .jpg. Was the zip file created with the Python script `transfer_files.py`{Style.RESET_ALL}")
            components = name.split("/")[:-1]
            if len(components) > 2:
                raise ValueError(f"{Fore.RED}Directory structure is deeper than 2 levels: {name}{Style.RESET_ALL}")
            for i in range(len(components)):
                directories.add("/".join(components[:i + 1]))
                print(f"{Fore.GREEN}directories: {directories}{Style.RESET_ALL}")
        jpg_count = {}
        for directory in directories:
            jpg_count[directory] = len([name for name in names if name.startswith(directory) and name.endswith(".jpg")])
        return sorted(list(directories)), jpg_count

zip_file = "datasets.zip"
directories, jpg_count = check_zipfile(zip_file)
print(f"Done. \n-----\n{len(directories)} directories found.")
for directory in directories:
    print(f"  - {directory}: {jpg_count[directory]} .jpg files")
