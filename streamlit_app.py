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

# --- 2. ASRS & AQ-10 ---
with tabs[1]:
    st.subheader("ASRS (ADHD)")
    asrs_q = [
        "1. Jak często masz problemy z wykończeniem końcowych szczegółów projektu, gdy jego główne części zostały już ukończone?",
        "2. Jak często masz trudności z uporządkowaniem rzeczy, gdy musisz wykonać zadanie wymagające organizacji?",
        "3. Jak często masz problemy z zapamiętywaniem spotkań lub terminów?",
        "4. Gdy masz zadanie wymagające dużego wysiłku umysłowego, jak często unikasz go lub opóźniasz jego rozpoczęcie?",
        "5. Jak często wiercisz się lub poruszasz dłońmi lub stopami, gdy musisz siedzieć przez dłuższy czas?",
        "6. Jak często czujesz się nadmiernie aktywny i zmuszony do robienia różnych rzeczy, jakbyś miał w sobie silnik?"
    ]
    asrs_res = [st.radio(q, list(asrs_opt.keys()), key=f"asrs_{i}") for i, q in enumerate(asrs_q)]
    
    st.divider()
    
    st.subheader("AQ-10 (Spektrum Autyzmu)")
    st.write("Zaznacz, jeśli poniższe stwierdzenie Cię dotyczy:")
    aq_q = [
        "1. Często zauważam ciche dźwięki, których inni nie dostrzegają.",
        "2. Zazwyczaj bardziej skupiam się na całym obrazie niż na jego szczegółach. (Zaznacz, jeśli NIE)",
        "3. Łatwo mi przychodzi robienie kilku rzeczy naraz. (Zaznacz, jeśli NIE)",
        "4. Jeśli następuje przerwa w moich planach, bardzo szybko potrafię do nich wrócić. (Zaznacz, jeśli NIE)",
        "5. Trudno mi 'czytać między wierszami', gdy z kimś rozmawiam.",
        "6. Wiem, jak stwierdzić, czy ktoś, kto mnie słucha, nudzi się. (Zaznacz, jeśli NIE)",
        "7. Kiedy czytam opowiadanie, trudno mi wyobrazić sobie, co czują bohaterowie.",
        "8. Lubię zbierać informacje o kategoriach rzeczy (np. typy samochodów, ptaków, pociągów).",
        "9. Łatwo mi przychodzi odgadnięcie, co ktoś myśli lub czuje, patrząc na jego twarz. (Zaznacz, jeśli NIE)",
        "10. Trudno mi zrozumieć intencje innych ludzi."
    ]
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

