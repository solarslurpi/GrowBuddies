from PIL import Image
from pathlib import Path

# scale images to 256x256


def resize_images(dir_in: str = None, dir_out: str = None, size: tuple = (256, 256)):
    """
    Resize all images in a directory.
    """
    if dir_in is None or not Path(dir_in).exists():
        raise ValueError(
            f"The input directory **{dir_in}** does not exist or was not specified."
        )
    if dir_out is None:
        raise ValueError("The output directory was not specified.")
    dir_out_path = Path(dir_out)
    try:
        dir_out_path.mkdir(exist_ok=True)
    except Exception as e:
        print(e)
    # Get the list of all image files in the dataset/healthy directory
    images_path = [img_path for img_path in Path(dir_in).glob("image_*")]
    print(f"Resizing {len(images_path)} images to {size[0]}x{size[1]}...")
    for img_path in images_path:
        # Open the image
        with Image.open(img_path) as im:
            # Resize the image
            im = im.resize(size, Image.LANCZOS)
            # Save the image
            img = dir_out_path / img_path.name
            im.save(img)


def main():
    resize_images(
        dir_in="datasets\healthy", dir_out="datasets\healthy_256", size=(256, 256)
    )
    print("DONE")


if __name__ == "__main__":
    main()
