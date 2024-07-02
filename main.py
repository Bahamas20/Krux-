import fitz  # PyMuPDF
import os
import csv
from openai import OpenAI
import re

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Function to perform OCR on a page and return the TextPage object
def ocr_page(page):
    # Perform OCR and return TextPage object
    text_page = page.get_textpage_ocr()
    return text_page

# Function to extract all text from the PDF using OCR and return as a string
def extract_all_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_page = ocr_page(page)

        # Extract text from TextPage object
        page_text = text_page.extractText()
        
        # Append page text to full text
        full_text += f"\n\n--- Text from Page {page_num + 1} ---\n\n"
        full_text += page_text

    return full_text

# Function to extract information from text using OpenAI's GPT-4 model
def extract_info_with_openai(text):
    prompt = f"""
    Extract the following information from the text below:
    1. Company Name
    2. Website
    3. Region of Company Location
    4. Description
    5. Name of Main Company Contact
    6. Role of Main Company Contact (CEO,Founder etc)
    7. Email of Main Company Contact
    8. Company Stage (Pre-Seed,Seed,Series A,Series B,Series C one of this options only)
    9. Sector 
    10. Business Model (no description just the model used)
    11. Revenue (in USD raised by the company)

    Text:
    {text}
    
    Information:
    """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract information from completion
    response_text = completion.choices[0].message.strip()  # Get the message from the completion
    print(response_text)
        
        # Use regex to extract each field
    company_name_match = re.search(r"1\. Company Name: (.+)", response_text)
    if company_name_match:
        company_name = company_name_match.group(1).strip()
    else:
        company_name = ""

    website_match = re.search(r"2\. Website: (.+)", response_text)
    if website_match:
        website = website_match.group(1).strip()
    else:
        website = ""

    region_match = re.search(r"3\. Region of Company Location: (.+)", response_text)
    if region_match:
        region = region_match.group(1).strip()
    else:
        region = ""

    description_match = re.search(r"4\. Description: (.+)", response_text)
    if description_match:
        description = description_match.group(1).strip()
    else:
        description = ""

    contact_name_match = re.search(r"5\. Name of Main Company Contact: (.+)", response_text)
    if contact_name_match:
        contact_name = contact_name_match.group(1).strip()
    else:
        contact_name = ""

    contact_role_match = re.search(r"6\. Role of Main Company Contact: (.+)", response_text)
    if contact_role_match:
        contact_role = contact_role_match.group(1).strip()
    else:
        contact_role = ""

    contact_email_match = re.search(r"7\. Email of Main Company Contact: (.+)", response_text)
    if contact_email_match:
        contact_email = contact_email_match.group(1).strip()
    else:
        contact_email = ""

    company_stage_match = re.search(r"8\. Company Stage: (.+)", response_text)
    if company_stage_match:
        company_stage = company_stage_match.group(1).strip()
    else:
        company_stage = ""

    sector_match = re.search(r"9\. Sector: (.+)", response_text)
    if sector_match:
        sector = sector_match.group(1).strip()
    else:
        sector = ""

    business_model_match = re.search(r"10\. Business Model: (.+)", response_text)
    if business_model_match:
        business_model = business_model_match.group(1).strip()
    else:
        business_model = ""

    revenue_match = re.search(r"11\. Revenue: (.+)", response_text)
    if revenue_match:
        revenue = revenue_match.group(1).strip()
    else:
        revenue = ""

    
    # Initialize variables to store extracted information
    company_name = ""
    website = ""
    region = ""
    description = ""
    contact_name = ""
    contact_role = ""
    contact_email = ""
    company_stage = ""
    sector = ""
    business_model = ""
    revenue = ""

    # Process each line to extract relevant information
    for line in info_lines:
        if line.startswith("1. Company Name"):
            company_name = line.split(":")[1].strip()
        elif line.startswith("2. Website"):
            website = line.split(":")[1].strip()
        elif line.startswith("3. Region of Company Location"):
            region = line.split(":")[1].strip()
        elif line.startswith("4. Description"):
            description = line.split(":")[1].strip()
        elif line.startswith("5. Name of Main Company Contact"):
            contact_name = line.split(":")[1].strip()
        elif line.startswith("6. Role of Main Company Contact"):
            contact_role = line.split(":")[1].strip()
        elif line.startswith("7. Email of Main Company Contact"):
            contact_email = line.split(":")[1].strip()
        elif line.startswith("8. Company Stage"):
            company_stage = line.split(":")[1].strip()
        elif line.startswith("9. Sector"):
            sector = line.split(":")[1].strip()
        elif line.startswith("10. Business Model"):
            business_model = line.split(":")[1].strip()
        elif line.startswith("11. Revenue"):
            revenue = line.split(":")[1].strip()
    
    # Return extracted information as dictionary
    return {
        "Company": company_name,
        "Website": website,
        "IC": region,
        "Description": description,
        "Name": contact_name,
        "Role": contact_role,
        "Email": contact_email,
        "Stage": company_stage,
        "Sector": sector,
        "Business Model": business_model,
        "Revenue (USD)": revenue
    }


# Function to save extracted information to a CSV file
def save_info_to_csv(info_dict, csv_file):
    fieldnames = [
        "Company", "Website", "IC", "Description", "Name", 
        "Role", "Email", "Stage", "Sector", 
        "Business Model", "Revenue (USD)"
    ]
    
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(info_dict)

# Main function
def main(pdf_path):
    try:
        # Extract text from PDF
        full_text = extract_all_text(pdf_path)
        
        # Extract information using OpenAI
        extracted_info = extract_info_with_openai(full_text)
        print("Extracted Information:")
        print(extracted_info)
        
        # Save extracted information to CSV file
        csv_file_path = pdf_path.replace('.pdf', '.csv')
        save_info_to_csv(extracted_info, csv_file_path)
        print(f"Extracted information saved to {csv_file_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pdf_path = "corgi.pdf"  # Replace with your input PDF path
    main(pdf_path)
