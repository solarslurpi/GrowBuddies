from pathlib import Path
from zipfile import ZipFile
import random

def check_zipfile(zip_file):
    with ZipFile(zip_file) as archive:
        names = archive.namelist()
        directories = set()
        for name in names:
            if not name.endswith(".jpg"):
                raise ValueError(f"Error {name} does not end in .jpg. Was the zip file created with the Python script `transfer_files.py`")
            components = name.split("/")[:-1]
            if len(components) > 2:
                raise ValueError(f"Directory structure is deeper than 2 levels: {name}")
            for i in range(len(components)):
                directories.add("/".join(components[:i + 1]))

        base_directory = "datasets"
        categories = [directory.split("/")[1] for directory in directories if directory != base_directory and directory.startswith(base_directory + "/")]

        jpg_count = {}
        for category in categories:
            jpg_count[category] = len([name for name in names if category in name])
        return jpg_count

#zip_file = "drgb.zip"
#jpg_count = check_zipfile(zip_file)
#for key, value in jpg_count.items():
#    print(f"Key: {key}, Value: {value}")
#------------------------------------------------------------------------------------------------------
# specify the zip file and the target directory
def pull_out_images(zip_filepath="drgb.zip", categories=["healthy","powdery_mildew"], nImages_per_directory=10):

    # open the zip file
    filepaths = {}
    with ZipFile(zip_filepath, 'r') as zip_ref:
        all_filepaths = zip_ref.namelist()
        for category in categories:
            filepaths[category] = [filepath for filepath in all_filepaths if category in filepath]
            filepaths[category] = random.sample(filepaths[category], nImages_per_directory)
            # Make a new directory for the category under the datasets directory. Create the datasets directory if it doesn't exist.    
            target_dir = Path("datasets") / category
            target_dir.mkdir(parents=True, exist_ok=True)
            # Copy the files in filepaths to the target directory.
            [zip_ref.extract(filepath, target_dir) for filepath in filepaths[category]]

# pull_out_images()
# print("Done")