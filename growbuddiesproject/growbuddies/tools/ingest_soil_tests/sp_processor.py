from base_processor import BaseProcessor
from growbuddies_config import soil_results_config
import pandas as pd
import pdfplumber
from pydantic import BaseModel, validator

class SaturatedPasteValues(BaseModel):
    pH: float
    Soluble_Salts: float
    Chloride: float
    Bicarbonate: float
    Sulfur: float
    Phosphorous: float
    Calcium_ppm: float
    Calcium_meq: float
    Magnesium_ppm: float
    Magnesium_meq: float
    Potassium_ppm: float
    Potassium_meq: float
    Sodium_ppm: float
    Sodium_meq: float
    Calcium_percent: float
    Magnesium_percent: float
    Potassium_percent: float
    Sodium_percent: float
    Boron: float
    Iron: float
    Manganese: float
    Copper: float
    Zinc: float
    Aluminum: float
    timestamp: int

    @validator('*', pre=True)
    def check_nan(cls, v):
        if pd.isna(v):
            raise ValueError('Value cannot be NaN')
        return v

class SPProcessor(BaseProcessor):
    def __init__(self, pdf_file: str) -> None:
        super().__init__(pdf_file)
        self._measurement_name = "SP"

    def process_pdf(self, pdf_file: str) -> None:
        with pdfplumber.open(pdf_file) as pdf:
            table = pdf.pages[0].extract_table()
        # As we process the pdfs, we put field names and values into this list.
        field_names = []
        values = []
        # Reset the current field name for the new logic
        current_field_name = None
          # Iterate over each row in the data
        for i, row in enumerate(table):
            field_name, value, unit = None, None, None

            # For the first eight rows, take the field name from the first column
            if i < 8:
                field_name = row[0]
                if field_name in soil_results_config.get("readings_to_exclude"):
                    continue
                value = row[3]
            # From the eighth row on, the field name could be in the second column
            else:
                # If the second column is not None or empty, take the field name from there
                if row[1]:
                    current_field_name = row[1]  # Update the current field name
                    field_name = current_field_name
                    unit = row[2]
                # If the second column is None or empty, but the third column has 'meq/l', use the current field name
                elif row[2] == 'meq/l':
                    field_name = f"{current_field_name} (meq/l)"
                    unit = row[2]
                # Otherwise, it might be a continuation of the previous field without a unit
                else:
                    continue
                
                value = row[3] if row[3] else None  # Take the value from the fourth column
                
                # If there is a unit, append it to the field name unless it's already there
                if unit and unit.strip() not in field_name:
                    field_name += f" ({unit.strip()})"

            # If there is a field name and a value, add them to the processed data
            if field_name and value:
                # Get rid of potentical commas (,) in the values.
                value = value.replace(",", "")
                field_names.append(soil_results_config.get("name_mapping").get(field_name, field_name))
                values.append(value)

        df = self._build_dataFrame(field_names, values, pdf_file)
        self._store_pdf("SP", df, pdf_file)

    @property
    def measurement_name(self):
        return self._measurement_name

# sp = SPPDFProcessor("/Users/happy/Documents/KISBuddy/code/soil_samples/SP/paste_report_Logan_Labs_6_30_2022.pdf")
# sp.start()