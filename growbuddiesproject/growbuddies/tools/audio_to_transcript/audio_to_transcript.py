import glob
import os
import time
from faster_whisper import WhisperModel
from common import MODEL_SIZES, COMPUTE_TYPES

TYPICAL_TRANSCRIPTION_TIME = (
    15 * 60
)  # Wild guess that the total amount of time it typically takes to audio transcribe is 10 minutes.


class AudioToTranscript:
    def __init__(
        self, model_name="large-v2", compute_type="int8", progress_callback=None
    ):
        self.model_name = model_name
        if self.model_name not in MODEL_SIZES:
            raise ValueError(f"Model should be one of {MODEL_SIZES}")
        self.compute_type = compute_type
        if self.compute_type not in COMPUTE_TYPES:
            raise ValueError(f"Compute type should be one of {COMPUTE_TYPES}")
        self.progress_callback = progress_callback

    def transcribe(self, audio_file_or_dir=None, transcript_folder=None):
        start_time = time.monotonic()
        audio_files_list = self._set_audios_list(audio_file_or_dir)
        if not audio_files_list:
            raise ValueError("No audio files found for transcription.")
        if self.progress_callback:
            progress_percentage = self._figure_percent_complete(start_time)
            self.progress_callback("Loading Whisper Model...",progress_percentage)
        model = WhisperModel(self.model_name, compute_type=self.compute_type)
        if self.progress_callback:
            progress_percentage = self._figure_percent_complete(start_time)
            self.progress_callback("Whisper model has been loaded...",progress_percentage)
        for audio_file in audio_files_list:
            self._process_audio_file(audio_file, transcript_folder, model, start_time)

    def _set_audios_list(self, audio_file_or_dir):
        if os.path.isdir(audio_file_or_dir):
            return glob.glob(os.path.join(audio_file_or_dir, "*.mp3"))
        elif os.path.isfile(audio_file_or_dir):
            return [audio_file_or_dir]
        else:
            raise ValueError("Invalid audio file or directory.")

    def _process_audio_file(self, audio_file, transcript_folder, model, start_time):
        name_part = os.path.splitext(os.path.basename(audio_file))[0]
        transcript_file = os.path.join(transcript_folder, name_part + ".txt")
        transcript_file = transcript_file.replace("\\","/")
        if not os.path.isfile(transcript_file):
            transcription_segments = model.transcribe(audio_file, beam_size=5)
            if self.progress_callback:
                progress_percentage = self._figure_percent_complete(start_time)
                self.progress_callback("Starting transcription of text segments...",progress_percentage)
            cnt =0
            with open(transcript_file, "w") as file:
                segments_generator = transcription_segments[0]
                for segment in segments_generator:
                    file.write(segment.text)
                    cnt += 1
                    if cnt % 10 == 0:
                        if self.progress_callback:
                            progress_percentage = self._figure_percent_complete(start_time)
                            self.progress_callback(f"Processed a total of {cnt} text segments...",progress_percentage)

    def _figure_percent_complete(self, start_time) -> int:
        elapsed_time = time.monotonic() - start_time
        progress_percentage = (elapsed_time / TYPICAL_TRANSCRIPTION_TIME) * 100
        progress_percentage = int(min(progress_percentage, 100))  # Ensure it does not exceed 100%
        return progress_percentage