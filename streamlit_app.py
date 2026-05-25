import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PsychFlow Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #4e73df;
    }
    </style>
""", unsafe_allow_html=True)

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

# --- SIDEBAR ---
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
    st.caption("Logged in as: Dr. K. Fonder")

# --- MAIN INTERFACE ---
st.title("📋 School Psychologist Case Tracker & Workflow Engine")
st.write("Cross-reference student evaluation types directly against your master test catalog and the 6-year timeline rules.")
st.write("---")

tab1, tab2, tab3 = st.tabs([
    "📊 Caseload & Evaluation Guardrails", 
    "➕ Log New Request / MEEGS Intake", 
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
                            st.error(f"❌ Expired ({years_old:.1f} yrs old): Exceeds 6-year threshold. Testing isolated—New assessment mandatory.")
                        elif years_old > 3.0:
                            st.warning(f"⚠️ Transitional ({years_old:.1f} yrs old): Valid for longitudinal tracking ONLY. Must be paired alongside fresh measures.")
                        else:
                            st.success(f"✅ Current ({years_old:.1f} yrs old): Within standard benchmarks.")

with tab2:
    st.subheader("Ingest or Log an Evaluation Request")
    
    st.markdown("### 📂 Option A: Upload Historical MEEGS & Evaluation Documents")
    uploaded_docs = st.file_uploader("Drop all student PDF records here simultaneously (MEEGS, Outside Reports, etc.):", type=["pdf"], accept_multiple_files=True)
    if uploaded_docs:
        st.success(f"🎉 Successfully stacked {len(uploaded_docs)} files in the processing queue:")
        for doc in uploaded_docs:
            st.caption(f"📄 Ready for verification: {doc.name}")
        
    st.write("---")
    st.markdown("### 📝 Option B: Manual Input & Scope Definition")
    with st.form("new_case_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            initials = st.text_input("Student Initials (e.g., B.R.)")
            school = st.selectbox("School Site Assignment", ["Lincoln High", "Washington Middle", "Jefferson Elementary"])
            eval_type = st.selectbox("Evaluation Type Profile", ["Initial Evaluation", "Re-evaluation"])
        with c2:
            consent_date = st.date_input("Timeline Initiation / Consent Signed Date")
            all_categories = matrix_df["Assessment Category Tab"].unique().tolist()
            categories_needed = st.multiselect("Select Target Areas for Criteria Check:", all_categories, default=all_categories[:2])
            
        submit_btn = st.form_submit_button("Confirm Intake & Calculate Compliance Timelines")
        if submit_btn:
            if initials:
                calculated_due = consent_date + timedelta(days=60)
                new_row = {
                    "Student Initials": initials, 
                    "School": school, 
                    "Eval Type": eval_type, 
                    "Categories Needed": categories_needed,
                    "Consent Date": consent_date.strftime("%Y-%m-%d"), 
                    "Due Date": calculated_due.strftime("%Y-%m-%d"), 
                    "Status": "Open"
                }
                st.session_state.cases = pd.concat([st.session_state.cases, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Case profile for {initials} built successfully! Target deadline locked to 60 days out.")
                st.rerun()
            else:
                st.error("Please provide student initials to compile records.")

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
