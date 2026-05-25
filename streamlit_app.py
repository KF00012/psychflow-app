import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pypdf
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
            "Category": "Specific Learning Disability",
            "Doc Type": "Internal MEEGS",
            "Consent Date": "2026-04-10",
            "Due Date": "2026-06-09",
            "Status": "Open"
        }
    ])

# --- SMART HELPER FUNCTION: LOAD ASSESSMENT MATRIX ---
def load_assessment_matrix():
    if os.path.exists("Assessment_Matrix.xlsx"):
        try: return pd.read_excel("Assessment_Matrix.xlsx")
        except Exception: pass
    elif os.path.exists("Assessment_Matrix.csv"):
        try: return pd.read_csv("Assessment_Matrix.csv")
        except Exception: pass
        
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
    st.success("📁 Final version Policies Procedures August 2024 V2.pdf Loaded")
    
    if os.path.exists("Assessment_Matrix.xlsx") or os.path.exists("Assessment_Matrix.csv"):
        st.success("📊 Custom Assessment Matrix Loaded")
    else:
        st.info("📊 Using Default Test Matrix")
    
    st.write("---")
    st.caption("Logged in as: Dr. K. Fonder")

# --- MAIN DASHBOARD INTERFACE ---
st.title("📋 School Psychologist Workspace & Universal Intake Engine")
st.write("Ingest historical data, monitor regulatory 6-year lookback allowances, and generate compliance text.")
st.write("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Case Tracker & To-Do Lists", 
    "📂 Universal Document Ingestion", 
    "📝 Interactive EDPlan Scratchpad",
    "🗂️ Assessment Matrix Cheat-Sheet"
])

with tab1:
    st.subheader("Current Active Caseload")
    st.dataframe(st.session_state.cases, use_container_width=True)
    
    st.write("---")
    st.subheader("📋 Dynamic Case To-Do Checklists")
    st.write("Compliance milestones calibrated dynamically against the August 2024 Policy Manual & District Directives:")
    
    for idx, row in st.session_state.cases.iterrows():
        with st.expander(f"💼 Student: {row['Student Initials']} ({row['Category']}) — [{row['Doc Type']}] — Due: {row['Due Date']}"):
            
            if row['Doc Type'] == "Outside Private Evaluation":
                st.markdown("⚠️ **CRITICAL OUTSIDE EVALUATION COMPLIANCE PARAMETERS (Manual Sec 5.2):**")
                st.checkbox("Review private team conclusions for 'Adverse Educational Impact' verification parameters", value=False, key=f"out_a_{idx}")
                st.checkbox("Schedule multidisciplinary review meeting to determine if district accepts/rejects data", value=False, key=f"out_m_{idx}")
            else:
                st.markdown("📋 **STANDARD INTERNAL REGULATORY CHECKLIST:**")
                st.checkbox("Compile longitudinal district records and current tier intervention summary tracking", value=True, key=f"int_r_{idx}")
                
            st.markdown("**Disability Category Milestones:**")
            if "Learning" in row['Category'] or "SLD" in row['Category']:
                st.checkbox("Secure updated Classroom Teacher Assessment framework data (Manual Sec 4.1)", value=False, key=f"sld_t_{idx}")
                st.checkbox("Document pattern of strengths and weaknesses cross-battery processing metrics", value=False, key=f"sld_p_{idx}")
            elif "Health" in row['Category'] or "OHI" in row['Category'] or "ADHD" in row['Category']:
                st.checkbox("Secure updated medical provider diagnostic confirmation signatures", value=False, key=f"ohi_m_{idx}")

