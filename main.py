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
    Extract the following information from the text below (if any of the information is not available in text or your knowledge then leave it NULL):
    1. Company Name
    2. Website
    3. Region of Company Location (Just list the main location (COUNTRY) no description needed)
    4. Description
    5. Name of Main Company Contact
    6. Role of Main Company Contact (CEO,Founder etc)
    7. Email of Main Company Contact
    8. Company Stage (Pre-Seed,Seed,Series A,Series B,Series C one of this options only)
    9. Sector 
    10. Business Model (no description just one main model used)
    11. Revenue (in USD raised by the company dont bold your response)

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
    response_text = completion.choices[0].message.content # Get the message from the completion
    print(response_text)
       # Use regex to extract each field
    company_name_match = re.search(r"(?i)company\s*name.*?:\s*(.+)", response_text)
    website_match = re.search(r"(?i)website.*?:\s*(.+)", response_text)
    region_match = re.search(r"(?i)region\s*of\s*company\s*location.*?:\s*(.+)", response_text)
    description_match = re.search(r"(?i)description.*?:\s*(.+)", response_text)
    contact_name_match = re.search(r"(?i)name\s*of\s*main\s*company\s*contact.*?:\s*(.+)", response_text)
    contact_role_match = re.search(r"(?i)role\s*of\s*main\s*company\s*contact.*?:\s*(.+)", response_text)
    contact_email_match = re.search(r"(?i)email\s*of\s*main\s*company\s*contact.*?:\s*(.+)", response_text)
    company_stage_match = re.search(r"(?i)company\s*stage.*?:\s*(.+)", response_text)
    sector_match = re.search(r"(?i)sector.*?:\s*(.+)", response_text)
    business_model_match = re.search(r"(?i)business\s*model.*?:\s*(.+)", response_text)
    revenue_match = re.search(r"(?i)revenue.*?:\s*(.+)", response_text)
    

    # Initialize variables to store extracted information
    company_name = company_name_match.group(1).strip() if company_name_match and not company_name_match.group(1).strip().lower() == "null" else ""
    website = website_match.group(1).strip() if website_match and not website_match.group(1).strip().lower() == "null" else ""
    region = region_match.group(1).strip() if region_match and not region_match.group(1).strip().lower() == "null" else ""
    description = description_match.group(1).strip() if description_match and not description_match.group(1).strip().lower() == "null" else ""
    contact_name = contact_name_match.group(1).strip() if contact_name_match and not contact_name_match.group(1).strip().lower() == "null" else ""
    contact_role = contact_role_match.group(1).strip() if contact_role_match and not contact_role_match.group(1).strip().lower() == "null" else ""
    contact_email = contact_email_match.group(1).strip() if contact_email_match and not contact_email_match.group(1).strip().lower() == "null" else ""
    company_stage = company_stage_match.group(1).strip() if company_stage_match and not company_stage_match.group(1).strip().lower() == "null" else ""
    sector = sector_match.group(1).strip() if sector_match and not sector_match.group(1).strip().lower() == "null" else ""
    business_model = business_model_match.group(1).strip() if business_model_match and not business_model_match.group(1).strip().lower() == "null" else ""
    revenue = revenue_match.group(1).strip() if revenue_match and not revenue_match.group(1).strip().lower() == "null" else ""


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
    pdf_path = "insync.pdf"  # Replace with your input PDF path
    main(pdf_path)
