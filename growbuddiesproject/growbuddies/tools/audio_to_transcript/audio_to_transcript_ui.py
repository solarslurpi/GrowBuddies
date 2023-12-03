
import argparse
from audio_to_transcript import AudioToTranscript
import os
# import youtube_dl  # Assuming youtube_dl is used for downloading audio from YouTube

# Function to parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert audio files to transcripts.")
    # parser.add_argument("--youtube_url", type=str, help="YouTube Video or Playlist URL", required=False)
    parser.add_argument("--mp3_filename", type=str, help="MP3 file path for transcription", required=False)
    parser.add_argument("--transcript_folder", type=str, help="Folder path to save transcripts", required=True)
    return parser.parse_args()

# def download_youtube_audio(youtube_url, download_folder):
#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'outtmpl': download_folder + '/%(title)s.%(ext)s',
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#         }],
#     }
#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([youtube_url])
#         info = ydl.extract_info(youtube_url, download=False)
#         return os.path.join(download_folder, info['title'] + '.mp3')
def progress_update(message, progress_percentage):
    print(f"{message} Progress: {progress_percentage}%")

def main():
    args = parse_arguments()

    # Validate if the transcript folder exists
    if not os.path.exists(args.transcript_folder):
        print(f"Transcript folder {args.transcript_folder} does not exist. Creating it.")
        os.makedirs(args.transcript_folder)

    # Create an instance of AudioToTranscript
    audio_transcriber = AudioToTranscript(progress_callback=progress_update)

    # Check if YouTube URL is provided and download the audio
    # if args.youtube_url:
    #     print(f"Downloading audio from YouTube URL: {args.youtube_url}")
    #     mp3_filename = download_youtube_audio(args.youtube_url, args.transcript_folder)
    #     audio_transcriber.transcribe(mp3_filename, args.transcript_folder)

    # Check if MP3 file is provided
    if args.mp3_filename:
        print(f"Transcribing MP3 file: {args.mp3_filename}")
        audio_transcriber.transcribe(args.mp3_filename, args.transcript_folder)

if __name__ == "__main__":
    main()
