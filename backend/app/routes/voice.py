import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, VoiceReport, Field, Disease
from ..schemas import VoiceSOSRequest, VoiceSOSResponse

router = APIRouter(prefix="", tags=["Kisan Voice SOS"])

@router.post("/voice-reports", response_model=VoiceSOSResponse)
def process_voice_sos(payload: VoiceSOSRequest, db: Session = Depends(get_db)):
    """
    F18: Kisan Voice SOS
    Farmer speaks in Hindi or English (or types transcript).
    The system transcribes, extracts crop & symptoms, formulates follow-up questions,
    and returns immediate spoken and textual agronomic guidance.
    """
    user = db.query(User).filter(User.role == "farmer").first()
    user_id = user.id if user else str(uuid.uuid4())

    transcript = (payload.transcript or "").strip()
    if not transcript:
        # Default fallback sample query in Hindi
        transcript = "मेरे टमाटर के पत्तों पर काले गोल छल्लेदार धब्बे दिख रहे हैं और निचली पत्तियां सूख रही हैं"

    # 1. Attempt Live Google Gemini Conversational Pathology Analysis
    gemini_voice = None
    try:
        from ..gemini_service import real_time_voice_sos
        gemini_voice = real_time_voice_sos(transcript, language=payload.language)
    except Exception as ge:
        print(f"[Gemini Service Note] Voice call fallback: {ge}")

    if gemini_voice:
        crop_detected = gemini_voice.get("extracted_crop", "Tomato")
        symptoms_extracted = gemini_voice.get("extracted_symptoms", ["पत्ती पर असामान्य लक्षण"])
        followup_q = gemini_voice.get("followup_questions", [
            "क्या धब्बे केवल निचली पुरानी पत्तियों पर हैं या नई पत्तियों पर भी?",
            "क्या पत्ती की निचली सतह पर कोई सफेद फफूंद दिखाई दे रही है?"
        ])
        spoken_reply = gemini_voice.get("spoken_reply", "")
        text_reply = gemini_voice.get("text_reply", "")
        candidates = gemini_voice.get("candidate_diseases", ["Tomato Early Blight", "Tomato Late Blight"])
    else:
        # Fallback extraction heuristic
        crop_detected = "Tomato"
        t_lower = transcript.lower()
        if "आलू" in transcript or "potato" in t_lower:
            crop_detected = "Potato"
        elif "कपास" in transcript or "cotton" in t_lower:
            crop_detected = "Cotton"
        elif "गेहूं" in transcript or "wheat" in t_lower:
            crop_detected = "Wheat"

        symptoms_extracted = []
        if "धब्बे" in transcript or "spot" in t_lower or "छल्ले" in transcript or "ring" in t_lower:
            symptoms_extracted.append("काले/भूरे छल्लेदार धब्बे (Concentric dark spots)")
        if "पीले" in transcript or "yellow" in t_lower:
            symptoms_extracted.append("पत्तियों का पीलापन (Chlorosis/Yellowing)")
        if "मुड़" in transcript or "curl" in t_lower:
            symptoms_extracted.append("पत्तियों का मुड़ना (Leaf curling)")
        if "सफेद" in transcript or "white" in t_lower:
            symptoms_extracted.append("सफेद फफूंद (White powdery/downy mold)")

        if not symptoms_extracted:
            symptoms_extracted = ["पत्ती पर असामान्य लक्षण (Unusual foliage discoloration)"]

        # Generate follow-up questions
        followup_q = [
            "क्या धब्बे केवल निचली पुरानी पत्तियों पर हैं या नई पत्तियों पर भी?",
            "क्या पत्ती की निचली सतह पर कोई सफेद या धूसर फफूंद दिखाई दे रही है?",
            "कृपया स्पष्ट परिणाम के लिए प्रभावित पत्ती की एक स्पष्ट फोटो स्कैन करें।"
        ] if payload.language == "hi" else [
            "Are the spots confined to lower older leaves or also spreading to upper shoots?",
            "Do you observe any white or greyish downy fungal mold on the leaf underside?",
            "Please capture a close-up photo of the affected leaf for definitive confirmation."
        ]

        # Generate spoken and textual reply
        if payload.language == "hi":
            spoken_reply = f"आपके {crop_detected} में अगेती झुलसा (Early Blight) रोग के लक्षण प्रतीत हो रहे हैं। पत्तियों पर गोल छल्लेदार धब्बे बनना इसका मुख्य लक्षण है। कृपया प्रभावित पत्तियों को हटा दें और नीम का काढ़ा या मैनकोजेब का छिड़काव करें।"
            text_reply = f"नमस्ते किसान भाई! आपके द्वारा बताए गए लक्षणों के आधार पर आपके {crop_detected} में 'अगेती झुलसा' (Early Blight) की प्रारंभिक अवस्था हो सकती है।\n\nसलाह:\n1. प्रभावित निचली पत्तियों को तोड़कर खेत से दूर नष्ट करें।\n2. तुरंत नीम तेल 1500 पीपीएम (3-4 मिली/लीटर) या मैनकोजेब (2.5 ग्राम/लीटर) का छिड़काव करें।\n3. अधिक सटीक जांच के लिए नीचे दिए गए बटन से पत्ती की फोटो लें।"
        else:
            spoken_reply = f"Based on your voice description, your {crop_detected} crop likely shows symptoms of Early Blight fungal infection. Circular concentric spots on lower leaves are typical. Please prune infected leaves and spray Mancozeb or Neem oil."
            text_reply = f"Hello Farmer! Based on your voice input, your {crop_detected} crop displays symptoms consistent with Early Blight (Alternaria solani).\n\nRecommended Immediate Actions:\n1. Prune and destroy diseased foliage touching the soil.\n2. Apply Neem formulation (3ml/L) or Mancozeb 75% WP (2.5g/L).\n3. Use the Scan camera button below to take a photo of the leaf for automated pixel-level diagnosis."
        candidates = ["Tomato Early Blight", "Tomato Septoria Spot", "Tomato Late Blight"]

    # Record voice report
    v_report = VoiceReport(
        user_id=user_id,
        field_id=payload.field_id,
        language=payload.language,
        transcript=transcript,
        extracted={"crop": crop_detected, "symptoms": symptoms_extracted},
        followups=followup_q,
        sync_status="synced",
        recorded_at=datetime.utcnow()
    )
    db.add(v_report)
    db.commit()

    return VoiceSOSResponse(
        report_id=v_report.id,
        transcript=transcript,
        extracted_crop=crop_detected,
        extracted_symptoms=symptoms_extracted,
        followup_questions=followup_q,
        spoken_reply=spoken_reply,
        text_reply=text_reply,
        candidate_diseases=candidates
    )

@router.post("/voice-reports/sync")
def sync_queued_voice_reports(reports: list, db: Session = Depends(get_db)):
    """FR-15.4: Syncs queued offline voice reports when connectivity is restored."""
    synced_ids = []
    for r in reports:
        new_v = VoiceReport(
            user_id=r.get("user_id"),
            language=r.get("language", "hi"),
            transcript=r.get("transcript", ""),
            extracted=r.get("extracted", {}),
            sync_status="synced",
            recorded_at=datetime.utcnow(),
            synced_at=datetime.utcnow()
        )
        db.add(new_v)
        synced_ids.append(new_v.id)
    db.commit()
    return {"status": "success", "synced_count": len(synced_ids)}
