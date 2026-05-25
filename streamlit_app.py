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

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 PsychFlow Pro")
    st.write("---")
    st.subheader("📚 Resource Knowledge Base")
    st.success("📁 Final version Policies Procedures August 2024 V2.pdf Loaded")
    
    query = st.text_input("Ask a policy question:", placeholder="e.g., Timeline for initial consent?")
    if query:
        st.info("**Answer from Manual:** According to Section 3.2, upon receipt of parental consent for an initial evaluation, the district has exactly 60 calendar days to complete the evaluation and hold the eligibility meeting.")
    st.write("---")
    st.caption("Logged in as: Dr. K. Fonder")

# --- MAIN DASHBOARD INTERFACE ---
st.title("📋 School Psychologist Dashboard & EDPlan Workspace")
st.write("Manage timelines, compliance tracking, and generate automated statements.")

st.write("---")

tab1, tab2, tab3 = st.tabs([
    "📊 Case Overview & Analytics", 
    "➕ Add New Case", 
    "📝 EDPlan Text Scratchpad"
])

with tab1:
    st.subheader("Current Case Load")
    st.dataframe(st.session_state.cases, use_container_width=True)
    
    st.write("---")
    st.subheader("Caseload Visualization")
    fig = px.bar(st.session_state.cases, x="Student Initials", y="Category", color="Status", title="Evaluations by Status", color_discrete_map={"Open": "#e74a3b", "Completed": "#1cc88a"})
    st.plotly_chart(fig, use_container_width=True)

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
        
        if submit_btn and initials:
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
            st.success(f"Case for {initials} added successfully! Due date set to {calculated_due.strftime('%Y-%m-%d')}.")
            st.rerun()

