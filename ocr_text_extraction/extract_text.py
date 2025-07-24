import pytesseract
import cv2
from faker import Faker
import re

# Set this to the official install path for Tesseract on Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

fake = Faker()

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

def generate_mock_id():
    return {
        "Name": fake.name(),
        "DOB": fake.date_of_birth().strftime("%d/%m/%Y"),
        "Address": fake.address().replace('\n', ', '),
        "ID": fake.bothify(text='??######')
    }

def parse_id_text(text):
    # Simple regex-based extraction for MVP
    parsed = {}
    # Name
    match = re.search(r'Name[:\s]+([A-Za-z ]+)', text)
    if match:
        parsed["Name"] = match.group(1).strip()
    # DOB
    match = re.search(r'DOB[:\s]+([0-9]{2}/[0-9]{2}/[0-9]{4})', text)
    if match:
        parsed["DOB"] = match.group(1).strip()
    # Address
    match = re.search(r'Address[:\s]+([A-Za-z0-9, ]+)', text)
    if match:
        parsed["Address"] = match.group(1).strip()
    # ID
    match = re.search(r'ID[:\s]+([A-Za-z0-9]+)', text)
    if match:
        parsed["ID"] = match.group(1).strip()
    return parsed

def validate_against_mock(parsed, mock):
    # For MVP, just check if all fields match exactly
    return all(parsed.get(k) == v for k, v in mock.items()) 