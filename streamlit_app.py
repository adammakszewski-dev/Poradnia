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
    asrs_q = [
        "1. Problemy z wykończeniem szczegółów projektu?",
        "2. Trudności z uporządkowaniem rzeczy/organizacją?",
        "3. Problemy z zapamiętywaniem spotkań/terminów?",
        "4. Unikanie zadań wymagających dużego wysiłku umysłowego?",
        "5. Wiercenie się/poruszanie rękami lub stopami?",
        "6. Uczucie nadmiernej aktywności, 'pędzenia jak z silnikiem'?"
    ]
    asrs_res = [st.radio(q, list(asrs_opt.keys()), key=f"asrs_{i}") for i, q in enumerate(asrs_q)]
    
    st.divider()
    st.subheader("AQ-10 (Spektrum Autyzmu)")
    st.write("Zaznacz, jeśli poniższe stwierdzenie Cię dotyczy:")
    aq_q = [
        "1. Często zauważam ciche dźwięki, których inni nie dostrzegają.",
        "2. Zazwyczaj bardziej skupiam się na całym obrazie niż na szczegółach. (Zaznacz, jeśli NIE)",
        "3. Łatwo mi przychodzi robienie kilku rzeczy naraz. (Zaznacz, jeśli NIE)",
        "4. Po przerwie szybko potrafię wrócić do planów. (Zaznacz, jeśli NIE)",
        "5. Trudno mi 'czytać między wierszami' w rozmowie.",
        "6. Wiem, jak stwierdzić, czy słuchacz się nudzi. (Zaznacz, jeśli NIE)",
        "7. Trudno mi wyobrazić sobie, co czują bohaterowie książek.",
        "8. Lubię zbierać informacje o kategoriach rzeczy (np. typy aut).",
        "9. Łatwo odgaduję myśli/uczucia z twarzy innych. (Zaznacz, jeśli NIE)",
        "10. Trudno mi zrozumieć intencje innych ludzi."
    ]
    aq_res = [st.checkbox(q, key=f"aq_{i}") for i, q in enumerate(aq_q)]

# --- 3. AUDIT ---
with tabs[2]:
    st.subheader("AUDIT (Alkohol)")
    audit_res = []
    audit_res.append(st.selectbox("1. Jak często pije Pan/Pani alkohol?", list(aud_opt_freq.keys()), key="a1"))
    audit_res.append(st.selectbox("2. Ile porcji w typowym dniu picia?", list(aud_opt_amt.keys()), key="a2"))
    audit_res.append(st.selectbox("3. Jak często 6 lub więcej porcji naraz?", list(aud_opt_freq.keys()), key="a3"))
    aud_qs = ["4. Brak kontroli nad przerwaniem picia?", "5. Zaniedbanie obowiązków?", "6. Picie rano?", "7. Wyrzuty sumienia?", "8. Luki w pamięci?"]
    for i, q in enumerate(aud_qs):
        audit_res.append(st.selectbox(q, list(aud_opt_freq.keys()), key=f"a{i+4}"))
    audit_res.append(st.selectbox("9. Uraz fizyczny przez picie?", list(aud_opt_9_10.keys()), key="a9"))
    audit_res.append(st.selectbox("10. Sugestie o ograniczeniu?", list(aud_opt_9_10.keys()), key="a10"))

