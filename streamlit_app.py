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
            "Category": "Initial Evaluation",
            "Consent Date": "2026-04-10",
            "Due Date": "2026-06-09",
            "Status": "Open",
            "Assigned Psychologist": "Dr. K. Fonder"
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
                # If a sheet layout doesn't specify a category column, auto-label it with the tab name
                if "Category" not in df.columns and "Category of Assessment" not in df.columns:
                    df["Workbook Tab / Category"] = sheet_name
                all_sheets.append(df)
            if all_sheets:
                return pd.concat(all_sheets, ignore_index=True)
        except Exception:
            pass
    return pd.DataFrame([
        {"Category": "Cognitive/Intellectual", "Tests Available": "WISC-V, WAIS-IV, WJ-IV COG, KABC-II"},
        {"Category": "Academic Achievement", "Tests Available": "WJ-IV ACH, KTEA-3, WIAT-4"},
        {"Category": "Executive Functioning / Attention", "Tests Available": "BRIEF-2, Conners-4, CEFI"},
        {"Category": "Social-Emotional / Behavioral", "Tests Available": "BASC-3, ASRS, Beck Scales"}
    ])

matrix_df = load_assessment_matrix()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 PsychFlow Pro")
    st.write("---")
    st.subheader("📚 Active Resources")
    st.success("📁 Policy Manual Loaded")
    if os.path.exists("Assessment_Matrix.xlsx"):
        st.success("📊 Custom Workbook Connected")
    else:
        st.info("📊 Using Default Test Matrix")
    st.write("---")
    st.caption("Logged in as: Dr. K. Fonder")

# --- MAIN DASHBOARD INTERFACE ---
st.title("📋 School Psychologist Case Tracker & Dashboard")
st.write("Manage timelines, compliance tracking, and case distribution seamlessly.")
st.write("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Case Overview", 
    "➕ Add New Case", 
    "📈 Visual Analytics",
    "🗂️ Assessment Matrix Cheat-Sheet"
])

with tab1:
    st.subheader("Current Case Load")
    st.dataframe(st.session_state.cases, use_container_width=True)

with tab2:
    st.subheader("Log a New Evaluation Request")
    with st.form("new_case_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            initials = st.text_input("Student Initials (e.g., A.B.)")
            school = st.selectbox("School", ["Lincoln High", "Washington Middle", "Jefferson Elementary"])
            category = st.selectbox("Evaluation Type", ["Initial Evaluation", "Re-evaluation", "Independent (IEE)"])
        with c2:
            consent_date = st.date_input("Consent Signed Date")
            psychologist = st.text_input("Assigned Psychologist", value="Dr. K. Fonder")
            
        submit_btn = st.form_submit_button("Add Case & Calculate Timelines")
        if submit_btn:
            if initials:
                calculated_due = consent_date + timedelta(days=60)
                new_row = {
                    "Student Initials": initials, 
                    "School": school, 
                    "Category": category, 
                    "Consent Date": consent_date.strftime("%Y-%m-%d"), 
                    "Due Date": calculated_due.strftime("%Y-%m-%d"), 
                    "Status": "Open", 
                    "Assigned Psychologist": psychologist
                }
                st.session_state.cases = pd.concat([st.session_state.cases, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Case for {initials} added successfully!")
                st.rerun()
            else:
                st.error("Please enter student initials.")

with tab3:
    st.subheader("Timeline & Compliance Tracking Visualization")
    if not st.session_state.cases.empty:
        fig = px.bar(st.session_state.cases, x="Student Initials", y="Category", color="Status", title="Evaluations by Status")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("🗂️ Interactive Assessment Tool Matrix")
    st.write("Your multi-tab workbook layout compiles dynamically below:")
    st.dataframe(matrix_df, use_container_width=True)
    st.write("---")
    st.markdown("### 📤 Upload Your Master Spreadsheet Workbook")
    uploaded_matrix = st.file_uploader("Drop your 'Assessments from EDPlan.xlsx' workbook file here", type=["xlsx"])
    if uploaded_matrix:
        with open("Assessment_Matrix.xlsx", "wb") as f:
            f.write(uploaded_matrix.getbuffer())
        st.success("🎉 Multi-tab workbook successfully parsed and loaded! Refreshing...")
        st.rerun()
