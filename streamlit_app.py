import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Poradnia - Diagnostyka", layout="wide")

st.title("🩺 Arkusz Badań Psychiatrycznych (ICD-11)")
st.info("Wypełnij wszystkie sekcje. Na dole strony możesz wysłać raport na e-mail.")

# --- SŁOWNIKI PUNKTACJI (Ukryte przed użytkownikiem) ---
opt_03 = {"Wcale": 0, "Kilka dni": 1, "Ponad połowa dni": 2, "Prawie codziennie": 3}
asrs_opt = {"Nigdy": 0, "Rzadko": 0, "Czasami": 1, "Często": 1, "Bardzo często": 1}

aud_opt_freq = {"Nigdy": 0, "Raz w miesiącu lub rzadziej": 1, "2-4 razy w miesiącu": 2, "2-3 razy w tygodniu": 3, "4 lub więcej razy w tygodniu": 4}
aud_opt_amt = {"1-2": 0, "3-4": 1, "5-6": 2, "7-9": 3, "10 i więcej": 4}
aud_opt_9_10 = {"Nie": 0, "Tak, ale nie w ostatnim roku": 2, "Tak, w ostatnim roku": 4}

aq_opts = ["Zdecydowanie się zgadzam", "Raczej się zgadzam", "Raczej się nie zgadzam", "Zdecydowanie się nie zgadzam"]

# --- ZAKŁADKI ---
tabs = st.tabs(["Nastrój (PHQ/GAD)", "Neuroatypowość", "Alkohol (AUDIT)", "Badanie Struktury Osobowości"])

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

# --- 2. ASRS & AQ-10 ---
with tabs[1]:
    st.subheader("ASRS (ADHD)")
    asrs_q = [
        "Jak często masz problemy z wykończeniem końcowych szczegółów projektu, gdy jego główne części zostały już ukończone?", 
        "Jak często masz trudności z uporządkowaniem rzeczy, gdy musisz wykonać zadanie wymagające organizacji?", 
        "Jak często masz problemy z zapamiętywaniem spotkań lub terminów?", 
        "Gdy masz zadanie wymagające dużego wysiłku umysłowego, jak często unikasz go lub opóźniasz jego rozpoczęcie?", 
        "Jak często wiercisz się lub poruszasz dłońmi lub stopami, gdy musisz siedzieć przez dłuższy czas?", 
        "Jak często czujesz się nadmiernie aktywny i zmuszony do robienia różnych rzeczy, jakbyś miał w sobie silnik?"
    ]
    asrs_res = [st.radio(q, list(asrs_opt.keys()), key=f"asrs_{i}") for i, q in enumerate(asrs_q)]
    
    st.divider()
    st.subheader("AQ-10 (Spektrum Autyzmu)")
    aq_q = [
        "1. Często zauważam ciche dźwięki, których inni nie dostrzegają.",
        "2. Zazwyczaj bardziej skupiam się na całym obrazie niż na jego szczegółach.",
        "3. Łatwo mi przychodzi robienie kilku rzeczy naraz.",
        "4. Jeśli następuje przerwa w moich planach, bardzo szybko potrafię do nich wrócić.",
        "5. Trudno mi 'czytać między wierszami', gdy z kimś rozmawiam.",
        "6. Wiem, jak stwierdzić, czy ktoś, kto mnie słucha, nudzi się.",
        "7. Kiedy czytam opowiadanie, trudno mi wyobrazić sobie, co czują bohaterowie.",
        "8. Lubię zbierać informacje o kategoriach rzeczy (np. typy samochodów, ptaków, pociągów).",
        "9. Łatwo mi przychodzi odgadnięcie, co ktoś myśli lub czuje, patrząc na jego twarz.",
        "10. Trudno mi zrozumieć intencje innych ludzi."
    ]
    aq_res = [st.radio(q, aq_opts, key=f"aq_{i}") for i, q in enumerate(aq_q)]

