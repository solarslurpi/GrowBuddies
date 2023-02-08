from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import io
import random

def check_zipfile(zip_file):
    with ZipFile(zip_file) as zf:
        names = zf.namelist()
        # Verify that the contents of the zip file is an image.
        # First select a random filename from the names list.
        image_name = random.choice(names)
        # Load the image into a buffer.
        image_buffer = zf.read(image_name)
        # Check if the image is a JPEG image.
        try:
            # io.BytesIO creates a binary stream from the contents of the buffer .
            image = Image.open(io.BytesIO(image_buffer))
            if image.format != 'JPEG':
                raise ValueError('The image format is not JPEG.')
            image.show(image_name)
        except IOError:
            raise ValueError('The contents of the buffer are not a valid image.')
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

# zip_file = "drgb.zip"
# jpg_count = check_zipfile(zip_file)
# for key, value in jpg_count.items():
#     print(f"Key: {key}, Value: {value}")
#------------------------------------------------------------------------------------------------------
def pull_out_images(zip_filepath="drgb.zip", categories=["healthy","powdery_mildew"],nImages_per_directory=10):

    # open the zip file
    filepaths = {}
    with ZipFile(zip_filepath, 'r') as zip_ref:
        all_filepaths = zip_ref.namelist()
        for category in categories:
            filepaths[category] = [filepath for filepath in all_filepaths if category in filepath]
            filepaths[category] = random.sample(filepaths[category], nImages_per_directory)
            # Make a new directory for the category under the datasets directory. Create the datasets directory if it doesn't exist.    
            # Copy the files in filepaths to the target directory.
            [zip_ref.extract(filepath) for filepath in filepaths[category]]

# pull_out_images()
# print("Done")
