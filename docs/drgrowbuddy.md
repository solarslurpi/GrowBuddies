# Dr GrowBuddy

## Data Sources

[PlantDoc dataset](https://github.com/pratikkayal/PlantDoc-Dataset)
[Plant Leaf dataset](https://data.mendeley.com/datasets/tywbtsjrjv/1)
[Plant Village dataset](https://knowyourdata-tfds.withgoogle.com/#tab=STATS&dataset=plant_village)

See other data sets. Seems to be many plant leaves. https://knowyourdata-tfds.withgoogle.com/


Data from a bing search in Python:
```
!pip install bing-image-downloader
!mkdir images
from bing_image_downloader import downloader

downloader.download("healthy green cannabis plant", limit=5, output_dir='images', adult_filter_off=True, force_replace=False)
```

Used to be google_image_downloader ... no longer works...asd@123qwe