# --- 3. AUDIT ---
with tabs[2]:
    st.subheader("AUDIT")
    audit_res = []
    audit_res.append(st.selectbox("1. Jak często pije Pan/Pani napoje alkoholowe?", list(aud_opt_freq.keys()), key="a1"))
    audit_res.append(st.selectbox("2. Ile porcji alkoholu wypija Pan/Pani w dniu, w którym Pan/Pani pije?", list(aud_opt_amt.keys()), key="a2"))
    audit_res.append(st.selectbox("3. Jak często wypija Pan/Pani 6 lub więcej porcji podczas jednego dnia?", list(aud_opt_freq.keys()), key="a3"))
    
    aud_qs = [
        "4. Jak często w ostatnim roku nie mógł Pan/Pani przestać pić po rozpoczęciu?",
        "5. Jak często w ostatnim roku nie zrobił Pan/Pani czegoś oczekiwanego z powodu picia?",
        "6. Jak często w ostatnim roku potrzebował Pan/Pani alkoholu rano ('klin')?",
        "7. Jak często w ostatnim roku miał Pan/Pani wyrzuty sumienia po piciu?",
        "8. Jak często w ostatnim roku nie pamiętał Pan/Pani co działo się wieczorem?"
    ]
    for i, q in enumerate(aud_qs):
        audit_res.append(st.selectbox(q, list(aud_opt_freq.keys()), key=f"a{i+4}"))
        
    audit_res.append(st.selectbox("9. Czy Ty lub ktoś inny doznał urazu w wyniku Twojego picia?", list(aud_opt_9_10.keys()), key="a9"))
    audit_res.append(st.selectbox("10. Czy ktoś sugerował Ci ograniczenie picia?", list(aud_opt_9_10.keys()), key="a10"))

# --- 4. BADANIE STRUKTURY OSOBOWOŚCI (PDS-ICD-11) ---
with tabs[3]:
    st.subheader("Badanie Struktury Osobowości (PDS-ICD-11)")
    st.write("Wybierz jedno stwierdzenie dla każdego obszaru, które najlepiej opisuje funkcjonowanie w ciągu ostatnich dwóch lat.")
    
    pds_points = []
    
    # Mapowanie punktacji 2-1-0-1-2 dla pytań 1-10
    score_map_21012 = {0: 2, 1: 1, 2: 0, 3: 1, 4: 2}
    
    pds_data_1_10 = [
        ("1. Tożsamość", ["Często brak poczucia Ja lub tożsamości, słabe granice", "Czasami dezorientacja co do tożsamości, naśladowanie innych", "Stabilne poczucie Ja / tożsamości", "Tożsamość zbyt sztywna/stała", "Tożsamość skrajnie sztywna i niezmienna za wszelką cenę"]),
        ("2. Poczucie własnej wartości", ["Poczucie bezwartościowości przez większość czasu", "Częste niskie poczucie własnej wartości", "Brak trudności z poczuciem własnej wartości", "Częste poczucie bycia lepszym od innych", "Stałe poczucie wyższości nad innymi"]),
        ("3. Postrzeganie siebie", ["Brak jakichkolwiek mocnych stron", "Niewiele mocnych stron", "Dobre poczucie swoich stron mocnych i słabych", "Niewiele ograniczeń/słabości", "Brak jakichkolwiek słabości lub ograniczeń"]),
        ("4. Cele", ["Rzadko zdolny do stawiania realistycznych celów", "Czasami trudno stawiać lub realizować cele", "Brak problemów ze stawianiem celów", "Nadmierne nastawienie na cel", "Skrajnie uparty w dążeniu do celu"]),
        ("5. Relacje (Zainteresowanie)", ["Silne unikanie ludzi / izolacja", "Czasami unika ludzi z powodu dyskomfortu", "Odpowiednia równowaga", "Cierpi, gdy jest sam", "Rozpacz/przerażenie przy braku innych"]),
        ("6. Przyjmowanie perspektywy", ["Nigdy nie rozumie myśli lub uczuć innych", "Często nie bierze pod uwagę innych", "Łatwo rozumie punkt widzenia innych", "Zbyt intensywnie analizuje myśli innych", "Skrajna, bolesna analiza intencji innych"]),
        ("7. Wzajemność", ["Zawsze samolubny lub manipulacyjny", "Czasami zbyt samolubny / dominujący", "Relacje oparte na wzajemności", "Nie umie dbać o własne potrzeby", "Skrajna uległość / bycie ofiarą"]),
        ("8. Konflikty", ["Szuka kłótni / brak trwałych relacji", "Częste konflikty w relacjach", "Zdolny do współpracy w sporze", "Unika sporów kosztem swoich potrzeb", "Unika sporów za wszelką cenę"]),
        ("9. Emocje", ["Częsty brak regulacji / wybuchy", "Czasami trudności z regulacją", "Odpowiednia regulacja i ekspresja", "Tłumienie emocji (aleksytymia)", "Prawie całkowite odcięcie od emocji"]),
        ("10. Zachowanie", ["Skrajna impulsywność", "Czasami działa pod wpływem impulsu", "Spontaniczny, ale pod kontrolą", "Nadmierna kontrola zachowania", "Skrajne zahamowanie / brak życia"])
    ]
    for i, (title, opts) in enumerate(pds_data_1_10):
        choice = st.radio(title, opts, key=f"pds_q_{i}")
        pds_points.append(score_map_21012[opts.index(choice)])

    st.markdown("**Dodatkowe obszary funkcjonowania:**")
    pds_data_11_14 = [
        ("11. Rzeczywistość pod wpływem stresu", ["Zazwyczaj trafna", "Nieco zniekształcona", "Znacznie zniekształcona", "Częsta utrata kontaktu"]),
        ("12. Krzywdzenie siebie", ["Nigdy", "Rzadko", "Czasami", "Często"]),
        ("13. Krzywdzenie innych", ["Nigdy", "Rzadko", "Czasami", "Często"]),
        ("14. Ogólne upośledzenie", ["Brak lub małe", "Łagodne", "Umiarkowane", "Ciężkie"])
    ]
    for i, (title, opts) in enumerate(pds_data_11_14):
        choice = st.radio(title, opts, key=f"pds_v_{i}")
        pds_points.append(opts.index(choice))

