import streamlit as st
from itertools import combinations

st.set_page_config(page_title="Kalıp Optimizasyon", layout="centered")

if "sayfa" not in st.session_state:
    st.session_state.sayfa = 1

# Sayfa 1: Robot Bilgileri
if st.session_state.sayfa == 1:
    st.title("🔧 1. Adım: Robot Bilgileri")
    robot_sayisi = st.number_input("Robot Sayısı", min_value=1, key="input_robot_sayisi")
    alan_x = st.number_input("Alan Genişliği (X mm)", min_value=1, key="input_alan_x")
    alan_y = st.number_input("Alan Derinliği (Y mm)", min_value=1, key="input_alan_y")
    if st.button("İleri → Kalıp Bilgileri"):
        if robot_sayisi and alan_x and alan_y:
            st.session_state.robot_sayisi = robot_sayisi
            st.session_state.alan_x = alan_x
            st.session_state.alan_y = alan_y
            st.session_state.sayfa = 2
            st.stop()
        else:
            st.warning("Lütfen tüm bilgileri doldurun!")

# Sayfa 2: Kalıp Bilgileri
elif st.session_state.sayfa == 2:
    st.title("📦 2. Adım: Kalıp Bilgileri")
    kalip_sayisi = st.number_input("Kalıp Sayısı", min_value=1, key="input_kalip_sayisi")
    kaliplar_list = []
    for i in range(kalip_sayisi):
        st.subheader(f"Kalıp {i+1}")
        ad = st.text_input("Ad", key=f"input_ad_{i}")
        x = st.number_input("X (mm)", min_value=1.0, key=f"input_x_{i}")
        y = st.number_input("Y (mm)", min_value=1.0, key=f"input_y_{i}")
        setup = st.number_input("Setup (dk)", min_value=0.0, key=f"input_setup_{i}")
        weld = st.number_input("Weld (dk)", min_value=0.0, key=f"input_weld_{i}")
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

# Sayfa 3: Sonuçlar
elif st.session_state.sayfa == 3:
    st.title("📊 3. Adım: Optimizasyon ve Sonuç")
    kaliplar = st.session_state.kaliplar
    robot_sayisi = st.session_state.robot_sayisi
    alan_x = st.session_state.alan_x
    alan_y = st.session_state.alan_y

    def uygun_kombinasyonlar(kaliplar, alan_x, alan_y):
        uygun = []
        for r in range(1, len(kaliplar)+1):
            for combo in combinations(kaliplar, r):
                if sum(k['x'] for k in combo) <= alan_x and max(k['y'] for k in combo) <= alan_y:
                    uygun.append(combo)
        uygun.sort(key=lambda c: -len(c))
        return uygun

    kullanilan_idler = set()
    robotlar = []
    for i in range(robot_sayisi):
        kalan_kaliplar = [k for k in kaliplar if k['id'] not in kullanilan_idler]
        sol_kombolar = uygun_kombinasyonlar(kalan_kaliplar, alan_x, alan_y)
        if not sol_kombolar:
            break
        sol = sol_kombolar[0]
        kullanilan_idler.update(k['id'] for k in sol)

        kalan_kaliplar = [k for k in kaliplar if k['id'] not in kullanilan_idler]
        sag_kombolar = uygun_kombinasyonlar(kalan_kaliplar, alan_x, alan_y)
        sag = sag_kombolar[0] if sag_kombolar else []
        kullanilan_idler.update(k['id'] for k in sag)

        robotlar.append((sol, sag))

    for idx, (sol, sag) in enumerate(robotlar, 1):
        st.markdown(f"### 🤖 Robot {idx}")
        st.markdown("**Sol Kalıplar:**")
        for k in sol:
            st.write(f"- {k['ad']} (Setup: {k['setup']} dk, Weld: {k['weld']} dk)")
        st.markdown("**Sağ Kalıplar:**")
        for k in sag:
            st.write(f"- {k['ad']} (Setup: {k['setup']} dk, Weld: {k['weld']} dk)")

        sol_weld = sum(k['weld'] for k in sol)
        sag_weld = sum(k['weld'] for k in sag)
        cevrim_suresi = sol_weld + sag_weld
        cevrim_parca = len(sol) + len(sag)
        cevrim_sayisi = int(540 // cevrim_suresi) if cevrim_suresi > 0 else 0
        toplam_parca = cevrim_sayisi * cevrim_parca
        st.info(f"Çevrim Süresi: {cevrim_suresi:.1f} dk | Parça/Çevrim: {cevrim_parca} | 9 Saat Üretim: {toplam_parca} adet")

    if st.button("← Geri"):
        st.session_state.sayfa = 2
        st.stop()
