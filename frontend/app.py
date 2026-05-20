import streamlit as st
import requests
import os
from PIL import Image
import io
import plotly.graph_objects as go

st.set_page_config(page_title="SmartID Identity Verification", page_icon="🆔", layout="centered")

API_BASE = os.environ.get("SMARTID_API_BASE", "http://localhost:8000")

# Project Banner/Logo
# Avoid external hotlinked assets (can 403 in some networks/browsers)
st.markdown(
    """
<div style='display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;'>
    <span style='font-size: 2.2rem; font-weight: 700;'>🆔 SmartID: Multi-Modal Identity Verification</span>
</div>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if 'face_result' not in st.session_state:
    st.session_state['face_result'] = None
if 'face_confidence' not in st.session_state:
    st.session_state['face_confidence'] = None
if 'id_result' not in st.session_state:
    st.session_state['id_result'] = None
if 'id_matched_fields' not in st.session_state:
    st.session_state['id_matched_fields'] = None
if 'id_not_matched_fields' not in st.session_state:
    st.session_state['id_not_matched_fields'] = None
if 'id_parsed_fields' not in st.session_state:
    st.session_state['id_parsed_fields'] = None
if 'force_update' not in st.session_state:
    st.session_state['force_update'] = 0

# Manual refresh button for summary card
if st.session_state['face_result'] is not None or st.session_state['id_result'] is not None:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("🔄 Refresh Summary Card", key="manual_refresh"):
            st.session_state['force_update'] += 1
            st.rerun()

# Enhanced Summary Card with better styling and debugging
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 1.5rem 2rem; margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1);'>
        <div style='display: flex; flex-direction: row; justify-content: space-between; align-items: center;'>
            <div style='flex: 1; text-align: center;'>
                <div style='background: rgba(255,255,255,0.9); border-radius: 10px; padding: 1rem; margin: 0.5rem;'>
                    <span style='font-size: 1.3rem; font-weight: 700; color: #2c3e50;'>Face Verification</span><br/>
                    <span style='font-size: 1.5rem; font-weight: 800; color: {face_color};'>{face_status}</span><br/>
                    <span style='font-size: 1.1rem; color: #34495e;'>Confidence: {face_confidence}</span>
                </div>
            </div>
            <div style='flex: 1; text-align: center;'>
                <div style='background: rgba(255,255,255,0.9); border-radius: 10px; padding: 1rem; margin: 0.5rem;'>
                    <span style='font-size: 1.3rem; font-weight: 700; color: #2c3e50;'>ID Validation</span><br/>
                    <span style='font-size: 1.5rem; font-weight: 800; color: {id_color};'>{id_status}</span><br/>
                    <span style='font-size: 1.1rem; color: #34495e;'>Fields: {matched}/4 Valid</span>
                </div>
            </div>
        </div>
    </div>
    """.format(
        face_color="green" if st.session_state['face_result'] else "red" if st.session_state['face_result'] is False else "#95a5a6",
        face_status="✅ MATCHED" if st.session_state['face_result'] else "❌ NOT MATCHED" if st.session_state['face_result'] is False else "⏳ PENDING",
        face_confidence=f"{st.session_state['face_confidence']:.3f}" if st.session_state['face_confidence'] is not None else "N/A",
        id_color="green" if st.session_state['id_result'] else "red" if st.session_state['id_result'] is False else "#95a5a6",
        id_status="✅ VALID" if st.session_state['id_result'] else "❌ INVALID" if st.session_state['id_result'] is False else "⏳ PENDING",
        matched=st.session_state['id_matched_fields'] if st.session_state['id_matched_fields'] is not None else "0"
    ), unsafe_allow_html=True)

# Enhanced Sidebar
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; padding: 1rem; margin-bottom: 1rem;'>
    <h3 style='color: white; text-align: center; margin: 0;'>🆔 SmartID</h3>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
**Multi-Modal Identity Verification**  
Upload your selfie and ID photo to verify your identity using face recognition and OCR.

