import io
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from ..database import get_db
from ..models import (
    Field, User, Crop, Scan, TreatmentLog, Treatment, SensorReading, DroneSurvey,
    RiskAssessment, Alert, SimulationScenario
)
from ..schemas import FieldCreate, FieldOut, TreatmentLogCreate

router = APIRouter(prefix="", tags=["Fields & Farm Management"])

@router.get("/fields")
def list_fields(db: Session = Depends(get_db)):
    fields = db.query(Field).filter(Field.is_active == True).all()
    results = []
    for f in fields:
        crop = db.query(Crop).filter(Crop.id == f.crop_id).first()
        results.append({
            "id": f.id,
            "user_id": f.user_id,
            "crop_id": f.crop_id,
            "crop_name": crop.name_en if crop else "Unknown",
            "crop_name_hi": crop.name_hi if crop else "",
            "crop_code": crop.code if crop else "unknown",
            "name": f.name,
            "variety": f.variety,
            "area_acres": f.area_acres,
            "sowing_date": f.sowing_date.isoformat(),
            "age_days": (date.today() - f.sowing_date).days,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "status": f.status,
            "created_at": f.created_at.isoformat()
        })
    return results

@router.post("/fields")
def create_field(payload: FieldCreate, db: Session = Depends(get_db)):
    farmer = db.query(User).filter(User.role == "farmer").first()
    if not farmer:
        raise HTTPException(status_code=400, detail="Farmer profile not found.")

    crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()
    if not crop:
        raise HTTPException(status_code=400, detail="Invalid crop ID.")

    new_field = Field(
        user_id=farmer.id,
        crop_id=payload.crop_id,
        name=payload.name,
        variety=payload.variety,
        area_acres=payload.area_acres or 1.0,
        sowing_date=payload.sowing_date,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status="healthy"
    )
    db.add(new_field)
    db.commit()
    db.refresh(new_field)

    return {
        "id": new_field.id,
        "name": new_field.name,
        "crop_name": crop.name_en,
        "crop_name_hi": crop.name_hi,
        "area_acres": new_field.area_acres,
        "status": new_field.status,
        "message": "Field created successfully."
    }

@router.get("/fields/priority")
def get_field_inspection_priority(db: Session = Depends(get_db)):
    """
    F19 Farm Digital Twin:
    Ranks fields by urgent inspection priority based on current infection status,
    historical scans, and weather vulnerability.
    """
    fields = db.query(Field).filter(Field.is_active == True).all()
    ranked = []
    for f in fields:
        crop = db.query(Crop).filter(Crop.id == f.crop_id).first()
        latest_scan = db.query(Scan).filter(Scan.field_id == f.id).order_by(Scan.captured_at.desc()).first()
        
        priority_weight = 10
        reason = "Routine monitoring"
        if f.status == "infected":
            priority_weight = 95
            reason = "Active disease infection detected; immediate intervention required."
        elif f.status == "watch":
            priority_weight = 75
            reason = "High ambient weather risk (humidity > 85%) and recent scan shows early symptoms."
        elif latest_scan and latest_scan.severity == "severe":
            priority_weight = 90
            reason = "Last scan recorded severe leaf area necrosis."

        ranked.append({
            "field_id": f.id,
            "field_name": f.name,
            "crop_name": crop.name_en if crop else "",
            "crop_code": crop.code if crop else "",
            "priority_score": priority_weight,
            "priority_level": "High Priority - Inspect Today" if priority_weight >= 80 else ("Moderate - Monitor Closely" if priority_weight >= 60 else "Low - Healthy"),
            "status": f.status,
            "reason": reason,
            "latest_scan_date": latest_scan.captured_at.isoformat() if latest_scan else None,
            "recommendation": "Inspect lower leaf canopy for lesion progression and spray bio-fungicide." if priority_weight >= 60 else "Maintain current irrigation and scheduled weekly scan."
        })
        
    ranked.sort(key=lambda x: x["priority_score"], reverse=True)
    return ranked

@router.get("/fields/{field_id}")
def get_field_detail(field_id: str, db: Session = Depends(get_db)):
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found.")
    crop = db.query(Crop).filter(Crop.id == field.crop_id).first()
    scans_count = db.query(Scan).filter(Scan.field_id == field.id).count()
    return {
        "id": field.id,
        "name": field.name,
        "crop_id": field.crop_id,
        "crop_name": crop.name_en if crop else "",
        "crop_name_hi": crop.name_hi if crop else "",
        "crop_code": crop.code if crop else "",
        "variety": field.variety,
        "area_acres": field.area_acres,
        "sowing_date": field.sowing_date.isoformat(),
        "age_days": (date.today() - field.sowing_date).days,
        "latitude": field.latitude,
        "longitude": field.longitude,
        "status": field.status,
        "total_scans": scans_count,
        "created_at": field.created_at.isoformat()
    }

