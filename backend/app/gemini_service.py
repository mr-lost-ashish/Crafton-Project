"""
CropGuard Real-Time Google Gemini Intelligence Service
Integrates Gemini Multimodal Vision & Reasoning using google-genai SDK.
Handles Real-Time Leaf Pathology, OOD Leaf Gatekeeper, Kisan Voice SOS,
and Microclimate Epidemiological Risk Modeling.
"""
import os
import json
import logging
from PIL import Image
from typing import Dict, Any, Optional

logger = logging.getLogger("cropguard.gemini")

# Priority order of fast, capable models with automatic fallback
CANDIDATE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3.8-flash"
]

def get_gemini_client():
    """Initializes and returns the Google GenAI client."""
    from google import genai
    
    # Read from environment (.env)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not configured. Please add it to your .env file.")
    return genai.Client(api_key=api_key)

def call_gemini_json(contents: list, system_instruction: str = None) -> Optional[Dict[str, Any]]:
    """
    Executes a structured JSON call to Gemini with model fallback.
    """
    from google.genai import types
    
    client = get_gemini_client()
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=system_instruction
    )
    
    last_err = None
    for model_name in CANDIDATE_MODELS:
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            if resp and resp.text:
                raw_text = resp.text.strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[1]
                    if raw_text.endswith("```"):
                        raw_text = raw_text.rsplit("```", 1)[0].strip()
                return json.loads(raw_text, strict=False)
        except Exception as e:
            logger.warning(f"Gemini model {model_name} failed: {e}. Trying next candidate...")
            last_err = e
            continue
            
    logger.error(f"All Gemini models exhausted. Last error: {last_err}")
    return None

def real_time_leaf_diagnosis(image_path: str, user_crop: str = "Tomato") -> Dict[str, Any]:
    """
    Real-Time Multimodal Plant Pathology Diagnosis using Google Gemini.
    Returns leaf validation, crop identification, pathogen detection, severity estimation,
    symptoms in Hindi/English, and ICAR/CIBRC verified treatments.
    """
    try:
        with Image.open(image_path) as img:
            rgb_img = img.convert("RGB")
            
            prompt = f"""You are an elite ICAR Plant Pathologist and Agronomist in India.
Analyze this agricultural photo in high detail.
Context Crop: {user_crop or 'Unknown'}

STEP 1: OUT-OF-DISTRIBUTION (OOD) VERIFICATION
- Is this a genuine plant leaf, crop foliage, or plant tissue?
- If the image depicts a human hand, face, random indoor object, pet, vehicle, bare ground with no leaves, or blank image:
  Set "is_leaf": false
  Set "leaf_validation_score": 0.0 to 0.4
  Set "rejection_reason": A polite, constructive explanation in English and Hindi telling the farmer how to take a proper photo of a leaf.
  Leave remaining diagnostic fields null.

STEP 2: PATHOLOGY & SYMPTOMATOLOGY (If is_leaf is true)
- Identify the exact Crop (e.g. Tomato, Potato, Wheat, Cotton, Rice, Mustard, Chili, etc.).
- Identify the Disease / Disorder name (e.g. Early Blight, Late Blight, Yellow Rust, Leaf Curl, Bacterial Canker, Powdery Mildew, or Abiotic Chlorosis/Nutrient Deficiency).
- Set "is_abiotic": true if it is nutrient deficiency (Potassium, Nitrogen, Iron chlorosis), water stress, or sunburn; false if infectious pathogen or pest.
- Estimate severity level: "mild" (<10% area), "moderate" (10-30% area), or "severe" (>30% area).
- Estimate "severity_pct" (1.0 to 100.0) representing localized leaf spot area.
- Calibrate confidence score (0.50 to 0.99).
- Provide detailed symptoms in English and Hindi.
- Provide actionable ICAR-grounded treatments:
  1. Organic / Bio-control (e.g. Trichoderma, Neem oil, Pseudomonas)
  2. Cultural / Sanitation (e.g. staking, pruning lower leaves, drip irrigation)
  3. Chemical: MUST state Indian CIBRC registration status (e.g. 'CIBRC Approved' or Registration number) and Pre-Harvest Interval (PHI in days). If disease is abiotic, prescribe micronutrient foliar spray (e.g. 13-0-45 or Zinc sulphate) rather than unnecessary fungicide.

Return strictly valid JSON with this exact schema:
{{
  "is_leaf": true,
  "leaf_validation_score": 0.98,
  "rejection_reason": null,
  "crop": "Tomato",
  "crop_hi": "टमाटर",
  "disease_name": "Tomato Early Blight",
  "disease_name_hi": "टमाटर का अगेती झुलसा",
  "scientific_name": "Alternaria solani",
  "is_abiotic": false,
  "severity": "moderate",
  "severity_pct": 24.5,
  "confidence": 0.94,
  "symptoms_en": "...",
  "symptoms_hi": "...",
  "treatments": [
    {{
      "type": "organic",
      "title_en": "...",
      "title_hi": "...",
      "instructions_en": "...",
      "instructions_hi": "...",
      "dosage": "...",
      "safety_notes_en": "...",
      "safety_notes_hi": "...",
      "cibrc_status": "Bio-formulation Approved",
      "pre_harvest_interval_days": 1
    }},
    {{
      "type": "cultural",
      "title_en": "...",
      "title_hi": "...",
      "instructions_en": "...",
      "instructions_hi": "...",
      "dosage": null,
      "safety_notes_en": null,
      "safety_notes_hi": null,
      "cibrc_status": null,
      "pre_harvest_interval_days": null
    }},
    {{
      "type": "chemical",
      "title_en": "Mancozeb 75% WP",
      "title_hi": "मैनकोज़ेब 75% डब्ल्यूपी",
      "instructions_en": "...",
      "instructions_hi": "...",
      "dosage": "2.0-2.5 g / L water",
      "safety_notes_en": "Wear mask and gloves. Avoid water contamination.",
      "safety_notes_hi": "दस्ताने व मास्क पहनें।",
      "cibrc_status": "CIBRC Reg. CIR-2918",
      "pre_harvest_interval_days": 7
    }}
  ]
}}
"""
            result = call_gemini_json([rgb_img, prompt])
            if result:
                return result
    except Exception as e:
        logger.error(f"Gemini leaf diagnosis error: {e}")
        
    return None

