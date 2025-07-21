import streamlit as st
from itertools import combinations
import random

# Sayfa ayarları
st.set_page_config(page_title="Kalıp Optimizasyon", layout="centered")

# Session state başlangıcı
if "sayfa" not in st.session_state:
    st.session_state.sayfa = 1

if st.session_state.sayfa == 1:
    st.title("🔧 1. Adım: Robot Bilgileri")
    # Girişler boş başlasın
    robot_sayisi = st.number_input("Robot Sayısı", min_value=1, key="robot_sayisi")
    alan_x = st.number_input("Alan Genişliği (X mm)", min_value=1, key="alan_x")
    alan_y = st.number_input("Alan Derinliği (Y mm)", min_value=1, key="alan_y")
    # Devam butonu
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
    # Her seferinde yeni liste oluştur
    kalip_sayisi = st.number_input("Kalıp Sayısı", min_value=1, key="kalip_sayisi")
    local_list = []
    # Tüm kalıp girişlerini her zaman göster
    for i in range(kalip_sayisi):
        st.subheader(f"Kalıp {i+1}")
        ad = st.text_input("Ad", key=f"ad_{i}")
        x = st.number_input("X (mm)", key=f"x_{i}", min_value=1.0, format="%.1f")
        y = st.number_input("Y (mm)", key=f"y_{i}", min_value=1.0, format="%.1f")
        setup = st.number_input("Setup (dk)", key=f"setup_{i}", min_value=0.0, format="%.1f")
        weld = st.number_input("Weld (dk)", key=f"weld_{i}", min_value=0.0, format="%.1f")
        local_list.append({"id": i, "ad": ad, "x": x, "y": y, "setup": setup, "weld": weld})
    # Butonlar
    col1, col2 = st.columns(2)
    if col1.button("← Geri"):
        st.session_state.sayfa = 1
        st.stop()
    if col2.button("İleri → Hesapla"):
        # Adı dolu kalıpları al
        st.session_state.kaliplar = [k for k in local_list if k["ad"]]
        if st.session_state.kaliplar:
            st.session_state.sayfa = 3
            st.stop()
        else:
            st.warning("En az bir kalıp adı giriniz.")

elif st.session_state.sayfa == 3:
    st.title("📊 3. Adım: Optimizasyon ve Sonuç")
    # Verileri al
    kaliplar = st.session_state.kaliplar
    R = st.session_state.robot_sayisi
    AX = st.session_state.alan_x
    AY = st.session_state.alan_y
    # Alan kombinasyonları
    def combos(kalip):
        groups = []
        for r in range(1, len(kalip)+1):
            for c in combinations(kalip, r):
                if sum(m['x'] for m in c) <= AX and max(m['y'] for m in c) <= AY:
                    groups.append(c)
        # en fazla kalıp sayısına göre sırala
        groups.sort(key=lambda g: -len(g))
        return groups
    # Robot atama
    used = set()
    robots = []
    for i in range(R):
        avail = [k for k in kaliplar if k['id'] not in used]
        grp = combos(avail)
        if not grp:
            break
        sol = grp[0]
        used |= {m['id'] for m in sol}
        avail2 = [k for k in kaliplar if k['id'] not in used]
        grp2 = combos(avail2)
        sag = grp2[0] if grp2 else []
        used |= {m['id'] for m in sag}
        robots.append((sol, sag))
    # Çıktı
    for idx, (sol, sag) in enumerate(robots, 1):
        st.markdown(f"### 🤖 Robot {idx}")
        st.markdown("**Sol Kalıplar:**")
        for m in sol:
            st.write(f"- {m['ad']} (Setup:{m['setup']} dk, Weld:{m['weld']} dk)")
        st.markdown("**Sağ Kalıplar:**")
        for m in sag:
            st.write(f"- {m['ad']} (Setup:{m['setup']} dk, Weld:{m['weld']} dk)")
        # 9 saatlik üretim
        sol_weld = sum(m['weld'] for m in sol)
        sag_weld = sum(m['weld'] for m in sag)
        cycle = sol_weld + sag_weld
        parts = len(sol) + len(sag)
        cycles9 = int(540 // cycle) if cycle>0 else 0
        total_parts = cycles9 * parts
        st.info(f"Çevrim Süresi: {cycle:.1f} dk | Parça/Çevrim: {parts} | 9 Saat Üretim: {total_parts} adet")
    if st.button("← Geri"):
        st.session_state.sayfa = 2
        st.stop()
