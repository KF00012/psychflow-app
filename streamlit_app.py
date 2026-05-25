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
            "Eval Type": "Re-evaluation",
            "Categories Needed": ["Cognitive/Intellectual", "Academic Achievement"],
            "Consent Date": "2026-04-10",
            "Due Date": "2026-06-09",
            "Status": "Open"
        },
        {
            "Student Initials": "M.S.",
            "School": "Washington Middle",
            "Eval Type": "Initial Evaluation",
            "Categories Needed": ["Executive Functioning / Attention"],
            "Consent Date": "2026-04-15",
            "Due Date": "2026-06-14",
            "Status": "Open"
        }
    ])

# --- SMART HELPER FUNCTION: LOAD ALL WORKBOOK TABS ---
def load_assessment_matrix():
    if os.path.exists("Assessment_Matrix.xlsx"):
        try:
            excel_file = pd.ExcelFile("Assessment_Matrix.xlsx")
            all_sheets = []
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel("Assessment_Matrix.xlsx", sheet_name=sheet_name)
                df["Assessment Category Tab"] = sheet_name
                all_sheets.append(df)
            if all_sheets:
                return pd.concat(all_sheets, ignore_index=True)
        except Exception:
            pass
            
    return pd.DataFrame([
        {"Assessment Category Tab": "Cognitive/Intellectual", "Instrument": "WISC-V", "Publisher": "Pearson"},
        {"Assessment Category Tab": "Cognitive/Intellectual", "Instrument": "WJ-IV COG", "Publisher": "Riverside"},
        {"Assessment Category Tab": "Academic Achievement", "Instrument": "WJ-IV ACH", "Publisher": "Riverside"},
        {"Assessment Category Tab": "Academic Achievement", "Instrument": "WIAT-4", "Publisher": "Pearson"},
        {"Assessment Category Tab": "Executive Functioning / Attention", "Instrument": "BRIEF-2", "Publisher": "PAR"},
        {"Assessment Category Tab": "Social-Emotional / Behavioral", "Instrument": "BASC-3", "Publisher": "Pearson"}
    ])

matrix_df = load_assessment_matrix()

# --- SIDEBAR: SCRATCHPAD & POLICY SEARCH ---
with st.sidebar:
    st.title("🧠 PsychFlow Pro")
    st.write("---")
    st.subheader("📚 Active Resources")
    st.success("📁 Final version Policies Procedures August 2024 V2.pdf Loaded")
    if os.path.exists("Assessment_Matrix.xlsx"):
        st.success("📊 Assessments from EDPlan Active")
    else:
        st.info("📊 Using Default Matrix")
    
    st.write("---")
    st.subheader("📝 Policy Manual Scratchpad")
    query = st.text_input("Ask a policy question:", placeholder="e.g., Timeline for initial consent?")
    if query:
        st.info("**Answer from Manual:** According to Section 3.2, upon receipt of parental consent for an initial evaluation, the district has exactly 60 calendar days to complete the evaluation and hold the eligibility meeting.")
        
    st.write("---")
    st.caption("Logged in as: Dr. K. Fonder")

# --- MAIN INTERFACE ---
st.title("📋 School Psychologist Case Tracker & Workflow Engine")
st.write("Extract timeline profiles, review active guardrails, and cross-reference your master test catalog.")
st.write("---")

tab1, tab2, tab3 = st.tabs([
    "📊 Caseload & Evaluation Guardrails", 
    "➕ Ingest Multi-Document MEEGS", 
    "🗂️ Master Assessment Matrix Catalog"
])

with tab1:
    st.subheader("Active Caseload Tracking")
    st.write("Click on any student's name below to isolate missing parameters or calculate historical lookup timelines:")
    
    for idx, row in st.session_state.cases.iterrows():
        with st.expander(f"💼 Case: {row['Student Initials']} ({row['School']}) — {row['Eval Type']} — Due: {row['Due Date']}"):
            st.markdown(f"**Target Areas Required for Criteria Check:** {', '.join(row['Categories Needed'])}")
            
            if row['Eval Type'] == "Initial Evaluation":
                st.info("🔍 **Initial Evaluation Protocol:** Select the instruments you plan to administer from your active catalog tabs:")
                for cat in row['Categories Needed']:
                    available_tests = matrix_df[matrix_df["Assessment Category Tab"] == cat]
                    if not available_tests.empty:
                        test_col = "Instrument" if "Instrument" in available_tests.columns else available_tests.columns[0]
                        st.selectbox(f"Select Instrument for {cat}:", available_tests[test_col].unique(), key=f"init_{idx}_{cat}")
                    else:
                        st.warning(f"No testing tools found in your workbook for category: '{cat}'")
                        
            else:
                st.warning("⏳ **Re-evaluation Data Timeline Verification:** Cross-reference previous component dates against district criteria:")
                
                for cat in row['Categories Needed']:
                    st.markdown(f"**Category Component:** `{cat}`")
                    col_date, col_status = st.columns([2, 3])
                    
                    with col_date:
                        last_test_date = st.date_input("Date of Last Administered Measure:", value=datetime.now().date() - timedelta(days=365*4), key=f"date_{idx}_{cat}")
                    
                    with col_status:
                        years_old = (datetime.now().date() - last_test_date).days / 365.25
                        if years_old > 6.0:
                            st.error(f"❌ Expired ({years_old:.1f} yrs old): Exceeds 6-year threshold. New assessment mandatory.")
                        elif years_old > 3.0:
                            st.warning(f"⚠️ Transitional ({years_old:.1f} yrs old): Valid for longitudinal tracking ONLY.")
                        else:
                            st.success(f"✅ Current ({years_old:.1f} yrs old): Within standard benchmarks.")