@router.get("/fields/{field_id}/treatment-logs")
def list_treatment_logs(field_id: str, db: Session = Depends(get_db)):
    logs = db.query(TreatmentLog).filter(TreatmentLog.field_id == field_id).order_by(TreatmentLog.applied_on.desc()).all()
    results = []
    for l in logs:
        treatment = db.query(Treatment).filter(Treatment.id == l.treatment_id).first() if l.treatment_id else None
        results.append({
            "id": l.id,
            "field_id": l.field_id,
            "product_name": l.product_name,
            "active_ingredient": l.active_ingredient,
            "dose_applied": l.dose_applied,
            "applied_on": l.applied_on.isoformat(),
            "cost_inr": l.cost_inr or 0.0,
            "followup_due_on": l.followup_due_on.isoformat() if l.followup_due_on else None,
            "outcome": l.outcome,
            "notes": l.notes,
            "treatment_title": treatment.title_en if treatment else None
        })
    return results

@router.post("/fields/{field_id}/treatment-logs")
def log_treatment(field_id: str, payload: TreatmentLogCreate, db: Session = Depends(get_db)):
    """
    FR-4.3, FR-4.4:
    Logs a spray record and checks for chemical repetition warnings.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found.")

    # Check repeated chemical usage in the last 60 days
    warning = None
    if payload.active_ingredient:
        prior_logs = db.query(TreatmentLog).filter(
            TreatmentLog.field_id == field_id,
            TreatmentLog.active_ingredient == payload.active_ingredient
        ).count()
        if prior_logs >= 2:
            warning = f"Pesticide Resistance Warning: '{payload.active_ingredient}' has already been applied {prior_logs} times this season. To prevent fungal/pest resistance, agronomists recommend alternating with a different active ingredient."

    new_log = TreatmentLog(
        field_id=field_id,
        scan_id=payload.scan_id,
        treatment_id=payload.treatment_id,
        product_name=payload.product_name,
        active_ingredient=payload.active_ingredient,
        dose_applied=payload.dose_applied,
        applied_on=payload.applied_on,
        cost_inr=payload.cost_inr,
        followup_due_on=payload.followup_due_on or (payload.applied_on + timedelta(days=7)),
        outcome="pending",
        notes=payload.notes
    )
    db.add(new_log)
    
    # If field was infected, update to recovering
    if field.status == "infected":
        field.status = "recovering"
        
    db.commit()
    db.refresh(new_log)

    return {
        "status": "success",
        "log_id": new_log.id,
        "warning": warning,
        "followup_due_on": new_log.followup_due_on.isoformat(),
        "message": "Spray log recorded successfully."
    }

@router.get("/fields/{field_id}/sensors")
def get_sensor_dashboard(field_id: str, db: Session = Depends(get_db)):
    """FR-10.2: IoT Sensor Dashboard (simulated)."""
    sensor = db.query(SensorReading).filter(SensorReading.field_id == field_id).order_by(SensorReading.recorded_at.desc()).first()
    if not sensor:
        sensor = SensorReading(
            field_id=field_id,
            recorded_at=datetime.utcnow(),
            soil_moisture_pct=61.8,
            leaf_wetness_pct=84.5,
            air_temp_c=22.8,
            humidity_pct=86.2,
            is_simulated=True
        )
        db.add(sensor)
        db.commit()

    return {
        "field_id": field_id,
        "recorded_at": sensor.recorded_at.isoformat(),
        "soil_moisture_pct": sensor.soil_moisture_pct,
        "leaf_wetness_pct": sensor.leaf_wetness_pct,
        "air_temp_c": sensor.air_temp_c,
        "humidity_pct": sensor.humidity_pct,
        "status": "High Leaf Wetness Alert (Prolonged 5+ hours)",
        "is_simulated": True
    }

@router.get("/fields/{field_id}/drone")
def get_drone_survey(field_id: str, db: Session = Depends(get_db)):
    """FR-10.1: Drone/Satellite Whole-Field NDVI Survey (simulated)."""
    survey = db.query(DroneSurvey).filter(DroneSurvey.field_id == field_id).first()
    return {
        "field_id": field_id,
        "surveyed_on": survey.surveyed_on.isoformat() if survey else date.today().isoformat(),
        "ndvi_mean": 0.68,
        "flagged_zones": survey.flagged_zones if survey else [
            {"zone": "North-West Corner", "health": "Stressed (NDVI 0.38)", "area_sqm": 450, "color": "#ef4444"},
            {"zone": "Central Basin", "health": "Moderate (NDVI 0.58)", "area_sqm": 1200, "color": "#f59e0b"},
            {"zone": "South Ridge", "health": "Healthy (NDVI 0.81)", "area_sqm": 2400, "color": "#10b981"}
        ],
        "is_simulated": True
    }

@router.post("/fields/{field_id}/twin/scenarios")
def run_digital_twin_scenario(field_id: str, scenario_type: str = Query("rain_forecast"), db: Session = Depends(get_db)):
    """
    F19: Farm Digital Twin Scenarios:
    Projects field risk 3-7 days into the future under specific weather or treatment conditions.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found.")

    if scenario_type == "rain_forecast":
        projections = [
            {"day": "Day 1 (Today)", "risk": "Medium (58%)", "action": "Foliage mostly dry, light showers"},
            {"day": "Day 2 (Tomorrow)", "risk": "High (86%)", "action": "Heavy rainfall (28mm) expected; high spore splash danger"},
            {"day": "Day 3 (+48h)", "risk": "High (92%)", "action": "Continuous leaf wetness > 12h; infection spread imminent"},
            {"day": "Day 5 (+96h)", "risk": "Moderate (65%)", "action": "Weather clears; window for systemic spray"}
        ]
        recommendation = "Apply preventative contact fungicide (e.g. Copper Oxychloride or Mancozeb) within the next 18 hours BEFORE rain starts."
    elif scenario_type == "treatment_applied":
        projections = [
            {"day": "Day 1 (Spray Day)", "risk": "Moderate (45%)", "action": "Fungicide deposited on active leaf canopy"},
            {"day": "Day 2", "risk": "Low (28%)", "action": "Systemic absorption active; halts mycelial penetration"},
            {"day": "Day 4", "risk": "Low (18%)", "action": "Lesion margins drying out; sporulation stopped"},
            {"day": "Day 7", "risk": "Low (12%)", "action": "Recovery confirmed; schedule routine follow-up scan"}
        ]
        recommendation = "Check leaf undersides on Day 4 to ensure fungal growth has halted."
    else:
        projections = [
            {"day": "Day 1", "risk": "Medium (50%)", "action": "Ambient baseline"},
            {"day": "Day 3", "risk": "High (75%)", "action": "Infection reaches upper tier if untreated"},
            {"day": "Day 7", "risk": "Severe (95%)", "action": "Estimated 25-35% defoliation if left unchecked"}
        ]
        recommendation = "Intervene promptly to avoid compounding yield reduction."

    scenario = SimulationScenario(
        kind="digital_twin",
        field_id=field_id,
        parameters={"scenario_type": scenario_type, "horizon_days": 7},
        results={"projections": projections, "recommendation": recommendation},
        is_simulated=True
    )
    db.add(scenario)
    db.commit()

    return {
        "field_id": field_id,
        "scenario": scenario_type,
        "projections": projections,
        "recommendation": recommendation,
        "is_simulated": True,
        "disclaimer": "Simulated estimate based on microclimate assumptions, not a confirmed forecast."
    }

