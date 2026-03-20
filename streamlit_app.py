import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Poradnia - Diagnostyka", layout="wide")

st.title("🩺 Arkusz Badań Psychiatrycznych (ICD-11)")
st.info("Wypełnij wszystkie sekcje. Na dole strony możesz wysłać raport na e-mail.")

# --- SŁOWNIKI PUNKTACJI ---
opt_03 = {"Wcale (0)": 0, "Kilka dni (1)": 1, "Ponad połowa dni (2)": 2, "Prawie codziennie (3)": 3}
asrs_opt = {"Nigdy (0)": 0, "Rzadko (0)": 0, "Czasami (1)": 1, "Często (1)": 1, "Bardzo często (1)": 1}

# AUDIT - Opcje tekstowe
aud_opt_freq = {"Nigdy (0)": 0, "Raz w miesiącu lub rzadziej (1)": 1, "2-4 razy w miesiącu (2)": 2, "2-3 razy w tygodniu (3)": 3, "4 lub więcej razy w tygodniu (4)": 4}
aud_opt_amt = {"1-2 (0)": 0, "3-4 (1)": 1, "5-6 (2)": 2, "7-9 (3)": 3, "10+ (4)": 4}
aud_opt_9_10 = {"Nie (0)": 0, "Tak, ale nie w ostatnim roku (2)": 2, "Tak, w ostatnim roku (4)": 4}

tabs = st.tabs(["Nastrój (PHQ/GAD)", "Neuroatypowość", "Alkohol (AUDIT)", "Osobowość (PDS-ICD-11)"])

# --- 1. PHQ & GAD ---
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("PHQ-9 (Depresja)")
        phq_q = ["Małe zainteresowanie lub brak przyjemności", "Uczucie smutku, beznadziejności", "Problemy ze snem", "Zmęczenie lub brak energii", "Brak apetytu/przejadanie się", "Poczucie gorszej wartości", "Problemy z koncentracją", "Spowolnienie/pobudzenie ruchowe", "Myśli o skrzywdzeniu się"]
        phq_res = [st.radio(q, list(opt_03.keys()), key=f"phq_{i}") for i, q in enumerate(phq_q)]
    with col2:
        st.subheader("GAD-7 (Lęk)")
        gad_q = ["Zdenerwowanie, lęk, napięcie", "Brak kontroli nad martwieniem się", "Zbyt wiele zmartwień", "Trudność z odprężeniem się", "Niepokój ruchowy", "Łatwa irytacja", "Obawa przed czymś strasznym"]
        gad_res = [st.radio(q, list(opt_03.keys()), key=f"gad_{i}") for i, q in enumerate(gad_q)]

# --- 2. ASRS & AQ ---
with tabs[1]:
    st.subheader("ASRS (ADHD)")
    asrs_q = ["Problemy z dokończeniem detali", "Trudność z organizacją", "Zapominanie o spotkaniach", "Unikanie wysiłku umysłowego", "Wiercenie się", "Poczucie nadmiernego napędu"]
    asrs_res = [st.radio(q, list(asrs_opt.keys()), key=f"asrs_{i}") for i, q in enumerate(asrs_q)]
    st.divider()
    st.subheader("AQ-10 (Autyzm)")
    aq_q = ["Często zauważam ciche dźwięki", "Skupiam się na szczegółach (tracąc ogół)", "Trudno mi czytać intencje innych", "Fascynują mnie liczby/daty", "Trudność ze small-talkiem"]
    aq_res = [st.checkbox(q, key=f"aq_{i}") for i, q in enumerate(aq_q)]

# --- 3. AUDIT ---
with tabs[2]:
    st.subheader("AUDIT (Alkohol)")
    audit_res = []
    audit_res.append(st.selectbox("1. Jak często pije Pan/Pani alkohol?", list(aud_opt_freq.keys()), key="a1"))
    audit_res.append(st.selectbox("2. Ile porcji wypija Pan/Pani w typowym dniu picia?", list(aud_opt_amt.keys()), key="a2"))
    audit_res.append(st.selectbox("3. Jak często wypija Pan/Pani 6 lub więcej porcji naraz?", list(aud_opt_freq.keys()), key="a3"))
    aud_qs = ["4. Niezdolność do przerwania picia?", "5. Zaniedbanie obowiązków?", "6. Picie poranne?", "7. Wyrzuty sumienia?", "8. Luki w pamięci?"]
    for i, q in enumerate(aud_qs):
        audit_res.append(st.selectbox(q, list(aud_opt_freq.keys()), key=f"a{i+4}"))
    audit_res.append(st.selectbox("9. Uraz fizyczny spowodowany piciem?", list(aud_opt_9_10.keys()), key="a9"))
    audit_res.append(st.selectbox("10. Sugestie innych o ograniczeniu?", list(aud_opt_9_10.keys()), key="a10"))

# --- 4. PDS-ICD-11 (ZGOD
