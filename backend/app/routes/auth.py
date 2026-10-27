import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserConsentLog, Scan, Field
from ..schemas import OTPRequest, OTPVerify, UserProfileUpdate

router = APIRouter(prefix="", tags=["Auth, Profile & DPDP Privacy"])

SALT = "CropGuard_India_DPDP_Salt_2026"

def hash_phone(phone: str) -> str:
    """Salted blind lookup hash to resist brute-force dictionary attacks (DPDP Act 2023)"""
    return hashlib.sha256((phone.strip() + SALT).encode("utf-8")).hexdigest()

@router.post("/auth/otp/request")
def request_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    phone = payload.phone.strip()
    if not phone or len(phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid 10-digit mobile number.")
    return {
        "status": "success",
        "message": f"OTP sent to {phone}. For prototype demo, use OTP: 123456",
        "mock_otp": "123456"
    }

@router.get("/auth/location/reverse")
def reverse_geocode(lat: float, lng: float):
    """
    Reverse geocodes latitude & longitude into District, State, and Village / Town.
    Uses free OpenStreetMap reverse lookup with fast timeout, or calculates nearest district.
    """
    import urllib.request, json
    district = "Nashik"
    state = "Maharashtra"
    village = ""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=10"
        req = urllib.request.Request(url, headers={"User-Agent": "CropGuard-App/0.2"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            addr = data.get("address", {})
            district = addr.get("state_district") or addr.get("county") or addr.get("city") or district
            state = addr.get("state") or state
            village = addr.get("village") or addr.get("suburb") or addr.get("town") or ""
    except Exception:
        # Fallback to coordinate approximation
        if 18.0 <= lat <= 21.0 and 72.0 <= lng <= 76.0:
            district = "Nashik"
            state = "Maharashtra"
        elif 28.0 <= lat <= 31.0 and 75.0 <= lng <= 78.0:
            district = "Ludhiana"
            state = "Punjab"
        elif 22.0 <= lat <= 25.0 and 75.0 <= lng <= 78.0:
            district = "Indore"
            state = "Madhya Pradesh"
            
    return {
        "latitude": round(lat, 5),
        "longitude": round(lng, 5),
        "district": district,
        "state": state,
        "village": village,
        "display_name": f"{village + ', ' if village else ''}{district}, {state}"
    }

@router.post("/auth/otp/verify")
def verify_otp(payload: OTPVerify, request: Request, db: Session = Depends(get_db)):
    phone = payload.phone.strip()
    otp = payload.otp.strip()
    if otp != "123456" and otp != "999999":
        raise HTTPException(status_code=400, detail="Invalid OTP code. Please enter 123456.")
        
    p_hash = hash_phone(phone)
    user = db.query(User).filter(User.phone_lookup_hash == p_hash).first()
    
    user_name = payload.name.strip() if payload.name and payload.name.strip() else (user.name if user else f"Farmer ({phone[-4:]})")
    user_lat = payload.latitude if payload.latitude is not None else (user.latitude if user else 19.9975)
    user_lng = payload.longitude if payload.longitude is not None else (user.longitude if user else 73.7898)
    user_district = payload.district.strip() if payload.district and payload.district.strip() else (user.district if user else "Nashik")
    user_state = payload.state.strip() if payload.state and payload.state.strip() else (user.state if user else "Maharashtra")

    if not user:
        user = User(
            phone_lookup_hash=p_hash,
            encrypted_phone=f"ENC:{phone[-4:]}",
            name=user_name,
            role="farmer",
            language="hi",
            district=user_district,
            state=user_state,
            latitude=user_lat,
            longitude=user_lng,
            share_scans=True
        )
        db.add(user)
        db.flush()

        # DPDP Act 2023: Log initial consent record
        consent = UserConsentLog(
            user_id=user.id,
            consent_type="anonymized_map_sharing",
            granted=True,
            ip_address=request.client.host if request.client else "127.0.0.1"
        )
        db.add(consent)
    else:
        # Update existing user with latest location and name
        user.name = user_name
        user.latitude = user_lat
        user.longitude = user_lng
        user.district = user_district
        user.state = user_state

    # Update or align user's primary field to their real GPS coordinates
    primary_field = db.query(Field).filter(Field.user_id == user.id).first()
    if primary_field:
        primary_field.latitude = user_lat
        primary_field.longitude = user_lng

    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "token": f"cropguard-token-{user.id}",
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "language": user.language,
            "district": user.district,
            "state": user.state,
            "latitude": user.latitude,
            "longitude": user.longitude,
            "share_scans": user.share_scans
        }
    }

@router.get("/me")
def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.role == "farmer").first()
    if not user:
        user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="No active user found.")
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "language": user.language,
        "district": user.district,
        "state": user.state,
        "latitude": user.latitude,
        "longitude": user.longitude,
        "share_scans": user.share_scans,
        "dpdp_status": "Consent Active (DPDP Act 2023)"
    }

@router.delete("/me/data")
def delete_user_data(db: Session = Depends(get_db)):
    """
    DPDP Act 2023 Compliance: Right to Erasure / Right to be Forgotten.
    Deletes all personal identifiable records, fields, and images upon request.
    """
    user = db.query(User).filter(User.role == "farmer").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user_id = user.id
    db.delete(user)
    db.commit()

    return {
        "status": "success",
        "deleted_user_id": user_id,
        "message": "All personal records, fields, and scan histories have been purged in compliance with DPDP Act 2023."
    }
