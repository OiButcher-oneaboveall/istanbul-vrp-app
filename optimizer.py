
import numpy as np
import random
from data_config import (
    cities, distance_matrix, hourly_speed_matrix,
    hourly_risk_matrix, fuel_consumption_matrix, co2_emission_factor,
    time_windows, service_times, START_HOUR
)

MAX_TOTAL_RISK = 1.5
HEDEF_TURU = "dengeli"

def get_speed(i, j, hour):
    t_idx = hour - START_HOUR
    return hourly_speed_matrix[i][j][t_idx] if 0 <= t_idx < 12 else 90

def get_risk(i, j, hour):
    t_idx = hour - START_HOUR
    return hourly_risk_matrix[i][j][t_idx] if 0 <= t_idx < 12 else 0.3

def get_fuel(i, j, hour):
    t_idx = hour - START_HOUR
    return fuel_consumption_matrix[i][j][t_idx] if 0 <= t_idx < 12 else 0.4

def compute_travel(i, j, hour, minute):
    dist = distance_matrix[i][j]
    speed = get_speed(i, j, hour)
    time = (dist / speed) * 60
    fuel = dist * get_fuel(i, j, hour)
    risk = get_risk(i, j, hour)
    co2 = fuel * co2_emission_factor
    return time, fuel, co2, risk

def route_metrics(route):
    total_time = 0
    total_fuel = 0
    total_co2 = 0
    total_risk = 0
    hour = START_HOUR
    minute = 0
    log = []

    for i in range(len(route) - 1):
        from_city = route[i]
        to_city = route[i+1]

        travel_min, fuel, co2, risk = compute_travel(from_city, to_city, hour, minute)
        total_time += travel_min
        total_fuel += fuel
        total_co2 += co2
        total_risk += risk

        minute += int(travel_min)
        hour += minute // 60
        minute = minute % 60

        if to_city != 0:
            early, late = time_windows[to_city]
            arrival_minutes = hour * 60 + minute
            if arrival_minutes < early * 60:
                wait = early * 60 - arrival_minutes
                total_time += wait
                minute += wait
                hour += minute // 60
                minute = minute % 60
            elif arrival_minutes > late * 60:
                return float('inf'), float('inf'), float('inf'), float('inf'), []

            service = service_times.get(to_city, 0)
            total_time += service
            minute += service
            hour += minute // 60
            minute = minute % 60

        log.append({
            "from": cities[from_city],
            "to": cities[to_city],
            "hour": hour,
            "minute": minute,
            "travel_min": round(travel_min, 1),
            "fuel(L)": round(fuel, 2),
            "co2(kg)": round(co2, 2),
            "risk": round(risk, 2)
        })

    return total_time, total_fuel, total_co2, total_risk, log