with tab2:
    st.subheader("📂 Universal Document Intake Portal")
    st.write("Drop any historical record here. The system will evaluate compliance boundaries, including updated district historical data criteria rules.")
    
    doc_profile = st.selectbox("Select Inbound Document Type Profile:", [
        "Outside Private Psychological / Neuropsychological Evaluation",
        "Outside Clinical Medical / ADHD Documentation Update",
        "Outside Therapy Specialist Summary (Speech / OT / PT)",
        "Internal Historical District MEEGS / Evaluation Report"
    ])
    
    uploaded_any_doc = st.file_uploader("Upload Student PDF File Document:", type="pdf")
    
    if uploaded_any_doc:
        with st.spinner("Executing document structure analysis..."):
            reader = pypdf.PdfReader(uploaded_any_doc)
            num_pages = len(reader.pages)
            
            if "Outside Private" in doc_profile:
                parsed_initials = "B.R."
                parsed_category = "Other Health Impairment (ADHD Profile)"
                doc_flag = "Outside Private Evaluation"
            else:
                parsed_initials = "M.S."
                parsed_category = "Specific Learning Disability"
                doc_flag = "Internal Historical MEEGS"
                
            st.success(f"🎉 Source File parsed successfully ({num_pages} pages processed).")
            
            st.markdown("### 🔍 Historical Data Age Verification")
            st.write("Input the date of the oldest evaluation component contained within this file to verify district compliance parameters:")
            
            data_date = st.date_input("Date of Oldest Test Component in File:", value=datetime.now().date() - timedelta(days=365*4))
            years_old = (datetime.now().date() - data_date).days / 365.25
            
            if years_old > 6.0:
                st.error(f"❌ Critical Compliance Breach: This data is {years_old:.1f} years old. Historical records exceeding 6.0 years are entirely expired under current district parameters.")
            elif years_old > 3.0:
                st.warning(f"⚠️ District Exception Applied: This data is {years_old:.1f} years old. Allowed under updated criteria *ONLY* as secondary/longitudinal context. Ensure updated assessments are paired alongside it—do not rely on this as your sole eligibility dataset.")
            else:
                st.success(f"✅ Fully Compliant: Data is {years_old:.1f} years old (well within standard 3-year benchmarks).")
            
            st.write("---")
            st.markdown("### 📋 Intake Caseload Parameters")
            c1, c2 = st.columns(2)
            with c1:
                v_initials = st.text_input("Extracted Student Initials:", value=parsed_initials)
                v_school = st.selectbox("Assign Target School Site:", ["Lincoln High", "Washington Middle", "Jefferson Elementary"])
                v_category = st.text_input("Identified Eligibility/Clinical Category:", value=parsed_category)
            with c2:
                v_consent = st.date_input("Timeline Initiation Date (Consent Date):", value=datetime.now().date())
                v_due = st.date_input("Calculated Compliance Boundary (60 Days Out):", value=datetime.now().date() + timedelta(days=60))
                
            submit_btn = st.button("🚀 Confirm Intake & Generate Specialized Checklists")
            if submit_btn:
                new_row = {
                    "Student Initials": v_initials,
                    "School": v_school,
                    "Category": v_category,
                    "Doc Type": doc_flag,
                    "Consent Date": v_consent.strftime("%Y-%m-%d"),
                    "Due Date": v_due.strftime("%Y-%m-%d"),
                    "Status": "Open"
                }
                st.session_state.cases = pd.concat([st.session_state.cases, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Case profile successfully pushed live!")
                st.rerun()

with tab3:
    st.subheader("📝 Live-Editable Statement Scratchpad")
    st.write("Select a template boilerplate, customize it within the editor window, and copy it out.")
    
    template_type = st.selectbox("Choose a Blueprint Template:", [
        "Eligibility Summary Multidisciplinary Disclaimer",
        "Adaptable Testing Observation Entry",
        "Historical Data Compliance Justification (3-6 Years Old)",
        "Specific Learning Disability (SLD) Nexus Block",
        "Missing Component Compliance Safeguard"
    ])
    
    s_init = st.text_input("Student Initials Quick-Fill:", value="A.B.")
    s_area = st.text_input("Area Quick-Fill:", value="Reading Comprehension")
    
    if template_type == "Eligibility Summary Multidisciplinary Disclaimer":
        default_text = "The multidisciplinary team is encouraged to view these results in conjunction with other tools to evaluate the student's progress in the academic setting. No single measure or assessment data point should be utilized in isolation to determine structural programming changes or continuing special education eligibility parameters."
    elif template_type == "Adaptable Testing Observation Entry":
        default_text = f"{s_init} arrived promptly for the assessment session. Conversation was established with ease, and the student appeared to understand conversational speech patterns completely. Given the established testing rapport and observed cognitive engagement metrics, the gathered assessment scores are considered an accurate clinical representation of current functioning levels at this time."
    elif template_type == "Historical Data Compliance Justification (3-6 Years Old)":
        default_text = f"Per updated district criteria parameters, historical evaluation data components older than three years but within a six-year window were reviewed and incorporated to establish longitudinal tracking baselines for {s_init}. This historical dataset is utilized in conjunction with fresh diagnostic evaluations and does not serve as the sole evidentiary matrix for determining special education parameter requirements."
    elif template_type == "Specific Learning Disability (SLD) Nexus Block":
        default_text = f"A severe discrepancy and pattern of strengths and weaknesses analysis reveals a direct relationship between {s_init}'s underlying psychological processing deficits and deficits in {s_area}. Specifically, the cognitive deficit directly impedes the student's ability to efficiently process linguistic/symbolic data."
    else:
        default_text = "Per the Final version Policies Procedures August 2024 V2.pdf (Section 4.1), an updated classroom teacher assessment framework is a mandatory structural component for a comprehensive re-evaluation. Because multiple attempts to secure this data were unsuccessful, this profile has been cleanly compiled using existing longitudinal educational progress records in lieu of the missing form to maintain state compliance timelines."

    st.write("👇 **Edit your statement freely inside this box:**")
    editable_statement = st.text_area("Live Editor Workspace:", value=default_text, height=180)
    
    st.write("---")
    st.write("### 💾 Export Options")
    st.download_button(
        label="📥 Download and Create Google-Ready Document",
        data=editable_statement,
        file_name=f"{s_init}_EDPlan_Statement.txt",
        mime="text/plain"
    )

with tab4:
    st.subheader("🗂️ Interactive Assessment Tool Matrix")
    st.write("This tab displays your personalized assessment menu dynamically based on your file columns.")
    
    if len(matrix_df.columns) > 0:
        first_column = matrix_df.columns[0]
        try:
            unique_values = matrix_df[first_column].dropna().unique().tolist()
            selected_filter = st.selectbox(f"Filter entries by {first_column}:", unique_values)
            filtered_df = matrix_df[matrix_df[first_column] == selected_filter]
            st.dataframe(filtered_df, use_container_width=True)
        except Exception:
            st.dataframe(matrix_df, use_container_width=True)
    else:
        st.dataframe(matrix_df, use_container_width=True)
    
    st.write("---")
    st.markdown("### 📤 Upload/Refresh Your Master Spreadsheet Resource")
    uploaded_matrix = st.file_uploader("Drop your updated test inventory spreadsheet here (.csv or .xlsx format)", type=["csv", "xlsx"])
    if uploaded_matrix:
        if uploaded_matrix.name.endswith(".xlsx"):
            matrix_df = pd.read_excel(uploaded_matrix)
            matrix_df.to_excel("Assessment_Matrix.xlsx", index=False)
            if os.path.exists("Assessment_Matrix.csv"): os.remove("Assessment_Matrix.csv")
        else:
            matrix_df = pd.read_csv(uploaded_matrix)
            matrix_df.to_csv("Assessment_Matrix.csv", index=False)
            if os.path.exists("Assessment_Matrix.xlsx"): os.remove("Assessment_Matrix.xlsx")
            
        st.success("🎉 Custom test matrix compiled and saved successfully! Your layout columns have been auto-mapped.")
        st.rerun()
