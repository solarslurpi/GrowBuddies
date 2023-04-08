# Dr GrowBuddy
- [colab notebook with data pre-processing learnings](https://colab.research.google.com/github/solarslurpi/GrowBuddies/blob/main/growbuddiesproject/growbuddies/drgrowbuddy/data_preprocessing_learnings.ipynb)

## Data Sources

[PlantDoc dataset](https://github.com/pratikkayal/PlantDoc-Dataset)
- this dataset doesn't look that great...
[Plant Leaf dataset](https://data.mendeley.com/datasets/tywbtsjrjv/1)
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), “Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network”, Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1


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


[Deep Learning research papers that include code](https://paperswithcode.com/sota)

I am not Daniel Bourke however I can give you maybe an example how you can achieve your goal (from my naive point of view).
The "easiest" example of such a "model" is probably something like this.
model layers:

CNN layers /block (You should probably use transfer learning and use something like EFFNETB0)
Transformer/ LSTM etc. (Again you should probably use transfer learning)
Flatten layer
Classifier (output_size = 2)
Now how can be combine the information???
I would probably do this during the forward pass (similar to what we have learned during the Transfer learning module)
For example (pure pseudo):

def forward(self, x,y):
image_infos = torch.select(input, dim, index) depending on your data
text_info = torch.select(input, dim, index) depending on your data
then you can use the CNN layer for your image data
image_infos_after_cnn = self.CNN_layers(image_infos) (but please turn of the gradient if you use transfer learning)
text_info_after_transformer = self.transformer(text_info) (but please turn of the gradient if you use transfer learning)
(then you can combine the using something like )
combined_text_and_image = torch.cat(image_infos_after_cnn, text_info_after_transformer, dim = 0)
Now you have both information in one tensor!! Finally, you can use your flatten layer and the classifier layer to classify if a plant has a Nitrogen deficiency.

return self.classifier( self.flatten(combined_text_and_image, start_dim = suitable, end_dim = suitable))

Additional remarks:

This probably a way to simple model, but I hope this gives you an idea how to combine different types of inputs and how to combine different types of inputs using torch.cat().
One simple improvement to this model that I can give you is that you should probably use some batch normalization before you use torch.cat()
PS: I hope this was helpful.