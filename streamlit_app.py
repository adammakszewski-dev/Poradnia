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
itq_opt = {"Wcale (0)": 0, "Trochę (1)": 1, "Umiarkowanie (2)": 2, "Znacznie (3)": 3, "Bardzo (4)": 4}

aud_opt_freq = {"Nigdy (0)": 0, "Raz w miesiącu lub rzadziej (1)": 1, "2-4 razy w miesiącu (2)": 2, "2-3 razy w tygodniu (3)": 3, "4 lub więcej razy w tygodniu (4)": 4}
aud_opt_amt = {"1-2 (0)": 0, "3-4 (1)": 1, "5-6 (2)": 2, "7-9 (3)": 3, "10+ (4)": 4}
aud_opt_9_10 = {"Nie (0)": 0, "Tak, ale nie w ostatnim roku (2)": 2, "Tak, w ostatnim roku (4)": 4}

tabs = st.tabs(["Nastrój (PHQ/GAD)", "Neuroatypowość", "Alkohol (AUDIT)", "Trauma (ITQ / ICD-11)"])

# --- 1. PHQ & GAD ---
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("PHQ-9 (Depresja)")
        phq_q = [
            "Małe zainteresowanie lub brak przyjemności", "Uczucie smutku, beznadziejności", 
            "Problemy ze snem", "Zmęczenie lub brak energii", "Brak apetytu/przejadanie się", 
            "Poczucie gorszej wartości", "Problemy z koncentracją", 
            "Spowolnienie/pobudzenie ruchowe", "Myśli o skrzywdzeniu się"
        ]
        phq_res = [st.radio(q, list(opt_03.keys()), key=f"phq_{i}") for i, q in enumerate(phq_q)]
    
    with col2:
        st.subheader("GAD-7 (Lęk)")
        gad_q = [
            "Zdenerwowanie, lęk, napięcie", "Brak kontroli nad martwieniem się", 
            "Zbyt wiele zmartwień", "Trudność z odprężeniem się", "Niepokój ruchowy", 
            "Łatwa irytacja", "Obawa przed czymś strasznym"
        ]
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
    st.subheader("AUDIT")
    audit_res = []
    audit_res.append(st.selectbox("1. Jak często pije Pan/Pani napoje alkoholowe?", list(aud_opt_freq.keys()), key="a1"))
    audit_res.append(st.selectbox("2. Ile porcji alkoholu wypija Pan/Pani w dniu, w którym Pan/Pani pije?", list(aud_opt_amt.keys()), key="a2"))
    audit_res.append(st.selectbox("3. Jak często wypija Pan/Pani 6 lub więcej porcji podczas jednego dnia?", list(aud_opt_freq.keys()), key="a3"))
    for i in range(4, 9):
        q_label = [
            "4. Jak często w ostatnim roku nie mógł Pan/Pani przestać pić po rozpoczęciu?",
            "5. Jak często w ostatnim roku nie zrobił Pan/Pani czegoś oczekiwanego z powodu picia?",
            "6. Jak często w ostatnim roku potrzebował Pan/Pani alkoholu rano ('klin')?",
            "7. Jak często w ostatnim roku miał Pan/Pani wyrzuty sumienia po piciu?",
            "8. Jak często w ostatnim roku nie pamiętał Pan/Pani co działo się wieczorem?"
        ][i-4]
        audit_res.append(st.selectbox(q_label, list(aud_opt_freq.keys()), key=f"a{i}"))
    audit_res.append(st.selectbox("9. Czy Ty lub ktoś inny doznał urazu w wyniku Twojego picia?", list(aud_opt_9_10.keys()), key="a9"))
    audit_res.append(st.selectbox("10. Czy ktoś sugerował Ci ograniczenie picia?", list(aud_opt_9_10.keys()), key="a10"))

