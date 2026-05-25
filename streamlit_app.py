import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

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
    .status-open { color: #e74a3b; font-weight: bold; }
    .status-completed { color: #1cc88a; font-weight: bold; }
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
        },
        {
            "Student Initials": "M.S.",
            "School": "Washington Middle",
            "Category": "Re-evaluation",
            "Consent Date": "2026-04-15",
            "Due Date": "2026-06-14",
            "Status": "Open",
            "Assigned Psychologist": "Dr. K. Fonder"
        }
    ])

# --- SIDEBAR: RESOURCE MANUAL & NAVIGATION ---
with st.sidebar:
    st.title("🧠 PsychFlow Pro")
    st.write("---")
    st.subheader("📚 Resource Knowledge Base")
    st.success("📁 Policy Manual Loaded")
    st.write("---")
    st.caption("Logged in as: Dr. K. Fonder")

# --- MAIN DASHBOARD INTERFACE ---
st.title("📋 School Psychologist Case Tracker & Dashboard")
st.write("Manage timelines, compliance tracking, and case distribution seamlessly.")
st.write("---")

# --- CASE MANAGEMENT & INPUT TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Case Overview", "➕ Add New Case", "📈 Visual Analytics"])

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
                st.success(f"Case for {initials} added successfully! Due date set to {calculated_due.strftime('%Y-%m-%d')} (60 days out).")
                st.rerun()
            else:
                st.error("Please enter student initials.")

with tab3:
    st.subheader("Timeline & Compliance Tracking Visualization")
    if not st.session_state.cases.empty:
        fig = px.bar(st.session_state.cases, x="Student Initials", y="Category", color="Status", title="Evaluations by Status", color_discrete_map={"Open": "#e74a3b", "Completed": "#1cc88a"})
        st.plotly_chart(fig, use_container_width=True)
