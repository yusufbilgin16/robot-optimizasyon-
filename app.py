import streamlit as st
from itertools import combinations
from copy import deepcopy
import random

st.set_page_config(page_title="Kalıp Optimizasyon", layout="centered")

if "sayfa" not in st.session_state:
    st.session_state.sayfa = 1
if "robot_sayisi" not in st.session_state:
    st.session_state.robot_sayisi = None
if "alan_x" not in st.session_state:
    st.session_state.alan_x = None
if "alan_y" not in st.session_state:
    st.session_state.alan_y = None
if "kaliplar" not in st.session_state:
    st.session_state.kaliplar = []

if st.session_state.sayfa == 1:
    st.title("🔧 1. Adım: Robot Bilgileri")
    st.session_state.robot_sayisi = st.number_input("Robot Sayısı", min_value=1, placeholder="Robot sayısını giriniz")
    st.session_state.alan_x = st.number_input("Sağ/Sol Alan Genişliği (X mm)", min_value=100, placeholder="Alan genişliği giriniz")
    st.session_state.alan_y = st.number_input("Sağ/Sol Alan Derinliği (Y mm)", min_value=100, placeholder="Alan derinliği giriniz")

    if st.button("İleri → Kalıp Bilgileri"):
        if st.session_state.robot_sayisi and st.session_state.alan_x and st.session_state.alan_y:
            st.session_state.sayfa = 2
            st.stop()
        else:
            st.warning("Lütfen tüm bilgileri doldurun!")

elif st.session_state.sayfa == 2:
    st.title("📦 2. Adım: Kalıp Bilgileri")
    kalip_sayisi = st.number_input("Toplam Kalıp Sayısı", min_value=1, placeholder="Kalıp sayısını giriniz")
    st.session_state.kaliplar = []

    if kalip_sayisi:
        for i in range(kalip_sayisi):
            st.subheader(f"Kalıp {i+1}")
            ad = st.text_input("Ad", key=f"ad_{i}", placeholder="Kalıp adını giriniz")
            x = st.number_input("Genişlik X (mm)", min_value=1, placeholder="Genişlik giriniz", key=f"x_{i}")
            y = st.number_input("Derinlik Y (mm)", min_value=1, placeholder="Derinlik giriniz", key=f"y_{i}")
            setup = st.number_input("Setup Süresi (dk)", min_value=0.0, placeholder="Setup süresi giriniz", key=f"setup_{i}")
            weld = st.number_input("Weld Süresi (dk)", min_value=0.0, placeholder="Weld süresi giriniz", key=f"weld_{i}")
            if ad:
                st.session_state.kaliplar.append({"id": i, "ad": ad, "x": x, "y": y, "setup": setup, "weld": weld})

    col1, col2 = st.columns(2)
    if col1.button("← Geri"):
        st.session_state.sayfa = 1
        st.stop()
    if col2.button("İleri → Hesapla"):
        if len(st.session_state.kaliplar) >= 1:
            st.session_state.sayfa = 3
            st.stop()
        else:
            st.warning("En az 1 kalıp girmelisiniz!")

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

    def rasgele_robotlar_olustur(kaliplar, robot_sayisi, kombinasyonlar):
        kullanilabilir = kaliplar[:]
        robotlar = []
        for _ in range(robot_sayisi):
            random.shuffle(kullanilabilir)
            sol = None
            sag = None
            for k in kombinasyonlar:
                if not sol:
                    sol = k
                elif not sag and not set(x['id'] for x in k) & set(x['id'] for x in sol):
                    sag = k
                if sol and sag:
                    break
            if not sol or not sag:
                return None
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
                if robotlar:
                    toplam = sum([0 for _ in robotlar])
                    if toplam < min_bekleme:
                        min_bekleme = toplam
                        en_iyi = deepcopy(robotlar)
        return en_iyi

    kombinasyonlar = uygun_kombinasyonlar_bul(kaliplar, alan_x, alan_y)
    if not kombinasyonlar:
        st.error("Hiçbir kombinasyon alana sığmıyor.")
    else:
        sonuc = en_iyi_robot_yerlesimi(kaliplar, robot_sayisi, kombinasyonlar)
        if sonuc:
            for i, (sol, sag) in enumerate(sonuc):
                st.markdown(f"### 🤖 Robot {i+1}")
                st.markdown("**Sol Kalıplar:**")
                for k in sol:
                    st.write(f"- {k['ad']} (Setup: {k['setup']}, Weld: {k['weld']})")
                st.markdown("**Sağ Kalıplar:**")
                for k in sag:
                    st.write(f"- {k['ad']} (Setup: {k['setup']}, Weld: {k['weld']})")

                sol_weld = sum(k["weld"] for k in sol)
                sag_weld = sum(k["weld"] for k in sag)

                cevrim_suresi = sol_weld + sag_weld
                cevrim_parca_sayisi = len(sol) + len(sag)
                cevrim_sayisi = int(540 / cevrim_suresi) if cevrim_suresi > 0 else 0

                st.info(f"Çevrim Süresi: {cevrim_suresi} dk | Çevrim Başına Parça: {cevrim_parca_sayisi} | Toplam Çevrim Sayısı (9 saat): {cevrim_sayisi} | Toplam Üretim (9 saat): {cevrim_sayisi * cevrim_parca_sayisi}")

        else:
            st.warning("Uygun yerleşim bulunamadı. Daha fazla kalıp deneyin.")

    if st.button("← Geri"):
        st.session_state.sayfa = 2
        st.stop()
