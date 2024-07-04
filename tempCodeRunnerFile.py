def ocr_page(page):
#     # Get a PIL image from the PDF page
#     pix = page.get_pixmap()
#     img = Image.open(io.BytesIO(pix.tobytes()))
    
#     # Perform OCR on the image
#     ocr_text = pytesseract.image_to_string(img)
#     return ocr_text