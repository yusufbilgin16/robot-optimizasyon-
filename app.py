import streamlit as st
from itertools import combinations
from copy import deepcopy

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

# --- Sayfa 1: Robot Bilgileri ---
if st.session_state.sayfa == 1:
    st.title("🔧 1. Adım: Robot Bilgileri")
    st.session_state.robot_sayisi = st.number_input("Robot Sayısı", min_value=1, placeholder="Robot sayısını giriniz")
    st.session_state.alan_x      = st.number_input("Alan Genişliği (X mm)", min_value=1, placeholder="X giriniz")
    st.session_state.alan_y      = st.number_input("Alan Derinliği (Y mm)", min_value=1, placeholder="Y giriniz")
    if st.button("İleri → Kalıp Bilgileri"):
        if st.session_state.robot_sayisi and st.session_state.alan_x and st.session_state.alan_y:
            st.session_state.sayfa = 2
        else:
            st.warning("Lütfen tüm bilgileri doldurun!")

# --- Sayfa 2: Kalıp Bilgileri ---
elif st.session_state.sayfa == 2:
    st.title("📦 2. Adım: Kalıp Bilgileri")
    n = st.number_input("Kalıp Sayısı", min_value=1, placeholder="Kaç kalıp?")
    # her rerun'da sıfırlamıyoruz, kullanıcının elle girdiği her kalıp session_state.kaliplar'a ekleniyor
    for i in range(len(st.session_state.kaliplar), n):
        st.subheader(f"Kalıp {i+1}")
        ad    = st.text_input("Ad", key=f"ad_{i}")
        x     = st.number_input("X (mm)", key=f"x_{i}", placeholder="Genişlik")
        y     = st.number_input("Y (mm)", key=f"y_{i}", placeholder="Derinlik")
        setup = st.number_input("Setup (dk)", key=f"setup_{i}", placeholder="Setup süresi")
        weld  = st.number_input("Weld (dk)", key=f"weld_{i}", placeholder="Weld süresi")
        if ad:
            st.session_state.kaliplar.append({"id":i,"ad":ad,"x":x,"y":y,"setup":setup,"weld":weld})

    cols = st.columns(2)
    if cols[0].button("← Geri"):
        st.session_state.sayfa = 1
    if cols[1].button("İleri → Hesapla"):
        if len(st.session_state.kaliplar)>=1:
            st.session_state.sayfa = 3
        else:
            st.warning("En az 1 kalıp girmelisiniz!")

# --- Sayfa 3: Optimizasyon ve Sonuç ---
elif st.session_state.sayfa == 3:
    st.title("📊 3. Adım: Optimizasyon ve Sonuç")
    kaliplar      = st.session_state.kaliplar
    R             = st.session_state.robot_sayisi
    AX, AY        = st.session_state.alan_x, st.session_state.alan_y

    # 1) Alana sığan tüm kombinasyonları üret
    def combos(kalip):
        out=[]
        for r in range(1,len(kalip)+1):
            for c in combinations(kalip, r):
                if sum(m["x"] for m in c)<=AX and max(m["y"] for m in c)<=AY:
                    out.append(c)
        # büyükten küçüğe sıralı (mümkün olduğunca çok kalıp)
        return sorted(out, key=lambda grp: -len(grp))

    # 2) Robotları sırayla en büyük sol+sağ ikilisiyle doldur (kalanı sonraki robota)
    kullan = set([m["id"] for m in kaliplar])
    robot_list=[]
    for k in range(R):
        uc = combos([m for m in kaliplar if m["id"] in kullan])
        if not uc: break
        sol = uc[0]    # en çok kalıp sayan grup
        kullan -= set(m["id"] for m in sol)
        # tekrar combos
        uc2 = combos([m for m in kaliplar if m["id"] in kullan])
        sag = uc2[0] if uc2 else []
        kullan -= set(m["id"] for m in sag)
        robot_list.append((sol,sag))

    # 3) Her robot için çıktı
    for idx,(sol,sag) in enumerate(robot_list,1):
        st.markdown(f"### 🤖 Robot {idx}")
        st.markdown("**Sol Kalıplar:**")
        for m in sol: st.write(f"- {m['ad']} (Setup:{m['setup']} dk, Weld:{m['weld']} dk)")
        st.markdown("**Sağ Kalıplar:**")
        for m in sag: st.write(f"- {m['ad']} (Setup:{m['setup']} dk, Weld:{m['weld']} dk)")

        # çevrim süresi ve 9 saatlik üretim
        sw = sum(m["weld"] for m in sol)
        sg = sum(m["weld"] for m in sag)
        cycle = sw+sg      # sağ kaynak + sol kaynak
        parts = len(sol)+len(sag)
        cycles9 = int(540//cycle) if cycle>0 else 0
        total_parts = cycles9*parts

        st.info(f"Çevrim Süresi: {cycle:.1f} dk | Parça/Çevrim: {parts} | 9 Saat Üretim: {total_parts} adet")

    st.button("← Geri", on_click=lambda: setattr(st.session_state, "sayfa", 2))