# --- 4. ITQ (ZAKTUALIZOWANE PYTANIA) ---
with tabs[3]:
    st.subheader("ITQ (Międzynarodowy Kwestionariusz Traumy)")
    st.write("W poniższej sekcji proszę odnieść się do najbardziej niepokojącego wydarzenia.")
    
    st.markdown("**Sekcja PTSD (Post-Traumatic Stress Disorder):**")
    itq_ptsd_q = [
        "P1. Czy miewa Pan/Pani niepokojące sny odtwarzające fragmenty przeżycia lub wyraźnie z nim powiązane?",
        "P2. Czy miewa Pan/Pani poczucie ponownego przeżywania tego wydarzenia (tzw. flashbacki)?",
        "P3. Czy unika Pan/Pani wewnętrznych przeżyć przypominających to wydarzenie (np. myśli, uczuć)?",
        "P4. Czy unika Pan/Pani zewnętrznych sytuacji (ludzi, miejsc, rozmów) przypominających wydarzenie?",
        "P5. Czy jest Pan/Pani bardzo czujny/czujna, ostrożny/ostrożna lub w stałej gotowości?",
        "P6. Czy czuje się Pan/Pani pobudzony/pobudzona i łatwo Pana/Panią przestraszyć?"
    ]
    itq_ptsd_res = [st.radio(q, list(itq_opt.keys()), key=f"itq_p_{i}") for i, q in enumerate(itq_ptsd_q)]

    st.markdown("**Wpływ objawów PTSD na życie:**")
    ptsd_func_q = [
        "P7. Czy powyższe objawy wpływały na Pana/Pani relacje lub życie towarzyskie?",
        "P8. Czy miały wpływ na Pana/Pani pracę lub zdolność do pracy?",
        "P9. Czy miały wpływ na inne ważne sfery życia (np. studia, rodzicielstwo)?"
    ]
    itq_ptsd_func = [st.radio(q, list(itq_opt.keys()), key=f"itq_pf_{i}") for i, q in enumerate(ptsd_func_q)]

    st.markdown("**Sekcja DSO (Zaburzenia samoorganizacji - Złożone PTSD):**")
    itq_dso_q = [
        "C1. Kiedy jestem zdenerwowany/zdenerwowana, dużo czasu zajmuje mi uspokojenie się.",
        "C2. Czuję się odrętwiały/odrętwiała emocjonalnie lub zablokowany/zablokowana.",
        "C3. Czuję się jakby nigdy nic mi się nie udawało.",
        "C4. Czuję się bezwartościowy/bezwartościowa.",
        "C5. Czuję się zdystansowany/zdystansowana lub odcięty/odcięta od ludzi.",
        "C6. Trudno jest mi być blisko emocjonalnie z ludźmi."
    ]
    itq_dso_res = [st.radio(q, list(itq_opt.keys()), key=f"itq_d_{i}") for i, q in enumerate(itq_dso_q)]

    st.markdown("**Wpływ objawów DSO na życie:**")
    dso_func_q = [
        "C7. Czy te odczucia wpływały na Pana/Pani relacje lub życie towarzyskie?",
        "C8. Czy miały wpływ na Pana/Pani pracę lub zdolność do pracy?",
        "C9. Czy miały wpływ na inne ważne sfery życia (np. studia, rodzicielstwo)?"
    ]
    itq_dso_func = [st.radio(q, list(itq_opt.keys()), key=f"itq_df_{i}") for i, q in enumerate(dso_func_q)]

# --- OBLICZENIA ---
s_phq = sum([opt_03[x] for x in phq_res])
s_gad = sum([opt_03[x] for x in gad_res])
s_asrs = sum([asrs_opt[x] for x in asrs_res])
s_aq = sum(aq_res)
s_itq_ptsd = sum([itq_opt[x] for x in itq_ptsd_res])
s_itq_dso = sum([itq_opt[x] for x in itq_dso_res])
s_audit = 0
for i, ans in enumerate(audit_res):
    if i < 3: s_audit += aud_opt_freq.get(ans, aud_opt_amt.get(ans, 0))
    elif i < 8: s_audit += aud_opt_freq.get(ans, 0)
    else: s_audit += aud_opt_9_10.get(ans, 0)

# --- RAPORT ---
st.divider()
st.header("📊 Wyniki zbiorcze")
col_res1, col_res2 = st.columns(2)
with col_res1:
    st.write(f"**PHQ-9:** {s_phq} | **GAD-7:** {s_gad}")
    st.write(f"**ASRS:** {s_asrs} | **AQ-10:** {s_aq}")
with col_res2:
    st.write(f"**AUDIT:** {s_audit}")
    st.write(f"**ITQ PTSD:** {s_itq_ptsd} | **ITQ DSO:** {s_itq_dso}")

# --- FORMULARZ E-MAIL ---
st.divider()
st.subheader("✉️ Wyślij raport")
with st.form("email_form"):
    pacjent = st.text_input("ID Pacjenta")
    email_do = st.text_input("Adres e-mail odbiorcy")
    
    # TUTAJ WPISZ SWOJE DANE
    M_USER = "TWOJ_EMAIL@gmail.com"
    M_PASS = "TWOJE_HASLO_APLIKACJI"
    
    wyslij = st.form_submit_button("Wyślij")
    if wyslij and pacjent and email_do:
        try:
            body = f"Wyniki dla: {pacjent}\n\nPHQ-9: {s_phq}\nGAD-7: {s_gad}\nASRS: {s_asrs}\nAQ-10: {s_aq}\nAUDIT: {s_audit}\nITQ PTSD: {s_itq_ptsd}\nITQ DSO: {s_itq_dso}"
            msg = MIMEMultipart(); msg['From'] = M_USER; msg['To
