
from sp_processor import SPProcessor
# from m3_processor import M3Processor
import pdfplumber  # Assuming you're using pdfplumber to read PDFs

class PDFProcessorFactory:
    @staticmethod
    def get_processor(pdf_file):
        # Implement logic to determine the type of PDF
        with pdfplumber.open(pdf_file) as pdf:
            # Example condition, replace with actual logic
            if "some condition for SP":
                return SPProcessor()
            else:
                # return M3Processor()
                pass