# --- 4. PDS-ICD-11 ---
with tabs[3]:
    st.subheader("PDS-ICD-11 (Zaburzenia Osobowości)")
    st.write("Wybierz jedno stwierdzenie, które najlepiej opisuje daną osobę w ciągu ostatnich dwóch lat.")
    
    pds_total = 0

    # PYTANIA 1-10 (Punktacja 2-1-0-1-2)
    pds_1_10_data = [
        ("1. Tożsamość", [
            "Często brak poczucia Ja lub tożsamości, słabe granice (2 pkt)",
            "Czasami dezorientacja co do tożsamości, naśladowanie innych (1 pkt)",
            "Stabilne poczucie Ja / tożsamości (0 pkt)",
            "Tożsamość zbyt sztywna/stała (np. tylko rola zawodowa) (1 pkt)",
            "Tożsamość skrajnie sztywna i niezmienna za wszelką cenę (2 pkt)"
        ]),
        ("2. Poczucie własnej wartości", [
            "Poczucie bezwartościowości przez większość czasu (2 pkt)",
            "Częste niskie poczucie własnej wartości, wpływ na relacje (1 pkt)",
            "Brak trudności z poczuciem własnej wartości (0 pkt)",
            "Częste poczucie bycia lepszym od innych (1 pkt)",
            "Stałe poczucie wyższości nad innymi (2 pkt)"
        ]),
        # ... (powtórz ten schemat dla pytań 3-10 zgodnie z moim poprzednim kodem) ...
    ]

    # Mapowanie punktacji dla pytań 1-10
    score_map_bipolar = {0: 2, 1: 1, 2: 0, 3: 1, 4: 2}

    # Przykład pętli dla 1-10
    for i, (title, opts) in enumerate(pds_1_10_data):
        choice = st.radio(title, opts, key=f"pds_new_{i}")
        pds_total += score_map_bipolar[opts.index(choice)]

    # PYTANIA 11-14 (Punktacja 0-1-2-3)
    pds_11_14_data = [
        ("11. Rzeczywistość pod wpływem stresu", ["Zazwyczaj trafna (0 pkt)", "Nieco zniekształcona (1 pkt)", "Znacznie zniekształcona (2 pkt)", "Częsta utrata kontaktu (3 pkt)"]),
        ("12. Krzywdzenie siebie", ["Nigdy (0 pkt)", "Rzadko (1 pkt)", "Czasami (2 pkt)", "Często (3 pkt)"]),
        ("13. Krzywdzenie innych", ["Nigdy (0 pkt)", "Rzadko (1 pkt)", "Czasami (2 pkt)", "Często (3 pkt)"]),
        ("14. Ogólne upośledzenie", ["Brak/małe (0 pkt)", "Łagodne (1 pkt)", "Umiarkowane (2 pkt)", "Ciężkie (3 pkt)"])
    ]

    for i, (title, opts) in enumerate(pds_11_14_data):
        choice = st.radio(title, opts, key=f"pds_v1114_{i}")
        pds_total += opts.index(choice)
# --- OBLICZENIA ---
s_phq = sum([opt_03[x] for x in phq_res])
s_gad = sum([opt_03[x] for x in gad_res])
s_asrs = sum([asrs_opt[x] for x in asrs_res])
s_aq = sum(aq_res)
s_pds = sum(pds_scores)

s_audit = 0
for i, ans in enumerate(audit_res):
    if i < 3: s_audit += aud_opt_freq.get(ans, aud_opt_amt.get(ans, 0))
    elif i < 8: s_audit += aud_opt_freq.get(ans, 0)
    else: s_audit += aud_opt_9_10.get(ans, 0)

# --- RAPORT ---
st.divider()
st.header("📊 Wyniki")
c1, c2 = st.columns(2)
with c1:
    st.write(f"**PHQ-9 (Depresja):** {s_phq}")
    st.write(f"**GAD-7 (Lęk):** {s_gad}")
    st.write(f"**ASRS (ADHD):** {s_asrs}")
with c2:
    st.write(f"**AUDIT (Alkohol):** {s_audit}")
    st.write(f"**AQ-10 (Autyzm):** {s_aq}")
    st.write(f"**PDS-ICD-11 (Osobowość):** {s_pds} / 32")

# --- WYSYŁKA ---
st.divider()
st.subheader("✉️ Wyślij raport na e-mail")
with st.form("final_mail"):
    p_id = st.text_input("ID Pacjenta")
    dest_mail = st.text_input("E-mail lekarza")
    
    # Dane SMTP - WPISZ SWOJE
    M_USER = "TWOJ_EMAIL@gmail.com"
    M_PASS = "TWOJE_HASLO_APLIKACJI"
    
    if st.form_submit_button("Wyślij"):
        if p_id and dest_mail:
            try:
                body = f"Wyniki pacjenta {p_id}:\n\nPHQ-9: {s_phq}\nGAD-7: {s_gad}\nASRS: {s_asrs}\nAUDIT: {s_audit}\nAQ-10: {s_aq}\nPDS-ICD-11: {s_pds}/32"
                msg = MIMEMultipart()
                msg['From'] = M_USER
                msg['To'] = dest_mail
                msg['Subject'] = f"Raport Diagnostyczny: {p_id}"
                msg.attach(MIMEText(body, 'plain'))
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(M_USER, M_PASS)
                    server.send_message(msg)
                st.success("Wysłano pomyślnie!")
            except Exception as e:
                st.error(f"Błąd wysyłki: {e}")
        else:
            st.warning("Uzupełnij pola ID i E-mail.")
