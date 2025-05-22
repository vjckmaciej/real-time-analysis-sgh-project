import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

# Lista miast (można rozszerzyć)
CITIES = [
    "Warszawa", "Kraków", "Gdańsk", "Wrocław", "Poznań",
    "Berlin", "Londyn", "Nowy Jork", "Paryż", "Tokio"
]

CITY_COORDS = {
    "Warszawa": {"lat": 52.2297, "lon": 21.0122},
    "Kraków": {"lat": 50.0647, "lon": 19.9450},
    "Gdańsk": {"lat": 54.3520, "lon": 18.6466},
    "Wrocław": {"lat": 51.1079, "lon": 17.0385},
    "Poznań": {"lat": 52.4064, "lon": 16.9252},
    "Berlin": {"lat": 52.5200, "lon": 13.4050},
    "Londyn": {"lat": 51.5074, "lon": -0.1278},
    "Nowy Jork": {"lat": 40.7128, "lon": -74.0060},
    "Paryż": {"lat": 48.8566, "lon": 2.3522},
    "Tokio": {"lat": 35.6895, "lon": 139.6917}
}

# Możliwe warunki pogodowe
CONDITIONS = ["clear", "rain", "cloudy", "snow", "storm", "fog"]

# Inicjalizacja producenta Kafka
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def generate_weather_data(city):
    coords = CITY_COORDS.get(city, {"lat": None, "lon": None})
    return {
        "city": city,
        "timestamp": int(time.time()),
        "temp": round(random.uniform(-10, 40), 1),
        "pressure": random.randint(980, 1050),
        "humidity": random.randint(40, 100),
        "condition": random.choice(CONDITIONS),
        "alert_24h": random.choice([True, False]),
        "lat": coords["lat"],
        "lon": coords["lon"]
    }

def main():
    print("Weather producer started...")
    while True:
        cities_sample = random.sample(CITIES, 10)
        for city in cities_sample:
            weather = generate_weather_data(city)
            producer.send("weather", value=weather)
            print(f"Sent: {weather}")
        time.sleep(10)

if __name__ == "__main__":
    main()
