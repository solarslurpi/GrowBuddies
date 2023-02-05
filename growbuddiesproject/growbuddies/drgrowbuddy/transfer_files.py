from pathlib import Path
from PIL import Image
import re
import hashlib
from colorama import init as colorama_init, Fore, Style

def transfer_files(src_dir: str = None, target_dir: str = None, size: tuple = (256, 256)):
    """
    This function transfers all files containing downloaded images, including subdirectories, from the source directory to the target directory.
    It's particularly useful in combination with the `bbid.py` script. The following operations are performed:
        - PNG and WEBP files are converted to JPG
        - MOV files are skipped
        - Files that already exist in the target directory are skipped
        - Images are saved to the size specified by the `size` argument.
    The transferred files are named "image_XXX.jpg", where XXX is a zero-padded incremental number based on the highest
    number of existing image files in the target directory.
    
    Arguments:
        src_dir (str): Path to the source directory.
        target_dir (str): Path to the target directory.
        size (tuple): The size to which the images are resized.

    Returns:
        None
    """
    colorama_init()
    src_path = Path(src_dir)
    target_path = Path(target_dir)
    target_path.mkdir(exist_ok=True)
    # Get the last number of an existing image file
    max_number = 0
    existing_images = [img for img in target_path.glob("image_*")]
    existing_image_hashes = []
    if existing_images:
        # Set the max_number to the highest number of an existing image file.
        max_number = max([int(re.search(r"(\d+)", img.name).group(1)) for img in existing_images])
        # Get the md5 hash of the existing image files. This way, we can avoid copying duplicate files.
        existing_image_hashes = [hashlib.md5(img.read_bytes()).hexdigest() for img in existing_images ]
    # Set up filters for handling the files to be copied.
    png_pattern = re.compile(r'\.png$', re.IGNORECASE)
    mov_pattern = re.compile(r'\.mov$', re.IGNORECASE)
    jpg_pattern = re.compile(r'\.(jpeg|jpg)$', re.IGNORECASE)
    webp_pattern = re.compile(r'\.webp$', re.IGNORECASE)
    
    for item in src_path.iterdir():
        if hashlib.md5(item.read_bytes()).hexdigest() in existing_image_hashes: 
            print(f"{Fore.YELLOW}Skipping {item}.  The image already exists in the target directory.{Style.RESET_ALL}")
            continue
        max_number += 1
        if item.is_dir():
            transfer_files(item, target_path / item.name)
        else:
            target_file = target_path / f"image_{max_number:03d}.jpg" 
            if mov_pattern.search(item.suffix):
                print(f"{Fore.YELLOW}Skipping {item} because it is a movie file.{Style.RESET_ALL}")
                continue
            elif jpg_pattern.search(item.suffix):
                # Copy both the data and metadata to the target file.
                # Resize
                with Image.open(item) as im:
                    im = im.resize(size, Image.LANCZOS)
                    im.save(target_file)
                print(f"{Fore.GREEN}Copying {item} to {target_file} and resized to {size}{Style.RESET_ALL}")
            elif png_pattern.search(item.suffix) or webp_pattern.search(item.suffix):
                # Convert the png file to jpg
                with Image.open(item) as im:
                    rgb_img = Image.open(item).convert('RGB').resize(size, Image.LANCZOS)
                    rgb_img.save(target_file,"jpeg")
                print(f"{Fore.BLUE}Converted {item} to {target_file} and resized to {size}{Style.RESET_ALL}")
            else:
                print (f"{Fore.RED}Unknown file type: {item}.  Skipping...{Style.RESET_ALL}")
                continue   
            

if __name__ == "__main__":
    transfer_files(src_dir="datasets/powdery_mildew_downloads", target_dir="datasets/powdery_mildew_256")

