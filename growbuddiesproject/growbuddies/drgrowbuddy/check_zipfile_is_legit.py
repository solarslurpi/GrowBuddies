import zipfile
import colors

def check_zipfile(zip_file):
    with zipfile.ZipFile(zip_file) as archive:
        names = archive.namelist()
        directories = set()
        for name in names:
            if not name.endswith(".jpg"):
                raise ValueError(f"{colors.Red}Error {name} does not end in .jpg. Was the zip file created with the Python script `transfer_files.py`{colors.Original}")
            components = name.split("/")[:-1]
            if len(components) > 2:
                raise ValueError(f"{colors.Red}Directory structure is deeper than 2 levels: {name}{colors.Original}")
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
