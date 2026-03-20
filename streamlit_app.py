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

# --- 2. ASRS & AQ-10 ---
with tabs[1]:
    st.subheader("ASRS (ADHD)")
    asrs_q = ["Problemy z wykończeniem szczegółów?", "Trudności z organizacją?", "Problemy z pamiętaniem o terminach?", "Unikanie wysiłku umysłowego?", "Wiercenie się?", "Nadmierna aktywność / silnik?"]
    asrs_res = [st.radio(q, list(asrs_opt.keys()), key=f"asrs_{i}") for i, q in enumerate(asrs_q)]
    
    st.divider()
    st.subheader("AQ-10 (Autyzm)")
    aq_q = [
        "1. Często zauważam ciche dźwięki, których inni nie dostrzegają.",
        "2. Bardziej skupiam się na całym obrazie niż na szczegółach. (Zaznacz, jeśli NIE)",
        "3. Łatwo mi robić kilka rzeczy naraz. (Zaznacz, jeśli NIE)",
        "4. Szybko wracam do planów po przerwie. (Zaznacz, jeśli NIE)",
        "5. Trudno mi 'czytać między wierszami'.",
        "6. Wiem, czy słuchacz się nudzi. (Zaznacz, jeśli NIE)",
        "7. Trudno mi wyobrazić sobie uczucia bohaterów.",
        "8. Lubię zbierać informacje o kategoriach rzeczy.",
        "9. Łatwo odgaduję myśli z twarzy. (Zaznacz, jeśli NIE)",
        "10. Trudno mi zrozumieć intencje innych."
    ]
    aq_res = [st.checkbox(q, key=f"aq_{i}") for i, q in enumerate(aq_q)]

# --- 3. AUDIT ---
with tabs[2]:
    st.subheader("AUDIT (Alkohol)")
    audit_res = []
    audit_res.append(st.selectbox("1. Jak często pijesz?", list(aud_opt_freq.keys()), key="a1"))
    audit_res.append(st.selectbox("2. Ile porcji w dniu picia?", list(aud_opt_amt.keys()), key="a2"))
    audit_res.append(st.selectbox("3. Jak często 6+ porcji naraz?", list(aud_opt_freq.keys()), key="a3"))
    aud_qs = ["4. Brak kontroli?", "5. Zaniedbania?", "6. Picie rano?", "7. Wyrzuty sumienia?", "8. Luki w pamięci?"]
    for i, q in enumerate(aud_qs):
        audit_res.append(st.selectbox(q, list(aud_opt_freq.keys()), key=f"a{i+4}"))
    audit_res.append(st.selectbox("9. Uraz przez picie?", list(aud_opt_9_10.keys()), key="a9"))
    audit_res.append(st.selectbox("10. Sugestie ograniczenia?", list(aud_opt_9_10.keys()), key="a10"))