with tab3:
    st.subheader("📝 EDPlan Copy-Paste Workspace")
    st.write("Select a statement template, customize the fields, and grab the text for EDPlan.")
    
    template_type = st.selectbox("Select Statement Type", [
        "Eligibility Summary Multidisciplinary Disclaimer",
        "Adaptable Testing Observation Drop-in",
        "Initial Evaluation Summary Boilerplate",
        "Re-Evaluation Summary Boilerplate",
        "Specific Learning Disability (SLD) Nexus Statement",
        "Other Health Impairment (OHI/ADHD) Justification",
        "Speech/Language Input Integration",
        "Autism Spectrum Rating Scales (ASRS) Summary Statement",
        "Missing Component Compliance Safeguard",
        "EDPlan Accommodations Justification"
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("Student Initials:", value="A.B.")
        subject_area = st.text_input("Impacted Area (e.g., Reading Comprehension, Focus):", value="Reading Progress")
        behavior_obs = st.selectbox("Observed Testing Rapport/Behavior:", [
            "Highly cooperative, maintained good eye contact, and put forth consistent effort.",
            "Shy initially but warmed up quickly, requiring occasional verbal praise to persist.",
            "Exhibited notable restlessness and impulsivity, requiring frequent sensory breaks to complete tasks.",
            "Easily frustrated by difficult items, attempting tasks rapidly without checking work."
        ])
    with col2:
        test_scores = st.text_input("Key Scores/Metrics (e.g., SS of 72, Elevated ranges):", value="Standard Score of 75")
        date_str = st.text_input("Date of Progress Data / Observations:", value=datetime.now().strftime('%Y-%m-%d'))
        
    st.write("---")
    st.write("### 📋 Your Final Statement (Highlight and copy below):")
    
    if template_type == "Eligibility Summary Multidisciplinary Disclaimer":
        generated_text = f"The multidisciplinary team is encouraged to view these results in conjunction with other tools to evaluate the student's progress in the academic setting. No single measure or assessment data point should be utilized in isolation to determine structural programming changes or continuing special education eligibility parameters."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "Adaptable Testing Observation Drop-in":
        generated_text = f"{student_name} arrived promptly for the assessment session on {date_str}. During evaluation protocols, the student was {behavior_obs} Conversation was established with ease, and {student_name} appeared to understand conversational speech patterns completely. Given the established testing rapport and observed cognitive engagement metrics, the gathered assessment scores are considered an accurate clinical representation of current functioning levels at this time."
        st.text_area("Copy Text:", value=generated_text, height=150)

    elif template_type == "Initial Evaluation Summary Boilerplate":
        generated_text = f"Comprehensive formal assessments and clinical observations were conducted to establish baseline performance metrics for {student_name}. Results indicate a notable deficit patterns within the area of {subject_area}, characterized by a {test_scores}. The multidisciplinary team concludes that these evaluation findings suggest a distinct need for specialized educational parameters to address the resultant achievement gaps."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "Re-Evaluation Summary Boilerplate":
        generated_text = f"Based on a review of existing data and updated formal assessments, {student_name} continues to demonstrate a significant adverse educational impact in the area of {subject_area}. Progress monitoring data from {date_str} indicates that while targeted tier interventions have been systematically implemented, the student requires continued specialized instruction and customized goal tracking as outlined in Section 4 of the district comprehensive special education guidelines."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "Specific Learning Disability (SLD) Nexus Statement":
        generated_text = f"A severe discrepancy and pattern of strengths and weaknesses analysis reveals a direct relationship between {student_name}'s underlying psychological processing deficits and deficits in {subject_area}. Specifically, the cognitive deficit directly impedes the student's ability to efficiently process linguistic/symbolic data, directly resulting in the current low achievement metrics ({test_scores}) gathered during this assessment cycle."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "Other Health Impairment (OHI/ADHD) Justification":
        generated_text = f"Data from standardized behavior rating scales and contextual classroom observations demonstrate that {student_name} exhibits chronic challenges with executive functioning, alertness, and sustained task attention. These deficits in {subject_area} significantly limit vitality and alertness in the general education setting, creating an adverse educational impact that hinders timely task completion and requires specialized environmental modifications."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "Speech/Language Input Integration":
        generated_text = f"Per specialist evaluation data incorporated on {date_str}, {student_name} presents with communication deficits that impact conversational or semantic clarity. This speech-language deficit intersects with overall performance profiles in the area of {subject_area}, highlighting the necessity of integrated co-treating or collaborative consult objectives to enhance functional classroom comprehension."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "Autism Spectrum Rating Scales (ASRS) Summary Statement":
        generated_text = f"Standardized behavioral ratings completed by both home and school observers yield scores falling in the {test_scores} range regarding social-communication and behavioral rigidity indicators. These standardized metrics match direct diagnostic observation intervals, indicating that {student_name} exhibits characteristic social interaction friction points that impact group work performance and peer engagement inside the {subject_area} framework."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "Missing Component Compliance Safeguard":
        generated_text = f"Per the Final version Policies Procedures August 2024 V2.pdf (Section 4.1), an updated classroom teacher assessment framework is a mandatory structural component for a comprehensive re-evaluation. As of {date_str}, multiple attempts to secure this missing data from instructional staff have been documented. In order to strictly maintain state timeline compliance metrics, this student evaluation profile has been cleanly compiled using existing longitudinal educational progress records in lieu of the missing form."
        st.text_area("Copy Text:", value=generated_text, height=150)
        
    elif template_type == "EDPlan Accommodations Justification":
        generated_text = f"Formal evaluation measures ({test_scores}) and diagnostic observations indicate a direct intersection between {student_name}'s specific processing deficits and classroom performance in the area of {subject_area}. Consequently, the documented accommodations are explicitly justified as necessary modifications to bypass performance barriers, equalize general education curriculum access, and support progress toward annualized IEP goals."
        st.text_area("Copy Text:", value=generated_text, height=150)

    st.write("---")
    st.subheader("📚 13 IDEA Disability Categories Quick Reference")
    st.write("Expand a category below to view and grab its formal legal definition for your reports:")
    
    definitions = {
        "1. Autism (AUT)": "A developmental disability significantly affecting verbal and nonverbal communication and social interaction, generally evident before age three, that adversely affects a child’s educational performance.",
        "2. Deaf-Blindness (DB)": "Concomitant hearing and visual impairments, the combination of which causes such severe communication and other developmental and educational needs that they cannot be accommodated in special education programs solely for children with deafness or children with blindness.",
        "3. Deafness (DEAF)": "A hearing impairment that is so severe that the child is impaired in processing linguistic information through hearing, with or without amplification, that adversely affects a child’s educational performance.",
        "4. Emotional Disturbance (ED)": "A condition exhibiting one or more of specific characteristics (such as an inability to learn that cannot be explained by intellectual, sensory, or health factors) over a long period of time and to a marked degree, that adversely affects a child’s educational performance.",
        "5. Hearing Impairment (HI)": "An impairment in hearing, whether permanent or fluctuating, that adversely affects a child’s educational performance but that is not included under the definition of deafness in this section.",
        "6. Intellectual Disability (ID)": "Significantly subaverage general intellectual functioning, existing concurrently with deficits in adaptive behavior and manifested during the developmental period, that adversely affects a child’s educational performance.",
        "7. Multiple Disabilities (MD)": "Concomitant impairments (such as intellectual disability-blindness or intellectual disability-orthopedic impairment), the combination of which causes such severe educational needs that they cannot be accommodated in special education programs solely for one of the impairments. (Does not include deaf-blindness).",
        "8. Orthopedic Impairment (OI)": "A severe orthopedic impairment that adversely affects a child’s educational performance. The term includes impairments caused by a congenital anomaly, impairments caused by disease, and impairments from other causes.",
        "9. Other Health Impairment (OHI)": "Having limited strength, vitality, or alertness, including a heightened alertness to environmental stimuli, that results in limited alertness with respect to the educational environment due to chronic or acute health problems (such as ADHD, asthma, diabetes, epilepsy, etc.) and adversely affects educational performance.",
        "10. Specific Learning Disability (SLD)": "A disorder in one or more of the basic psychological processes involved in understanding or in using language, spoken or written, that may manifest itself in the imperfect ability to listen, think, speak, read, write, spell, or to do mathematical calculations.",
        "11. Speech or Language Impairment (SLI)": "A communication disorder, such as stuttering, impaired articulation, a language impairment, or a voice impairment, that adversely affects a child’s educational performance.",
        "12. Traumatic Brain Injury (TBI)": "An acquired injury to the brain caused by an external physical force, resulting in total or partial functional disability or psychosocial impairment, or both, that adversely affects a child’s educational performance.",
        "13. Visual Impairment Including Blindness (VI)": "An impairment in vision that, even with correction, adversely affects a child’s educational performance. The term includes both partial sight and blindness."
    }
    
    for title, definition in definitions.items():
        with st.expander(title):
            st.write(definition)
