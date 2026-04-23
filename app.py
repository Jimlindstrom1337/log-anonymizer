import streamlit as st
from anonymizer import anonymize, deanonymize, Lexicon

st.set_page_config(page_title="Log Anonymizer", layout="wide")
st.title("Log Anonymizer")
st.caption("Kör lokalt — ingen data lämnar din maskin.")

if "last_input" not in st.session_state:
    st.session_state.last_input = ""
    st.session_state.anon_output = ""
    st.session_state.lexicon = Lexicon()

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Original logg")
    input_text = st.text_area(
        "original",
        height=350,
        placeholder="2024-01-15 INFO User 19850312-1234 logged in from 192.168.1.1...",
        label_visibility="collapsed",
    )

if input_text.strip() != st.session_state.last_input:
    if input_text.strip():
        lexicon = Lexicon()
        out, lexicon = anonymize(input_text, lexicon)
        st.session_state.last_input = input_text.strip()
        st.session_state.anon_output = out
        st.session_state.lexicon = lexicon
    else:
        st.session_state.last_input = ""
        st.session_state.anon_output = ""
        st.session_state.lexicon = Lexicon()

with col2:
    st.subheader("2. Anonymiserad logg — skicka till Claude")
    st.text_area("anon", value=st.session_state.anon_output, height=350, label_visibility="collapsed")
    if st.session_state.anon_output:
        st.download_button(
            "Ladda ner anonymiserad logg",
            data=st.session_state.anon_output,
            file_name="anonymized.log",
            mime="text/plain",
        )

st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("3. Klistra in Claudes svar")
    claude_input = st.text_area(
        "claude",
        height=300,
        placeholder="Klistra in Claudes svar här...",
        label_visibility="collapsed",
    )

with col4:
    st.subheader("4. Svar med riktiga värden")
    entries = st.session_state.lexicon.entries()
    if claude_input.strip() and entries:
        restored = deanonymize(claude_input, st.session_state.lexicon)
        st.text_area("restored", value=restored, height=300, label_visibility="collapsed")
    else:
        st.text_area("restored", value="", height=300, label_visibility="collapsed")

if entries := st.session_state.lexicon.entries():
    TYPE_LABELS = {
        "phone": "Telefon",
        "email": "E-post",
        "personnummer": "Personnummer",
        "ip_address": "IP-adress",
        "ipv6": "IPv6",
    }
    st.divider()
    st.subheader(f"Lathund — {len(entries)} värden anonymiserade")
    cols = st.columns([1, 2, 2])
    cols[0].markdown("**Typ**")
    cols[1].markdown("**Original**")
    cols[2].markdown("**Anonymiserat (till Claude)**")
    for entry in entries:
        c1, c2, c3 = st.columns([1, 2, 2])
        c1.write(TYPE_LABELS.get(entry["type"], entry["type"]))
        c2.code(entry["original"])
        c3.code(entry["replacement"])
