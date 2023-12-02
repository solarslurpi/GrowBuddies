
import streamlit as st
from ui_pickers import pick_directory, pick_file
from audio_to_transcript import AudioToTranscript

# Initialize session state
if 'transcript_folder' not in st.session_state:
    st.session_state.transcript_folder = ""

if 'mp3_filename' not in st.session_state:
    st.session_state.mp3_filename = ""

# Title of the app
st.title("Streamlit UI")

# Input for YouTube video or playlist URL
youtube_url = st.text_input("YouTube Video or Playlist URL")

# File uploader for mp3 files
mp3_file_button = st.button("Choose an mp3 file")

# Input for Transcript Folder
transcript_dir_button = st.button("Set Transcript Directory")

start_transcribe_button = st.button("Start")

if transcript_dir_button:
    #st.session_state.transcript_folder = pick_directory()
    transcript_folder = pick_directory()
    st.session_state.transcript_folder = transcript_folder
    st.success(f"Transcript Directory: {st.session_state.transcript_folder}")
    print(f"Transcript Directory: {st.session_state.transcript_folder}")

if mp3_file_button:
    mp3_filename = pick_file()
    st.session_state.mp3_filename = mp3_filename
    st.success(f"mp3 filename: {st.session_state.mp3_filename}")

if st.session_state.mp3_filename is not None and st.session_state.transcript_folder is not None and start_transcribe_button:
    cancel_button = st.button("Cancel Download")
    audio_to_transcript = AudioToTranscript()
    audio_to_transcript.transcribe(st.session_state.mp3_filename, st.session_state.transcript_folder, cancel_button)
    st.write("Processing is complete.")

    


