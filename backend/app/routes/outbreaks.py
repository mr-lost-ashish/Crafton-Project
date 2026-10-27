from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db, snap_to_grid
from ..models import OutbreakEvent, Scan, Disease, Crop, Alert

router = APIRouter(prefix="", tags=["Outbreaks & Radar"])

@router.get("/outbreaks")
def get_outbreak_points(
    crop: Optional[str] = Query(None),
    disease: Optional[str] = Query(None),
    days: int = Query(14),
    db: Session = Depends(get_db)
):
    """
    Anonymized community outbreak scan pins.
    Snapped to 1 km grid for privacy (FR-6.1 / DPDP Act 2023).
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = db.query(Scan).filter(Scan.captured_at >= cutoff)
    
    if disease:
        query = query.filter(Scan.top_disease_id == disease)

    scans = query.all()
    points = []
    
    for s in scans:
        if not s.latitude or not s.longitude:
            continue
            
        crop_obj = s.field.crop if s.field and s.field.crop else None
        if crop and crop_obj and crop_obj.code != crop:
            continue

        d_obj = s.top_disease
        snapped_lat, snapped_lng = snap_to_grid(s.latitude, s.longitude, grid_size=0.01)

        is_confirmed = (s.lifecycle_status in ['farmer_verified', 'expert_verified'])
        report_status = "confirmed" if is_confirmed else "suspected"

        points.append({
            "id": s.id,
            "disease_name": d_obj.name_en if d_obj else "Unknown Foliar Disease",
            "disease_name_hi": d_obj.name_hi if d_obj else "",
            "crop_name": crop_obj.name_en if crop_obj else "Tomato",
            "latitude": snapped_lat,
            "longitude": snapped_lng,
            "report_status": report_status,
            "lifecycle_status": s.lifecycle_status,
            "severity": s.severity or "moderate",
            "captured_at": s.captured_at.isoformat(),
            "is_synthetic": False
        })

    # Synthetic demo points clearly flagged
    synthetic_nodes = [
        {"lat": 20.005, "lng": 73.792, "disease": "Tomato Late Blight", "crop": "Tomato", "status": "confirmed", "severity": "severe"},
        {"lat": 19.992, "lng": 73.784, "disease": "Tomato Late Blight", "crop": "Tomato", "status": "suspected", "severity": "moderate"},
        {"lat": 20.012, "lng": 73.811, "disease": "Tomato Early Blight", "crop": "Tomato", "status": "confirmed", "severity": "moderate"},
        {"lat": 20.082, "lng": 73.865, "disease": "Tomato Early Blight", "crop": "Tomato", "status": "suspected", "severity": "mild"},
        {"lat": 19.982, "lng": 73.771, "disease": "Tomato Late Blight", "crop": "Tomato", "status": "confirmed", "severity": "severe"},
    ]
    for idx, node in enumerate(synthetic_nodes, start=101):
        points.append({
            "id": f"syn_point_{idx}",
            "disease_name": node["disease"],
            "disease_name_hi": "टमाटर झुलसा रोग",
            "crop_name": node["crop"],
            "latitude": node["lat"],
            "longitude": node["lng"],
            "report_status": node["status"],
            "lifecycle_status": "farmer_verified" if node["status"] == "confirmed" else "suspected",
            "severity": node["severity"],
            "captured_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "is_synthetic": True
        })

    return {
        "timeframe_days": days,
        "total_reports": len(points),
        "reports": points
    }

@router.get("/radar")
def get_outbreak_radar(
    crop: Optional[str] = Query(None),
    days: int = Query(14),
    db: Session = Depends(get_db)
):
    """
    F15: Disease Outbreak Radar (Single Source of Truth: OutbreakEvent)
    Strict Alerting Rules:
    - Minimum Cluster Threshold: Requires at least 3 distinct confirmed reports (min_cluster_threshold >= 3)
      before triggering community alerts or colouring a zone RED.
    - Prevents single uncalibrated AI predictions from causing false alarms or alert fatigue.
    """
    events = db.query(OutbreakEvent).all()
    zone_results = []
    
    for ev in events:
        if crop and ev.crop.code != crop:
            continue

        # Gating rule: Calculate risk level based on verified cluster threshold
        if ev.confirmed_count >= 3:
            effective_risk_level = "red" if ev.confirmed_count >= 5 else "amber"
        else:
            effective_risk_level = "green" # Insufficient verified evidence to trigger regional alert

        zone_results.append({
            "id": ev.id,
            "disease_id": ev.disease_id,
            "disease_name": ev.disease.name_en if ev.disease else "Crop Disease",
            "disease_name_hi": ev.disease.name_hi if ev.disease else "",
            "crop_id": ev.crop_id,
            "crop_name": ev.crop.name_en if ev.crop else "",
            "center_lat": ev.center_lat,
            "center_lng": ev.center_lng,
            "radius_km": ev.radius_km,
            "risk_level": effective_risk_level,
            "confirmed_count": ev.confirmed_count,
            "suspected_count": ev.suspected_count,
            "min_cluster_threshold": ev.min_cluster_threshold,
            "is_threshold_met": (ev.confirmed_count >= ev.min_cluster_threshold),
            "trend": ev.trend or "steady",
            "is_synthetic": ev.is_synthetic,
            "last_reported": ev.last_reported.isoformat()
        })

    total_confirmed = sum(z["confirmed_count"] for z in zone_results)
    total_suspected = sum(z["suspected_count"] for z in zone_results)
    active_alerts = db.query(Alert).filter(Alert.type == "outbreak").count()

    return {
        "status": "success",
        "zones": zone_results,
        "summary": {
            "total_zones": len(zone_results),
            "total_confirmed_cases": total_confirmed,
            "total_suspected_cases": total_suspected,
            "active_outbreak_alerts": active_alerts,
            "cluster_threshold_note": "A cluster requires >= 3 verified reports to trigger regional warning alerts."
        }
    }