def real_time_voice_sos(transcript: str, language: str = "hi") -> Dict[str, Any]:
    """
    Real-Time Conversational Agronomist Assistant using Google Gemini.
    Processes farmer voice queries in Hindi, English, Hinglish, Marathi, etc.
    """
    prompt = f"""You are 'Kisan Mitra', an expert KVK agronomist speaking directly to an Indian farmer.
The farmer has spoken or submitted this problem description:
"{transcript}"

Language requested for spoken & primary text: {"Hindi (हिन्दी)" if language == "hi" else "English"}

Tasks:
1. Extract the crop mentioned (or infer from symptoms if not explicitly stated).
2. Extract the physical symptoms mentioned.
3. Determine 2-3 most likely candidate diseases or pest infestations.
4. Formulate 2-3 essential follow-up questions to ask the farmer to narrow down the diagnosis.
5. Write a warm, compassionate, spoken voice reply (2-3 concise spoken sentences, ideal for text-to-speech audio playback in {language}).
6. Write a structured, practical text reply with bullet points for immediate farmer actions, organic home remedy, and recommended spray.

Return strictly valid JSON:
{{
  "extracted_crop": "Tomato",
  "extracted_symptoms": ["काले छल्लेदार धब्बे", "निचली पत्तियां सूखना"],
  "candidate_diseases": ["Tomato Early Blight", "Septoria Leaf Spot", "Target Spot"],
  "followup_questions": [
    "क्या यह धब्बे केवल निचली पुरानी पत्तियों पर हैं या नई पत्तियों पर भी?",
    "क्या पत्ती के पीछे कोई सफेद या धूसर फफूंद दिखाई दे रही है?"
  ],
  "spoken_reply": "नमस्ते किसान भाई! आपके टमाटर में अगेती झुलसा के लक्षण दिख रहे हैं। प्रभावित पत्तियों को तुरंत तोड़कर नष्ट करें और नीम तेल या मैनकोजेब का छिड़काव करें।",
  "text_reply": "नमस्ते किसान भाई!\n\nलक्षणों के आधार पर आपके टमाटर में अगेती झुलसा (Early Blight) का प्रकोप हो सकता है।\n\nतत्काल उपाय:\n1. रोगग्रस्त पत्तियों को तोड़कर खेत से दूर जमीन में गाड़ दें।\n2. नीम का तेल (10,000 ppm) 3 मिली प्रति लीटर पानी में मिलाकर छिड़कें।\n3. रोग अधिक होने पर मैनकोज़ेब 75% WP (2.5 ग्राम/लीटर) का छिड़काव करें।\n4. सटीक जांच के लिए ऐप में 'कैमरा स्कैन' का उपयोग करें।"
}}
"""
    result = call_gemini_json([prompt])
    if result:
        return result
        
    return None

