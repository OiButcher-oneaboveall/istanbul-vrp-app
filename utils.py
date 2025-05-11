import plotly.express as px
import plotly.graph_objects as go

def plot_risk_vs_time(df):
    fig = px.line(df, x="Risk Sınırı", y="Süre (dk)", markers=True,
                  title="Risk Sınırı ile Rota Süresi Arasındaki İlişki")
    fig.update_layout(xaxis_title="Risk Sınırı", yaxis_title="Toplam Süre (dk)")
    return fig

def plot_speed_sensitivity(df):
    fig = px.bar(df, x="Hız Değişimi", y="Süre (dk)", text="Süre (dk)",
                 title="Hız Değişiminin Süreye Etkisi")
    fig.update_layout(xaxis_title="Hız Değişimi (%)", yaxis_title="Toplam Süre (dk)")
    return fig

def plot_risk_distribution(log):
    risk_values = [entry["to"] for entry in log]
    city_counts = {city: risk_values.count(city) for city in set(risk_values)}
    fig = px.pie(names=city_counts.keys(), values=city_counts.values(),
                 title="Rota Boyunca Ziyaret Edilen Şehir Dağılımı")
    return fig
