import fitz  # PyMuPDF
import os
import csv
from openai import OpenAI
import re
from datetime import datetime
import base64
import requests

# Get today's date
today = datetime.today()

# Format date as DD-Month-YY
formatted_date = today.strftime("%d-%B-%y")

# Initialize OpenAI client with API key
api_key=os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def convert_image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_image_with_openai(base64_image):
    # This is a placeholder for the actual OpenAI API call.
    # Replace with the correct OpenAI API call for image analysis.
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }
    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "What are the important details in this image write in one paragraph"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return (response.json()['choices'][0]['message']['content'])

# Function to perform OCR on a page and return the TextPage object
def ocr_page(page):
    # Extract images from the page
    if (page.get_images()):
        pix = page.get_pixmap()
        image_bytes = pix.tobytes()
        image_base64 = convert_image_to_base64(image_bytes)
        image_analysis = analyze_image_with_openai(image_base64)
        return image_analysis

# Function to extract all text from the PDF using OCR and return as a string
def extract_all_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_page = ocr_page(page)

        # Append page text to full text
        full_text += f"\n\n--- Text from Page {page_num + 1} ---\n\n"
        full_text += text_page

    return full_text

# Function to extract information from text using OpenAI's GPT-4 model
def extract_info_with_openai(text):
    prompt = f"""
    Extract the following information from the text below (if any of the information is not available in text or your knowledge then leave it NULL):
    1. Company Name
    2. Website
    3. Country of Company Location (Just list the main Country no description needed, if not stated use your knowledge)
    4. Description (write 2-3 sentences at least)
    5. Name of Main Company Contact
    6. Role of Main Company Contact (CEO,Founder etc)
    7. Email of Main Company Contact
    8. Company Stage (Pre-Seed,Seed,Series A,Series B,Series C one of this options only)
    9. Sector 
    10. Business Model (no description just one main model used)
    11. Revenue (in USD raised by the company dont bold your response or give the expected sales, whatever information about profits)
    12. AS notes (any extra notes or remarks about the company that you know or found that is useful information for venture capitalist)

    Text:
    {text}
    
    Information:
    """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    # Extract information from completion
    response_text = completion.choices[0].message.content # Get the message from the completion
       # Use regex to extract each field
    company_name_match = re.search(r"(?i)company\s*name.*?:\s*(.+)", response_text)
    website_match = re.search(r"(?i)website.*?:\s*(.+)", response_text)
    region_match = re.search(r"(?i)country\s*of\s*company\s*location.*?:\s*(.+)", response_text)
    description_match = re.search(r"(?i)description.*?:\s*(.+)", response_text)
    contact_name_match = re.search(r"(?i)name\s*of\s*main\s*company\s*contact.*?:\s*(.+)", response_text)
    contact_role_match = re.search(r"(?i)role\s*of\s*main\s*company\s*contact.*?:\s*(.+)", response_text)
    contact_email_match = re.search(r"(?i)email\s*of\s*main\s*company\s*contact.*?:\s*(.+)", response_text)
    company_stage_match = re.search(r"(?i)company\s*stage.*?:\s*(.+)", response_text)
    sector_match = re.search(r"(?i)sector.*?:\s*(.+)", response_text)
    business_model_match = re.search(r"(?i)business\s*model.*?:\s*(.+)", response_text)
    revenue_match = re.search(r"(?i)revenue.*?:\s*(.+)", response_text)
    notes_match = re.search(r"(?i)notes.*?:\s*(.+)", response_text)

    

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
    notes = notes_match.group(1).strip() if notes_match and not notes_match.group(1).strip().lower() == "null" else ""




    # Return extracted information as dictionary
    return {
        "Company": company_name,
        "Website": website,
        "IC": region,
        "Pipeline stage":"",
        "Description": description,
        "dataroom":"",
        "deal team":"",
        "Name": contact_name,
        "Role": contact_role,
        "Email": contact_email,
        "Deal source": "", 
        "Last Updated": formatted_date,
        "Company Stage": company_stage,
        "Vertical / Sector": sector,
        "Business Model": business_model,
        "Technology": "",
        "Revenue (USD)": revenue,
        "AS Notes": notes
    }


# Function to save extracted information to a CSV file
def save_info_to_csv(info_list, csv_file):
    fieldnames = [
        "Company", "Website", "IC", "Pipeline stage", "Description","dataroom","deal team", "Name", 
        "Role", "Email", "Deal source", "Last Updated", "Company Stage", "Vertical / Sector", 
        "Business Model", "Technology","Revenue (USD)","AS Notes"
    ]
    
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for info_dict in info_list:
            writer.writerow(info_dict)

# Main function
def main(directory_path):
    try:
        info_list = []
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(directory_path, filename)
                # Extract text from PDF
                full_text = extract_all_text(pdf_path)
        
                # Extract information using OpenAI
                extracted_info = extract_info_with_openai(full_text)
                print("Extracted Information:")
                print(extracted_info)
                
                info_list.append(extracted_info)

        # Save extracted information to CSV file
        csv_file_path = os.path.join(".", 'combined_info.csv')
        save_info_to_csv(info_list, csv_file_path)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    directory_path = '.'
    main(directory_path)
