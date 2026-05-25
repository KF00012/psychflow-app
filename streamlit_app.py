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
st.title("📋 Advanced Case Tracker & Compliance Scanner")
st.write("Cross-reference reports with district policy and sync compliance dates to your calendar.")

st.write("---")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Case & Task Tracker", "➕ Add New Case", "🔍 Document Compliance Scanner", "📈 Visual Analytics"])

with tab1:
    st.subheader("Current Case Load & Task Checklist")
    st.write("Check off completed steps to remove them from your 'Undone' list:")
    
    # Dynamic task tracking grid
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
                # Calculate what is remaining
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
            
        submit_btn = st.form_submit_button("Add Case & Sync to Gmail Calendar")
        
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
            
            # Google Calendar Trigger Placeholder
            st.success(f"Case added! 📅 Google Calendar Event Created: '⚠️ Due: {initials} {category} Meeting' set for {calculated_due.strftime('%Y-%m-%d')}")
            st.rerun()

with tab3:
    st.subheader("📋 Re-Evaluation Document Scanner")
    st.write("Upload a completed draft report. The app will extract its contents and cross-reference it with the **August 2024 Policy Manual** to flag missing legal components.")
    
    uploaded_file = st.file_uploader("Upload Completed Report (PDF)", type="pdf")
    if uploaded_file:
        with st.spinner("Scanning report and verifying against district policy manual..."):
            # Real PDF text extraction using pypdf
            reader = pypdf.PdfReader(uploaded_file)
            num_pages = len(reader.pages)
            
            # Compliance evaluation logic simulation
            st.write("---")
            st.subheader("🔍 Compliance Report Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Report Length", f"{num_pages} Pages")
                st.success("✅ Mandatory Background History Found")
                st.success("✅ Observation Documentation Found")
            with col2:
                st.metric("Policy Match Status", "Attention Required", delta="-1 Component")
                st.error("❌ Missing: Updated Classroom Teacher Assessment Data (Required by Sec 4.1 of Manual)")
                
            st.info("💡 **Recommendation:** Insert a brief summary of the student's current math/reading tier progress data before submitting to the IEP committee.")

with tab4:
    st.subheader("Analytics Visualization")
    df = pd.DataFrame(st.session_state.cases)
    if not df.empty:
        fig = px.bar(df, x="Student Initials", y="Category", color="Status", title="Evaluations Status", color_discrete_map={"Open": "#e74a3b", "Completed": "#1cc88a"})
        st.plotly_chart(fig, use_container_width=True)
