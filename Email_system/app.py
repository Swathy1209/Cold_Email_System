

import streamlit as st
import pandas as pd
import os
import json
from llm import (
    get_client, 
    generate_email, 
    generate_subject_lines, 
    simulate_ab_test,
    rewrite_for_region, 
    personalise_opening, 
    improve_email,
    get_best_subject,
    get_reply_score,
    get_why_this_works,
    auto_improve_using_feedback,
    MODEL_NAME
)
from utils import validate_inputs, score_to_emoji, word_count, build_export_text

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ColdCraft AI Elite",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; }
.main-header {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    padding: 2.5rem 2rem 2rem 2rem;
    border-radius: 16px; color: white; margin-bottom: 2rem;
}
.main-header h1 { color: white; font-size: 2.4rem; margin: 0; }
.main-header p { color: rgba(255,255,255,0.75); font-size: 1rem; margin-top: 0.5rem; }
.stButton > button { background: linear-gradient(135deg, #302b63, #24243e); color: white; border: none; border-radius: 8px; padding: 0.6rem 1.5rem; font-weight: 600; font-size: 0.95rem; width: 100%; transition: opacity 0.2s; }
.stButton > button:hover { opacity: 0.85; }
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <h1>✉️ ColdCraft AI Elite</h1>
    <p>Persona Targeting · A/B Testing · Autonomous Feedback Execution · CSV Integration</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar Inputs ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "Groq API Key", type="password",
        value="[ENCRYPTION_KEY]",
        help="Your key is securely used without persistence."
    )
    st.divider()

    st.markdown("### 🎯 Campaign Details")
    product = st.text_area(
        "Product Description",
        placeholder="e.g. ERP software for mid-sized companies that reduces manual finance processes by 60%",
        height=90,
    )
    audience = st.text_input("Target Audience", placeholder="e.g. CFOs")
    region = st.selectbox("Campaign Region", ["Global", "US", "UAE", "UK", "India"])
    persona = st.selectbox("Persona Focus", ["Founder", "CFO", "Head of Operations", "Other (General)"])
    st.divider()
    
    st.markdown("### � Data Input Method")
    input_mode = st.radio("Select how to input recipient data:", ["Manual Entry", "Load from CSV Dataset"])
    
    # Initialize variables for the UI
    name_val = ""
    role_val = ""
    company_type_val = ""
    location_val = ""
    notes_val = ""

    if input_mode == "Load from CSV Dataset":
        csv_path = r"C:\Users\swathiga\Downloads\Email_system\Email_Dataset.csv"
        
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                st.success(f"Loaded {len(df)} leads successfully.")
                
                # Create a selector for the leads
                def format_lead(row):
                    fname = str(row.get('first name', ''))
                    lname = str(row.get('last name', ''))
                    company = str(row.get('company', ''))
                    return f"{fname} {lname} - {company}"

                # Only include rows that have at least a first name
                valid_df = df.dropna(subset=['first name'])
                
                selected_lead_idx = st.selectbox(
                    "Select a Lead to generate an email for:",
                    options=valid_df.index,
                    format_func=lambda x: format_lead(valid_df.loc[x])
                )
                
                if selected_lead_idx is not None:
                    row = valid_df.loc[selected_lead_idx]
                    name_val = str(row.get('first name', ''))
                    role_val = str(row.get('title', ''))
                    
                    ind = str(row.get('industry', ''))
                    comp = str(row.get('company', ''))
                    company_type_val = f"{comp} ({ind})" if ind and ind != 'nan' else comp
                    
                    city = str(row.get('city', ''))
                    country = str(row.get('country', ''))
                    
                    # Clean up location formatting
                    loc_parts = [p for p in [city, country] if p and str(p).lower() not in ['nan', 'undefined']]
                    location_val = ", ".join(loc_parts)
                    
                    linked = str(row.get('linkedin url', ''))
                    notes_val = f"LinkedIn Profile: {linked}" if linked and linked != 'nan' else ""
            else:
                st.error("Dataset not found at the specified path.")
        except Exception as e:
             st.error(f"Error loading CSV: {str(e)}")
             
    st.divider()
    st.markdown("### �👤 Recipient Details")
    
    name = st.text_input("Recipient Name", value=name_val, placeholder="Ahmed")
    role = st.text_input("Role / Title", value=role_val, placeholder="CFO")
    company_type = st.text_input("Company Type", value=company_type_val, placeholder="Logistics company")
    location = st.text_input("Recipient Location", value=location_val, placeholder="Dubai")
    linkedin_notes = st.text_area(
        "LinkedIn / Context Notes",
        value=notes_val,
        placeholder="e.g. Recently posted about supply chain visibility challenges.",
        height=80,
    )

    st.divider()
    col_btn_1, col_btn_2 = st.columns(2)
    with col_btn_1:
        generate_btn = st.button("🚀 Generate Data", use_container_width=True)
    with col_btn_2:
        regenerate_btn = st.button("🔁 Regenerate", use_container_width=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "inputs" not in st.session_state:
    st.session_state.inputs = None

# ── Generation logic ───────────────────────────────────────────────────────────
if generate_btn or regenerate_btn:
    inputs = {
        "product": product, "audience": audience, "region": region, "persona": persona,
        "name": name, "role": role, "company_type": company_type,
        "location": location, "linkedin_notes": linkedin_notes,
    }

    is_valid, error = validate_inputs(inputs)
    if not api_key:
        st.error("⚠️ Please enter your Groq API key in the sidebar.")
    elif not is_valid:
        st.error(f"⚠️ {error}")
    else:
        try:
            client = get_client(api_key)

            with st.spinner(f"Initiating sequence with {MODEL_NAME}…"):
                progress_bar = st.progress(0, text="Starting API Connection...")

                progress_bar.progress(10, text=f"Mapping logic to {persona} Persona…")
                opener = personalise_opening(client, name, role, company_type, location, linkedin_notes, product, region, persona)

                progress_bar.progress(25, text="Drafting Persona-targeted email body…")
                email = generate_email(client, product, audience, region, name, role, company_type, location, opener, persona)

                progress_bar.progress(40, text="Generating targeted subject lines…")
                subjects = generate_subject_lines(client, product, audience, email, name, role, company_type, region, location, persona)
                best_sub = get_best_subject(subjects)

                progress_bar.progress(50, text="Simulating Subject Line A/B Test…")
                ab_test = simulate_ab_test(client, subjects)

                progress_bar.progress(60, text="Calculating Reply Probability & Scoring…")
                score_data = get_reply_score(client, email)

                progress_bar.progress(70, text="Analyzing structural efficacy…")
                why_works = get_why_this_works(client, email)

                progress_bar.progress(80, text="Iterating for maximum performance…")
                iteration_data = improve_email(client, email, role, region, name, company_type, location, persona)

                progress_bar.progress(85, text="Autonomously refining copy based on feedback…")
                improvements = score_data.get("improvements", [])
                auto_improved = auto_improve_using_feedback(client, email, improvements, region, persona)

                progress_bar.progress(95, text=f"Deep cultural adaptation for {region}…")
                regional_email = rewrite_for_region(client, email, name, role, company_type, region, location)

                progress_bar.progress(100, text="Done ✅")

            st.session_state.results = {
                "email": email, "opener": opener,
                "subjects": subjects, "best_subject": best_sub, 
                "ab_test_result": ab_test, 
                "score_data": score_data, "why_works": why_works,
                "iteration": iteration_data, "regional_email": regional_email,
                "persona": persona,
                "auto_improved_email": auto_improved
            }
            st.session_state.inputs = inputs
            st.success("All outputs generated successfully!")

        except Exception as e:
            st.error(f"**Execution Error:** {str(e)}")
            st.info("💡 Review your API key and verify internet connectivity/model readiness.")


# ── Results display ────────────────────────────────────────────────────────────
if st.session_state.results:
    r = st.session_state.results
    inp = st.session_state.inputs
    current_region = inp.get('region', 'Global')
    active_persona = r.get("persona", inp.get("persona", "Other"))

    tabs_labels = [
        "📧 Email", 
        "📩 Subject Lines", 
        "🧪 A/B Testing",
        "🌍 Region Version", 
        "🎯 Personalization", 
        "🔁 Iteration", 
        "🚀 Auto Improve",
        "📊 Score Dashboard", 
        "🧠 Why This Works", 
        "📤 Export"
    ]
    tabs = st.tabs(tabs_labels)

    # ── Tab 1: Email ───────────────────────────────────────────────
    with tabs[0]:
        st.info(f"**👤 Persona Applied:** {active_persona} — Messaging optimized for {active_persona} executive outcomes.")
        
        html_block = f"""
        <div style="background: #f9f9fb; border: 1px solid #e8e8ef; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <div style="font-weight: 600; color: #1a1a2e; margin-bottom: 1rem; border-bottom: 2px solid #e0e0f0; padding-bottom: 0.5rem;">PRIMARY 1. Generated Cold Email</div>
            <div style="background: white; border-left: 4px solid #302b63; padding: 1.25rem 1.5rem; border-radius: 0 8px 8px 0; font-size: 0.95rem; line-height: 1.7; color: #2d2d2d; white-space: pre-wrap;">{r.get("email", "")}</div>
            <div style="color: #999; font-size: 0.78rem; margin-top: 0.5rem; text-align: right;">📊 {word_count(r.get("email", ""))} words</div>
        </div>
        """
        st.markdown(html_block, unsafe_allow_html=True)

    # ── Tab 2: Subject Lines ───────────────────────────────────────────────────
    with tabs[1]:
        best = r.get("best_subject", {})
        if best:
            st.success(f"**🏆 Best Subject Line:** {best.get('subject', 'N/A')}")

        st.subheader("All Genereated Subjects")
        for i, s in enumerate(r.get("subjects", []), 1):
            with st.expander(f"{i}. {s.get('subject', 'Untitled')} [Score: {s.get('score', 0)}/10]"):
                st.write(s.get("reasoning", ""))

    # ── Tab 3: A/B Testing ─────────────────────────────────────────────────────
    with tabs[2]:
        ab = r.get("ab_test_result", {})
        if ab and ab.get("winner") and ab.get("winner") != "N/A":
            st.success(f"**Winner:** {ab.get('winner', 'N/A')}")
            st.markdown("### Why it wins")
            st.info(ab.get('reason', 'N/A'))
            st.markdown("### Comparison")
            st.write(ab.get('comparison', 'N/A'))
        else:
            st.warning("⚠️ A/B Test Simulation Failed (No conclusive structure generated from API).")

    # ── Tab 4: Regional Version ─────────────────────────────────────────────────────
    with tabs[3]:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.subheader("Base Version")
            st.info(r.get("email", ""))
        with col2:
            st.subheader(f"🌍 {current_region} Version")
            st.success(r.get("regional_email", ""))

    # ── Tab 5: Personalization ─────────────────────────────────────────────────────
    with tabs[4]:
        st.subheader("🎯 Personalised Opening Line")
        st.info(r.get("opener", ""))

    # ── Tab 6: Iteration ───────────────────────────────────────────────────────────
    with tabs[5]:
        it = r.get("iteration", {})
        st.markdown("### Diagnosis")
        st.warning(it.get("diagnosis", "N/A"))
        
        col3, col4 = st.columns(2, gap="large")
        with col3:
            st.subheader("🔴 Before (Original)")
            st.error(r.get("email", ""))

        with col4:
            st.subheader("🟢 After (Improved Email)")
            st.success(it.get("improved_email", "N/A"))
            st.markdown(f"**Why it improves replies:** {it.get('why_better', 'N/A')}")

    # ── Tab 7: Auto Improve ────────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown("### 🚀 Autonomous Optimization")
        st.markdown("Leverage structural scoring flaws to automatically rewrite the email natively solving its defects.")
        
        if st.button("🚀 Re-Run Optimization Using Latest Score", use_container_width=True):
            with st.spinner("Generating auto-improved email based on scorecard..."):
                client = get_client(api_key)
                imp_list = r.get("score_data", {}).get("improvements", [])
                auto_body = auto_improve_using_feedback(client, r.get("email"), imp_list, inp["region"], active_persona)
                st.session_state.results["auto_improved_email"] = auto_body
            st.rerun()

        if r.get("auto_improved_email"):
            st.success("### ✨ Auto Improved Email")
            st.info(r.get("auto_improved_email"))
        else:
             st.warning("Autonomous improvement iteration missing.")

    # ── Tab 8: Score Dashboard ─────────────────────────────────────────────────────
    with tabs[7]:
        eval_data = r.get("score_data", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Personalization", f"{eval_data.get('personalization', 0)}/10")
        c2.metric("Clarity", f"{eval_data.get('clarity', 0)}/10")
        c3.metric("CTA Strength", f"{eval_data.get('cta', 0)}/10")
        c4.metric("Reply Probability", f"{eval_data.get('reply_probability', 0)}/10")

        overall = int(eval_data.get("overall", 0))
        st.progress(overall * 10, text=f"Overall Email Quality Score: {overall}/10")
        
        ca, cb = st.columns(2)
        with ca:
            st.subheader("💪 Strengths")
            for strength in eval_data.get("strengths", []):
                st.markdown(f"✅ {strength}")
        with cb:
            st.subheader("⚠️ Improvements Needed")
            for imp in eval_data.get("improvements", []):
                st.markdown(f"🔧 {imp}")

    # ── Tab 9: Why This Works ──────────────────────────────────────────────────────
    with tabs[8]:
        st.subheader("🧠 Why This Strategy Converts")
        why = r.get("why_works", [])
        if why:
            for item in why:
                st.markdown(f"- {item}")
        else:
            st.markdown("Analysis unavailable.")

    # ── Tab 10: Export ──────────────────────────────────────────────────────────────
    with tabs[9]:
        st.markdown("### 📄 Professional Reporting")
        export_text = build_export_text(inp, r)
        st.download_button(
            label="📥 Download Full Report (.txt)", 
            data=export_text, 
            file_name="cold_email_report.txt", 
            mime="text/plain", 
            use_container_width=True
        )
        st.markdown("---")
        st.text(export_text)

# ── Empty state ────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color: #999;">
        <div style="font-size: 3rem;">⚡</div>
        <h3 style="color: #bbb; font-family: 'DM Serif Display', serif;">Awaiting Input</h3>
        <p>Fill in your campaign details in the sidebar to run the Elite B2B generation sequence.</p>
    </div>
    """, unsafe_allow_html=True)
