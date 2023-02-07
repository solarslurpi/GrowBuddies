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
        jpg_count = {}
        for directory in directories:
            jpg_count[directory] = len([name for name in names if name.startswith(directory) and name.endswith(".jpg")])
        return sorted(list(directories)), jpg_count

zip_file = "drgb.zip"
directories, jpg_count = check_zipfile(zip_file)
print(f"Done. \n-----\n{len(directories)} directories found.")
for directory in directories:
    print(f"  - {directory}: {jpg_count[directory]} .jpg files")
