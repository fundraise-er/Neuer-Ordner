import streamlit as st
import json
import os
from datetime import datetime

# === Hilfsfunktionen ===
def load_data(teamname):
    filename = f"{teamname}_daten.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return []

def save_data(teamname, data):
    filename = f"{teamname}_daten.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def berechne_statistiken(eintraege):
    if not eintraege:
        return 0, 0, 0, 0, 0
    betraege = [e['betrag'] for e in eintraege]
    tage = list(set([e['datum'] for e in eintraege]))
    anzahl = len(betraege)
    gesamt = sum(betraege)
    durchschnitt = gesamt / anzahl if anzahl else 0
    wochenschnitt = gesamt / len(tage) if tage else 0
    spender_pro_tag = anzahl / len(tage) if tage else 0
    return anzahl, gesamt, durchschnitt, wochenschnitt, spender_pro_tag

# === UI ===
st.set_page_config(page_title="Fundraising Tracker", layout="centered")
st.title("📊 Fundraising Fortschritt Tracker")

# === Login ===
teamname = st.text_input("Teammitglied-Name eingeben:")

if teamname:
    daten = load_data(teamname)

    with st.form("spender_form"):
        st.subheader("➕ Spender erfassen")
        betrag = st.number_input("Betrag (€)", min_value=1.0, step=1.0)
        intervall = st.selectbox("Intervall", ["monatlich", "vierteljährlich", "halbjährlich", "jährlich"])
        alter = st.number_input("Alter", min_value=10, max_value=120, step=1)
        erstzahlung = st.checkbox("Erstzahlung")
        submitted = st.form_submit_button("Speichern")

        if submitted:
            spender = {
                "datum": datetime.today().strftime("%Y-%m-%d"),
                "betrag": betrag,
                "intervall": intervall,
                "alter": alter,
                "erstzahlung": erstzahlung
            }
            daten.append(spender)
            save_data(teamname, daten)
            st.success("✅ Spender gespeichert!")

    # === KPIs auswerten ===
    if st.button("📊 Wochenschnitt & KPIs auswerten"):
        anzahl, gesamt, durchschnitt, wochenschnitt, spender_pro_tag = berechne_statistiken(daten)
        st.subheader("📈 Übersicht")
        st.metric("Anzahl Spender", anzahl)
        st.metric("Gesamtbetrag (€)", f"{gesamt:.2f}")
        st.metric("Durchschnitt (€)", f"{durchschnitt:.2f}")
        st.metric("Wochenschnitt (auf 5 Tage)", f"{wochenschnitt:.2f}")
        st.metric("Formulare pro Tag", f"{spender_pro_tag:.2f}")

    # === Spenderliste und Löschen ===
    st.subheader("📋 Erfasste Spender")
    for i, spender in enumerate(daten):
        cols = st.columns([5, 1])
        with cols[0]:
            st.write(f"{spender['datum']} | {spender['betrag']} € | {spender['intervall']} | {spender['alter']} Jahre | {'Erstzahlung' if spender['erstzahlung'] else 'Folgezahlung'}")
        with cols[1]:
            if st.button("🗑️ Löschen", key=f"del_{i}"):
                daten.pop(i)
                save_data(teamname, daten)
                st.experimental_rerun()

else:
    st.info("Bitte gib deinen Namen ein, um loszulegen.")