**Instructions:**
- Upload a clear selfie and a photo of your ID.
- Click **Verify Face** to check if your face matches your ID.
- Click **Extract and Validate ID** to extract and validate text from your ID.
""")

# Debug section in sidebar
with st.sidebar.expander("🔧 Debug Info"):
    st.write("**Session State:**")
    st.json({
        "face_result": st.session_state['face_result'],
        "face_confidence": st.session_state['face_confidence'],
        "id_result": st.session_state['id_result'],
        "id_matched_fields": st.session_state['id_matched_fields'],
        "id_parsed_fields": st.session_state['id_parsed_fields']
    })
    st.write("**API Base:**", API_BASE)

st.markdown("""
<style>
.big-font { font-size:22px !important; font-weight: 600; }
.result-box { 
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
    border-radius: 12px; 
    padding: 20px; 
    margin-top: 15px; 
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.success-box {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    border-radius: 12px;
    padding: 20px;
    margin-top: 15px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.error-box {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    border-radius: 12px;
    padding: 20px;
    margin-top: 15px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Tabs for workflow
face_tab, id_tab = st.tabs(["🔍 Face Verification", "📝 ID Validation"])

with face_tab:
    st.subheader("Step 1: Upload Images for Face Verification")
    selfie = st.file_uploader("📸 Upload your selfie", type=['jpg', 'jpeg', 'png'], key="selfie", help="Upload a clear selfie photo.")
    id_img = st.file_uploader("🪪 Upload your ID photo", type=['jpg', 'jpeg', 'png'], key="id_face", help="Upload the photo section of your ID.")
    col1, col2 = st.columns(2)
    with col1:
        if selfie:
            st.image(selfie, caption="Selfie Preview", use_container_width=True)
    with col2:
        if id_img:
            st.image(id_img, caption="ID Photo Preview", use_container_width=True)
    st.markdown("")
    if st.button("Run Face Verification", help="Compares your selfie and ID photo using deep learning."):
        if selfie and id_img:
            with st.spinner("Verifying face, please wait..."):
                files = {
                    "selfie": (selfie.name, selfie, selfie.type or "image/jpeg"),
                    "id_photo": (id_img.name, id_img, id_img.type or "image/jpeg")
                }
                try:
                    res = requests.post(f"{API_BASE}/verify-face", files=files)
                    if res.ok:
                        data = res.json()
                        matched = data.get("matched", False)
                        confidence = data.get("confidence", 0.0)
                        st.session_state['face_result'] = matched
                        st.session_state['face_confidence'] = confidence
                        st.session_state['force_update'] += 1
                        st.toast(f"Face verification {'matched' if matched else 'not matched'} (confidence: {confidence})", icon="✅" if matched else "❌")
                        
                        if matched:
                            st.markdown(f'<div class="success-box big-font">Face Verification: ✅ MATCHED</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-box big-font">Face Verification: ❌ NOT MATCHED</div>', unsafe_allow_html=True)
                        
                        st.write(f"**Confidence score:** {confidence:.3f}")
                        
                        # Plotly gauge for confidence
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = confidence * 100,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Confidence (%)"},
                            gauge = {
                                'axis': {'range': [0, 100]},
                                'bar': {'color': "#00cc96" if matched else "#ef553b"},
                                'steps': [
                                    {'range': [0, 50], 'color': '#ffe5e5'},
                                    {'range': [50, 70], 'color': '#fff5cc'},
                                    {'range': [70, 100], 'color': '#e5ffe5'}
                                ],
                                'threshold': {
                                    'line': {'color': "#636efa", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 70
                                }
                            }
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                        st.success("Face verification complete.")
                        
                        # Add a refresh button to update the summary card
                        if st.button("🔄 Refresh Summary Card", key="face_refresh"):
                            st.rerun()
                    else:
                        st.error("API Error: " + res.text)
                except Exception as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("Please upload both a selfie and an ID photo.")

with id_tab:
    st.subheader("Step 2: Upload ID for Validation")
    id_img_val = st.file_uploader("🪪 Upload your ID photo for OCR", type=['jpg', 'jpeg', 'png'], key="id_val", help="Upload a clear image of your ID for text extraction and validation.")
    if id_img_val:
        st.image(id_img_val, caption="ID Photo Preview", use_container_width=True)
    if st.button("Run ID Validation", help="Extracts and validates ID fields using OCR and mock data."):
        if id_img_val:
            with st.spinner("Extracting and validating ID text..."):
                files = {"id_image": (id_img_val.name, id_img_val, id_img_val.type or "image/jpeg")}
                try:
                    res = requests.post(f"{API_BASE}/extract-id-text", files=files)
                    if res.ok:
                        data = res.json()
                        valid = data.get("valid", False)
                        parsed = data.get("parsed_fields", {})
                        expected = data.get("expected_reference") or {}
                        
                        # Store parsed fields in session state
                        st.session_state['id_parsed_fields'] = parsed
                        
                        # Determine reasons for validation failure
                        reasons = []
                        matched_fields = 0
                        total_fields = 4
                        for field in ["Name", "DOB", "Address", "ID"]:
                            if field not in parsed:
                                reasons.append(f"Field '{field}' was not found in the ID.")
                            elif expected:
                                if parsed.get(field) != expected.get(field):
                                    reasons.append(f"Field '{field}' does not match expected value.")
                                else:
                                    matched_fields += 1
                            else:
                                # Format-only mode: count as matched if present
                                matched_fields += 1
                        not_matched_fields = total_fields - matched_fields
                        
                        # Update session state
                        st.session_state['id_result'] = valid
                        st.session_state['id_matched_fields'] = matched_fields
                        st.session_state['id_not_matched_fields'] = not_matched_fields
                        
                        # Force immediate update of the summary card
                        st.session_state['force_update'] += 1
                        st.success("Session state updated! Check the summary card above.")
                        
                        # Display results immediately
                        if valid:
                            st.toast("ID validation successful!", icon="✅")
                            st.markdown(f'<div class="success-box big-font">ID Validation: ✅ VALID</div>', unsafe_allow_html=True)
                            st.success("All required fields are present and match the expected format.")
                        else:
                            st.toast("ID validation failed.", icon="❌")
                            st.markdown(f'<div class="error-box big-font">ID Validation: ❌ INVALID</div>', unsafe_allow_html=True)
                            st.error("ID validation failed for the following reasons:")
                            for reason in reasons:
                                st.write(f"- {reason}")
                        
                        # Display parsed fields
                        st.subheader("📋 Extracted Fields")
                        col1, col2 = st.columns(2)
                        with col1:
                            for field in ["Name", "DOB"]:
                                if field in parsed:
                                    st.write(f"**{field}:** {parsed[field]}")
                                else:
                                    st.write(f"**{field}:** ❌ Not found")
                        with col2:
                            for field in ["Address", "ID"]:
                                if field in parsed:
                                    st.write(f"**{field}:** {parsed[field]}")
                                else:
                                    st.write(f"**{field}:** ❌ Not found")
                        
                        # Plotly pie chart for matched vs not matched fields
                        pie_labels = ["Matched Fields", "Not Matched Fields"]
                        pie_values = [matched_fields, not_matched_fields]
                        pie_colors = ["#00cc96", "#ef553b"]
                        pie_fig = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_values, marker_colors=pie_colors, hole=0.4)])
                        pie_fig.update_layout(title_text="ID Field Validation", showlegend=True)
                        st.plotly_chart(pie_fig, use_container_width=True)
                        st.info("ID validation complete.")
                        
                        # Add a refresh button to update the summary card
                        if st.button("🔄 Refresh Summary Card"):
                            st.rerun()
                    else:
                        st.error("API Error: " + res.text)
                except Exception as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("Please upload an ID photo.") 