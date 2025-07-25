import streamlit as st
from itertools import combinations
import copy

st.set_page_config(page_title="Maksimum Üretim için En Kısa Çevrim Optimizasyonu", layout="centered")

if "sayfa" not in st.session_state:
    st.session_state.sayfa = 1

if st.session_state.sayfa == 1:
    st.title("🔧 1. Adım: Robot Bilgileri")
    robot_sayisi = st.number_input("Robot Sayısı", min_value=1)
    alan_x = st.number_input("Alan Genişliği (X mm)", min_value=1)
    alan_y = st.number_input("Alan Derinliği (Y mm)", min_value=1)
    if st.button("İleri → Kalıp Bilgileri"):
        if robot_sayisi and alan_x and alan_y:
            st.session_state.robot_sayisi = robot_sayisi
            st.session_state.alan_x = alan_x
            st.session_state.alan_y = alan_y
            st.session_state.sayfa = 2
            st.stop()
        else:
            st.warning("Lütfen tüm bilgileri doldurun!")

elif st.session_state.sayfa == 2:
    st.title("📦 2. Adım: Kalıp Bilgileri")
    kalip_sayisi = st.number_input("Kalıp Sayısı", min_value=1)
    kaliplar_list = []
    for i in range(kalip_sayisi):
        st.subheader(f"Kalıp {i+1}")
        ad = st.text_input("Ad", key=f"ad_{i}")
        x = st.number_input("X (mm)", min_value=1.0, key=f"x_{i}")
        y = st.number_input("Y (mm)", min_value=1.0, key=f"y_{i}")
        setup = st.number_input("Setup (dk)", min_value=0.0, key=f"setup_{i}")
        weld = st.number_input("Weld (dk)", min_value=0.0, key=f"weld_{i}")
        if ad:
            kaliplar_list.append({"id": i, "ad": ad, "x": x, "y": y, "setup": setup, "weld": weld})

    col1, col2 = st.columns(2)
    if col1.button("← Geri"):
        st.session_state.sayfa = 1
        st.stop()
    if col2.button("İleri → Hesapla"):
        if kaliplar_list:
            st.session_state.kaliplar = kaliplar_list
            st.session_state.sayfa = 3
            st.stop()
        else:
            st.warning("En az bir kalıp adı giriniz!")

elif st.session_state.sayfa == 3:
    st.title("📊 3. Adım: Maksimum Üretim Sonuçları")
    kaliplar = copy.deepcopy(st.session_state.kaliplar)
    robot_sayisi = st.session_state.robot_sayisi
    alan_x = st.session_state.alan_x
    alan_y = st.session_state.alan_y

    def uygun_kombinasyonlar(kaliplar, alan_x, alan_y):
        uygun = []
        for r in range(1, len(kaliplar)+1):
            for combo in combinations(kaliplar, r):
                if sum(k['x'] for k in combo) <= alan_x and max(k['y'] for k in combo) <= alan_y:
                    uygun.append(combo)
        return uygun

    def hesapla_cikti(sol, sag):
        sol_setup = sum(k['setup'] for k in sol)
        sol_weld = sum(k['weld'] for k in sol)
        sag_setup = sum(k['setup'] for k in sag)
        sag_weld = sum(k['weld'] for k in sag)
        bekleme_sagdan = max(0, sol_setup - sag_weld)
        bekleme_soldan = max(0, sag_setup - sol_weld)
        toplam_bekleme = bekleme_sagdan + bekleme_soldan
        cevrim_suresi = sol_weld + sag_weld + toplam_bekleme
        cevrim_sayisi = int(540 // cevrim_suresi) if cevrim_suresi > 0 else 0
        kalip_bazli_adetler = {}
        for k in sol + sag:
            kalip_bazli_adetler[k['ad']] = cevrim_sayisi
        return kalip_bazli_adetler, cevrim_suresi, toplam_bekleme * cevrim_sayisi

    kaliplar_sorted = sorted(kaliplar, key=lambda k: k['setup'] + k['weld'], reverse=True)
    robot_kaliplari = [[] for _ in range(robot_sayisi)]

    for idx, kalip in enumerate(kaliplar_sorted):
        robot_kaliplari[idx % robot_sayisi].append(kalip)

    for idx, kalip_grubu in enumerate(robot_kaliplari, 1):
        st.markdown(f"### 🤖 Robot {idx}")
        en_iyi_cevrim_suresi = float('inf')
        en_iyi_sol = []
        en_iyi_sag = []

        sol_combos = uygun_kombinasyonlar(kalip_grubu, alan_x, alan_y)
        for sol in sol_combos:
            kalan2 = [k for k in kalip_grubu if k not in sol]
            sag_combos = uygun_kombinasyonlar(kalan2, alan_x, alan_y)
            if not sag_combos:
                sag_combos = [()]  # Sağ taraf boş olmasına izin ver
            for sag in sag_combos:
                _, cevrim_suresi, _ = hesapla_cikti(sol, sag)
                if cevrim_suresi < en_iyi_cevrim_suresi and cevrim_suresi > 0:
                    en_iyi_cevrim_suresi = cevrim_suresi
                    en_iyi_sol = sol
                    en_iyi_sag = sag

        if not en_iyi_sol and kalip_grubu:
            en_iyi_sol = [kalip_grubu[0]]  # En az 1 kalıp mutlaka atanacak

        if en_iyi_sol or en_iyi_sag:
            st.markdown("**Sol Kalıplar:**")
            for k in en_iyi_sol:
                st.write(f"- {k['ad']} (Setup: {k['setup']} dk, Weld: {k['weld']} dk)")
            st.markdown("**Sağ Kalıplar:**")
            for k in en_iyi_sag:
                st.write(f"- {k['ad']} (Setup: {k['setup']} dk, Weld: {k['weld']} dk)")

            kalip_bazli_adetler, cevrim_suresi, toplam_bekleme = hesapla_cikti(en_iyi_sol, en_iyi_sag)
            st.info(f"Çevrim Süresi: {cevrim_suresi:.1f} dk")
            for kalip, adet in kalip_bazli_adetler.items():
                st.write(f"{kalip} = {adet} adet")
            st.write(f"9 Saatte Robotun Bekleme Süresi: {toplam_bekleme:.1f} dk")
        else:
            st.warning("❗ Bu robot için uygun kalıp kombinasyonu bulunamadı.")

    if st.button("← Geri"):
        st.session_state.sayfa = 2
        st.stop()
