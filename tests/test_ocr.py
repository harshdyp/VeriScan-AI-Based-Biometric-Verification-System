from smartid.ocr.extract_text import parse_id_text, validate_against_mock


def test_parse_id_text_extracts_fields():
    text = """
    Name: Jane Doe
    DOB: 01/02/1990
    Address: 123 Main St, City
    ID: AB123456
    """
    parsed = parse_id_text(text)
    assert parsed["Name"] == "Jane Doe"
    assert parsed["DOB"] == "01/02/1990"
    assert parsed["Address"].startswith("123 Main St")
    assert parsed["ID"] == "AB123456"


def test_validate_against_mock_false_when_mismatch():
    parsed = {"Name": "A", "DOB": "01/01/2000", "Address": "B", "ID": "C"}
    mock = {"Name": "X", "DOB": "02/02/2002", "Address": "Y", "ID": "Z"}
    assert validate_against_mock(parsed, mock) is False


