# The goal of this class is to convert audios (I'm assuming mp3's) into transcripts and then save the transcripts into a file.

import glob
import os
import time
from faster_whisper import WhisperModel
import streamlit as st
from common import MODEL_SIZES, COMPUTE_TYPES

TYPICAL_TRANSCRIPTION_TIME = 10 * 60 

class AudioToTranscript:
    def __init__(self, model_name="large-v2", compute_type="int8"):
        self.model_name = model_name
        if self.model_name not in MODEL_SIZES:
            raise f"model should be one of {MODEL_SIZES}"
        self.compute_type = compute_type
        if self.compute_type not in COMPUTE_TYPES:
            raise (f"compute type should be one of {COMPUTE_TYPES}")

    def transcribe(
        self, audio_file_or_dir=None, transcript_folder=None, cancel_flag=None):
        progress_bar = st.progress(0, text="Let's Begin.")
        start_time = time.monotonic()
        audio_files_list = self._set_audios_list(audio_file_or_dir)
        if not audio_files_list:
            st.error("I could not read the list of audio files or directory location.")
            st.stop()
        if not  transcript_folder or not os.path.isdir(transcript_folder):
            st.error("Transcript folder location won't work: {transcript_folder}.")
            st.stop()
        
        progress_bar.progress(self._get_progress(start_time), "Loading the (Faster) Whisper Model." )
        model = WhisperModel(
            self.model_name, device="cuda", compute_type=self.compute_type
        )
        progress_bar.progress(self._get_progress(start_time), "Model has been loaded." )
        #
        # transcribe the audio files
        #
        try:
            for index, audio_filename in enumerate(audio_files_list):
                if cancel_flag:
                    st.warning("Transcibing cancelled.")
                    st.stop()
                # Set the filename transcription will be written to
                name_part = self._get_basename(audio_filename)
                filename = name_part + "-" + self.model_name + ".txt"
                filepath = os.path.join(transcript_folder, filename)
                if not os.path.isfile(filepath):
                    # Faster Whisper returns a tupe
                    progress_bar.progress(self._get_progress(start_time), "Starting transcription")
                    transcription_segments = model.transcribe(audio_filename, beam_size=5)
                    # Initialize an empty string
                    with open(filepath, 'w') as file:
                        segments_generator = transcription_segments[0]
                        batch_size = 100000  
                        batch = []
                        cnt = 0
                        for segment in segments_generator:
                            cnt += 1
                            progress_bar.progress(self._get_progress(start_time), f"Transcribing segment {cnt}" )
                            batch.append(segment.text)
                            if len(batch) >= batch_size:
                                file.write(''.join(batch) )
                                batch = []  # Reset the batch

                        # Write any remaining segments in the final batch
                        if batch:
                            file.write(''.join(batch))
                        progress_bar.progress(self._get_progress(start_time), "Done." )
        except Exception as e:
            st.warning(f"Failed to transcribe audio. Error: {e}.")
            st.stop()

    def _get_basename(self, file):
        base = os.path.basename(file)
        return os.path.splitext(base)[0]
    
    def _set_audios_list(self, file_or_dir=None):
           # check if audios is a directory.  If it is, create
        # a list of audio filenames.
        if os.path.isdir(file_or_dir):
            # Assuming a directory path was entered that contains many audios...
            return glob.glob(os.path.join(file_or_dir, "*"))
        elif isinstance(file_or_dir, str) and not os.path.isdir(file_or_dir):
            # AIf str, but not a folder, assuming string is the filename of an audio file.
            return [file_or_dir]

        return None

    def _get_progress(self, start_time:float) -> float:
        elapsed_time = time.monotonic() - start_time
        progress = elapsed_time/TYPICAL_TRANSCRIPTION_TIME 
        progress = progress if progress < 1.0 else 1.0
        return progress