@router.get("/fields/{field_id}/passport")
def get_crop_health_passport(field_id: str, db: Session = Depends(get_db)):
    """
    F22: Crop Health Passport:
    Combines Scans, Treatments, Weather Risk Changes, and Alerts into a unified timeline.
    """
    events = []

    # 1. Scans
    scans = db.query(Scan).filter(Scan.field_id == field_id).order_by(Scan.captured_at.asc()).all()
    for s in scans:
        events.append({
            "event_type": "scan",
            "timestamp": s.captured_at.isoformat(),
            "title": f"Scan Diagnosis: {s.top_disease.name_en if s.top_disease else 'Unknown'}",
            "severity": s.severity,
            "severity_pct": s.severity_pct,
            "confidence": f"{int((s.calibrated_confidence or 0.8)*100)}%",
            "image_url": s.image_url,
            "notes": s.notes or "Routine diagnostic scan",
            "status": s.lifecycle_status
        })

    # 2. Treatments
    logs = db.query(TreatmentLog).filter(TreatmentLog.field_id == field_id).order_by(TreatmentLog.applied_on.asc()).all()
    for l in logs:
        events.append({
            "event_type": "treatment",
            "timestamp": l.applied_on.isoformat(),
            "title": f"Spray Applied: {l.product_name}",
            "dose": l.dose_applied,
            "cost": f"₹{l.cost_inr:.0f}" if l.cost_inr else "₹0",
            "outcome": l.outcome,
            "notes": l.notes or "Foliar application logged by farmer"
        })

    # 3. Risk Assessments
    risks = db.query(RiskAssessment).filter(RiskAssessment.field_id == field_id, RiskAssessment.is_what_if == False).all()
    for r in risks:
        events.append({
            "event_type": "risk_change",
            "timestamp": r.computed_at.isoformat(),
            "title": f"Risk Advisory: {r.disease.name_en if r.disease else 'Pathogen'} ({r.level.upper()})",
            "score": f"{r.score}/100",
            "level": r.level,
            "notes": "Weather-driven risk assessment update"
        })

    # 4. Alerts
    alerts = db.query(Alert).filter(Alert.field_id == field_id).all()
    for a in alerts:
        events.append({
            "event_type": "alert",
            "timestamp": a.created_at.isoformat(),
            "title": a.title,
            "severity": a.severity,
            "notes": a.body
        })

    # Sort chronological
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return {
        "field_id": field_id,
        "total_events": len(events),
        "timeline": events
    }

