# ========================
# 2. app.py ✅ (FINAL VERSION)
# ========================

import streamlit as st
import pandas as pd
import json
import io
from resume_parser import parse_resume, score_resume_against_jd

st.set_page_config(page_title="Resume Parser App", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        border: none;
    }
    .stDownloadButton>button {
        background-color: #059669;
        color: white;
        border-radius: 10px;
        padding: 0.5em 1.1em;
        border: none;
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        border-radius: 8px;
        border: 1px solid #d1d5db;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 AI Resume Parser")
job_description = st.text_area("📌 Paste Job Description (Optional)", height=200)
uploaded_files = st.file_uploader("📤 Upload Resumes", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.markdown("---")
        with st.spinner(f"Parsing `{uploaded_file.name}`..."):
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            parsed = parse_resume(temp_path)
            parsed["Filename"] = uploaded_file.name

            if job_description.strip():
                score, feedback = score_resume_against_jd(parsed.get("Skills", []), job_description)
                parsed["JD Score"] = feedback

                # Role alignment from JD
                target_role = None
                for role, score in parsed["Role Comparison"]:
                    if role.lower() in job_description.lower():
                        target_role = role
                        break

                if target_role:
                    matched_score = dict(parsed["Role Comparison"]).get(target_role, 0)
                    predicted = parsed["Predicted Role"]
                    parsed["Role Match Check"] = {
                        "Desired Role": target_role,
                        "Predicted Role": predicted,
                        "Match Score": matched_score,
                        "Is Match": target_role == predicted
                    }

            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("👤 Summary")
                st.markdown(f"**Name:** {parsed['Name']}")
                st.markdown(f"**Role:** {parsed['Predicted Role']}")
                st.markdown(f"**Phone:** {parsed['Phone']}")
                st.markdown(f"**Email:** {parsed['Email']}")
                st.markdown(f"**LinkedIn:** {parsed['LinkedIn']}")
                st.markdown(f"**GitHub:** {parsed['GitHub']}")

            with col2:
                st.subheader("📊 Role Compatibility")
                df_roles = pd.DataFrame(parsed["Role Comparison"], columns=["Role", "Score"])
                st.bar_chart(df_roles.set_index("Role"))

            if "Role Match Check" in parsed:
                st.subheader("🎯 Desired Role vs Resume Fit")
                match_data = parsed["Role Match Check"]
                if match_data["Is Match"]:
                    st.success(f"✅ Resume matches the desired role: **{match_data['Desired Role']}**")
                else:
                    st.warning(f"⚠️ Desired role is **{match_data['Desired Role']}**, but resume better fits **{match_data['Predicted Role']}**")
                    st.markdown(f"📉 **Match Score for '{match_data['Desired Role']}':** `{match_data['Match Score']}`")

            st.subheader("🧠 Extracted Skills")
            st.success(", ".join(parsed["Skills"]))

            st.subheader("🎓 Education")
            for edu in parsed["Education"]:
                st.markdown(f"- {edu}")

            st.subheader("🏆 Achievements")
            for ach in parsed["Achievements"]:
                st.markdown(f"- {ach}")

            st.subheader("📁 Projects")
            for proj in parsed["Projects"]:
                st.markdown(f"- {proj}")

            if job_description.strip():
                st.subheader("📌 JD Match Summary")
                st.info(parsed["JD Score"]["JD Summary"])

            with st.expander("🧾 Full Parsed JSON"):
                st.json(parsed)

            # After parsing each resume
            json_str = json.dumps(parsed, indent=4)
            st.download_button(
                label="📥 Download Full Parsed Data (JSON)",
                data=json_str,
                file_name=f"{parsed['Name'].replace(' ', '_')}_parsed.json",
                mime="application/json"
            )

            # Pie chart for Top 3 Roles
            st.subheader("📈 Top Role Fit Analysis")
            top_roles = parsed["Role Comparison"][:3]
            pie_df = pd.DataFrame(top_roles, columns=["Role", "Score"])
            st.plotly_chart({
                "data": [
                    {
                        "values": pie_df["Score"],
                        "labels": pie_df["Role"],
                        "type": "pie"
                    }
                ],
                "layout": {"title": "Top 3 Role Fit"}
            }, use_container_width=True)

            st.markdown("---")