import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np

from optimizer import get_best_route  # Bu fonksiyon dışarıda yazılmış olacak
from data_config import cities, city_coords

st.set_page_config(layout="wide")
st.title("🚐 Zaman Pencereli ve Risk Kısıtlı Araç Rotalama - İstanbul")

# Sidebar - Parametreler
st.sidebar.header("⚖️ Parametreler")
max_risk = st.sidebar.slider("Maksimum Toplam Risk", 0.0, 3.0, 1.2, 0.1)
generations = st.sidebar.slider("Nesil Sayısı", 100, 2000, 1000, 100)
pop_size = st.sidebar.slider("Popülasyon Büyüklüğü", 10, 500, 300, 10)

# Algoritmayı çalıştır
if st.button(":rocket: Optimizasyonu Çalıştır"):
    with st.spinner("En iyi rota hesaplanıyor..."):
        result = get_best_route(max_risk=max_risk, generations=generations, pop_size=pop_size)

    if result is None:
        st.error("Hiçbir uygun rota bulunamadı. Parametreleri gözden geçirin.")
    else:
        d, t, r, log, route = result

        # Harita
        m = folium.Map(location=[41.0, 28.95], zoom_start=11)
        for i in range(len(route) - 1):
            c1, c2 = cities[route[i]], cities[route[i+1]]
            folium.Marker(location=city_coords[c1], popup=c1, tooltip=c1).add_to(m)
            folium.PolyLine(locations=[city_coords[c1], city_coords[c2]], color='blue').add_to(m)

        st.subheader(":world_map: Optimum Rota Haritası")
        st_data = st_folium(m, width=900)

        # Metinsel bilgiler
        h, m_ = int(t // 60), int(t % 60)
        st.success(f"**En iyi rota:** {' → '.join(cities[i] for i in route)}")
        st.write(f"**Toplam Mesafe:** {round(d, 2)} km")
        st.write(f"**Toplam Risk:** {round(r, 2)}")
        st.write(f"**Tahmini Yolculuk Süresi:** {h} saat {m_} dakika")

        # Zaman çizelgesi
        df = pd.DataFrame(log)
        st.subheader(":hourglass: Zaman Çizelgesi")
        st.dataframe(df, use_container_width=True)
else:
    st.info("Lütfen sol menüyü kullanarak parametreleri belirleyin ve 'Optimizasyonu Çalıştır' butonuna basın.")
