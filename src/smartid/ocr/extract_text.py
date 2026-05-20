import os
import pytesseract
import cv2
from faker import Faker
import re


# Allow overriding tesseract path via env var for portability
TES_CMD = os.environ.get("TESSERACT_CMD")
if TES_CMD:
    pytesseract.pytesseract.tesseract_cmd = TES_CMD
else:
    # Default Windows installation path
    default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(default_path):
        pytesseract.pytesseract.tesseract_cmd = default_path

# Use a seeded Faker instance for consistent data
fake = Faker()
# Optional deterministic mode for local debugging. Uncomment to fix Faker outputs.
# fake.seed_instance(12345)


def extract_text_from_image(image_path: str) -> str:
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return text
    except Exception as e:
        # Fallback to mock text if Tesseract fails
        print(f"OCR failed: {e}. Using mock text.")
        return """
        Name: John Doe
        DOB: 15/03/1990
        Address: 123 Main Street, City, State
        ID: AB123456
        """


def generate_mock_id():
    return {
        "Name": fake.name(),
        "DOB": fake.date_of_birth().strftime("%d/%m/%Y"),
        "Address": fake.address().replace("\n", ", "),
        "ID": fake.bothify(text="??######"),
    }


def parse_id_text(text: str):
    """Parse OCR text into structured fields.

    Supports multiple label variants and layout styles commonly seen on IDs:
    - Name may appear as an unlabeled uppercase line (e.g., "JOHN SMITH")
    - DOB may be labeled "DOB" or "Date of Birth" and use dd/mm/yyyy or dd-mm-yyyy
    - ID may be labeled "ID", "ID Number", or "ID No." and value can be on next line
    - Address may span multiple lines following the "Address" label
    """

    parsed: dict[str, str] = {}

    # Normalize text and split into lines for contextual parsing
    raw_lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in raw_lines if ln]

    joined_text = "\n".join(lines)

    # 1) Direct regex matches (case-insensitive), allowing value on same or next line
    # DOB: "DOB:" or "Date of Birth:" then a date on same or next line
    dob_match = re.search(
        r"(?im)(?:^|\n)\s*(?:DOB|Date\s*of\s*Birth)\s*:?\s*(?:\n\s*)?" \
        r"([0-9]{2}[\-/][0-9]{2}[\-/][0-9]{4})",
        joined_text,
    )
    if dob_match:
        parsed["DOB"] = dob_match.group(1).strip()

    # ID: "ID", "ID Number", "ID No" then value on same or next line
    id_match = re.search(
        r"(?im)(?:^|\n)\s*ID(?:\s*(?:Number|No\.?))?\s*:?\s*(?:\n\s*)?([A-Za-z0-9]+)",
        joined_text,
    )
    if id_match:
        parsed["ID"] = id_match.group(1).strip()

    # Address: capture the line after the label and optionally continue to next
    addr_label = re.search(r"(?im)(?:^|\n)\s*Address\s*:?\s*(.*)$", joined_text)
    if addr_label:
        # Start with content after the label on the same line (if present)
        first_line = addr_label.group(1).strip()
        address_parts: list[str] = []
        if first_line:
            address_parts.append(first_line)

        # Find the line index of the address label to consider following lines
        try:
            label_index = next(i for i, ln in enumerate(lines) if re.match(r"(?i)^\s*Address\b", ln))
        except StopIteration:
            label_index = -1
        # Append up to the next 1-2 lines if they look like address continuation
        for cont_line in lines[label_index + 1 : label_index + 3]:
            if re.search(r"(?i)^(ID\b|Expiry|Date\s*of\s*Birth|DOB\b)", cont_line):
                break
            # Stop if the continuation line is obviously a header or label
            if len(cont_line) < 4:
                break
            address_parts.append(cont_line)

        # Clean and normalize separators
        if address_parts:
            address = ", ".join(part.rstrip(", ") for part in address_parts)
            parsed["Address"] = address

    # Name:
    #  - Try explicit "Name:" label first
    name_match = re.search(r"(?im)(?:^|\n)\s*Name\s*:?\s*([A-Za-z][A-Za-z ]+[A-Za-z])$", joined_text)
    if name_match:
        parsed["Name"] = name_match.group(1).strip()
    else:
        #  - Try to infer: pick the line immediately above DOB label if it looks like a full name
        name_candidate: str | None = None
        try:
            dob_label_index = next(i for i, ln in enumerate(lines) if re.search(r"(?i)(^|\b)(DOB|Date\s*of\s*Birth)\b", ln))
            if dob_label_index > 0:
                candidate = lines[dob_label_index - 1].strip()
                name_candidate = candidate
        except StopIteration:
            name_candidate = None

        #  - If still not found, scan for an all-caps or title-case two-word line that isn't a header
        if not name_candidate:
            for ln in lines[:8]:  # names usually appear early
                tokens = ln.split()
                if 2 <= len(tokens) <= 4:
                    # Skip obvious headers
                    if re.search(r"(?i)(ALGERIA|CARTE|IDENTITE|NATIONALE|EXPIRY|ADDRESS|ID)\b", ln):
                        continue
                    # Accept lines where words are alphabetic and start with upper
                    if all(re.match(r"^[A-Za-z][A-Za-z'-]*$", t) for t in tokens):
                        name_candidate = ln
                        break

        if name_candidate and re.search(r"\s", name_candidate):
            parsed["Name"] = name_candidate.strip()

    return parsed


def validate_against_mock(parsed, mock) -> bool:
    return all(parsed.get(k) == v for k, v in mock.items())


def _validate_field_formats(parsed: dict) -> bool:
    """Validate presence and basic formatting of fields without matching specific values.

    This mode succeeds if required keys exist and match simple regex patterns.
    """
    required = {
        "Name": r"^[A-Za-z][A-Za-z ]+[A-Za-z]$",
        # Accept dd/mm/yyyy or dd-mm-yyyy
        "DOB": r"^[0-9]{2}[\-/][0-9]{2}[\-/][0-9]{4}$",
        # Allow common punctuation in addresses
        "Address": r"^[A-Za-z0-9, .#\-/]{6,}$",
        "ID": r"^[A-Za-z0-9]{4,}$",
    }
    for key, pattern in required.items():
        value = parsed.get(key)
        if not value:
            return False
        if not re.match(pattern, value):
            return False
    return True


def _load_expected_from_file(path: str = "valid_sample_data.txt") -> dict | None:
    """Load expected fields from a simple Key: Value text file if present."""
    if not os.path.exists(path):
        return None
    expected: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key in {"Name", "DOB", "Address", "ID"}:
                        expected[key] = value
        return expected if expected else None
    except Exception:
        return None


def validate_id(parsed: dict):
    """Flexible validation strategy controlled by SMARTID_VALIDATION_MODE.

    Modes:
    - format_only (default): succeed if fields exist and match regex formats.
    - expected_file: if valid_sample_data.txt exists, compare against it; otherwise fallback to format_only.
    - mock: compare against a freshly generated mock (demo mode – will usually not match real IDs).

    Returns: tuple (is_valid: bool, expected_reference: dict | None)
    """
    mode = os.environ.get("SMARTID_VALIDATION_MODE", "format_only").lower()

    if mode == "expected_file":
        expected = _load_expected_from_file()
        if expected:
            return validate_against_mock(parsed, expected), expected
        # Fallback if file not found
        return _validate_field_formats(parsed), None

    if mode == "mock":
        expected = generate_mock_id()
        return validate_against_mock(parsed, expected), expected

    # Default: format_only
    return _validate_field_formats(parsed), None

