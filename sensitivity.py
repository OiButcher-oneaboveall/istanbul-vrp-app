import numpy as np
import pandas as pd
from optimizer import get_best_route

def risk_vs_time_analysis(risk_values, generations=500, pop_size=200):
    results = []
    for risk in risk_values:
        res = get_best_route(max_risk=risk, generations=generations, pop_size=pop_size)
        if res:
            d, t, r, log, route = res
            results.append({"Risk Sınırı": risk, "Süre (dk)": t, "Mesafe (km)": d, "Toplam Risk": r})
        else:
            results.append({"Risk Sınırı": risk, "Süre (dk)": None, "Mesafe (km)": None, "Toplam Risk": None})
    return pd.DataFrame(results)

def speed_sensitivity_analysis(speed_change_rates=[-0.1, 0.0, 0.1], base_speed_matrix=None):
    from data_config import speed_hourly_matrix

    if base_speed_matrix is None:
        base_speed_matrix = speed_hourly_matrix.copy()

    outputs = []
    for rate in speed_change_rates:
        adjusted = (base_speed_matrix * (1 + rate)).astype(int)

        from data_config import speed_hourly_matrix as shm_ref
        shm_ref[:, :] = adjusted

        res = get_best_route()
        if res:
            d, t, r, log, route = res
            outputs.append({"Hız Değişimi": f"{int(rate * 100)}%", "Süre (dk)": t, "Mesafe (km)": d, "Risk": r})
        else:
            outputs.append({"Hız Değişimi": f"{int(rate * 100)}%", "Süre (dk)": None, "Mesafe (km)": None, "Risk": None})

    shm_ref[:, :] = base_speed_matrix
    return pd.DataFrame(outputs)
