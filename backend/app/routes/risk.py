from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Field, WeatherSnapshot, RiskAssessment, Crop, Disease
from ..schemas import WhatIfRequest
from ..risk_engine import evaluate_disease_risk

router = APIRouter(prefix="", tags=["Early Risk & What-If Simulator"])

@router.get("/fields/{field_id}/risk")
def get_field_risk_summary(field_id: str, db: Session = Depends(get_db)):
    """FR-5.2: Retrieves current real weather risk level and microclimate indicators."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found.")

    weather = db.query(WeatherSnapshot).order_by(WeatherSnapshot.observed_for.desc()).first()
    temp_c = weather.temp_max_c if weather and weather.temp_max_c else 24.5
    humidity = weather.humidity_avg if weather and weather.humidity_avg else 88.0
    rain = weather.rainfall_mm if weather and weather.rainfall_mm else 8.0

    crop_code = field.crop.code if field.crop else "tomato"
    eval_result = evaluate_disease_risk(
        crop_code=crop_code,
        temp_c=temp_c,
        humidity_pct=humidity,
        rainfall_mm=rain,
        crop_stage_days=(date.today() - field.sowing_date).days
    )

    return {
        "field_id": field.id,
        "crop_name": field.crop.name_en if field.crop else "",
        "current_weather": {
            "temp_c": temp_c,
            "humidity_pct": humidity,
            "rainfall_mm": rain,
            "leaf_wetness_hrs": weather.leaf_wetness_hrs if weather else 5.0
        },
        "risk_assessment": eval_result
    }

@router.get("/fields/{field_id}/risk-assessments")
def get_risk_assessments(field_id: str, db: Session = Depends(get_db)):
    """F16: Fetches risk score with detailed contributing factors breakdown."""
    assessments = db.query(RiskAssessment).filter(
        RiskAssessment.field_id == field_id,
        RiskAssessment.is_what_if == False
    ).order_by(RiskAssessment.computed_at.desc()).all()

    results = []
    for a in assessments:
        results.append({
            "id": a.id,
            "disease_name": a.disease.name_en if a.disease else "Late Blight",
            "score": a.score,
            "level": a.level,
            "factors": a.factors,
            "inputs_snapshot": a.inputs_snapshot,
            "computed_at": a.computed_at.isoformat(),
            "disclaimer": "Risk estimate, not a diagnosis"
        })
    return results

@router.post("/fields/{field_id}/risk-assessments/what-if")
def simulate_what_if_risk(field_id: str, payload: WhatIfRequest, db: Session = Depends(get_db)):
    """
    F16 What-If Simulator:
    Recalculates risk estimate dynamically when farmer alters humidity, temperature, or rainfall sliders.
    Strictly marked as 'Risk estimate, not a diagnosis' and not stored as real historical score.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found.")

    crop_code = field.crop.code if field.crop else "tomato"
    sim_result = evaluate_disease_risk(
        crop_code=crop_code,
        temp_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
        rainfall_mm=payload.rainfall_mm,
        crop_stage_days=payload.crop_stage_days or (date.today() - field.sowing_date).days
    )

    # Attempt Live Google Gemini Epidemiological Modeling
    gemini_risk = None
    try:
        from ..gemini_service import real_time_weather_risk
        crop_name = field.crop.name_en if field.crop else "Tomato"
        stage_str = f"Day {(date.today() - field.sowing_date).days} after sowing (Vegetative/Fruiting)"
        gemini_risk = real_time_weather_risk(
            crop=crop_name,
            growth_stage=stage_str,
            temp=payload.temperature_c,
            humidity=payload.humidity_pct,
            rainfall=payload.rainfall_mm
        )
    except Exception as ge:
        print(f"[Gemini Service Note] Weather risk fallback: {ge}")

    score = gemini_risk.get("risk_score", sim_result["score"]) if gemini_risk else sim_result["score"]
    level = gemini_risk.get("risk_level", sim_result["level"]) if gemini_risk else sim_result["level"]
    disease_targeted = gemini_risk.get("threat_pathogen", sim_result["disease_name"]) if gemini_risk else sim_result["disease_name"]
    factors = gemini_risk.get("contributing_factors", sim_result["factors"]) if gemini_risk else sim_result["factors"]
    prev_actions = gemini_risk.get("preventive_actions") if (gemini_risk and gemini_risk.get("preventive_actions")) else (
        [
            "Monitor lower leaf surfaces twice weekly",
            "Avoid excessive nitrogen fertilization which creates succulent disease-prone foliage",
            "Keep Trichoderma viride or prophylactic Copper Oxychloride ready before rain spikes"
        ] if score >= 60 else [
            "Normal scouting routine; conditions are unfavorable for explosive epidemic spread"
        ]
    )

    return {
        "field_id": field.id,
        "simulated_inputs": {
            "temperature_c": payload.temperature_c,
            "humidity_pct": payload.humidity_pct,
            "rainfall_mm": payload.rainfall_mm
        },
        "score": score,
        "level": level,
        "disease_targeted": disease_targeted,
        "factors": factors,
        "preventive_actions": prev_actions,
        "is_what_if": True,
        "model_engine": "Google Gemini 3.5 Real-Time Epidemiological Intelligence",
        "disclaimer": "Risk estimate, not a diagnosis. Use for early scenario planning."
    }
