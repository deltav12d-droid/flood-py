from fastapi import FastAPI
import requests

app = FastAPI()

API_KEY = 'ce70bf8bdb2bbf3ad192ee196735d6cf'  # Your OpenWeatherMap API Key
KERALA_COORDS = (10.8505, 76.2711)  # Kerala center

@app.get("/")
def read_root():
    return {"message": "Kerala Flood & Weather API is running."}

@app.get("/weather")
def get_weather():
    lat, lon = KERALA_COORDS
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    response = requests.get(weather_url)
    if response.status_code != 200:
        return {"error": "Failed to fetch weather data."}

    data = response.json()
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    description = data['weather'][0]['description']
    rain = data.get('rain', {}).get('1h', 0)

    flood_warning = []
    if rain >= 5:
        flood_warning = [
            {"city": "Kochi", "coords": [9.9312, 76.2673]},
            {"city": "Trivandrum", "coords": [8.5241, 76.9366]},
            {"city": "Kozhikode", "coords": [11.2588, 75.7804]}
        ]

    return {
        "temperature": temp,
        "humidity": humidity,
        "condition": description,
        "rainfall_last_hour": rain,
        "flood_warning": flood_warning
    }

# To run this:
# uvicorn main:app --reload

