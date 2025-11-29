# data_fetcher/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")  # optional
OPENAQ_URL = "https://api.openaq.org/v2/latest"  # example

app = FastAPI()

class FetchRequest(BaseModel):
    city: str
    date: str = None  # optional

def check_festival(date_str):
    # Expand this to a real lookup or calendar file
    d = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.today()
    festivals = {(10,24), (11,4), (3,8), (8,31)}  # placeholder
    return 1 if (d.month, d.day) in festivals else 0

@app.post("/fetch")
def fetch(req: FetchRequest):
    city = req.city
    date_str = req.date or datetime.today().strftime("%Y-%m-%d")
    festival_flag = check_festival(date_str)

    # Default fallback values
    aqi = 80
    temp = 25

    # If OpenWeather key provided, fetch weather (optional)
    if OPENWEATHER_KEY:
        try:
            # simple get by city name
            r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric", timeout=5)
            if r.ok:
                data = r.json()
                temp = int(data["main"]["temp"])
        except Exception as e:
            print("Weather fetch failed:", e)

    # If you want AQI from OpenAQ (city-level), try:
    try:
        r = requests.get(OPENAQ_URL, params={"city": city, "limit":1}, timeout=5)
        if r.ok:
            j = r.json()
            if j.get("results"):
                # rough approach: take PM2.5 or overall avg; here we'll fallback
                aqi = int(j["results"][0].get("measurements", [{}])[0].get("value", aqi))
    except Exception as e:
        print("AQI fetch failed:", e)

    # Simulate viral_cases from external surveillance (optional)
    viral_cases = max(0, int((aqi/100)*10 + (1 if festival_flag else 0)*5))

    return {
        "city": city,
        "date": date_str,
        "aqi": aqi,
        "temp": temp,
        "festival_flag": festival_flag,
        "viral_cases": viral_cases
    }
