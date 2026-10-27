from typing import List, Dict, Any

def evaluate_disease_risk(
    crop_code: str,
    temp_c: float,
    humidity_pct: float,
    rainfall_mm: float,
    leaf_wetness_hrs: float = 4.0,
    crop_stage_days: int = 35
) -> Dict[str, Any]:
    """
    Computes disease risk score (0 to 100) and contributing factors
    based on micro-meteorological variables and crop growth stage.
    """
    score = 15 # baseline ambient risk
    factors = []
    disease_target = "Tomato Late Blight" if crop_code == "tomato" else ("Potato Late Blight" if crop_code == "potato" else "Crop Fungal Pathogen")

    # 1. Temperature Analysis
    if 12.0 <= temp_c <= 24.0:
        score += 30
        factors.append({
            "factor": f"Temperature ({temp_c:.1f}°C)",
            "impact": "Optimal temperature window (12-24°C) accelerates fungal sporangial germination",
            "weight": "+30%"
        })
    elif 24.1 <= temp_c <= 30.0:
        score += 15
        factors.append({
            "factor": f"Temperature ({temp_c:.1f}°C)",
            "impact": "Warm temperature favors rapid lesion expansion and bacterial proliferation",
            "weight": "+15%"
        })
    else:
        score += 5
        factors.append({
            "factor": f"Temperature ({temp_c:.1f}°C)",
            "impact": "Temperature extremes inhibit rapid spore viability",
            "weight": "+5%"
        })

    # 2. Humidity Analysis
    if humidity_pct >= 90.0:
        score += 35
        factors.append({
            "factor": f"Relative Humidity ({humidity_pct:.0f}%)",
            "impact": "Extreme humidity (>90%) creates prolonged water film essential for zoospore swimming",
            "weight": "+35%"
        })
    elif humidity_pct >= 75.0:
        score += 20
        factors.append({
            "factor": f"Relative Humidity ({humidity_pct:.0f}%)",
            "impact": "Elevated moisture (>75%) triggers sporulation on leaf surfaces",
            "weight": "+20%"
        })
    else:
        score += 5
        factors.append({
            "factor": f"Relative Humidity ({humidity_pct:.0f}%)",
            "impact": "Moderate or dry humidity limits spore germination",
            "weight": "+5%"
        })

    # 3. Rainfall & Leaf Wetness
    if rainfall_mm > 15.0 or leaf_wetness_hrs >= 6.0:
        score += 20
        factors.append({
            "factor": f"Rainfall & Wetness ({rainfall_mm:.1f}mm, {leaf_wetness_hrs:.1f}h wetness)",
            "impact": "Persistent free moisture washes spores into soil and splashes inoculum to adjacent plants",
            "weight": "+20%"
        })
    elif rainfall_mm > 2.0:
        score += 10
        factors.append({
            "factor": f"Light Rain ({rainfall_mm:.1f}mm)",
            "impact": "Intermittent light shower maintains canopy humidity",
            "weight": "+10%"
        })

    # 4. Crop Growth Stage
    if 25 <= crop_stage_days <= 60:
        score += 10
        factors.append({
            "factor": f"Crop Stage ({crop_stage_days} days after sowing)",
            "impact": "Vegetative canopy closure limits sunlight penetration and traps moist air inside foliage",
            "weight": "+10%"
        })

    # Normalize to 0-100 range
    final_score = min(max(int(score), 5), 98)

    if final_score >= 65:
        level = "high"
    elif final_score >= 40:
        level = "medium"
    else:
        level = "low"

    return {
        "disease_name": disease_target,
        "score": final_score,
        "level": level,
        "factors": factors,
        "disclaimer": "Risk estimate, not a diagnosis"
    }
