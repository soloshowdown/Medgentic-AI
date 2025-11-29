"""Data preprocessing utilities for cleaning and normalizing hospital data."""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List


def clean_pollution_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and normalize pollution data."""
    cleaned = {}
    
    # Normalize AQI values (0-500 scale)
    aqi = data.get('aqi', 0)
    cleaned['aqi'] = max(0, min(500, float(aqi)))
    
    # Normalize PM2.5 and PM10 (typical ranges)
    cleaned['pm25'] = max(0, min(500, float(data.get('pm25', 0))))
    cleaned['pm10'] = max(0, min(600, float(data.get('pm10', 0))))
    
    # Categorize AQI
    if aqi <= 50:
        cleaned['aqi_category'] = 'Good'
    elif aqi <= 100:
        cleaned['aqi_category'] = 'Moderate'
    elif aqi <= 150:
        cleaned['aqi_category'] = 'Unhealthy for Sensitive'
    elif aqi <= 200:
        cleaned['aqi_category'] = 'Unhealthy'
    elif aqi <= 300:
        cleaned['aqi_category'] = 'Very Unhealthy'
    else:
        cleaned['aqi_category'] = 'Hazardous'
    
    return cleaned


def normalize_festival_data(festivals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize festival data structure."""
    normalized = []
    for fest in festivals:
        normalized.append({
            'name': fest.get('name', ''),
            'date': fest.get('date', ''),
            'type': fest.get('type', 'religious'),
            'impact_score': max(0, min(1, float(fest.get('impact_score', 0.5))))
        })
    return normalized


def normalize_weather_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize weather data."""
    return {
        'temperature': float(data.get('temperature', 25)),
        'humidity': max(0, min(100, float(data.get('humidity', 50)))),
        'precipitation': max(0, float(data.get('precipitation', 0))),
        'wind_speed': max(0, float(data.get('wind_speed', 0)))
    }


def calculate_severity_score(factors: Dict[str, float]) -> float:
    """Calculate overall severity score (0-1) from multiple factors."""
    weights = {
        'pollution': 0.3,
        'festival': 0.25,
        'disease': 0.25,
        'weather': 0.2
    }
    
    score = 0.0
    for factor, weight in weights.items():
        value = factors.get(factor, 0.0)
        score += weight * max(0, min(1, float(value)))
    
    return max(0, min(1, score))

