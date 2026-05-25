import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import re
from pypdf import PdfReader

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PsychFlow Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIMULATED DATABASE / SESSION STATE ---
if 'cases' not in st.session_state:
    st.session_state.cases = pd.DataFrame([
        {
            "Student Initials": "J.D.",
            "School": "Lincoln High",
            "Category": "Re-evaluation",
            "Consent Date": "2026-04-10",
            "Due Date": "2026-06-09",
            "Status": "Open"
        }
    ])

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 PsychFlow Pro")
    st.write("---")
    st.subheader("📚 Active Resources")
    st.success("📁 Policy Manual Active")
    st.write("---")
    st.caption("Logged in as: Dr. K. Fonder")

# --- MAIN INTERFACE ---
st.title("📋 School Psychologist Case Tracker & Engine")
st.write("Extract timeline profiles directly from historical student documents.")
st.write("---")

tab1, tab2 = st.tabs(["📊 Case Overview", "➕ Ingest Multi-Document MEEGS"])

with tab1:
    st.subheader("Current Active Caseload")
    st.dataframe(st.session_state.cases, use_container_width=True)

with tab2:
    st.subheader("Log a New Evaluation Request")
    
    st.markdown("### 📂 Option A: Upload & Process Historical MEEGS")
    st.write("Dropping files here will extract all text and scan for historical lookup dates:")
    
    uploaded_docs = st.file_uploader("Drop all student PDF records here simultaneously:", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_docs:
        st.markdown("#### 🔍 Extraction & Processing Results:")
        
        for doc in uploaded_docs:
            with st.spinner(f"Processing and scanning {doc.name}..."):
                try:
                    # Read text layers out of the uploaded PDF file
                    reader = PdfReader(doc)
                    full_text = ""
                    for page in reader.pages:
                        text_content = page.extract_text()
                        if text_content:
                            full_text += text_content
                    
                    # Regex logic to scan for standard MM/DD/YYYY or YYYY-MM-DD dates inside the report text
                    found_dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', full_text)
                    
                    with st.expander(f"📄 Document Analysis Summary: {doc.name}", expanded=True):
                        st.write(f"**Total Characters Processed:** {len(full_text)}")
                        
                        if found_dates:
                            st.info(f"🔎 Found {len(found_dates)} timeline dates inside this file record.")
                            
                            # Take the first detected date as a baseline evaluation test date benchmark
                            try:
                                clean_date_str = found_dates[0].replace('/', '-')
                                # Handle standard short-year formatting gracefully
                                if len(clean_date_str.split('-')[-1]) == 2:
                                    parsed_date = datetime.strptime(clean_date_str, "%m-%d-%y").date()
                                else:
                                    parsed_date = datetime.strptime(clean_date_str, "%m-%d-%Y").date()
                                    
                                years_old = (datetime.now().date() - parsed_date).days / 365.25
                                
                                st.markdown(f"**Extracted Baseline Assessment Date:** `{parsed_date}`")
                                
                                if years_old > 6.0:
                                    st.error(f"❌ Expired Benchmark ({years_old:.1f} yrs old): Exceeds 6-year policy constraint. Fresh testing mandatory.")
                                elif years_old > 3.0:
                                    st.warning(f"⚠️ Transitional Benchmark ({years_old:.1f} yrs old): Valid for tracking metrics ONLY.")
                                else:
                                    st.success(f"✅ Current Benchmark ({years_old:.1f} yrs old): Within standard guidelines.")
                            except Exception:
                                st.warning(f"Detected potential target timeline markers: {found_dates[:3]}")
                        else:
                            st.warning("⚠️ Text layers parsed successfully, but no standard compliance date profiles were detected.")
                except Exception as e:
                    st.error(f"Could not extract data layer from {doc.name}: {str(e)}")
        st.write("---")
        
    st.markdown("### 📝 Option B: Manual Input Intake")
    with st.form("manual_case_form", clear_on_submit=True):
        initials = st.text_input("Student Initials (e.g., B.R.)")
        school = st.selectbox("School Site Assignment", ["Lincoln High", "Washington Middle", "Jefferson Elementary"])
        consent_date = st.date_input("Timeline Initiation / Consent Signed Date")
        
        submit_btn = st.form_submit_button("Confirm Intake & Calculate Compliance Timelines")
        if submit_btn:
            if initials:
                calculated_due = consent_date + timedelta(days=60)
                new_row = {
                    "Student Initials": initials, 
                    "School": school, 
                    "Category": "Manual Entry Profile",
                    "Consent Date": consent_date.strftime("%Y-%m-%d"), 
                    "Due Date": calculated_due.strftime("%Y-%m-%d"), 
                    "Status": "Open"
                }
                st.session_state.cases = pd.concat([st.session_state.cases, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Case profile for {initials} built successfully! Target deadline locked to 60 days out.")
                st.rerun()
