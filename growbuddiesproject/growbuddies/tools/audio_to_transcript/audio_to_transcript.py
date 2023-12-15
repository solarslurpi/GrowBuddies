
import argparse
from audio_to_transcript import AudioToTranscript
import os
import sys


# Function to parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert audio files to transcripts.")
    parser.add_argument("--youtube_url", type=str, help="YouTube Video or Playlist URL", required=False)
    parser.add_argument("--mp3_filename", type=str, help="MP3 file path for transcription", required=False)
    parser.add_argument("--transcript_folder", type=str, help="Folder path to save transcripts", required=False)
    return parser.parse_args()


def progress_update(message, progress_percentage):
    print(f"{message} Progress: {progress_percentage}%")

def main():
    args = parse_arguments()

    # Validate if the transcript folder exists
    try:
        transcript_folder = args.transcript_folder if args.transcript_folder else os.path.join(os.getcwd(), "transcripts")

        if not os.path.exists(transcript_folder):
            print(f"Transcript folder '{transcript_folder}' does not exist. Creating it.")
            os.makedirs(transcript_folder)
    except OSError as error:
        print(f"Error creating directory '{transcript_folder}': {error}")
        sys.exit(1)
    # Create an instance of AudioToTranscript
    audio_transcriber = AudioToTranscript(progress_callback=progress_update)

    # Check if YouTube URL is provided and download the audio
    if args.youtube_url:
         print(f"Downloading audio from YouTube URL: {args.youtube_url}")
         mp3_filename = audio_transcriber.download_youtube_audio(args.youtube_url, transcript_folder)
         audio_transcriber.transcribe(mp3_filename, transcript_folder)

    # Check if MP3 file is provided
    if args.mp3_filename:
        print(f"Transcribing MP3 file: {args.mp3_filename}")
        audio_transcriber.transcribe(args.mp3_filename, args.transcript_folder)

if __name__ == "__main__":
    main()