# --- 4. PDS-ICD-11 ---
with tabs[3]:
    st.subheader("PDS-ICD-11 (Osobowość)")
    pds_points = []
    score_map_21012 = {0: 2, 1: 1, 2: 0, 3: 1, 4: 2}
    
    pds_data_1_10 = [
        ("1. Tożsamość", ["Brak poczucia Ja / słabe granice", "Dezorientacja / naśladowanie", "Stabilne poczucie Ja", "Tożsamość zbyt sztywna", "Tożsamość skrajnie niezmienna"]),
        ("2. Poczucie wartości", ["Bezwartościowość", "Niskie poczucie wartości", "Brak trudności", "Poczucie bycia lepszym", "Poczucie wyższości"]),
        ("3. Postrzeganie siebie", ["Brak mocnych stron", "Niewiele mocnych stron", "Dobre wyczucie", "Niewiele ograniczeń", "Brak ograniczeń"]),
        ("4. Cele", ["Brak realizacji celów", "Trudności z celami", "Realistyczne cele", "Nadmierne parcie", "Skrajny upór w celach"]),
        ("5. Relacje", ["Izolacja / unikanie", "Dyskomfort z innymi", "Równowaga", "Lęk przed samotnością", "Przerażenie samotnością"]),
        ("6. Perspektywa", ["Brak rozumienia innych", "Często ignoruje innych", "Rozumie innych", "Nadmierna analiza", "Skrajna analiza innych"]),
        ("7. Wzajemność", ["Samolubny/Manipulacyjny", "Dominujący", "Wzajemność", "Brak dbania o siebie", "Bycie ofiarą/Uległość"]),
        ("8. Konflikty", ["Szukanie kłótni", "Częste spory", "Współpraca w sporze", "Unikanie sporów", "Unikanie za wszelką cenę"]),
        ("9. Emocje", ["Brak regulacji", "Trudna regulacja", "Dobra regulacja", "Tłumienie", "Odcięcie emocjonalne"]),
        ("10. Zachowanie", ["Impulsywność", "Działanie pod wpływem chwili", "Kontrolowana spontaniczność", "Nadmierna kontrola", "Skrajne zahamowanie"])
    ]
    for i, (title, opts) in enumerate(pds_data_1_10):
        choice = st.radio(title, opts, key=f"pds_q_{i}")
        pds_points.append(score_map_21012[opts.index(choice)])

    st.markdown("**Dodatkowe (0-3 pkt):**")
    pds_data_11_14 = [
        ("11. Rzeczywistość w stresie", ["Trafna", "Nieco zniekształcona", "Znacznie zniekształcona", "Utrata kontaktu"]),
        ("12. Krzywdzenie siebie", ["Nigdy", "Rzadko", "Czasami", "Często"]),
        ("13. Krzywdzenie innych", ["Nigdy", "Rzadko", "Czasami", "Często"]),
        ("14. Upośledzenie życia", ["Brak", "Łagodne", "Umiarkowane", "Ciężkie"])
    ]
    for i, (title, opts) in enumerate(pds_data_11_14):
        choice = st.radio(title, opts, key=f"pds_v_{i}")
        pds_points.append(opts.index(choice))

# --- OBLICZENIA ---
s_phq = sum([opt_03[x] for x in phq_res])
s_gad = sum([opt_03[x] for x in gad_res])
s_asrs = sum([asrs_opt[x] for x in asrs_res])
s_aq = sum(aq_res)
s_pds = sum(pds_points)
s_audit = 0
for i, ans in enumerate(audit_res):
    if i < 3: s_audit += aud_opt_freq.get(ans, aud_opt_amt.get(ans, 0))
    elif i < 8: s_audit += aud_opt_freq.get(ans, 0)
    else: s_audit += aud_opt_9_10.get(ans, 0)

# --- RAPORT I WYSYŁKA ---
st.divider()
st.header("📊 Wyniki")
c1, c2 = st.columns(2)
with c1:
    st.write(f"**PHQ-9:** {s_phq} | **GAD-7:** {s_gad} | **ASRS:** {s_asrs}")
with c2:
    st.write(f"**AUDIT:** {s_audit} | **AQ-10:** {s_aq} | **PDS-ICD-11:** {s_pds}/32")

st.subheader("✉️ Wyślij raport")
with st.form("mail_form"):
    p_id = st.text_input("ID Pacjenta")
    email_target = st.text_input("E-mail odbiorcy")
    M_USER = "TWOJ_EMAIL@gmail.com"
    M_PASS = "TWOJE_HASLO_APLIKACJI"
    
    if st.form_submit_button("Wyślij"):
        if p_id and email_target:
            try:
                # BEZPIECZNY ZAPIS TREŚCI MAILA
                body_content = f"""Raport dla pacjenta: {p_id}

WYNIKI SKAL:
- PHQ-9 (Depresja): {s_phq}
- GAD-7 (Lęk): {s_gad}
- ASRS (ADHD): {s_asrs}
- AQ-10 (Autyzm): {s_aq}
- AUDIT (Alkohol): {s_audit}
- PDS-ICD-11 (Osobowość): {s_pds}/32
"""
                msg = MIMEMultipart()
                msg['From'] = M_USER
                msg['To'] = email_target
                msg['Subject'] = f"Raport: {p_id}"
                msg.attach(MIMEText(body_content, 'plain'))
                
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(M_USER, M_PASS)
                    server.send_message(msg)
                st.success("Raport został wysłany!")
            except Exception as e:
                st.error(f"Błąd wysyłki: {e}")