# --- 4. PDS-ICD-11 ---
with tabs[3]:
    st.subheader("PDS-ICD-11 (Osobowość)")
    st.write("Wybierz jedno stwierdzenie dla każdego obszaru (ostatnie 2 lata):")
    
    pds_points = []
    score_map_21012 = {0: 2, 1: 1, 2: 0, 3: 1, 4: 2}

    pds_data_1_10 = [
        ("1. Tożsamość", ["Często brak poczucia Ja / słabe granice", "Czasami dezorientacja / naśladowanie innych", "Stabilne poczucie Ja / tożsamości", "Tożsamość zbyt sztywna (tylko jedna rola)", "Tożsamość skrajnie niezmienna i ograniczona"]),
        ("2. Poczucie własnej wartości", ["Poczucie bezwartościowości przez większość czasu", "Częste niskie poczucie wartości", "Brak trudności z poczuciem wartości", "Częste poczucie bycia lepszym od innych", "Stałe poczucie wyższości"]),
        ("3. Postrzeganie siebie", ["Brak jakichkolwiek mocnych stron", "Niewiele mocnych stron", "Dobre poczucie stron mocnych i słabych", "Niewiele ograniczeń/słabości", "Brak jakichkolwiek słabości/ograniczeń"]),
        ("4. Cele", ["Rzadko zdolny do realistycznych celów", "Czasem trudno stawiać/realizować cele", "Brak problemów z celami", "Nadmierne nastawienie na cel / brak korekty", "Skrajnie uparty w dążeniu do celu"]),
        ("5. Relacje (Zainteresowanie)", ["Silne unikanie ludzi / izolacja", "Czasem unika ludzi (dyskomfort)", "Równowaga bycia z innymi i samemu", "Cierpi / czuje lęk, gdy jest sam", "Rozpacz/przerażenie przy braku innych"]),
        ("6. Przyjmowanie perspektywy", ["Nigdy nie rozumie myśli/uczuć innych", "Często nie bierze pod uwagę innych", "Łatwo rozumie innych", "Zbyt intensywnie analizuje innych", "Skrajna, bolesna analiza myśli innych"]),
        ("7. Wzajemność", ["Zawsze samolubny / manipulacyjny", "Czasem zbyt samolubny / dominujący", "Relacje oparte na wzajemności", "Nie umie dbać o własne potrzeby", "Skrajna uległość / bycie ofiarą"]),
        ("8. Konflikty", ["Szuka kłótni / brak trwałych relacji", "Częste konflikty", "Zdolny do współpracy w sporze", "Unika sporów kosztem swoich potrzeb", "Unika sporów za wszelką cenę"]),
        ("9. Emocje", ["Częsta brak regulacji / wybuchy", "Czasem trudności z regulacją", "Odpowiednia regulacja i ekspresja", "Tłumienie emocji (aleksytymia)", "Prawie całkowite odcięcie od emocji"]),
        ("10. Zachowanie", ["Skrajna impulsywność / kłopoty", "Czasem działa pod wpływem impulsu", "Spontaniczny, ale pod kontrolą", "Nadmierna kontrola (brak radości)", "Skrajne zahamowanie / brak życia"])
    ]

    for i, (title, opts) in enumerate(pds_data_1_10):
        choice = st.radio(title, opts, key=f"pds_q_{i}")
        pds_points.append(score_map_21012[opts.index(choice)])

    st.markdown("**Dodatkowe wskaźniki (0-3 pkt):**")
    pds_data_11_14 = [
        ("11. Rzeczywistość w stresie", ["Trafna", "Nieco zniekształcona", "Znacznie zniekształcona", "Utrata kontaktu / halucynacje"]),
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

# --- RAPORT ---
st.divider()
st.header("📊 Wyniki końcowe")
col_a, col_b = st.columns(2)
with col_a:
    st.write(f"**PHQ-9 (Depresja):** {s_phq}")
    st.write(f"**GAD-7 (Lęk):** {s_gad}")
    st.write(f"**ASRS (ADHD):** {s_asrs}")
with col_b:
    st.write(f"**AUDIT (Alkohol):** {s_audit}")
    st.write(f"**AQ-10 (Autyzm):** {s_aq}")
    st.write(f"**PDS-ICD-11 (Osobowość):** {s_pds} / 32")

# --- WYSYŁKA ---
st.divider()
st.subheader("✉️ Wyślij raport")
with st.form("mail_form"):
    p_id = st.text_input("Identyfikator Pacjenta")
    email_target = st.text_input("E-mail odbiorcy")
    
    M_USER = "TWOJ_EMAIL@gmail.com"
    M_PASS = "TWOJE_HASLO_APLIKACJI"
    
    if st.form_submit_button("Wyślij"):
        if p_id and email_target:
            try:
                content = f"Wyniki: {p_id}\n\nPHQ-9: {s_phq}\nGAD-7:
            
