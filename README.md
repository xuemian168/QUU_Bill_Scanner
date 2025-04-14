# QUU Water Bill Data Extractor

A Python script to extract data from Queensland Urban Utilities (QUU) water bills in PDF format. This tool helps you analyze water usage and billing information across multiple bills.

## ⚠️ Important PDF Requirements

- The bill information **MUST** be on the first page of the PDF
- Only standard QUU water bill format is supported
- PDF files must not be password-protected or secured
- Each PDF should contain only one bill

## Features

- Extracts key information from QUU water bills:
  - Property address details
  - Total amount due
  - Due date
  - Water usage (kL)
  - Days charged
  - Current period daily usage
  - Last year's daily usage comparison
- Processes multiple PDF bills at once
- Exports data to CSV format for easy analysis
- Supports debug mode for troubleshooting
- Handles different address formats (MACGREGOR, SUNNYBANK HILLS)

## Requirements

- Python 3.6 or higher
- PyPDF2 library

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your QUU PDF bills in a directory
2. Run the script with the directory path:
```bash
python main.py <directory_path>
```

For example:
```bash
python main.py "QUU_Bill_Apr14"
```

## Output

The script generates a CSV file with the following information for each bill:
- Filename
- Full address
- Street number
- Street name
- Suburb
- Postcode
- Total amount due
- Due date
- Water usage (kL)
- Days charged
- Current period daily usage
- Last year daily usage

The output file is named `water_usage_data_YYYYMMDD_HHMMSS.csv` with the current timestamp.

## Example Output Format

```csv
filename,full_address,street_number,street_name,suburb,postcode,total_due,due_date,water_usage_kl,days_charged,current_period_daily_usage,last_year_daily_usage
EXAMPLE_STREET_123.pdf,123 EXAMPLE STREET SUBURB 4000,123,EXAMPLE STREET,SUBURB,4000,150.75,01/05/2024,12,90,133,120
```

## Troubleshooting

If the script fails to extract data:
1. Make sure your PDF files are readable and not password-protected
2. Check if the PDF files follow the standard QUU bill format
3. Verify that the bill information is on the first page of the PDF
4. Run the script with debug mode enabled to see detailed extraction information

## Notes

- The script is specifically designed for QUU water bills
- PDF files should be readable and not password-protected
- Large PDF files may take longer to process
- The script uses regular expressions to extract data, so any significant changes to the QUU bill format may require updates to the patterns
- Only processes the first page of each PDF file
- Multi-page PDFs are supported but only if the bill information is on the first page

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
