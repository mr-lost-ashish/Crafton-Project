from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# --- Auth Schemas ---
class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    district: Optional[str] = None
    state: Optional[str] = None

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None # hi, en
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    district: Optional[str] = None
    state: Optional[str] = None
    share_scans: Optional[bool] = None

# --- Crop & Disease Schemas ---
class TreatmentOut(BaseModel):
    id: str
    disease_id: str
    type: str # organic, chemical, preventive, cultural
    min_severity: str
    title: str
    instructions: str
    active_ingredient: Optional[str] = None
    dosage: Optional[str] = None
    timing: Optional[str] = None
    pre_harvest_interval_days: Optional[int] = None
    max_applications_per_season: Optional[int] = None
    safety_notes: Optional[str] = None
    source_name: str
    source_url: Optional[str] = None

class DiseaseOut(BaseModel):
    id: str
    crop_id: Optional[str] = None
    model_label: str
    category: str
    scientific_name: Optional[str] = None
    name: str
    symptoms: Optional[str] = None
    reference_image_url: Optional[str] = None
    treatments: Optional[List[TreatmentOut]] = []

class CropOut(BaseModel):
    id: str
    code: str
    name: str
    icon_url: Optional[str] = None

# --- Field Schemas ---
class FieldCreate(BaseModel):
    crop_id: str
    name: str
    variety: Optional[str] = None
    area_acres: Optional[float] = 1.0
    sowing_date: date
    latitude: float
    longitude: float

class FieldOut(BaseModel):
    id: str
    user_id: str
    crop_id: str
    crop_name: Optional[str] = None
    crop_code: Optional[str] = None
    name: str
    variety: Optional[str] = None
    area_acres: Optional[float] = None
    sowing_date: date
    latitude: float
    longitude: float
    status: str
    created_at: datetime

# --- Scan & Diagnosis Schemas ---
class PredictionItem(BaseModel):
    disease_id: str
    disease_name: str
    confidence: float
    category: str

class ScanDiagnosisResponse(BaseModel):
    scan_id: str
    field_id: str
    image_url: str
    result_status: str # confident, uncertain, escalated
    top_disease: Optional[str] = None
    top_confidence: float
    severity: str # mild, moderate, severe
    severity_pct: float
    predictions: List[PredictionItem]
    treatments: List[TreatmentOut]
    followup_reminder: Optional[str] = None
    requires_second_opinion: bool = False

class ScanFeedback(BaseModel):
    user_feedback: str # correct, incorrect, unsure
    confirmed_disease_id: Optional[str] = None
    notes: Optional[str] = None

class SecondOpinionRequest(BaseModel):
    leaf_underside_url: Optional[str] = None
    growth_stage: Optional[str] = None
    symptoms_reported: List[str] = [] # yellowing, spots, curling, insects
    answers: Optional[Dict[str, Any]] = None

class SecondOpinionResponse(BaseModel):
    session_id: str
    scan_id: str
    rescored_predictions: List[PredictionItem]
    final_confidence: float
    outcome: str # resolved, still_uncertain, escalated
    recommended_disease: Optional[DiseaseOut] = None
    recommend_expert_verification: bool = False
    message: str

# --- Treatment Plan Schemas ---
class PlanStepOut(BaseModel):
    id: str
    step_order: int
    phase: str
    description: str
    due_on: Optional[date] = None
    estimated_cost_inr: float
    requires_expert: bool
    done_at: Optional[datetime] = None
    treatment_id: Optional[str] = None

class TreatmentPlanOut(BaseModel):
    id: str
    field_id: str
    scan_id: str
    status: str
    estimated_cost_inr: float
    actual_cost_inr: float
    steps: List[PlanStepOut]

# --- Spray / Treatment Log Schemas ---
class TreatmentLogCreate(BaseModel):
    scan_id: Optional[str] = None
    treatment_id: Optional[str] = None
    product_name: str
    active_ingredient: Optional[str] = None
    dose_applied: Optional[str] = None
    applied_on: date
    cost_inr: Optional[float] = 0.0
    followup_due_on: Optional[date] = None
    notes: Optional[str] = None

# --- What-If Simulator & Risk Schemas ---
class WhatIfRequest(BaseModel):
    temperature_c: float
    humidity_pct: float
    rainfall_mm: float
    crop_stage_days: Optional[int] = 35

class ContributingFactor(BaseModel):
    factor: str
    impact: str
    weight: str

class RiskAssessmentOut(BaseModel):
    id: Optional[str] = None
    field_id: str
    disease_name: str
    score: int
    level: str # low, medium, high
    factors: List[ContributingFactor]
    is_what_if: bool
    disclaimer: str = "Risk estimate, not a diagnosis"

# --- Outbreak & Radar Schemas ---
class RiskZoneOut(BaseModel):
    id: str
    disease_id: str
    disease_name: str
    crop_id: str
    crop_name: str
    center_lat: float
    center_lng: float
    radius_km: float
    risk_level: str # green, amber, red
    confirmed_count: int
    suspected_count: int
    trend: str # rising, steady, falling
    is_synthetic: bool

class OutbreakPoint(BaseModel):
    id: str
    disease_name: str
    crop_name: str
    latitude: float
    longitude: float
    report_status: str # confirmed, suspected
    severity: str
    captured_at: datetime
    is_synthetic: bool

class RadarResponse(BaseModel):
    zones: List[RiskZoneOut]
    points: List[OutbreakPoint]
    active_alerts: int

# --- Village Simulation (F23) ---
class VillageSimulationRequest(BaseModel):
    village_name: str
    center_lat: float
    center_lng: float
    crop_id: str
    disease_id: str
    intensity: Optional[int] = 5

# --- Loss Calculator (F24) ---
class LossScenarioRequest(BaseModel):
    crop_value_inr: float
    treatment_cost_inr: float
    loss_pct_if_early: float
    loss_pct_if_delayed: float
    delay_days: int

class LossScenarioResponse(BaseModel):
    crop_value_inr: float
    treatment_cost_inr: float
    early_loss_inr: float
    delayed_loss_inr: float
    estimated_difference_inr: float
    disclaimer: str = "Estimate, not a guaranteed saving"

# --- Voice SOS (F18) ---
class VoiceSOSRequest(BaseModel):
    language: str = "hi"
    audio_base64: Optional[str] = None
    transcript: Optional[str] = None
    field_id: Optional[str] = None

class VoiceSOSResponse(BaseModel):
    report_id: str
    transcript: str
    extracted_crop: Optional[str] = None
    extracted_symptoms: List[str] = []
    followup_questions: List[str] = []
    spoken_reply: str
    text_reply: str
    candidate_diseases: List[str] = []

# --- Community Rescue (F20) ---
class CommunityReportCreate(BaseModel):
    field_id: Optional[str] = None
    scan_id: Optional[str] = None
    symptoms_text: str

class CommunitySolutionCreate(BaseModel):
    body: str
    treatment_id: Optional[str] = None
