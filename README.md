## VeriScan — AI‑Based Biometric Verification System (Face + OCR)

### Why this exists (Problem)
Onboarding and KYC flows need to verify that a person is who they claim to be. Manual checks are slow and error‑prone. This project demonstrates an automated, privacy‑respecting pipeline combining face similarity and OCR‑based ID parsing to validate identity quickly.

### What this does (Approach)
- Face matching using `facenet-pytorch` to compute embeddings and cosine similarity
- OCR with Tesseract to extract fields from an ID image, parse with regex, and validate against a generated mock profile (or format-only checks)
- Streamlit UI for uploading images and visualizing results (modern styling and charts)
- FastAPI backend exposing two endpoints with clear contracts

### What we found (Results)
- End‑to‑end demo achieves responsive UX on CPU‑only machines.
- Example run yields stable face similarity confidence and parses synthetic ID fields; see the included notebook for a lightweight evaluation of OCR quality and similarity score distribution on sample images.

---

## Project Structure

```
.
├─ api/                   # Thin adapter that exposes FastAPI app
│  └─ main.py
├─ frontend/              # Streamlit UI
│  └─ app.py
├─ src/
│  └─ smartid/
│     ├─ face/
│     │  └─ verify_face.py
│     ├─ ocr/
│     │  └─ extract_text.py
│     └─ __init__.py
├─ tests/                 # Unit tests (pytest)
│  ├─ test_face.py
│  └─ test_ocr.py
├─ notebooks/
│  └─ evaluation.ipynb    # Minimal metrics & exploratory analysis
├─ .github/workflows/     # (optional) CI pipeline location
├─ docker-compose.yml     # One‑command run for backend + frontend
├─ Dockerfile
├─ requirements.txt
└─ README.md
```

---

## Quickstart

### Local (recommended)
1) Install dependencies
```bash
python -m venv .venv && . .venv/Scripts/activate  # Windows PowerShell: . .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

2) Install Tesseract OCR
- **Windows (Easy)**: Double-click `install_tesseract.bat` or run:
  ```powershell
  .\install_tesseract.ps1
  ```
- **Manual**: Download from [UB Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr`

3) Run services
- **Windows (Easy)**: Double-click `start_app.bat` or run:
  ```powershell
  .\start_app.ps1
  ```
- **Manual**:
  ```bash
  $env:PYTHONPATH = "$PWD\src"
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
  streamlit run frontend/app.py --server.port 8501
  ```

### Docker / Compose
```bash
docker compose up --build
```
Then open: `http://localhost:8501` (UI) and `http://localhost:8000/docs` (API).

### Public demo link (optional)
If you want an external link for interviewers, you can tunnel the ports:
```bash
# Requires: cloudflared or ngrok
cloudflared tunnel --url http://localhost:8501
cloudflared tunnel --url http://localhost:8000
```
Paste the generated URLs into your interview notes.

---

## API
- POST `/verify-face`: multipart form with `selfie`, `id_photo` → `{ matched: bool, confidence: float }`
- POST `/extract-id-text`: multipart form with `id_image` → `{ ocr_text, parsed_fields, expected_reference, valid }`

See interactive docs at `http://localhost:8000/docs`.

---

## Development

### Run tests
```bash
pytest -q
```

### Lint/format (optional)
```bash
pip install ruff black
ruff check .
black .
```

---

## Evaluation Notebook
Open `notebooks/evaluation.ipynb` for a small report showing:
- Sample similarity scores for known same/different pairs
- OCR extraction quality on included images
- Simple visualizations (histograms, success rates)

---

## Notes
- This is an MVP. Replace mock validation with real checks and tune thresholds before production use.
- Ensure Tesseract is installed and `pytesseract.pytesseract.tesseract_cmd` is configured if not in PATH.

---

## License
MIT
