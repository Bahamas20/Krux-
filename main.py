import fitz
import os
import csv
from openai import OpenAI
import re
from datetime import datetime
import base64
import requests
from PIL import Image
import io
import pytesseract


today = datetime.today()

formatted_date = today.strftime("%d-%B-%y")

# Initialize OpenAI client with API key
api_key=os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# def convert_image_to_base64(image_bytes):
#     return base64.b64encode(image_bytes).decode('utf-8')

# def analyze_image_with_openai(base64_image):

#     headers = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {api_key}"
#     }
#     payload = {
#     "model": "gpt-4o",
#     "messages": [
#         {
#         "role": "user",
#         "content": [
#             {
#             "type": "text",
#             "text": "What are the important details in this image write in one paragraph"
#             },
#             {
#             "type": "image_url",
#             "image_url": {
#                 "url": f"data:image/jpeg;base64,{base64_image}"
#             }
#             }
#         ]
#         }
#     ],
#     "max_tokens": 300
#     }

#     response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

#     return (response.json()['choices'][0]['message']['content'])

# Function to perform OCR on a page and return the TextPage object using OpenAI Vision
# def ocr_page(page):
#     # Extract images from the page
#     pix = page.get_pixmap()
#     image_bytes = pix.tobytes()
#     image_base64 = convert_image_to_base64(image_bytes)
#     image_analysis = analyze_image_with_openai(image_base64)
#     return image_analysis

# Function to extract all text from the PDF using OCR (pytesseract) and return as a string
def ocr_page(page):

    pix = page.get_pixmap()
    img = Image.open(io.BytesIO(pix.tobytes()))
    
    ocr_text = pytesseract.image_to_string(img)
    return ocr_text

def extract_all_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        ocr_text = ocr_page(page)
        
        page_text = page.get_text("text")
        
        full_text += page_text + ocr_text

    return full_text

def extract_info_with_openai(text):
    prompt = f"""
    Extract the following information from the text below (if any of the information is not available in text or your own knowledge then leave it NULL with no reasoning):
    1. Company Name
    2. Website
    3. Country of Company Location (Just list the Main Country no description needed, if not stated use your knowledge)
    4. Description (write 2 sentences at least)
    5. Name of Main Company Contact
    6. Role of Main Company Contact (CEO,Founder etc)
    7. Email of Main Company Contact (or any email contact to company)
    8. Company Stage (Pre-Seed,Seed,Series A,Series B,Series C give one of this options ONLY)
    9. Sector 
    10. Business Model (no description just one main model used)
    11. Revenue (Provide the Annual Recurring Revenue (ARR) in the format ARR: .. If ARR is not available, deduce the closest metric and calculate ARR based on that metric (e.g., multiply MRR by 12, or any monthly revenu by 12).ONLYY If neither ARR nor a directly calculable metric is available, provide the closest metric: .. For example, if net profit is the closest metric, then Net Profit: .. . IF not always try to deduce ARR no matter what.( Use M for millions and K for thousands )
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
        temperature=0.2
    )
    
    response_text = completion.choices[0].message.content

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
                
                full_text = extract_all_text(pdf_path)
                extracted_info = extract_info_with_openai(full_text)
                
                # txt_filename = os.path.splitext(filename)[0] + '.txt'
                # txt_path = os.path.join(directory_path, txt_filename)
                
                # with open(txt_path, 'w', encoding='utf-8') as txt_file:
                #     txt_file.write(full_text)
                
                # print(f"Text saved to: {txt_path}")
                
                info_list.append(extracted_info)

        csv_file_path = os.path.join(".", 'records_of_arr.csv')
        save_info_to_csv(info_list, csv_file_path)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    directory_path = './small_sample'
    main(directory_path)
