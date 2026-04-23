import streamlit as st
from anonymizer import anonymize

st.set_page_config(page_title="Log Anonymizer", layout="wide")
st.title("Log Anonymizer")
st.caption("Kör lokalt — ingen data lämnar din maskin.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Original logg")
    input_text = st.text_area(
        "Klistra in din logg här",
        height=400,
        placeholder="2024-01-15 INFO User 19850312-1234 logged in from 192.168.1.1...",
        label_visibility="collapsed",
    )

with col2:
    st.subheader("Anonymiserad logg")
    if input_text.strip():
        output_text, lexicon = anonymize(input_text)
        st.text_area(
            "Resultat",
            value=output_text,
            height=400,
            label_visibility="collapsed",
        )
        st.download_button(
            "Ladda ner anonymiserad logg",
            data=output_text,
            file_name="anonymized.log",
            mime="text/plain",
        )
    else:
        st.text_area("Resultat", value="", height=400, label_visibility="collapsed")

if input_text.strip():
    entries = lexicon.entries()
    if entries:
        st.divider()
        st.subheader(f"Lexikon — {len(entries)} ersättningar")
        cols = st.columns([1, 2, 2])
        cols[0].markdown("**Typ**")
        cols[1].markdown("**Original**")
        cols[2].markdown("**Ersatt med**")
        for entry in entries:
            c1, c2, c3 = st.columns([1, 2, 2])
            c1.write(entry["type"])
            c2.code(entry["original"])
            c3.code(entry["replacement"])
    else:
        st.info("Ingen känslig data hittades i texten.")
