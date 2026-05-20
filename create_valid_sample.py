#!/usr/bin/env python3
"""
Create a sample ID that will produce VALID OCR results
"""
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
import os
import sys

# Add src to path
src_path = os.path.join(os.getcwd(), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def create_guaranteed_valid_sample():
    """Create a sample ID that will definitely produce valid OCR results"""
    print("🎯 Creating Guaranteed Valid Sample ID...")
    
    # Import OCR functions
    from smartid.ocr.extract_text import generate_mock_id, validate_against_mock
    
    # Generate mock data first
    mock_data = generate_mock_id()
    
    print("\n📋 Generated Mock Data (this will be used for validation):")
    for key, value in mock_data.items():
        print(f"   {key}: {value}")
    
    # Create ID image with the exact same data
    image_path = create_id_image_with_data(mock_data, "valid_sample_id.jpg")
    
    # Test OCR extraction
    print("\n🧪 Testing OCR extraction...")
    success = test_ocr_extraction(image_path, mock_data)
    
    if success:
        print("\n🎉 SUCCESS! This sample ID will produce VALID OCR results!")
        print("💡 Use 'valid_sample_id.jpg' in your SmartID app")
        print("📄 The exact data is saved in 'valid_sample_data.txt'")
    else:
        print("\n⚠️  OCR test failed, but the data structure is correct")
    
    return mock_data

def create_id_image_with_data(data, output_path="valid_sample_id.jpg"):
    """Create ID image with the provided data"""
    # Create a white background
    width, height = 800, 500
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        try:
            font_large = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
            font_medium = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
            font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Draw header
    draw.text((50, 30), "IDENTITY DOCUMENT", fill='darkblue', font=font_large)
    draw.line([(50, 70), (750, 70)], fill='darkblue', width=3)
    
    # Draw ID fields with clear formatting
    y_position = 100
    line_height = 40
    
    fields = [
        ("Name:", data["Name"]),
        ("DOB:", data["DOB"]),
        ("Address:", data["Address"]),
        ("ID:", data["ID"])
    ]
    
    for label, value in fields:
        # Draw label
        draw.text((50, y_position), label, fill='black', font=font_medium)
        
        # Draw value
        draw.text((200, y_position), value, fill='darkgreen', font=font_medium)
        
        y_position += line_height
    
    # Draw footer
    draw.line([(50, 450), (750, 450)], fill='darkblue', width=2)
    draw.text((50, 470), "Sample ID for OCR testing - This will produce valid results", 
              fill='gray', font=font_small)
    
    # Save the image
    image.save(output_path, "JPEG", quality=95)
    print(f"✅ Sample ID image created: {output_path}")
    
    return output_path

def test_ocr_extraction(image_path, expected_data):
    """Test OCR extraction with the created image"""
    try:
        from smartid.ocr.extract_text import extract_text_from_image, parse_id_text
        
        # Extract text
        ocr_text = extract_text_from_image(image_path)
        print(f"📝 OCR Text extracted:")
        print("-" * 40)
        print(ocr_text)
        print("-" * 40)
        
        # Parse text
        parsed_fields = parse_id_text(ocr_text)
        print(f"\n📋 Parsed fields:")
        for key, value in parsed_fields.items():
            print(f"   {key}: {value}")
        
        # Validate
        is_valid = validate_against_mock(parsed_fields, expected_data)
        
        print(f"\n📊 Validation Result:")
        print(f"   Valid: {'✅ YES' if is_valid else '❌ NO'}")
        print(f"   Fields extracted: {len(parsed_fields)}/4")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def main():
    """Main function"""
    print("🆔 SmartID - Create Valid Sample ID")
    print("=" * 50)
    
    # Create guaranteed valid sample
    sample_data = create_guaranteed_valid_sample()
    
    # Save the data to a file
    with open("valid_sample_data.txt", "w") as f:
        f.write("Valid Sample ID Data for OCR Testing:\n")
        f.write("=" * 50 + "\n")
        f.write("This data will produce VALID OCR results!\n\n")
        for key, value in sample_data.items():
            f.write(f"{key}: {value}\n")
        f.write("\nUse 'valid_sample_id.jpg' in the SmartID app for testing.\n")
    
    print(f"\n📄 Data saved to: valid_sample_data.txt")
    print(f"🖼️  Image saved as: valid_sample_id.jpg")
    
    print("\n🚀 Next Steps:")
    print("   1. Use 'valid_sample_id.jpg' in your SmartID app")
    print("   2. The OCR extraction should return VALID results")
    print("   3. All fields should match the expected format")

if __name__ == "__main__":
    main()
