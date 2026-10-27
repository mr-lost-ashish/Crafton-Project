from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Alert, ExpertTicket, Supplier, SupplierProduct, User, Scan, Disease

router = APIRouter(prefix="", tags=["Alerts, Expert Dashboard & Marketplace"])

# --- Alerts ---
@router.get("/alerts")
def list_alerts(db: Session = Depends(get_db)):
    farmer = db.query(User).filter(User.role == "farmer").first()
    alerts = db.query(Alert).filter(Alert.user_id == farmer.id if farmer else True).order_by(Alert.created_at.desc()).all()
    results = []
    for a in alerts:
        results.append({
            "id": a.id,
            "field_id": a.field_id,
            "type": a.type,
            "severity": a.severity, # info, warning, critical
            "title": a.title,
            "body": a.body,
            "language": a.language,
            "created_at": a.created_at.isoformat(),
            "read_at": a.read_at.isoformat() if a.read_at else None,
            "action_taken": a.action_taken
        })
    return results

@router.patch("/alerts/{alert_id}")
def update_alert(
    alert_id: str,
    action_taken: Optional[bool] = Query(None),
    mark_read: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    if mark_read:
        alert.read_at = datetime.utcnow()
    if action_taken is not None:
        alert.action_taken = action_taken

    db.commit()
    return {"status": "success", "alert_id": alert.id, "action_taken": alert.action_taken}

# --- Expert Tickets (F11) ---
@router.get("/expert/tickets")
def list_expert_tickets(status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """FR-8.2: Expert dashboard listing open escalated diagnosis tickets."""
    query = db.query(ExpertTicket)
    if status:
        query = query.filter(ExpertTicket.status == status)
    tickets = query.order_by(ExpertTicket.created_at.desc()).all()

    results = []
    for t in tickets:
        farmer = db.query(User).filter(User.id == t.requested_by).first()
        scan = db.query(Scan).filter(Scan.id == t.scan_id).first()
        diag = db.query(Disease).filter(Disease.id == t.expert_diagnosis_id).first() if t.expert_diagnosis_id else None

        results.append({
            "id": t.id,
            "scan_id": t.scan_id,
            "farmer_name": farmer.name if farmer else "Farmer",
            "farmer_district": farmer.district if farmer else "Nashik",
            "farmer_note": t.farmer_note,
            "status": t.status,
            "image_url": scan.image_url if scan else "/sample_images/tomato_early_blight.jpg",
            "model_prediction": scan.top_disease.name_en if scan and scan.top_disease else "Unknown",
            "expert_diagnosis_name": diag.name_en if diag else None,
            "expert_reply": t.expert_reply,
            "created_at": t.created_at.isoformat(),
            "answered_at": t.answered_at.isoformat() if t.answered_at else None
        })
    return results

@router.patch("/expert/tickets/{ticket_id}")
def answer_expert_ticket(
    ticket_id: str,
    diagnosis_id: str = Query(...),
    reply_text: str = Query(...),
    db: Session = Depends(get_db)
):
    """FR-8.2: Expert submits verified diagnosis and advice to the farmer."""
    ticket = db.query(ExpertTicket).filter(ExpertTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    expert = db.query(User).filter(User.role == "expert").first()
    ticket.status = "answered"
    ticket.assigned_to = expert.id if expert else ticket.assigned_to
    ticket.expert_diagnosis_id = diagnosis_id
    ticket.expert_reply = reply_text
    ticket.answered_at = datetime.utcnow()

    # Update linked scan to confirmed
    scan = db.query(Scan).filter(Scan.id == ticket.scan_id).first()
    if scan:
        scan.user_confirmed_disease_id = diagnosis_id
        scan.lifecycle_status = "expert_verified"
        scan.expert_verified_by = expert.id if expert else None
        scan.expert_verified_at = datetime.utcnow()

    # Create alert for the farmer
    alert = Alert(
        user_id=ticket.requested_by,
        field_id=scan.field_id if scan else None,
        type="followup",
        severity="info",
        title="विशेषज्ञ की सलाह प्राप्त हुई (Expert Reply Received)",
        body=f"डॉ. सुनीता शर्मा (ICAR-KVK) ने आपके टिकट का उत्तर दिया है: '{reply_text[:100]}...'",
        language="hi"
    )
    db.add(alert)
    db.commit()

    return {
        "status": "success",
        "ticket_id": ticket.id,
        "message": "Expert diagnosis submitted and alert sent to farmer."
    }

@router.post("/expert/tickets/{ticket_id}/gemini-draft")
def draft_expert_reply_with_gemini(ticket_id: str, db: Session = Depends(get_db)):
    """
    KVK Expert Copilot powered by Google Gemini:
    Drafts an immediate clinical plant pathology reply grounded in ICAR guidelines.
    """
    ticket = db.query(ExpertTicket).filter(ExpertTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    farmer = db.query(User).filter(User.id == ticket.requested_by).first()
    scan = db.query(Scan).filter(Scan.id == ticket.scan_id).first()
    crop_name = scan.field.crop.name_en if scan and scan.field and scan.field.crop else "Tomato"
    symptoms = ticket.farmer_note or (scan.top_disease.symptoms_en if scan and scan.top_disease else "Foliar spotting")
    severity = scan.severity if scan else "moderate"

    try:
        from ..gemini_service import real_time_expert_reply
        draft = real_time_expert_reply(
            farmer_name=farmer.name if farmer else "Farmer",
            crop=crop_name,
            symptoms=symptoms,
            severity=severity
        )
        if draft:
            return draft
    except Exception as e:
        print(f"[Gemini Service Note] Expert draft fallback: {e}")

    # Fallback draft
    return {
        "expert_reply_hi": f"नमस्ते {farmer.name if farmer else 'किसान भाई'}, आपके {crop_name} में {symptoms} के आधार पर अगेती झुलसा का संक्रमण है। तुरंत मैनकोज़ेब (2.5 ग्राम/लीटर) का छिड़काव करें।",
        "expert_reply_en": f"Dear {farmer.name if farmer else 'Farmer'}, based on the symptoms of {symptoms} on your {crop_name}, this is Early Blight. Apply Mancozeb 75% WP (2.5g/L) immediately.",
        "diagnosis_confirmed": "Early Blight (Alternaria solani)",
        "urgency": "High - Apply within 24 hours"
    }

# --- Suppliers / Marketplace (F12) ---
@router.get("/suppliers")
def list_suppliers(near: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """FR-9.1: Nearby agricultural input shops with available stocks and treatment links."""
    suppliers = db.query(Supplier).all()
    results = []
    for s in suppliers:
        prods = []
        for p in s.products:
            prods.append({
                "id": p.id,
                "name": p.product_name,
                "price_inr": p.price_inr,
                "in_stock": p.in_stock,
                "treatment_id": p.treatment_id
            })
        results.append({
            "id": s.id,
            "name": s.name,
            "address": s.address,
            "phone": s.phone,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "distance_km": 2.4 if "Main" in s.name else 4.1,
            "products": prods,
            "is_mock": s.is_mock
        })
    return results