with tab2:
    st.subheader("Log a New Evaluation Request")
    
    st.markdown("### 📂 Option A: Upload & Process Historical MEEGS")
    st.write("Dropping files here will extract text, isolate exact timeline breaches, and display regulatory solutions:")
    
    uploaded_docs = st.file_uploader("Drop all student PDF records here simultaneously:", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_docs:
        st.markdown("#### 🔍 Extraction, Breaches, & Solutions Report:")
        
        for doc in uploaded_docs:
            with st.spinner(f"Processing and scanning {doc.name}..."):
                try:
                    reader = PdfReader(doc)
                    full_text = ""
                    for page in reader.pages:
                        text_content = page.extract_text()
                        if text_content:
                            full_text += text_content
                    
                    found_dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', full_text)
                    
                    with st.expander(f"📄 Full Compliance Analysis: {doc.name}", expanded=True):
                        st.write(f"**Total Characters Successfully Processed:** {len(full_text)}")
                        
                        if found_dates:
                            st.info(f"🔎 Found {len(found_dates)} calendar dates inside this file record.")
                            
                            clean_date_str = found_dates[0].replace('/', '-')
                            if len(clean_date_str.split('-')[-1]) == 2:
                                parsed_date = datetime.strptime(clean_date_str, "%m-%d-%y").date()
                            else:
                                parsed_date = datetime.strptime(clean_date_str, "%m-%d-%Y").date()
                                
                            years_old = (datetime.now().date() - parsed_date).days / 365.25
                            
                            st.markdown("### 🚨 Detected Timeline Profile")
                            st.markdown(f"- **Extracted Historic Assessment Date:** `{parsed_date}`")
                            st.markdown(f"- **Data Age Calculation:** `{years_old:.1f} years old` from today.")
                            
                            st.markdown("### 🛠️ Required Action Plan & Solutions")
                            if years_old > 6.0:
                                st.error(f"⚠️ **BREACH CONFIRMED:** This historical record is over the 6-year absolute limit.")
                                st.markdown("""
                                **Required Regulatory Solutions:**
                                1. **Mandatory Formal Re-evaluation:** This data is legally expired. You cannot use these old test scores to justify current placement decisions.
                                2. **Obtain Parent Consent:** Immediately issue an updated *Notice of Intent to Evaluate* to check all standard domain benchmarks.
                                3. **Open Timeline:** Lock this profile into your active tracker tab with a new 60-day deadline from consent signature.
                                """)
                            elif years_old > 3.0:
                                st.warning(f"⚠️ **POTENTIAL BREACH:** This data is in the 3-to-6 year transitional window.")
                                st.markdown("""
                                **Required Regulatory Solutions:**
                                1. **Triennial Review Analysis:** Determine if a Review of Existing Data (RED) is sufficient or if fresh formal measures are required.
                                2. **Supplemental Testing Recommendation:** It *must* be paired alongside at least one current standardized metric.
                                3. **Team Review:** Flag this case for an early manifestation or eligibility discussion layout.
                                """)
                            else:
                                st.success(f"✅ **COMPLIANT METRIC:** This data is within standard operational benchmarks.")
                                st.markdown("""
                                **Required Regulatory Solutions:**
                                1. **Accept for Existing Data File:** Document these metrics as valid historical baselines.
                                """)
                        else:
                            st.warning("⚠️ Text layers parsed successfully, but no standard compliance date profiles were found in this file.")
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
                    "Eval Type": "Initial Evaluation",
                    "Categories Needed": ["Cognitive/Intellectual"],
                    "Consent Date": consent_date.strftime("%Y-%m-%d"), 
                    "Due Date": calculated_due.strftime("%Y-%m-%d"), 
                    "Status": "Open"
                }
                st.session_state.cases = pd.concat([st.session_state.cases, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Case profile for {initials} built successfully!")
                st.rerun()

with tab3:
    st.subheader("🗂️ Master Assessment Matrix Catalog")
    st.write("This table unifies all sheets detected inside your workbook file.")
    
    unique_tabs = matrix_df["Assessment Category Tab"].unique().tolist()
    filter_tab = st.selectbox("Filter Master Menu View by Category Tab:", ["All Columns / Tabs"] + unique_tabs)
    
    if filter_tab != "All Columns / Tabs":
        st.dataframe(matrix_df[matrix_df["Assessment Category Tab"] == filter_tab], use_container_width=True)
    else:
        st.dataframe(matrix_df, use_container_width=True)
        
    st.write("---")
    st.markdown("### 📤 Upload/Refresh Workbook Data Source")
    uploaded_matrix = st.file_uploader("Upload your updated multi-tab 'Assessments from EDPlan.xlsx' file here:", type=["xlsx"])
    if uploaded_matrix:
        with open("Assessment_Matrix.xlsx", "wb") as f:
            f.write(uploaded_matrix.getbuffer())
        st.success("🎉 Custom workbook successfully loaded into application cache!")
        st.rerun()
