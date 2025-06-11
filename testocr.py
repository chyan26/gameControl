import time
import pytesseract
import easyocr
from PIL import Image, ImageFilter, ImageEnhance
import os
os.environ["TESSDATA_PREFIX"] = "/opt/local/share/tessdata"

import torch
print("Is GPU available:", torch.cuda.is_available())
print("GPU device name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")

def evaluate_ocr_speed(image_path):
    """
    Evaluates the speed of easyOCR and pytesseract for OCR tasks.
    """
    # Load the image
    img = Image.open(image_path)

    # Crop the lower-right corner (adjust coordinates as needed)
    width, height = img.size
    left = width * 0.86  # Start at 86% of the width
    top = height * 0.86  # Start at 86% of the height
    right = width * 0.93  # End at 93% of the width
    bottom = height * 0.90  # End at 90% of the height

    start_time = time.time()
    cropped_img = img.crop((left, top, right, bottom))
    # Enhance the image
    cropped_img = cropped_img.filter(ImageFilter.SHARPEN)  # Sharpen the image
    enhancer = ImageEnhance.Contrast(cropped_img)
    cropped_img = enhancer.enhance(2.0)  # Increase contrast
    cropped_img.save("cropped_image.png")  # Save cropped image for debugging
    cropped_img_time = time.time() - start_time 
    print(f"Cropped image saved as 'cropped_image.png' in {cropped_img_time:.3f} seconds")
    # Measure pytesseract speed
    start_time = time.time()
    text_tesseract = pytesseract.image_to_string(cropped_img, config='--oem 1 --psm 6 digits')
    tesseract_time = time.time() - start_time
    print(f"pytesseract OCR result: {text_tesseract.strip()}")
    print(f"pytesseract time: {tesseract_time:.3f} seconds")

    # Measure easyOCR speed
    reader = easyocr.Reader(['en'], gpu=False)  # Initialize easyOCR reader
    start_time = time.time()
    result_easyocr = reader.readtext("cropped_image.png", detail=0)  # Extract text without bounding box details
    easyocr_time = time.time() - start_time
    print(f"easyOCR OCR result: {result_easyocr[0]}")
    print(f"easyOCR time: {easyocr_time:.3f} seconds")

    # Compare results
    print("\nComparison:")
    print(f"pytesseract time: {tesseract_time:.3f} seconds")
    print(f"easyOCR time: {easyocr_time:.3f} seconds")
    print(f"Faster OCR: {'pytesseract' if tesseract_time < easyocr_time else 'easyOCR'}")

# Example usage
image_path = "test_data/example.png"  # Replace with the path to your test image
evaluate_ocr_speed(image_path)