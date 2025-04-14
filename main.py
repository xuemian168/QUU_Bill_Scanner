import os
import re
import sys
import csv
from datetime import datetime
from PyPDF2 import PdfReader

def clean_text(text):
    """Clean up the extracted text by adding spaces between words."""
    # Add space between lowercase followed by uppercase
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Add space between number and letter
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
    return text

def extract_info_from_pdf(pdf_path, debug=False):
    """Extract relevant information from the water usage PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = reader.pages[0].extract_text()
        text = clean_text(text)
        
        if debug:
            print("\nDEBUG - Extracted text:")
            print("-" * 50)
            print(text)
            print("-" * 50)
        
        # Dictionary to store extracted information
        info = {}
        info['filename'] = os.path.basename(pdf_path)
        
        # Extract address
        address_pattern = r"Property Location:\s*(\d+)\s*(.*?)\s*(MACGREGOR|SUNNYBANK HILLS)\s*(\d{4})"
        address_match = re.search(address_pattern, text, re.MULTILINE | re.IGNORECASE)
        if address_match:
            info['street_number'] = address_match.group(1).strip()
            info['street_name'] = address_match.group(2).strip()
            info['suburb'] = address_match.group(3).strip()
            info['postcode'] = address_match.group(4).strip()
            info['full_address'] = f"{info['street_number']} {info['street_name']} {info['suburb']} {info['postcode']}"
        
        # Extract total due amount
        due_pattern = r"Total\s*due\s*\$?([\d,]+\.\d{2})"
        due_match = re.search(due_pattern, text, re.IGNORECASE)
        if due_match:
            info['total_due'] = float(due_match.group(1).replace(',', ''))
        
        # Extract due date
        due_date_pattern = r"due\s*date\s*(\d{2}/\d{2}/\d{4})"
        due_date_match = re.search(due_date_pattern, text, re.IGNORECASE)
        if due_date_match:
            info['due_date'] = due_date_match.group(1)
        
        # Extract water usage information with multiple patterns
        water_usage_patterns = [
            r"Water\s*usage.*?(\d+)",
            r"Usage.*?(\d+)",
            r"Water.*?(\d+)\s*kL",
            r"(\d+)\s*kL",
            r"Water\s*usage\s*\(kL\)\s*(\d+)",
            r"Water\s*Usage.*?:\s*(\d+)"
        ]
        
        water_usage_value = None
        for pattern in water_usage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                water_usage_value = int(match.group(1))
                break
        
        if water_usage_value is not None:
            info['water_usage_kl'] = water_usage_value
        elif debug:
            print(f"DEBUG - Could not find water usage in file: {pdf_path}")
            print("Tried patterns:", water_usage_patterns)
        
        # Extract other information
        days_charged_pattern = r"Days\s*charged\s*(\d+)"
        current_period_pattern = r"Current\s*period\s*(\d+)"
        last_year_pattern = r"Same\s*period\s*last\s*year\s*(\d+)"
        
        days_charged_match = re.search(days_charged_pattern, text, re.IGNORECASE)
        current_period_match = re.search(current_period_pattern, text, re.IGNORECASE)
        last_year_match = re.search(last_year_pattern, text, re.IGNORECASE)
        
        if days_charged_match:
            info['days_charged'] = int(days_charged_match.group(1))
        if current_period_match:
            info['current_period_daily_usage'] = int(current_period_match.group(1))
        if last_year_match:
            info['last_year_daily_usage'] = int(last_year_match.group(1))
        
        if debug:
            print("\nDEBUG - Extracted information:")
            for key, value in info.items():
                print(f"{key}: {value}")
        
        return info
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        if debug:
            import traceback
            print(traceback.format_exc())
        return None

def process_directory(directory_path, debug=False):
    """Process all PDF files in the directory and save results to CSV."""
    results = []
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    total_files = len(pdf_files)
    
    print(f"Found {total_files} PDF files to process")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(directory_path, pdf_file)
        print(f"Processing file {i}/{total_files}: {pdf_file}")
        
        info = extract_info_from_pdf(pdf_path, debug=debug)
        if info:
            results.append(info)
    
    return results

def save_to_csv(results, output_file):
    """Save the results to a CSV file."""
    if not results:
        print("No results to save")
        return
    
    # Define the field names for the CSV
    fieldnames = [
        'filename', 'full_address', 'street_number', 'street_name', 'suburb', 'postcode',
        'total_due', 'due_date', 'water_usage_kl', 'days_charged',
        'current_period_daily_usage', 'last_year_daily_usage'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    if not os.path.exists(directory_path):
        print(f"Error: Directory {directory_path} does not exist")
        sys.exit(1)
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"water_usage_data_{timestamp}.csv"
    
    print(f"Starting to process PDF files in: {directory_path}")
    # Enable debug mode for the first run
    results = process_directory(directory_path, debug=True)
    
    if results:
        save_to_csv(results, output_file)
        print(f"\nProcessing complete!")
        print(f"Processed {len(results)} files successfully")
        print(f"Results saved to: {output_file}")
        
        # Print summary of unique addresses and their water usage
        print("\n处理的地址和用水量:")
        for result in sorted(results, key=lambda x: x.get('full_address', '')):
            water_usage = result.get('water_usage_kl', 'N/A')
            print(f"- {result['full_address']}: {water_usage} kL")
    else:
        print("No results were generated")

if __name__ == "__main__":
    main()
