from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
from face_recognition.verify_face import compare_faces
from ocr_text_extraction.extract_text import extract_text_from_image, generate_mock_id, parse_id_text, validate_against_mock
import traceback

app = FastAPI()

@app.post("/verify-face")
def verify_face_api(selfie: UploadFile = File(...), id_photo: UploadFile = File(...)):
    with open("selfie.jpg", "wb") as f:
        shutil.copyfileobj(selfie.file, f)
    with open("id.jpg", "wb") as f:
        shutil.copyfileobj(id_photo.file, f)
    result = compare_faces("selfie.jpg", "id.jpg")
    return {"match": bool(result)}

@app.post("/extract-id-text")
def extract_id_text_api(id_image: UploadFile = File(...)):
    try:
        with open("temp_id.jpg", "wb") as f:
            shutil.copyfileobj(id_image.file, f)
        text = extract_text_from_image("temp_id.jpg")
        parsed = parse_id_text(text)
        mock = generate_mock_id()
        match = validate_against_mock(parsed, mock)
        return {
            "ocr_text": text,
            "parsed_fields": parsed,
            "mock_data": mock,
            "valid": match
        }
    except Exception as e:
        tb = traceback.format_exc()
        with open("ocr_error.log", "w") as logf:
            logf.write(tb)
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}\n{tb}") 