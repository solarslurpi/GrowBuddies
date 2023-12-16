import glob
import streamlit as st
from pdf_processor_factory import PDFProcessorFactory

# from base_processor import BaseProcessor


st.title("Soil Reports Processor")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Directory input
folder_path = st.text_input("Or enter a directory path")



if st.button("Start Processing"):
    if uploaded_file is None and folder_path is None:
        st.error("No file or folder path provided. Please upload a file or provide a folder path.")
    else:
        try:
                        # pdf_file_obj or a list of files is determined in the super init.
            if uploaded_file:
                processor = PDFProcessorFactory.get_processor(uploaded_file)
                processor.process_pdf(uploaded_file)
            else:
                pdf_files = glob.glob(folder_path +'/*.pdf')
                for pdf_file in bp.pdf_files:
                    processor = PDFProcessorFactory.get_processor(pdf_file)
                    processor.process_pdf(uploaded_file)
            st.success("Successful Processing.")
        except Exception as e:
            # Handle any exceptions that occur during processing
            st.error(f"An error occurred during processing: {e}")

