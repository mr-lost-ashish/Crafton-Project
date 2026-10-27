from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CommunityReport, CommunitySolution, User, Scan
from ..schemas import CommunityReportCreate, CommunitySolutionCreate

router = APIRouter(prefix="", tags=["Community Crop Rescue Network"])

@router.get("/community/reports")
def list_community_reports(status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    F20: Community Crop Rescue Network
    Farmers post rescue requests; community and KVK experts collaborate to verify solutions.
    """
    query = db.query(CommunityReport)
    if status:
        query = query.filter(CommunityReport.status == status)
    reports = query.order_by(CommunityReport.created_at.desc()).all()

    results = []
    for r in reports:
        author = db.query(User).filter(User.id == r.user_id).first()
        verifier = db.query(User).filter(User.id == r.verified_by).first() if r.verified_by else None
        
        solutions = []
        for sol in r.solutions:
            sol_author = db.query(User).filter(User.id == sol.author_id).first()
            solutions.append({
                "id": sol.id,
                "author_name": sol_author.name if sol_author else "Community Member",
                "author_role": sol_author.role if sol_author else "farmer",
                "body": sol.body,
                "is_expert_verified": sol.is_expert_verified,
                "improved_count": sol.improved_count,
                "no_change_count": sol.no_change_count,
                "worse_count": sol.worse_count,
                "created_at": sol.created_at.isoformat()
            })

        results.append({
            "id": r.id,
            "author_name": author.name if author else "Fellow Farmer",
            "author_district": author.district if author else "Nashik",
            "symptoms_text": r.symptoms_text,
            "status": r.status, # open, verified, resolved
            "verified_by_name": verifier.name if verifier else None,
            "verified_at": r.verified_at.isoformat() if r.verified_at else None,
            "scan_image_url": r.scan.image_url if r.scan else "/sample_images/tomato_early_blight.jpg",
            "solutions": solutions,
            "created_at": r.created_at.isoformat()
        })
    return results

@router.post("/community/reports")
def create_community_report(payload: CommunityReportCreate, db: Session = Depends(get_db)):
    farmer = db.query(User).filter(User.role == "farmer").first()
    if not farmer:
        raise HTTPException(status_code=400, detail="User not found.")

    new_report = CommunityReport(
        user_id=farmer.id,
        field_id=payload.field_id,
        scan_id=payload.scan_id,
        symptoms_text=payload.symptoms_text,
        status="open",
        created_at=datetime.utcnow()
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "status": "success",
        "report_id": new_report.id,
        "message": "Crop rescue ticket posted to community network."
    }

@router.patch("/community/reports/{report_id}")
def verify_community_report(report_id: str, new_status: str = Query("verified"), db: Session = Depends(get_db)):
    """Expert verifies or marks resolution on community rescue ticket."""
    report = db.query(CommunityReport).filter(CommunityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    expert = db.query(User).filter(User.role == "expert").first()
    report.status = new_status
    if new_status == "verified":
        report.verified_by = expert.id if expert else None
        report.verified_at = datetime.utcnow()

    db.commit()
    return {"status": "success", "report_status": report.status}

@router.post("/community/reports/{report_id}/solutions")
def add_solution_or_vote(
    report_id: str,
    solution_id: Optional[str] = Query(None),
    outcome_vote: Optional[str] = Query(None), # improved, no_change, worse
    payload: Optional[CommunitySolutionCreate] = None,
    db: Session = Depends(get_db)
):
    """
    FR-17.3, FR-17.4:
    Post a solution to a rescue ticket, or record an outcome vote (improved, no change, worse).
    """
    if solution_id and outcome_vote:
        sol = db.query(CommunitySolution).filter(CommunitySolution.id == solution_id).first()
        if not sol:
            raise HTTPException(status_code=404, detail="Solution not found.")
        if outcome_vote == "improved":
            sol.improved_count += 1
        elif outcome_vote == "no_change":
            sol.no_change_count += 1
        elif outcome_vote == "worse":
            sol.worse_count += 1
        db.commit()
        return {
            "status": "success",
            "solution_id": sol.id,
            "improved": sol.improved_count,
            "no_change": sol.no_change_count,
            "worse": sol.worse_count
        }

    if not payload or not payload.body:
        raise HTTPException(status_code=400, detail="Solution text body is required.")

    user = db.query(User).filter(User.role == "expert").first() or db.query(User).first()
    new_sol = CommunitySolution(
        report_id=report_id,
        author_id=user.id,
        body=payload.body,
        treatment_id=payload.treatment_id,
        is_expert_verified=(user.role == "expert"),
        created_at=datetime.utcnow()
    )
    db.add(new_sol)
    db.commit()
    db.refresh(new_sol)

    return {
        "status": "success",
        "solution_id": new_sol.id,
        "is_expert_verified": new_sol.is_expert_verified,
        "message": "Solution submitted successfully."
    }
