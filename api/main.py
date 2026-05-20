from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os
import sys
import traceback

# Ensure `src` directory is on the Python path so we can import the modular package
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from smartid.face.verify_face import compare_faces
from smartid.ocr.extract_text import (
    extract_text_from_image,
    parse_id_text,
    validate_id,
)

app = FastAPI()
FACE_THRESHOLD = float(os.environ.get("SMARTID_FACE_THRESHOLD", "0.7"))

@app.post("/verify-face")
def verify_face_api(selfie: UploadFile = File(...), id_photo: UploadFile = File(...)):
    try:
        # Save uploaded files
        with open("selfie.jpg", "wb") as f:
            shutil.copyfileobj(selfie.file, f)
        with open("id.jpg", "wb") as f:
            shutil.copyfileobj(id_photo.file, f)
        
        # Compare faces
        prob = compare_faces("selfie.jpg", "id.jpg")
        matched = prob >= FACE_THRESHOLD
        
        return {"matched": matched, "confidence": round(prob, 3)}
        
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Face verification error: {e}")
        print(f"Traceback: {tb}")
        raise HTTPException(
            status_code=500, 
            detail=f"Face verification failed: {str(e)}"
        )

@app.post("/extract-id-text")
def extract_id_text_api(id_image: UploadFile = File(...)):
    try:
        with open("temp_id.jpg", "wb") as f:
            shutil.copyfileobj(id_image.file, f)
        text = extract_text_from_image("temp_id.jpg")
        parsed = parse_id_text(text)
        valid, expected = validate_id(parsed)
        return {
            "ocr_text": text,
            "parsed_fields": parsed,
            "expected_reference": expected,  # may be None in format-only mode
            "valid": valid,
        }
    except Exception as e:
        tb = traceback.format_exc()
        with open("ocr_error.log", "w") as logf:
            logf.write(tb)
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}\n{tb}") 