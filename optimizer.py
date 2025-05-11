import numpy as np
import random
from data_config import (
    cities, distance_matrix, risk_matrix, speed_hourly_matrix,
    service_times, START_HOUR, MAX_TOTAL_RISK, time_windows
)

def get_speed(city_idx, hour_idx):
    window_idx = hour_idx - START_HOUR
    if 0 <= window_idx < 12:
        return speed_hourly_matrix[city_idx, window_idx]
    return 90

def compute_piecewise_travel_time(from_city, to_city, start_hour, start_minute, distance):
    remaining_distance = distance
    hour = int(start_hour)
    minute = int(start_minute)
    total_minutes = 0

    while remaining_distance > 0:
        current_speed = min(get_speed(from_city, hour), get_speed(to_city, hour))
        remaining_time_in_hour = 60 - minute
        max_distance_this_hour = current_speed * (remaining_time_in_hour / 60)

        if remaining_distance <= max_distance_this_hour:
            travel_time = (remaining_distance / current_speed) * 60
            total_minutes += travel_time
            minute += travel_time
            hour += int(minute) // 60
            minute = int(minute) % 60
            break
        else:
            total_minutes += remaining_time_in_hour
            remaining_distance -= max_distance_this_hour
            hour += 1
            minute = 0

    return total_minutes, hour, minute

def route_metrics_with_log(route):
    total_distance = 0
    total_time = 0
    total_risk = 0
    hour = START_HOUR
    minute = 0
    log = []

    for i in range(len(route) - 1):
        from_city = route[i]
        to_city = route[i + 1]
        departure = f"{int(hour):02d}:{int(minute):02d}"
        distance = distance_matrix[from_city][to_city]

        wait_time = 0
        if to_city != 0:
            earliest, latest = time_windows[to_city]
            arrival_total_minutes = hour * 60 + minute
            earliest_minutes = earliest * 60
            latest_minutes = latest * 60
            if arrival_total_minutes < earliest_minutes:
                additional_wait = earliest_minutes - arrival_total_minutes
                wait_time += additional_wait
                minute += additional_wait
                hour += minute // 60
                minute %= 60
            elif arrival_total_minutes > latest_minutes:
                return float('inf'), float('inf'), float('inf'), []

        travel_minutes, hour, minute = compute_piecewise_travel_time(from_city, to_city, hour, minute, distance)
        total_distance += distance
        total_time += travel_minutes + wait_time
        total_risk += risk_matrix[from_city][to_city]

        arrival = f"{int(hour):02d}:{int(minute):02d}"
        service = service_times.get(to_city, 0)
        total_time += service
        minute += service
        hour += minute // 60
        minute %= 60
        departure_after_service = f"{int(hour):02d}:{int(minute):02d}"

        log.append({
            "from": cities[from_city],
            "to": cities[to_city],
            "departure": departure,
            "arrival": arrival,
            "service": service,
            "wait": wait_time,
            "departure_after_service": departure_after_service
        })

        if hour >= 18:
            return float('inf'), float('inf'), float('inf'), []

    return total_distance, total_time, total_risk, log

def initialize_population(size, num_cities):
    population = []
    for _ in range(size):
        ind = list(range(1, num_cities))
        random.shuffle(ind)
        population.append([0] + ind + [0])
    return population

def fitness(route):
    d, t, r, _ = route_metrics_with_log(route)
    if r > MAX_TOTAL_RISK or d == float('inf'):
        return float('inf')
    return t

def selection(pop):
    return min(random.sample(pop, 5), key=fitness)

def crossover(p1, p2):
    start, end = sorted(random.sample(range(1, len(p1) - 1), 2))
    child = [None] * len(p1)
    child[start:end] = p1[start:end]
    pointer = 1
    for gene in p2[1:-1]:
        if gene not in child:
            while child[pointer] is not None:
                pointer += 1
            child[pointer] = gene
    child[0] = child[-1] = 0
    return child

def mutate(route, rate=0.02):
    for i in range(1, len(route) - 2):
        if random.random() < rate:
            j = random.randint(1, len(route) - 2)
            route[i], route[j] = route[j], route[i]

def get_best_route(max_risk=1.2, generations=1000, pop_size=300):
    global MAX_TOTAL_RISK
    MAX_TOTAL_RISK = max_risk

    population = initialize_population(pop_size, len(cities))
    for _ in range(generations):
        new_pop = []
        for _ in range(pop_size):
            p1 = selection(population)
            p2 = selection(population)
            c = crossover(p1, p2)
            mutate(c)
            new_pop.append(c)
        population = new_pop

    valid_population = [r for r in population if fitness(r) != float('inf')]
    if valid_population:
        best_route = min(valid_population, key=fitness)
        d, t, r, log = route_metrics_with_log(best_route)
        return d, t, r, log, best_route
    else:
        return None