def real_time_weather_risk(crop: str, growth_stage: str, temp: float, humidity: float, rainfall: float) -> Dict[str, Any]:
    """
    Real-Time Epidemiological Weather Risk Calculation using Google Gemini.
    """
    prompt = f"""You are an agricultural epidemiologist for Indian agro-climatic zones.
Calculate the microclimate disease infection risk for:
- Crop: {crop}
- Growth Stage: {growth_stage}
- Ambient Temperature: {temp}°C
- Relative Humidity: {humidity}%
- Rainfall / Precipitation: {rainfall} mm

Analyze how these atmospheric conditions favor fungal sporulation, bacterial blight multiplication, or insect pest outbreaks.
Return strictly valid JSON:
{{
  "risk_score": 78,
  "risk_level": "high",
  "threat_pathogen": "Late Blight (Phytophthora infestans) & Early Blight",
  "contributing_factors": [
    {{"factor": "High Relative Humidity (88%)", "weight": "42%", "impact": "Favors rapid fungal spore germination"}},
    {{"factor": "Optimal Temperature (24°C)", "weight": "35%", "impact": "Ideal incubation temperature range"}},
    {{"factor": "Rain Splash / Leaf Wetness", "weight": "23%", "impact": "Disperses inoculum across adjacent plants"}}
  ],
  "preventive_actions": [
    "Avoid overhead sprinkler irrigation; switch to drip to minimize leaf wetness duration.",
    "Apply protective preventive spray of Copper Oxychloride 50% WP (2.5g/L) before continuous rain.",
    "Improve canopy aeration by pruning lower lateral suckers."
  ],
  "reasoning": "High humidity above 85% paired with moderate temperatures creates critical epidemiological conditions for foliar blights within 48 hours."
}}
"""
    result = call_gemini_json([prompt])
    if result:
        return result
        
    return None

def real_time_second_opinion(initial_crop: str, initial_disease: str, symptoms_checked: list, crop_stage: str = "fruiting", underside_notes: str = None) -> Dict[str, Any]:
    """
    Evaluates second-opinion consultation using Google Gemini.
    """
    prompt = f"""You are an agricultural diagnostic specialist conducting an AI Second Opinion review.
Initial Suspected Diagnosis: {initial_disease} on {initial_crop}
Crop Stage: {crop_stage}
Farmer Confirmed Symptoms: {', '.join(symptoms_checked)}
Underside Leaf Observations: {underside_notes or 'Faint yellowish halo, dry brittle center, no active mold'}

Re-evaluate the differential diagnosis candidates. Rescore each candidate from 0.0 to 1.0 calibrated probability.
Return strictly valid JSON:
{{
  "outcome": "confirmed" or "revised" or "still_uncertain",
  "top_disease": "Tomato Early Blight",
  "top_confidence": 0.89,
  "clinical_notes": "Concentric rings confirmed on upper blade without sporulating downy mildew on underside definitively rules out Late Blight in favor of Alternaria solani.",
  "recommended_action": "Proceed with targeted Early Blight IPM treatment plan."
}}
"""
    result = call_gemini_json([prompt])
    if result:
        return result
        
    return None

def real_time_expert_reply(farmer_name: str, crop: str, symptoms: str, severity: str) -> Dict[str, Any]:
    """
    Generates an expert KVK reply for an escalated ticket.
    """
    prompt = f"""You are Dr. Sunita Sharma, Senior Plant Pathologist at Krishi Vigyan Kendra (KVK).
A farmer named {farmer_name} escalated an emergency crop ticket:
- Crop: {crop}
- Symptoms: {symptoms}
- Severity Level: {severity}

Write a professional, compassionate, and precise agronomic consultation reply in Hindi and English with specific ICAR dosage recommendations and safety advice.
Return strictly valid JSON:
{{
  "expert_reply_hi": "प्रिय किसान भाई, आपके द्वारा भेजे गए विवरण का विश्लेषण करने के बाद...",
  "expert_reply_en": "Dear Farmer, upon clinical review of your crop symptoms...",
  "diagnosis_confirmed": "Early Blight with secondary bacterial leaf spot",
  "urgency": "High - Spray within 24 hours"
}}
"""
    result = call_gemini_json([prompt])
    if result:
        return result
        
    return None
