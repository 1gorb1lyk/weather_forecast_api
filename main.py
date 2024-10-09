from fastapi import FastAPI
from app.weather_utils.weather_processing import WeatherProcessing

app = FastAPI()


@app.get("/weather/")
async def get_weather(city: str) -> dict:
    forecast = await WeatherProcessing(city).get_city_weather_data()
    return forecast

