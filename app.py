
import streamlit as st
from itertools import combinations
from copy import deepcopy
import random

st.set_page_config(page_title="Kalıp Optimizasyon", layout="centered")

# Sayfa kontrolü
if "sayfa" not in st.session_state:
    st.session_state.sayfa = 1
if "robot_sayisi" not in st.session_state:
    st.session_state.robot_sayisi = 1
if "alan_x" not in st.session_state:
    st.session_state.alan_x = 1000
if "alan_y" not in st.session_state:
    st.session_state.alan_y = 500
if "kaliplar" not in st.session_state:
    st.session_state.kaliplar = []

# ----------------------------- SAYFA 1 -----------------------------
if st.session_state.sayfa == 1:
    st.title("🔧 1. Adım: Robot Bilgileri")
    st.session_state.robot_sayisi = st.number_input("Robot Sayısı", min_value=1, max_value=50, value=3)
    st.session_state.alan_x = st.number_input("Sağ/Sol Alan Genişliği (X mm)", min_value=100, value=1000)
    st.session_state.alan_y = st.number_input("Sağ/Sol Alan Derinliği (Y mm)", min_value=100, value=500)

    if st.button("İleri → Kalıp Bilgileri"):
        st.session_state.sayfa = 2
        st.experimental_rerun()

# ----------------------------- SAYFA 2 -----------------------------
elif st.session_state.sayfa == 2:
    st.title("📦 2. Adım: Kalıp Bilgileri")

    kalip_sayisi = st.number_input("Toplam Kalıp Sayısı", min_value=1, max_value=200, value=6)
    st.session_state.kaliplar = []

    for i in range(kalip_sayisi):
        st.subheader(f"Kalıp {i+1}")
        ad = st.text_input("Ad", key=f"ad_{i}")
        x = st.number_input("Genişlik X (mm)", min_value=1, value=200, key=f"x_{i}")
        y = st.number_input("Derinlik Y (mm)", min_value=1, value=200, key=f"y_{i}")
        setup = st.number_input("Setup Süresi (dk)", min_value=0.0, value=2.0, key=f"setup_{i}")
        weld = st.number_input("Weld Süresi (dk)", min_value=0.0, value=4.0, key=f"weld_{i}")
        if ad:
            st.session_state.kaliplar.append({"id": i, "ad": ad, "x": x, "y": y, "setup": setup, "weld": weld})

    col1, col2 = st.columns(2)
    if col1.button("← Geri"):
        st.session_state.sayfa = 1
        st.experimental_rerun()
    if col2.button("İleri → Hesapla"):
        st.session_state.sayfa = 3
        st.experimental_rerun()

# ----------------------------- SAYFA 3 -----------------------------
elif st.session_state.sayfa == 3:
    st.title("📊 3. Adım: Optimizasyon ve Sonuç")

    kaliplar = st.session_state.kaliplar
    robot_sayisi = st.session_state.robot_sayisi
    alan_x = st.session_state.alan_x
    alan_y = st.session_state.alan_y

    def uygun_kombinasyonlar_bul(kaliplar, alan_x, alan_y):
        uygun = []
        for i in range(1, len(kaliplar)+1):
            for combo in combinations(kaliplar, i):
                toplam_x = sum(k["x"] for k in combo)
                max_y = max(k["y"] for k in combo)
                if toplam_x <= alan_x and max_y <= alan_y:
                    uygun.append(combo)
        return uygun

    def bekleme_suresi_dogru(sol_kaliplar, sag_kaliplar):
        sol_setup = sum(k["setup"] for k in sol_kaliplar)
        sol_weld = sum(k["weld"] for k in sol_kaliplar)
        sag_setup = sum(k["setup"] for k in sag_kaliplar)
        sag_weld = sum(k["weld"] for k in sag_kaliplar)
        bekleme_sagdan = max(0, sol_setup - sag_weld)
        bekleme_soldan = max(0, sag_setup - sol_weld)
        return bekleme_sagdan + bekleme_soldan

    def toplam_bekleme_suresi(robotlar):
        return sum(bekleme_suresi_dogru(sol, sag) for sol, sag in robotlar)

    def rasgele_robotlar_olustur(kaliplar, robot_sayisi, kombinasyonlar):
        kullanilabilir = kaliplar[:]
        robotlar = []
        for _ in range(robot_sayisi):
            random.shuffle(kullanilabilir)
            secili = [k for k in kombinasyonlar if all(item in [z['id'] for z in kullanilabilir] for item in [x['id'] for x in k])]
            if len(secili) < 2:
                return None
            sol = random.choice(secili)
            kalan = [k for k in secili if not set(x['id'] for x in k) & set(x['id'] for x in sol)]
            if not kalan:
                return None
            sag = random.choice(kalan)
            robotlar.append((list(sol), list(sag)))
            kullanilmis_id = set(x['id'] for x in sol + sag)
            kullanilabilir = [k for k in kullanilabilir if k['id'] not in kullanilmis_id]
        return robotlar

    def en_iyi_robot_yerlesimi(kaliplar, robot_sayisi, kombinasyonlar, nesil=30, birey_sayisi=20):
        en_iyi = None
        min_bekleme = float('inf')
        for _ in range(nesil):
            for _ in range(birey_sayisi):
                robotlar = rasgele_robotlar_olustur(kaliplar, robot_sayisi, kombinasyonlar)
                if not robotlar:
                    continue
                toplam = toplam_bekleme_suresi(robotlar)
                if toplam < min_bekleme:
                    min_bekleme = toplam
                    en_iyi = deepcopy(robotlar)
        return en_iyi, min_bekleme

    if len(kaliplar) < robot_sayisi * 2:
        st.warning("Yeterli sayıda kalıp tanımlanmalı (her robot için en az 2).")
    else:
        kombinasyonlar = uygun_kombinasyonlar_bul(kaliplar, alan_x, alan_y)
        if not kombinasyonlar:
            st.error("Hiçbir kombinasyon alana sığmıyor.")
        else:
            sonuc, bekleme = en_iyi_robot_yerlesimi(kaliplar, robot_sayisi, kombinasyonlar)
            if sonuc:
                st.success(f"🔧 Toplam Bekleme Süresi: {bekleme:.2f} dakika (Tüm Robotlar İçin)")
                for i, (sol, sag) in enumerate(sonuc):
                    st.markdown(f"### 🤖 Robot {i+1}")
                    st.markdown("**Sol Kalıplar:**")
                    for k in sol:
                        st.write(f"- {k['ad']} (Setup: {k['setup']}, Weld: {k['weld']})")
                    st.markdown("**Sağ Kalıplar:**")
                    for k in sag:
                        st.write(f"- {k['ad']} (Setup: {k['setup']}, Weld: {k['weld']})")
            else:
                st.warning("Uygun yerleşim bulunamadı. Daha fazla kalıp deneyin.")

    if st.button("← Geri"):
        st.session_state.sayfa = 2
        st.experimental_rerun()
