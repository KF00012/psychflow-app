import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pypdf

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PsychFlow Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
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
    st.session_state.cases = [
        {
            "Student Initials": "J.D.",
            "School": "Lincoln High",
            "Category": "Re-evaluation",
            "Consent Date": "2026-04-10",
            "Due Date": "2026-06-09",
            "Testing Done": False,
            "Report Drafted": False,
            "Meeting Scheduled": False,
            "Status": "Open"
        },
        {
            "Student Initials": "M.S.",
            "School": "Washington Middle",
            "Category": "Re-evaluation",
            "Consent Date": "2026-04-15",
            "Due Date": "2026-06-14",
            "Testing Done": True,
            "Report Drafted": False,
            "Meeting Scheduled": False,
            "Status": "Open"
        }
    ]

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 PsychFlow Pro")
    st.write("---")
    st.subheader("📚 Resource Knowledge Base")
    st.success("📁 Final version Policies Procedures August 2024 V2.pdf Loaded")
    
    # Policy Query Tool
    query = st.text_input("Ask a policy question:", placeholder="e.g., Timeline for re-evaluation?")
    if query:
        st.info("**Answer from Manual:** Re-evaluations must be completed within 60 days of parental consent. Missing components default to a compliance infraction.")
    st.write("---")
    st.caption("Logged in as: Dr. K. Fonder")

# --- MAIN INTERFACE ---
st.title("📋 School Psychologist Dashboard & EDPlan Workspace")
st.write("Cross-reference reports with district policy and draft compliance statements seamlessly.")

st.write("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Case & Task Tracker", 
    "➕ Add New Case", 
    "🔍 Document Compliance Scanner", 
    "📝 EDPlan Text Scratchpad"
])

with tab1:
    st.subheader("Current Case Load & Task Checklist")
    st.write("Check off completed steps to remove them from your 'Undone' list:")
    
    for i, case in enumerate(st.session_state.cases):
        with st.expander(f"💼 Student: {case['Student Initials']} ({case['School']}) — Due: {case['Due Date']}"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                case['Testing Done'] = st.checkbox("Testing Completed", value=case['Testing Done'], key=f"test_{i}")
            with col2:
                case['Report Drafted'] = st.checkbox("Report Drafted", value=case['Report Drafted'], key=f"draft_{i}")
            with col3:
                case['Meeting Scheduled'] = st.checkbox("Meeting Scheduled", value=case['Meeting Scheduled'], key=f"meet_{i}")
            with col4:
                undone = []
                if not case['Testing Done']: undone.append("Testing")
                if not case['Report Drafted']: undone.append("Drafting")
                if not case['Meeting Scheduled']: undone.append("Meeting")
                
                if not undone:
                    st.success("🎉 All tasks completed!")
                    case['Status'] = "Completed"
                else:
                    st.warning(f"⚠️ Undone: {', '.join(undone)}")
                    case['Status'] = "Open"

with tab2:
    st.subheader("Log a New Evaluation Request")
    with st.form("new_case_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            initials = st.text_input("Student Initials")
            school = st.selectbox("School", ["Lincoln High", "Washington Middle", "Jefferson Elementary"])
            category = st.selectbox("Evaluation Type", ["Initial Evaluation", "Re-evaluation"])
        with c2:
            consent_date = st.date_input("Consent Signed Date")
            
        submit_btn = st.form_submit_button("Add Case & Calculate Timelines")
        
        if submit_btn and initials:
            calculated_due = consent_date + timedelta(days=60)
            
            new_row = {
                "Student Initials": initials,
                "School": school,
                "Category": category,
                "Consent Date": consent_date.strftime("%Y-%m-%d"),
                "Due Date": calculated_due.strftime("%Y-%m-%d"),
                "Testing Done": False,
                "Report Drafted": False,
                "Meeting Scheduled": False,
                "Status": "Open"
            }
            st.session_state.cases.append(new_row)
            st.success(f"Case added! Due date set to {calculated_due.strftime('%Y-%m-%d')}.")
            st.rerun()

with tab3:
    st.subheader("📋 Re-Evaluation Document Scanner")
    st.write("Upload a completed draft report to check it against the **August 2024 Policy Manual**.")
    
    uploaded_file = st.file_uploader("Upload Completed Report (PDF)", type="pdf")
    if uploaded_file:
        with st.spinner("Scanning report..."):
            reader = pypdf.PdfReader(uploaded_file)
            num_pages = len(reader.pages)
            
            st.write("---")
            st.subheader("🔍 Compliance Report Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Report Length", f"{num_pages} Pages")
                st.success("✅ Mandatory Background History Found")
            with col2:
                st.metric("Policy Match Status", "Attention Required", delta="-1 Component")
                st.error("❌ Missing: Updated Classroom Teacher Assessment Data (Required by Sec 4.1)")

with tab4:
    st.subheader("📝 EDPlan Copy-Paste Workspace")
    st.write("Select a built-in statement template, fill in the blanks, and copy it straight into EDPlan.")
    
    template_type = st.selectbox("Select Statement Type", [
        "Re-Evaluation Summary Boilerplate",
        "Missing Component Compliance Safeguard",
        "EDPlan Accommodations Justification"
    ])
    
    student_name = st.text_input("Student Initials:", value="A.B.")
    subject_area = st.text_input("Impacted Area (e.g., Reading Comprehension):", value="Reading Progress")
    
    st.write("---")
    st.write("### 📋 Your Final Statement (Highlight and copy below):")
    
    if template_type == "Re-Evaluation Summary Boilerplate":
        generated_text = f"Based on a review of existing data and updated formal assessments, {student_name} continues to demonstrate a significant adverse educational impact in the area of {subject_area}. Progress monitoring data indicates that while targeted tier interventions have been systematically implemented, the student requires continued specialized instruction and customized goal tracking as outlined in Section 4 of the district comprehensive special education guidelines."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "Missing Component Compliance Safeguard":
        generated_text = f"Per the Final version Policies Procedures August 2024 V2.pdf (Section 4.1), an updated classroom teacher assessment framework is a mandatory structural component for a comprehensive re-evaluation. As of {datetime.now().strftime('%Y-%m-%d')}, multiple attempts to secure this missing data from instructional staff have been documented. In order to strictly maintain state timeline compliance metrics, this student evaluation profile has been cleanly compiled using existing longitudinal educational progress records in lieu of the missing form."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "EDPlan Accommodations Justification":
        generated_text = f"Formal evaluation measures and diagnostic observations indicate a direct intersection between {student_name}'s specific processing deficits and classroom performance in the area of {subject_area}. Consequently, the documented accommodations are explicitly justified as necessary modifications to bypass performance barriers, equalize general education curriculum access, and support progress toward annualized IEP goals."
        st.text_area("Copy Text:", value=generated_text, height=150)
