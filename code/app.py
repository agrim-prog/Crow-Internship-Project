# Streamlit interface. Calls the same call_and_parse_pipeline function from
# Week 3 - this file doesn't reimplement any extraction logic, it just
# gives it a face.

import os
import sys
import json

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))
from call_and_parse import call_and_parse_pipeline, LABELS

st.set_page_config(page_title="Crow Lease Abstractor", page_icon="\U0001F4C4")

st.title("Crow Lease Abstractor")
st.caption("Paste or upload a commercial lease and get its key terms back as a clean summary.")

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.warning("ANTHROPIC_API_KEY is not set. Set it in your terminal before running this app.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
sample_files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".txt")) if os.path.isdir(DATA_DIR) else []

col_input, col_result = st.columns(2)

with col_input:
    st.subheader("Document")

    choice = st.selectbox("Try a sample lease, or paste your own below:",
                           ["Paste my own"] + sample_files)

    if choice == "Paste my own":
        lease_text = st.text_area("Lease text", height=400)
    else:
        lease_text = open(os.path.join(DATA_DIR, choice)).read()
        st.text_area("Lease text", value=lease_text, height=400, disabled=True)

    run = st.button("Abstract this lease", type="primary", use_container_width=True)

with col_result:
    st.subheader("Result")

    if run:
        if not lease_text.strip():
            st.warning("Paste or select a lease first.")
        else:
            with st.spinner("Reading the lease..."):
                result, problems = call_and_parse_pipeline(lease_text)

            if result is None:
                st.error("Couldn't parse a result from this document. " + "; ".join(problems))
            else:
                flags = result.get("review_flags") or {}

                for key, label in LABELS.items():
                    value = result.get(key)
                    flag_name = f"{key}_unclear"
                    is_flagged = flags.get(flag_name, False)

                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.markdown(f"**{label}**")
                    with c2:
                        if value is None:
                            st.markdown(":orange[Not found in document]")
                        elif key == "monthly_rent":
                            marker = " :red[\u26a0 needs review]" if is_flagged else ""
                            st.markdown(f"${value:,.2f}{marker}")
                        else:
                            marker = " :red[\u26a0 needs review]" if is_flagged else ""
                            st.markdown(f"{value}{marker}")

                provisions = result.get("key_provisions") or []
                if provisions:
                    st.markdown("**Key provisions**")
                    for item in provisions:
                        st.markdown(f"- {item}")

                notes = result.get("uncertainty_notes")
                if notes:
                    st.info(f"Notes: {notes}")

                if problems:
                    st.warning("Validation issues: " + "; ".join(problems))

                st.download_button(
                    "Download as JSON",
                    data=json.dumps(result, indent=2),
                    file_name="lease_abstract.json",
                    mime="application/json",
                )

                with st.expander("Raw JSON"):
                    st.json(result)
    else:
        st.caption("Run a lease to see the result here.")