# --- OBLICZENIA (W tle) ---
s_phq = sum([opt_03[x] for x in phq_res])
s_gad = sum([opt_03[x] for x in gad_res])
s_asrs = sum([asrs_opt[x] for x in asrs_res])

# Obliczanie AQ-10 z ukrytym kluczem odwróconym
s_aq = 0
for i, ans in enumerate(aq_res):
    ans_idx = aq_opts.index(ans)
    if i in [0, 4, 6, 7, 9]: # Punkty za "Zgadzam się"
        if ans_idx in [0, 1]: s_aq += 1
    else: # Punkty za "Nie zgadzam się" (Pytania: 2, 3, 4, 6, 9)
        if ans_idx in [2, 3]: s_aq += 1

s_pds = sum(pds_points)

s_audit = 0
for i, ans in enumerate(audit_res):
    if i < 3: s_audit += aud_opt_freq.get(ans, aud_opt_amt.get(ans, 0))
    elif i < 8: s_audit += aud_opt_freq.get(ans, 0)
    else: s_audit += aud_opt_9_10.get(ans, 0)

# --- RAPORT NA EKRANIE ---
st.divider()
st.header("📊 Wyniki zbiorcze")
col_res1, col_res2 = st.columns(2)
with col_res1:
    st.write(f"**PHQ-9:** {s_phq}")
    st.write(f"**GAD-7:** {s_gad}")
    st.write(f"**ASRS:** {s_asrs}")
with col_res2:
    st.write(f"**AUDIT:** {s_audit}")
    st.write(f"**AQ-10:** {s_aq}")
    st.write(f"**Struktura Osobowości:** {s_pds} / 32")

# --- FORMULARZ E-MAIL (Zabezpieczony format) ---
st.divider()
st.subheader("✉️ Wyślij raport")
with st.form("email_form"):
    pacjent = st.text_input("ID Pacjenta")
    email_do = st.text_input("Adres e-mail odbiorcy")
    
    # TUTAJ WPISZ SWOJE DANE (Hasło aplikacji z Google)
    M_USER = "TWOJ_EMAIL@gmail.com"
    M_PASS = "TWOJE_HASLO_APLIKACJI"
    
    wyslij = st.form_submit_button("Wyślij")
    if wyslij and pacjent and email_do:
        try:
            body = f"""Wyniki dla pacjenta: {pacjent}

PHQ-9 (Depresja): {s_phq}
GAD-7 (Lęk): {s_gad}
ASRS (ADHD): {s_asrs}
AQ-10 (Autyzm): {s_aq}
AUDIT (Alkohol): {s_audit}
Struktura Osobowości (PDS): {s_pds}/32"""

            msg = MIMEMultipart()
            msg['From'] = M_USER
            msg['To'] = email_do
            msg['Subject'] = f"Raport Diagnostyczny: {pacjent}"
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(M_USER, M_PASS)
                server.send_message(msg)
            
            st.success("Raport został wysłany pomyślnie!")
        except Exception as e:
            st.error(f"Wystąpił błąd podczas wysyłania: {e}")
