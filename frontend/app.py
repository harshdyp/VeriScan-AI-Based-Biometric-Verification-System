import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="SmartID Identity Verification", page_icon="🆔", layout="centered")

# Sidebar
st.sidebar.title("🆔 SmartID")
st.sidebar.markdown("""
**Multi-Modal Identity Verification**  
Upload your selfie and ID photo to verify your identity using face recognition and OCR.

**Instructions:**
- Upload a clear selfie and a photo of your ID.
- Click **Verify Face** to check if your face matches your ID.
- Click **Extract and Validate ID** to extract and validate text from your ID.
""")

st.title("SmartID Identity Verification")
st.markdown("""
<style>
.big-font { font-size:22px !important; font-weight: 600; }
.result-box { background: #f0f2f6; border-radius: 8px; padding: 16px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    selfie = st.file_uploader("📸 Upload your selfie", type=['jpg', 'jpeg', 'png'], key="selfie")
    if selfie:
        st.image(selfie, caption="Selfie Preview", use_column_width=True)
with col2:
    id_img = st.file_uploader("🪪 Upload your ID photo", type=['jpg', 'jpeg', 'png'], key="id")
    if id_img:
        st.image(id_img, caption="ID Photo Preview", use_column_width=True)

st.markdown("---")

col3, col4 = st.columns(2)
with col3:
    if st.button("🔍 Verify Face"):
        if selfie and id_img:
            with st.spinner("Verifying face, please wait..."):
                files = {
                    "selfie": (selfie.name, selfie, selfie.type or "image/jpeg"),
                    "id_photo": (id_img.name, id_img, id_img.type or "image/jpeg")
                }
                try:
                    res = requests.post("http://localhost:8000/verify-face", files=files)
                    if res.ok:
                        match = res.json().get("match", False)
                        st.markdown(f'<div class="result-box big-font">Face Match: <span style="color: {"green" if match else "red"};">{"✅ Yes" if match else "❌ No"}</span></div>', unsafe_allow_html=True)
                    else:
                        st.error("API Error: " + res.text)
                except Exception as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("Please upload both a selfie and an ID photo.")

with col4:
    if st.button("📝 Extract and Validate ID"):
        if id_img:
            with st.spinner("Extracting and validating ID text..."):
                files = {"id_image": (id_img.name, id_img, id_img.type or "image/jpeg")}
                try:
                    res = requests.post("http://localhost:8000/extract-id-text", files=files)
                    if res.ok:
                        data = res.json()
                        valid = data.get("valid", False)
                        parsed = data.get("parsed_fields", {})
                        mock = data.get("mock_data", {})
                        # Determine reasons for validation failure
                        reasons = []
                        for field in ["Name", "DOB", "Address", "ID"]:
                            if field not in parsed:
                                reasons.append(f"Field '{field}' was not found in the ID.")
                            elif parsed.get(field) != mock.get(field):
                                reasons.append(f"Field '{field}' does not match the expected format or value.")
                        if valid:
                            st.markdown(f'<div class="result-box big-font">ID Valid: <span style="color: green;">✅ Yes</span></div>', unsafe_allow_html=True)
                            st.success("All required fields are present and match the expected format.")
                        else:
                            st.markdown(f'<div class="result-box big-font">ID Valid: <span style="color: red;">❌ No</span></div>', unsafe_allow_html=True)
                            st.error("ID validation failed for the following reasons:")
                            for reason in reasons:
                                st.write(f"- {reason}")
                    else:
                        st.error("API Error: " + res.text)
                except Exception as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("Please upload an ID photo.") 