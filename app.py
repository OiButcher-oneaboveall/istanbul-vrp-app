import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.express as px

from optimizer import get_best_route
from data_config import cities, city_coords
from sensitivity import risk_vs_time_analysis, speed_sensitivity_analysis
from utils import plot_risk_vs_time, plot_speed_sensitivity, plot_risk_distribution

st.set_page_config(layout="wide")
st.title("🚐 Zaman Pencereli ve Risk Kısıtlı Araç Rotalama - İstanbul")

# Sidebar parametreler
st.sidebar.header("⚙️ Parametreler")
max_risk = st.sidebar.slider("Maksimum Toplam Risk", 0.0, 3.0, 1.2, 0.1)
generations = st.sidebar.slider("Nesil Sayısı", 100, 2000, 1000, 100)
pop_size = st.sidebar.slider("Popülasyon Büyüklüğü", 10, 500, 300, 10)

# Kullanıcı analizi seçsin
mode = st.sidebar.radio("İşlem Seçiniz:", ["🚀 Optimizasyon", "🔬 Duyarlılık Analizi"])

if mode == "🚀 Optimizasyon":
    if st.button("Rota Hesapla"):
        with st.spinner("En iyi rota hesaplanıyor..."):
            result = get_best_route(max_risk=max_risk, generations=generations, pop_size=pop_size)

        if result is None:
            st.error("Hiçbir uygun rota bulunamadı. Parametreleri gözden geçirin.")
        else:
            d, t, r, log, route = result

            m = folium.Map(location=[41.0, 28.95], zoom_start=11)
            for i in range(len(route) - 1):
                c1, c2 = cities[route[i]], cities[route[i+1]]
                folium.Marker(location=city_coords[c1], popup=c1, tooltip=c1).add_to(m)
                folium.PolyLine(locations=[city_coords[c1], city_coords[c2]], color='blue').add_to(m)

            st.subheader("🗺️ Optimum Rota Haritası")
            st_folium(m, width=900)

            h, m_ = int(t // 60), int(t % 60)
            st.success(f"**En iyi rota:** {' → '.join(cities[i] for i in route)}")
            st.write(f"**Toplam Mesafe:** {round(d, 2)} km")
            st.write(f"**Toplam Risk:** {round(r, 2)}")
            st.write(f"**Tahmini Süre:** {h} saat {m_} dakika")

            st.subheader("⏱️ Zaman Çizelgesi")
            df = pd.DataFrame(log)
            st.dataframe(df, use_container_width=True)

            st.subheader("📊 Rota Risk Dağılımı")
            st.plotly_chart(plot_risk_distribution(log), use_container_width=True)

elif mode == "🔬 Duyarlılık Analizi":
    st.subheader("📉 Risk Sınırı vs. Süre")
    df_risk = risk_vs_time_analysis(np.arange(0.6, 2.1, 0.2), generations=generations, pop_size=pop_size)
    st.plotly_chart(plot_risk_vs_time(df_risk), use_container_width=True)
    st.dataframe(df_risk, use_container_width=True)

    st.subheader("🚗 Hız Değişimi vs. Süre")
    df_speed = speed_sensitivity_analysis()
    st.plotly_chart(plot_speed_sensitivity(df_speed), use_container_width=True)
    st.dataframe(df_speed, use_container_width=True)
