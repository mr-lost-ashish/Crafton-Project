from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Crop, Disease, OutbreakEvent, Alert, Scan, User, Field
)
from ..schemas import VillageSimulationRequest

router = APIRouter(prefix="/admin", tags=["Admin Console & Judge Simulation"])

@router.post("/simulations/village")
def inject_village_outbreak(payload: VillageSimulationRequest, db: Session = Depends(get_db)):
    """
    F23: Village Outbreak Simulation (Judge-facing Demo Mode)
    Injects a synthetic verified outbreak cluster in a selected village.
    """
    disease = db.query(Disease).filter(Disease.id == payload.disease_id).first()
    crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()

    d_name = disease.name_en if disease else "Tomato Late Blight"
    c_name = crop.name_en if crop else "Tomato"

    # 1. Create or Update Outbreak Event (Single source of truth)
    ob = OutbreakEvent(
        disease_id=payload.disease_id,
        crop_id=payload.crop_id,
        center_lat=payload.center_lat,
        center_lng=payload.center_lng,
        radius_km=12.0,
        confirmed_count=payload.intensity * 3,
        suspected_count=payload.intensity,
        min_cluster_threshold=3,
        trend="rising",
        risk_level="red",
        first_reported=datetime.utcnow(),
        last_reported=datetime.utcnow(),
        is_synthetic=True
    )
    db.add(ob)
    db.flush()

    # 2. Trigger Alerts for Matching Growers
    farmers = db.query(User).filter(User.role == "farmer").all()
    created_alerts_count = 0
    for f in farmers:
        matching_field = db.query(Field).filter(Field.user_id == f.id, Field.crop_id == payload.crop_id).first()
        alert = Alert(
            user_id=f.id,
            field_id=matching_field.id if matching_field else None,
            type="outbreak",
            outbreak_id=ob.id,
            severity="critical",
            title=f"[SIMULATED] Outbreak Alert: {d_name} in {payload.village_name}",
            body=f"Epidemic Cluster Warning: {payload.intensity * 3} confirmed cases of {d_name} reported in {payload.village_name}. Spore infection danger is RED. Inspect your {c_name} crop immediately.",
            language=f.language or "hi"
        )
        db.add(alert)
        created_alerts_count += 1

    db.commit()

    return {
        "status": "success",
        "outbreak_id": ob.id,
        "village": payload.village_name,
        "disease": d_name,
        "risk_zone_color": "RED",
        "alerts_generated": created_alerts_count,
        "is_simulated": True,
        "message": f"Simulated outbreak injected in {payload.village_name}. Confirmed cases: {payload.intensity * 3}. Radar recolored to Red and {created_alerts_count} emergency alerts sent."
    }

@router.delete("/simulations")
def reset_all_simulated_data(db: Session = Depends(get_db)):
    """
    F23: Single-click reset to clean up all synthetic demo outbreak data
    and restore the prototype to baseline.
    """
    db.query(OutbreakEvent).filter(OutbreakEvent.is_synthetic == True).delete()
    db.query(Alert).filter(Alert.title.contains("[SIMULATED]")).delete()
    db.commit()

    return {
        "status": "success",
        "message": "All simulated village outbreaks and demo alerts have been completely cleared."
    }

@router.get("/feedback")
def export_retraining_dataset(db: Session = Depends(get_db)):
    """
    FR-11.2: Review user-corrected scans and export them as labeled retraining data.
    """
    scans = db.query(Scan).filter(Scan.lifecycle_status.in_(['farmer_verified', 'expert_verified', 'rejected'])).all()
    records = []
    for s in scans:
        confirmed_disease = s.user_confirmed_disease.name_en if s.user_confirmed_disease else None
        top_disease = s.top_disease.name_en if s.top_disease else None
        records.append({
            "scan_id": s.id,
            "image_url": s.image_url,
            "model_prediction": top_disease,
            "calibrated_confidence": s.calibrated_confidence,
            "lifecycle_status": s.lifecycle_status,
            "ground_truth_label": confirmed_disease or top_disease,
            "severity_pct": s.severity_pct,
            "recorded_at": s.captured_at.isoformat()
        })
    return {
        "total_labeled_scans": len(records),
        "dataset": records
    }