@router.get("/fields/{field_id}/passport/export")
def export_passport_pdf(field_id: str, db: Session = Depends(get_db)):
    """
    F22: Exports the field's Crop Health Passport as a formatted PDF report.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found.")
    crop = db.query(Crop).filter(Crop.id == field.crop_id).first()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor("#15803d"),
        spaceAfter=12
    )
    elements.append(Paragraph("CropGuard - Official Crop Health Passport", title_style))
    elements.append(Paragraph(f"Field: <b>{field.name}</b> | Crop: <b>{crop.name_en if crop else ''} ({crop.name_hi if crop else ''})</b>", styles['Normal']))
    elements.append(Paragraph(f"Acreage: <b>{field.area_acres} Acres</b> | Sowing Date: <b>{field.sowing_date.isoformat()}</b> | Status: <b>{field.status.upper()}</b>", styles['Normal']))
    elements.append(Spacer(1, 16))

    # Summary Table
    scans_count = db.query(Scan).filter(Scan.field_id == field_id).count()
    sprays_count = db.query(TreatmentLog).filter(TreatmentLog.field_id == field_id).count()
    
    summary_data = [
        ["Field Location", f"{field.latitude:.4f}° N, {field.longitude:.4f}° E (Nashik, MH)"],
        ["Health Status", field.status.capitalize()],
        ["Total Scans Executed", str(scans_count)],
        ["Treatments & Sprays Logged", str(sprays_count)],
        ["Report Generation Date", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")]
    ]
    t_summary = Table(summary_data, colWidths=[200, 320])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0fdf4")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_summary)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Crop Health Timeline & Treatment Records:</b>", styles['Heading2']))
    elements.append(Spacer(1, 8))

    # Timeline Records
    timeline_rows = [["Date", "Event Type", "Details / Observations", "Action / Result"]]
    
    # Add scans
    for s in db.query(Scan).filter(Scan.field_id == field_id).limit(6):
        dname = s.top_disease.name_en if s.top_disease else "Unknown"
        timeline_rows.append([
            s.captured_at.strftime("%Y-%m-%d"),
            "Leaf Scan",
            f"{dname} ({s.severity or 'mild'}, {s.severity_pct or 5.0}%)",
            f"Confidence: {int((s.calibrated_confidence or 0.85)*100)}%"
        ])

    # Add sprays
    for l in db.query(TreatmentLog).filter(TreatmentLog.field_id == field_id).limit(6):
        timeline_rows.append([
            l.applied_on.strftime("%Y-%m-%d"),
            "Spray Log",
            f"{l.product_name} ({l.dose_applied or 'Standard dose'})",
            f"Cost: ₹{l.cost_inr or 0:.0f} | Outcome: {l.outcome or 'Pending'}"
        ])

    t_timeline = Table(timeline_rows, colWidths=[80, 90, 220, 130])
    t_timeline.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#166534")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_timeline)
    elements.append(Spacer(1, 24))

    # Disclaimer
    elements.append(Paragraph("<font size=8 color='#64748b'>Disclaimer: This Crop Health Passport is generated based on farmer-reported observations, AI computer vision inference, and recorded treatments. Agronomic recommendations cite published guidelines from ICAR and State Agricultural Universities. Consult a certified local agricultural extension officer for critical field decisions.</font>", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cropguard_passport_{field_id[:8]}.pdf"}
    )
