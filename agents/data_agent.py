"""Data Agent - Collects external data from various sources."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random
from nest import Agent, tool
from utils.preprocessor import clean_pollution_data, normalize_weather_data, normalize_festival_data


# Festival calendar for India (2024-2025)
FESTIVAL_CALENDAR = {
    "2024-10-31": {"name": "Diwali", "type": "religious", "impact_score": 0.8},
    "2024-11-01": {"name": "Diwali", "type": "religious", "impact_score": 0.8},
    "2024-11-12": {"name": "Diwali", "type": "religious", "impact_score": 0.7},
    "2025-03-14": {"name": "Holi", "type": "religious", "impact_score": 0.6},
    "2025-03-15": {"name": "Holi", "type": "religious", "impact_score": 0.6},
    "2024-09-07": {"name": "Ganpati", "type": "religious", "impact_score": 0.7},
    "2024-09-08": {"name": "Ganpati", "type": "religious", "impact_score": 0.7},
    "2024-06-16": {"name": "Eid al-Adha", "type": "religious", "impact_score": 0.5},
    "2024-10-03": {"name": "Navratri Start", "type": "religious", "impact_score": 0.6},
    "2024-10-12": {"name": "Navratri End", "type": "religious", "impact_score": 0.6},
}


def fetch_pollution_data(city: str, date: str) -> Dict[str, Any]:
    """Fetch pollution data from Open-Meteo or generate synthetic data."""
    try:
        # Try Open-Meteo Air Quality API
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": get_city_coords(city)[0],
            "longitude": get_city_coords(city)[1],
            "hourly": "pm10,pm2_5",
            "start_date": date,
            "end_date": date
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            hourly = data.get('hourly', {})
            if hourly.get('pm2_5') and hourly.get('pm10'):
                pm25 = sum(hourly['pm2_5']) / len(hourly['pm2_5'])
                pm10 = sum(hourly['pm10']) / len(hourly['pm10'])
                aqi = calculate_aqi(pm25, pm10)
                return {
                    "aqi": aqi,
                    "pm25": pm25,
                    "pm10": pm10,
                    "source": "open-meteo"
                }
    except Exception as e:
        print(f"Open-Meteo API failed: {e}")
    
    # Fallback: Generate synthetic data based on city and season
    return generate_synthetic_pollution(city, date)


def get_city_coords(city: str) -> tuple:
    """Get approximate coordinates for Indian cities."""
    coords = {
        "Mumbai": (19.0760, 72.8777),
        "Delhi": (28.6139, 77.2090),
        "Bangalore": (12.9716, 77.5946),
        "Kolkata": (22.5726, 88.3639),
        "Chennai": (13.0827, 80.2707),
        "Hyderabad": (17.3850, 78.4867),
        "Pune": (18.5204, 73.8567),
    }
    return coords.get(city, (19.0760, 72.8777))  # Default to Mumbai


def calculate_aqi(pm25: float, pm10: float) -> float:
    """Calculate AQI from PM2.5 and PM10 values."""
    # Simplified AQI calculation (using PM2.5 as primary)
    if pm25 <= 12:
        aqi = (pm25 / 12) * 50
    elif pm25 <= 35.4:
        aqi = 50 + ((pm25 - 12) / (35.4 - 12)) * 50
    elif pm25 <= 55.4:
        aqi = 100 + ((pm25 - 35.4) / (55.4 - 35.4)) * 50
    elif pm25 <= 150.4:
        aqi = 150 + ((pm25 - 55.4) / (150.4 - 55.4)) * 100
    elif pm25 <= 250.4:
        aqi = 200 + ((pm25 - 150.4) / (250.4 - 150.4)) * 100
    else:
        aqi = 300 + min(200, ((pm25 - 250.4) / 100) * 200)
    return min(500, aqi)


def generate_synthetic_pollution(city: str, date: str) -> Dict[str, Any]:
    """Generate synthetic pollution data."""
    # Base pollution levels by city
    base_aqi = {
        "Delhi": 180,
        "Mumbai": 120,
        "Bangalore": 80,
        "Kolkata": 150,
        "Chennai": 100,
        "Hyderabad": 110,
        "Pune": 90,
    }.get(city, 100)
    
    # Add seasonal variation
    month = int(date.split("-")[1])
    if month in [10, 11, 12, 1]:  # Winter months (higher pollution)
        base_aqi += 30
    elif month in [3, 4, 5]:  # Summer
        base_aqi += 20
    
    # Add random variation
    aqi = base_aqi + random.randint(-20, 40)
    pm25 = aqi * 0.6 + random.randint(-10, 20)
    pm10 = aqi * 0.8 + random.randint(-15, 25)
    
    return {
        "aqi": max(50, min(400, aqi)),
        "pm25": max(30, min(300, pm25)),
        "pm10": max(50, min(400, pm10)),
        "source": "synthetic"
    }


def fetch_weather_data(city: str, date: str) -> Dict[str, Any]:
    """Fetch weather data from Open-Meteo or generate synthetic."""
    try:
        coords = get_city_coords(city)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords[0],
            "longitude": coords[1],
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "start_date": date,
            "end_date": date,
            "timezone": "Asia/Kolkata"
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            daily = data.get('daily', {})
            if daily.get('temperature_2m_max'):
                return {
                    "temperature": (daily['temperature_2m_max'][0] + daily['temperature_2m_min'][0]) / 2,
                    "humidity": random.randint(40, 80),
                    "precipitation": daily.get('precipitation_sum', [0])[0],
                    "wind_speed": random.uniform(5, 15),
                    "source": "open-meteo"
                }
    except Exception as e:
        print(f"Weather API failed: {e}")
    
    # Fallback: Synthetic data
    month = int(date.split("-")[1])
    if month in [4, 5, 6]:  # Summer
        temp = random.uniform(35, 45)
    elif month in [11, 12, 1, 2]:  # Winter
        temp = random.uniform(15, 25)
    else:
        temp = random.uniform(25, 35)
    
    return {
        "temperature": temp,
        "humidity": random.randint(50, 90),
        "precipitation": random.uniform(0, 20),
        "wind_speed": random.uniform(5, 20),
        "source": "synthetic"
    }


def fetch_festival_data(date: str) -> List[Dict[str, Any]]:
    """Fetch festival data for the given date."""
    festivals = []
    
    # Check exact date
    if date in FESTIVAL_CALENDAR:
        festivals.append(FESTIVAL_CALENDAR[date])
    
    # Check nearby dates (within 2 days)
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    for i in range(-2, 3):
        check_date = (date_obj + timedelta(days=i)).strftime("%Y-%m-%d")
        if check_date in FESTIVAL_CALENDAR and check_date != date:
            fest = FESTIVAL_CALENDAR[check_date].copy()
            fest['days_away'] = i
            festivals.append(fest)
    
    return festivals


def fetch_health_data(city: str, date: str) -> Dict[str, Any]:
    """Fetch health/disease data (synthetic for now)."""
    month = int(date.split("-")[1])
    
    # Seasonal disease patterns in India
    dengue_season = month in [6, 7, 8, 9, 10]  # Monsoon
    viral_fever_season = month in [1, 2, 12]  # Winter
    h1n1_season = month in [1, 2, 3]  # Late winter/early spring
    
    return {
        "dengue_risk": 0.7 if dengue_season else 0.2,
        "viral_fever_risk": 0.6 if viral_fever_season else 0.3,
        "h1n1_risk": 0.5 if h1n1_season else 0.2,
        "seasonal_factor": month,
        "source": "synthetic"
    }


@tool
def collect_all_data(city: str, date: str) -> Dict[str, Any]:
    """Collect all external data: pollution, weather, festivals, health.
    
    Args:
        city: City name (e.g., "Mumbai", "Delhi")
        date: Date in YYYY-MM-DD format
    
    Returns:
        Dictionary with all collected data
    """
    try:
        # Fetch all data sources
        pollution = fetch_pollution_data(city, date)
        weather = fetch_weather_data(city, date)
        festivals = fetch_festival_data(date)
        health = fetch_health_data(city, date)
        
        # Clean and normalize
        pollution_cleaned = clean_pollution_data(pollution)
        weather_cleaned = normalize_weather_data(weather)
        festivals_cleaned = normalize_festival_data(festivals)
        
        return {
            "city": city,
            "date": date,
            "pollution": pollution_cleaned,
            "weather": weather_cleaned,
            "festivals": festivals_cleaned,
            "health": health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "city": city,
            "date": date,
            "pollution": clean_pollution_data({"aqi": 100, "pm25": 50, "pm10": 80}),
            "weather": normalize_weather_data({"temperature": 25, "humidity": 60, "precipitation": 0, "wind_speed": 10}),
            "festivals": [],
            "health": {"dengue_risk": 0.3, "viral_fever_risk": 0.3, "h1n1_risk": 0.2}
        }


# Create and export agent
data_agent = Agent(
    name="DataAgent",
    instructions="Collects external data from pollution APIs, weather services, festival calendars, and health datasets. Returns structured JSON with all relevant data.",
    tools=[collect_all_data]
)

if __name__ == "__main__":
    from nest import run
    run(data_agent, port=8010)

