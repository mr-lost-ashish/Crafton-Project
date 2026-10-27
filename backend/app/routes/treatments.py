from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Disease, Treatment, TreatmentPlan, TreatmentPlanStep, TreatmentLog, LossScenario
from ..schemas import LossScenarioRequest, LossScenarioResponse

router = APIRouter(prefix="", tags=["Treatments, Planner & Loss Calculator"])

@router.get("/diseases/{disease_id}")
def get_disease_detail(disease_id: str, lang: str = Query("hi"), db: Session = Depends(get_db)):
    """FR-2.5, FR-2.6: Disease details with ICAR cited treatments (language-aware)."""
    d = db.query(Disease).filter(Disease.id == disease_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Disease not found.")

    treatments = db.query(Treatment).filter(Treatment.disease_id == d.id).all()
    t_list = []
    for t in treatments:
        t_list.append({
            "id": t.id,
            "type": t.type,
            "min_severity": t.min_severity,
            "title": t.title_hi if lang == "hi" and t.title_hi else t.title_en,
            "instructions": t.instructions_hi if lang == "hi" and t.instructions_hi else t.instructions_en,
            "active_ingredient": t.active_ingredient,
            "dosage": t.dosage,
            "timing": t.timing,
            "pre_harvest_interval_days": t.pre_harvest_interval_days,
            "max_applications_per_season": t.max_applications_per_season,
            "safety_notes": t.safety_notes_hi if lang == "hi" and t.safety_notes_hi else t.safety_notes_en,
            "source_name": t.source_name,
            "source_url": t.source_url
        })

    return {
        "id": d.id,
        "name": d.name_hi if lang == "hi" and d.name_hi else d.name_en,
        "name_en": d.name_en,
        "name_hi": d.name_hi,
        "scientific_name": d.scientific_name,
        "category": d.category,
        "symptoms": d.symptoms_hi if lang == "hi" and d.symptoms_hi else d.symptoms_en,
        "reference_image_url": d.reference_image_url,
        "treatments": t_list
    }

@router.patch("/treatment-plans/{plan_id}/steps/{step_id}")
def update_treatment_step(
    plan_id: str,
    step_id: str,
    done: bool = Query(True),
    actual_cost: Optional[float] = Query(None),
    treatment_log_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """F21: Marks a step in the Smart Treatment Plan as done, updates actual cost, and links spray record."""
    step = db.query(TreatmentPlanStep).filter(
        TreatmentPlanStep.plan_id == plan_id,
        TreatmentPlanStep.id == step_id
    ).first()
    if not step:
        raise HTTPException(status_code=404, detail="Plan step not found.")

    plan = db.query(TreatmentPlan).filter(TreatmentPlan.id == plan_id).first()

    if done:
        step.done_at = datetime.utcnow()
        if treatment_log_id:
            step.treatment_log_id = treatment_log_id
        if actual_cost is not None and plan:
            plan.actual_cost_inr = (plan.actual_cost_inr or 0.0) + actual_cost
    else:
        step.done_at = None

    db.commit()
    return {
        "status": "success",
        "step_id": step.id,
        "done_at": step.done_at.isoformat() if step.done_at else None,
        "plan_actual_cost_inr": plan.actual_cost_inr if plan else 0.0
    }

@router.post("/fields/{field_id}/loss-scenarios", response_model=LossScenarioResponse)
def compute_loss_avoidance(field_id: str, payload: LossScenarioRequest, db: Session = Depends(get_db)):
    """
    F24: Loss-Avoidance Calculator
    Compares early vs delayed intervention scenarios using user-editable crop value,
    treatment costs, and delay days.
    Labelled: 'Estimate, not a guaranteed saving'.
    """
    crop_val = max(payload.crop_value_inr, 1000.0)
    treat_cost = max(payload.treatment_cost_inr, 0.0)
    
    # Loss in early intervention: minimal crop loss + treatment cost
    early_loss = (crop_val * (payload.loss_pct_if_early / 100.0)) + treat_cost
    
    # Loss in delayed intervention: compounding crop loss + higher treatment cost
    delayed_loss = (crop_val * (payload.loss_pct_if_delayed / 100.0)) + (treat_cost * 1.5)
    
    diff_saved = max(delayed_loss - early_loss, 0.0)

    # Save scenario
    scenario = LossScenario(
        field_id=field_id,
        crop_value_inr=crop_val,
        treatment_cost_inr=treat_cost,
        loss_pct_if_early=payload.loss_pct_if_early,
        loss_pct_if_delayed=payload.loss_pct_if_delayed,
        delay_days=payload.delay_days,
        estimated_difference_inr=diff_saved
    )
    db.add(scenario)
    db.commit()

    return LossScenarioResponse(
        crop_value_inr=crop_val,
        treatment_cost_inr=treat_cost,
        early_loss_inr=round(early_loss, 2),
        delayed_loss_inr=round(delayed_loss, 2),
        estimated_difference_inr=round(diff_saved, 2),
        disclaimer="Estimate, not a guaranteed saving. Actual yields depend on local soil, weather, and spray timing."
    )
