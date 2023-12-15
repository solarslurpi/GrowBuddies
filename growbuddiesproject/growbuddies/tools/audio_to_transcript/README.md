
# audio_to_transcript
The idea behind `audio_to_transcript` is to be able to capture the knowledge of domain experts who have either made a podcast, I have had a conversation with that is recorded, or made YouTube videos.  Once the audio is captured within:
- YouTube playlists (code there, not merged in)
- YouTube video (code there, not merged in)
- Folder of mp3 files (not implemented)
- a single mp3 file
This code will use `FasterWhisper` to translate the file into a high fidelity transcript.  From that, I can use ChatGPT to gather out the main talking points and put these talking points within a file I can subsequently use for RAG LLM inference or LLM training.
## audio_to_transcript_ui.py
This Python script serves as a command-line interface for an audio trans
# audio_to_transcript
The idea behind `audio_to_transcript` is to be able to capture the knowledge of domain experts who have either made a podcast, I have had a conversation with that is recorded, or made YouTube videos.  The audio source can be:
- YouTube playlists (not tested)
- YouTube video 
- Folder of mp3 files (not implemented)
- a single mp3 file
This code will use [`FasterWhisper`](https://github.com/SYSTRAN/faster-whisper) to translate the file into a high fidelity transcript.  From that, I can use ChatGPT4 to gather out the main talking points and put these talking points within a file I can subsequently use for RAG LLM inference or LLM training.

# audio_to_transcript_ui.py
This Python script serves as a command-line interface for an audio transcription application. It utilizes the `AudioToTranscript` module for transcription and employs `argparse` for parsing command-line arguments.

Arguments:
- --mp3_filename (optional): Specifies the path to the MP3 file for transcription.
- --transcript_folder (required): Designates the folder path where the transcripts will be saved. This argument is mandatory.
- --youtube_url (optional): Allows the user to input a YouTube video or playlist URL for downloading and transcribing audio. This feature is currently commented out, indicating potential future functionality.

The script's primary function, `parse_arguments()`, sets up these arguments. The main workflow includes validating the existence of the transcript folder, creating an `AudioToTranscript` instance, and handling the transcription process based on the provided arguments. While the `youtube_url` argument is prepared for future use, the current focus is on transcribing local MP3 files.

Example Usage:
1. Transcribing a local MP3 file:
   python audio_to_transcript_ui.py --mp3_filename "/path/to/audiofile.mp3" --transcript_folder "/path/to/transcript_folder"

2. (Future functionality) Transcribing audio from a YouTube URL:
   python audio_to_transcript_ui.py --youtube_url "https://www.youtube.com/watch?v=example" --transcript_folder "/path/to/transcript_folder"

# audio_to_transcript.py
This module, `audio_to_transcript.py`, contains the class `AudioToTranscript` used for transcribing audio files. It leverages the `WhisperModel` from the `faster_whisper` module for efficient transcription.

Key Features:
- Initialization with optional `model_size`, `compute_type`, and `progress_callback` parameters. It validates the `model_size` against predefined `MODEL_SIZES` and `compute_type` against `COMPUTE_TYPES`.
- The `transcribe` method handles the transcription process. It accepts `audio_file_or_dir` (either a single audio file or a directory of audio files) and `transcript_folder` for saving the transcriptions. The method validates the input audio source, loads the Whisper model, and processes each audio file for transcription.
- Private methods like `_set_audios_list` and `_process_audio_file` are used for listing audio files and processing each audio file, respectively.
- The `_figure_percent_complete` method calculates the transcription progress percentage based on the elapsed time and a predefined typical transcription time. This information can be sent back to the caller for display if the caller has included a callback function.

Usage:
- Initialize an instance of `AudioToTranscript` with desired model and compute type.
- Call the `transcribe` method with the path to the audio file(s) and the transcript folder.
- See `audio_to_transcript_ui.py` for an example.

Note: The module assumes the presence of a working `WhisperModel` for transcription and includes progress reporting functionality, which can be integrated with a callback function for real-time updates.
"""
# Instructions on Use
- clone the GrowBuddies project or download the following files into a directory:
   - audio_to_transcript.py
   - audio_to_transcript_ui.py
   - common.py
   - requirements.txt
- create a virtual environment within this directory.  I use venv:
```
python -m venv .venv
```
- install the libraries
```
pip install -r requirements.txt
```
## CUDA Support
The Windows PC I use has an NVidia Graphics card.  In `audio+to+transcript.py`, the Whisper model is loaded by telling it whether you want CUDA support or not.  Here is how it is currently implemented:
```
model = WhisperModel(self.model_name, compute_type=self.compute_type, device="cuda")
```
For cuda support, as noted in [Faster Whisper's GitHub](https://github.com/SYSTRAN/faster-whisper?tab=readme-ov-file#gpu), the cuBLAS and cuDNN libraries for CUDA 11 are required (at least as of this writing). If you want to use a GPU, make sure all the dlls are available within your PATH environment variable.cription application. It utilizes the `AudioToTranscript` module for transcription and employs `argparse` for parsing command-line arguments.

Arguments:
- --mp3_filename (optional): Specifies the path to the MP3 file for transcription.
- --transcript_folder (required): Designates the folder path where the transcripts will be saved. This argument is mandatory.
- --youtube_url (optional): Allows the user to input a YouTube video or playlist URL for downloading and transcribing audio. This feature is currently commented out, indicating potential future functionality.

The script's primary function, `parse_arguments()`, sets up these arguments. The main workflow includes validating the existence of the transcript folder, creating an `AudioToTranscript` instance, and handling the transcription process based on the provided arguments. While the `youtube_url` argument is prepared for future use, the current focus is on transcribing local MP3 files.

Example Usage:
1. Transcribing a local MP3 file:
   python audio_to_transcript_ui.py --mp3_filename "/path/to/audiofile.mp3" --transcript_folder "/path/to/transcript_folder"

2. (Future functionality) Transcribing audio from a YouTube URL:
   python audio_to_transcript_ui.py --youtube_url "https://www.youtube.com/watch?v=example" --transcript_folder "/path/to/transcript_folder"

## audio_to_transcript.py
This module, `audio_to_transcript.py`, contains the class `AudioToTranscript` used for transcribing audio files. It leverages the `WhisperModel` from the `faster_whisper` module for efficient transcription.

Key Features:
- Initialization with optional `model_size`, `compute_type`, and `progress_callback` parameters. It validates the `model_size` against predefined `MODEL_SIZES` and `compute_type` against `COMPUTE_TYPES`.
- The `transcribe` method handles the transcription process. It accepts `audio_file_or_dir` (either a single audio file or a directory of audio files) and `transcript_folder` for saving the transcriptions. The method validates the input audio source, loads the Whisper model, and processes each audio file for transcription.
- Private methods like `_set_audios_list` and `_process_audio_file` are used for listing audio files and processing each audio file, respectively.
- The `_figure_percent_complete` method calculates the transcription progress percentage based on the elapsed time and a predefined typical transcription time. This information can be sent back to the caller for display if the caller has included a callback function.

Usage:
- Initialize an instance of `AudioToTranscript` with desired model and compute type.
- Call the `transcribe` method with the path to the audio file(s) and the transcript folder.
- See `audio_to_transcript_ui.py` for an example.

Note: The module assumes the presence of a working `WhisperModel` for transcription and includes progress reporting functionality, which can be integrated with a callback function for real-time updates.
"""

