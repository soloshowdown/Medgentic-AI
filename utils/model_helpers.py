"""Model helper functions for predictions and calculations."""
import numpy as np
from typing import Dict, Any


def predict_opd_load(base_load: int, factors: Dict[str, float]) -> int:
    """Predict OPD load based on base load and factors."""
    multiplier = 1.0
    
    # Pollution impact
    aqi = factors.get('aqi', 50)
    if aqi > 200:
        multiplier += 0.3
    elif aqi > 150:
        multiplier += 0.2
    elif aqi > 100:
        multiplier += 0.1
    
    # Festival impact
    festival_score = factors.get('festival_score', 0)
    multiplier += festival_score * 0.4
    
    # Disease impact
    disease_score = factors.get('disease_score', 0)
    multiplier += disease_score * 0.3
    
    # Weather impact (extreme temperatures)
    temp = factors.get('temperature', 25)
    if temp > 40 or temp < 10:
        multiplier += 0.15
    
    return int(base_load * multiplier)


def predict_emergency_load(base_emergency: int, factors: Dict[str, float]) -> int:
    """Predict emergency department load."""
    multiplier = 1.0
    
    # Festival accidents
    festival_score = factors.get('festival_score', 0)
    multiplier += festival_score * 0.5
    
    # Pollution emergencies
    aqi = factors.get('aqi', 50)
    if aqi > 200:
        multiplier += 0.25
    
    # Disease outbreaks
    disease_score = factors.get('disease_score', 0)
    multiplier += disease_score * 0.4
    
    return int(base_emergency * multiplier)


def predict_icu_load(base_icu: int, factors: Dict[str, float]) -> int:
    """Predict ICU load."""
    multiplier = 1.0
    
    # Severe pollution cases
    aqi = factors.get('aqi', 50)
    if aqi > 300:
        multiplier += 0.4
    elif aqi > 200:
        multiplier += 0.2
    
    # Disease severity
    disease_score = factors.get('disease_score', 0)
    if disease_score > 0.7:
        multiplier += 0.5
    elif disease_score > 0.4:
        multiplier += 0.3
    
    return int(base_icu * multiplier)


def calculate_resource_requirements(loads: Dict[str, int]) -> Dict[str, Any]:
    """Calculate resource requirements based on predicted loads."""
    opd = loads.get('opd', 0)
    emergency = loads.get('emergency', 0)
    icu = loads.get('icu', 0)
    ventilator = loads.get('ventilator', 0)
    
    # Staff requirements (heuristic)
    staff = {
        'doctors': max(5, int(opd / 20) + int(emergency / 10) + int(icu / 2)),
        'nurses': max(10, int(opd / 10) + int(emergency / 5) + int(icu / 1)),
        'paramedics': max(5, int(emergency / 8)),
        'pharmacists': max(2, int(opd / 50))
    }
    
    # Bed requirements
    beds = {
        'general': max(20, int(opd * 0.1)),
        'emergency': max(10, int(emergency * 0.3)),
        'icu': max(5, icu),
        'ventilator': max(2, ventilator)
    }
    
    # Supply estimates
    supplies = {
        'oxygen_cylinders': max(10, int(icu * 2) + int(ventilator * 3)),
        'medications': 'High' if (opd + emergency) > 200 else 'Normal',
        'ppe_kits': max(50, int((opd + emergency) * 0.3)),
        'blood_units': max(5, int(emergency * 0.1))
    }
    
    return {
        'staff': staff,
        'beds': beds,
        'supplies': supplies
    }

