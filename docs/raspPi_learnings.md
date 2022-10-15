# raspPi_learnings

## Why This Page
As I do projects, I'll use commands here and there unique to a platform - in this case Raspberry Pi/Linux - that I don't use very much.  I'm listing commands and flows I found useful when bumbling about on the Raspberry Pi.

## Using Rsync to Copy Files from Rasp Pi to Another Computer
Currently I am on a Windows PC.  The challenge is to start an Bash session in the right directory.
- open Explorer, go to the directory to use rsync, type in bash in the text field for the filepath.

:::{figure} images/explorer_with_bash.jpg
:align: center
:scale: 100

Getting to Bash Command Line Through Explorer
:::


A wsl window will open at this location.
```
sudo rsync -avh pi@growbuddy:/home/pi/growbuddy_1_data.zip  .

```