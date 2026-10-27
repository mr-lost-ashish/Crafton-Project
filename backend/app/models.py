import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, DateTime, Date, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from .database import Base

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    # DPDP Act 2023: Blind lookup hash for fast auth + encrypted phone for SMS delivery
    phone_lookup_hash = Column(String(128), unique=True, nullable=False)
    encrypted_phone = Column(Text, nullable=True)
    name = Column(String(128), nullable=True)
    role = Column(String(32), default="farmer", nullable=False) # farmer, expert, admin
    language = Column(String(8), default="hi", nullable=False) # hi, en, mr, pa
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    district = Column(String(64), nullable=True)
    state = Column(String(64), nullable=True)
    share_scans = Column(Boolean, default=True, nullable=False)
    push_token = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    fields = relationship("Field", back_populates="user", cascade="all, delete-orphan")
    scans = relationship("Scan", back_populates="user", foreign_keys="Scan.user_id")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    expert_profile = relationship("ExpertProfile", back_populates="user", uselist=False)
    consent_logs = relationship("UserConsentLog", back_populates="user", cascade="all, delete-orphan")

class UserConsentLog(Base):
    """DPDP Act (2023) Compliance: Explicit consent tracking & data governance"""
    __tablename__ = "user_consent_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    consent_type = Column(String(64), nullable=False) # 'anonymized_map_sharing', 'telemetry_processing', 'push_alerts'
    granted = Column(Boolean, default=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=True)

    user = relationship("User", back_populates="consent_logs")

class ExpertProfile(Base):
    __tablename__ = "expert_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    organization = Column(String(128), nullable=True) # e.g. ICAR Krishi Vigyan Kendra
    specialization = Column(JSON, nullable=True)
    regions_covered = Column(JSON, nullable=True)

    user = relationship("User", back_populates="expert_profile")

class Crop(Base):
    __tablename__ = "crops"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    code = Column(String(64), unique=True, nullable=False) # tomato, potato, wheat, cotton
    name_en = Column(String(128), nullable=False)
    name_hi = Column(String(128), nullable=True)
    icon_url = Column(String(256), nullable=True)

    stages = relationship("CropStage", back_populates="crop", cascade="all, delete-orphan")
    diseases = relationship("Disease", back_populates="crop")

class CropStage(Base):
    __tablename__ = "crop_stages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    stage_name = Column(String(64), nullable=False)
    start_day = Column(Integer, nullable=False)
    end_day = Column(Integer, nullable=False)
    scan_interval_days = Column(Integer, default=7)

    crop = relationship("Crop", back_populates="stages")

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=True)
    model_label = Column(String(128), unique=True, nullable=False)
    category = Column(String(32), nullable=False) # fungal, bacterial, viral, pest, nutrient_abiotic, healthy
    scientific_name = Column(String(128), nullable=True)
    name_en = Column(String(128), nullable=False)
    name_hi = Column(String(128), nullable=True)
    symptoms_en = Column(Text, nullable=True)
    symptoms_hi = Column(Text, nullable=True)
    reference_image_url = Column(String(256), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    crop = relationship("Crop", back_populates="diseases")
    treatments = relationship("Treatment", back_populates="disease", cascade="all, delete-orphan")

class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    disease_id = Column(String(36), ForeignKey("diseases.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(32), nullable=False) # organic, chemical, cultural, preventive
    min_severity = Column(String(32), default="mild", nullable=False)
    title_en = Column(String(256), nullable=False)
    title_hi = Column(String(256), nullable=True)
    instructions_en = Column(Text, nullable=False)
    instructions_hi = Column(Text, nullable=True)
    active_ingredient = Column(String(128), nullable=True)
    dosage = Column(String(128), nullable=True)
    timing = Column(String(128), nullable=True)
    pre_harvest_interval_days = Column(Integer, nullable=True)
    max_applications_per_season = Column(Integer, nullable=True)
    safety_notes_en = Column(Text, nullable=True)
    safety_notes_hi = Column(Text, nullable=True)
    # India Pesticide Safety & CIBRC Compliance
    cibrc_status = Column(String(64), default="CIBRC Approved for target crop", nullable=False)
    is_banned_in_india = Column(Boolean, default=False, nullable=False)
    source_name = Column(String(128), nullable=False) # e.g. ICAR-IIHR, MPKV Rahuri
    source_url = Column(String(256), nullable=True)
    reviewed_by = Column(String(128), default="ICAR Agronomy Panel", nullable=True)
    last_reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    disease = relationship("Disease", back_populates="treatments")

class Field(Base):
    __tablename__ = "fields"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    name = Column(String(128), nullable=False)
    variety = Column(String(128), nullable=True)
    area_acres = Column(Float, nullable=True)
    sowing_date = Column(Date, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    boundary = Column(JSON, nullable=True)
    status = Column(String(32), default="healthy", nullable=False) # healthy, watch, infected, recovering
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="fields")
    crop = relationship("Crop")
    scans = relationship("Scan", back_populates="field", cascade="all, delete-orphan")
    treatment_logs = relationship("TreatmentLog", back_populates="field", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="field", cascade="all, delete-orphan")

class Scan(Base):
    """
    Consolidated Single-State Scan Model:
    Avoids drifting status fields by using a single lifecycle state:
    - 'suspected': AI inference result (not verified)
    - 'second_opinion_pending': AI confidence low, additional data requested
    - 'escalated': sent to KVK extension specialist
    - 'farmer_verified': confirmed by grower in field
    - 'expert_verified': certified by agronomist (only these trigger community radar alerts)
    - 'rejected': false detection / rejected
    """
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    image_url = Column(String(256), nullable=False)
    captured_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source = Column(String(32), default="server", nullable=False)
    model_version = Column(String(32), default="v1.1-calibrated-leaf-net", nullable=True)
    top_disease_id = Column(String(36), ForeignKey("diseases.id"), nullable=True)
    raw_confidence = Column(Float, nullable=True)
    calibrated_confidence = Column(Float, nullable=True) # Temperature scaled
    severity = Column(String(32), nullable=True) # mild, moderate, severe
    severity_pct = Column(Float, nullable=True)
    is_leaf_valid = Column(Boolean, default=True, nullable=False) # Out-of-distribution gatekeeper
    leaf_validation_score = Column(Float, default=1.0, nullable=False)
    # Unified State Machine
    lifecycle_status = Column(String(32), default="suspected", nullable=False)
    user_confirmed_disease_id = Column(String(36), ForeignKey("diseases.id"), nullable=True)
    expert_verified_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    expert_verified_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    field = relationship("Field", back_populates="scans")
    user = relationship("User", back_populates="scans", foreign_keys=[user_id])
    expert_verifier = relationship("User", foreign_keys=[expert_verified_by])
    top_disease = relationship("Disease", foreign_keys=[top_disease_id])
    user_confirmed_disease = relationship("Disease", foreign_keys=[user_confirmed_disease_id])
    predictions = relationship("ScanPrediction", back_populates="scan", cascade="all, delete-orphan")

class ScanPrediction(Base):
    __tablename__ = "scan_predictions"

    scan_id = Column(String(36), ForeignKey("scans.id", ondelete="CASCADE"), primary_key=True)
    rank = Column(Integer, primary_key=True)
    disease_id = Column(String(36), ForeignKey("diseases.id"), nullable=False)
    confidence = Column(Float, nullable=False)

    scan = relationship("Scan", back_populates="predictions")
    disease = relationship("Disease")

class TreatmentLog(Base):
    __tablename__ = "treatment_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=True)
    treatment_id = Column(String(36), ForeignKey("treatments.id"), nullable=True)
    product_name = Column(String(128), nullable=True)
    active_ingredient = Column(String(128), nullable=True)
    dose_applied = Column(String(128), nullable=True)
    applied_on = Column(Date, nullable=False)
    cost_inr = Column(Float, nullable=True)
    followup_due_on = Column(Date, nullable=True)
    outcome = Column(String(32), default="pending", nullable=True)
    notes = Column(Text, nullable=True)

    field = relationship("Field", back_populates="treatment_logs")
    treatment = relationship("Treatment")

class WeatherSnapshot(Base):
    """Weather records snapped to 0.05 deg grid (approx 5 km) to eliminate coordinate drift duplicates"""
    __tablename__ = "weather_snapshots"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    grid_lat = Column(Float, nullable=False)
    grid_lng = Column(Float, nullable=False)
    observed_for = Column(Date, nullable=False)
    is_forecast = Column(Boolean, default=False, nullable=False)
    temp_min_c = Column(Float, nullable=True)
    temp_max_c = Column(Float, nullable=True)
    humidity_avg = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    leaf_wetness_hrs = Column(Float, nullable=True)

class OutbreakEvent(Base):
    """
    Unified Single Source of Truth for Outbreaks & Radar:
    Requires at least 3 distinct confirmed cases before escalating to an Amber/Red outbreak alert.
    """
    __tablename__ = "outbreak_events"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    disease_id = Column(String(36), ForeignKey("diseases.id"), nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_km = Column(Float, default=12.0, nullable=False)
    confirmed_count = Column(Integer, default=0, nullable=False)
    suspected_count = Column(Integer, default=0, nullable=False)
    min_cluster_threshold = Column(Integer, default=3, nullable=False)
    trend = Column(String(32), default="rising", nullable=True)
    risk_level = Column(String(32), default="amber", nullable=True) # green, amber, red
    first_reported = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_reported = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_synthetic = Column(Boolean, default=False, nullable=False)

    disease = relationship("Disease")
    crop = relationship("Crop")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(32), nullable=False) # weather_risk, outbreak, followup, reminder
    outbreak_id = Column(String(36), ForeignKey("outbreak_events.id"), nullable=True)
    severity = Column(String(32), default="warning", nullable=True) # info, warning, critical
    title = Column(String(256), nullable=False)
    body = Column(Text, nullable=False)
    language = Column(String(8), default="hi", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)
    action_taken = Column(Boolean, default=False, nullable=True)

    user = relationship("User", back_populates="alerts")
    field = relationship("Field", back_populates="alerts")

class ExpertTicket(Base):
    __tablename__ = "expert_tickets"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    scan_id = Column(String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    farmer_note = Column(Text, nullable=True)
    status = Column(String(32), default="open", nullable=False) # open, answered, closed
    expert_diagnosis_id = Column(String(36), ForeignKey("diseases.id"), nullable=True)
    expert_reply = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    answered_at = Column(DateTime, nullable=True)

    scan = relationship("Scan")
    requester = relationship("User", foreign_keys=[requested_by])
    expert = relationship("User", foreign_keys=[assigned_to])
    expert_diagnosis = relationship("Disease", foreign_keys=[expert_diagnosis_id])

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(128), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String(256), nullable=True)
    phone = Column(String(32), nullable=True)
    is_mock = Column(Boolean, default=True, nullable=False)

    products = relationship("SupplierProduct", back_populates="supplier", cascade="all, delete-orphan")

class SupplierProduct(Base):
    __tablename__ = "supplier_products"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    supplier_id = Column(String(36), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    treatment_id = Column(String(36), ForeignKey("treatments.id"), nullable=True)
    product_name = Column(String(128), nullable=False)
    price_inr = Column(Float, nullable=True)
    in_stock = Column(Boolean, default=True, nullable=True)

    supplier = relationship("Supplier", back_populates="products")

class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False)
    status = Column(String(32), default="active", nullable=False)
    estimated_cost_inr = Column(Float, default=0.0, nullable=True)
    actual_cost_inr = Column(Float, default=0.0, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    steps = relationship("TreatmentPlanStep", back_populates="plan", cascade="all, delete-orphan")

class TreatmentPlanStep(Base):
    __tablename__ = "treatment_plan_steps"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    plan_id = Column(String(36), ForeignKey("treatment_plans.id", ondelete="CASCADE"), nullable=False)
    step_order = Column(Integer, nullable=False)
    phase = Column(String(32), nullable=False)
    treatment_id = Column(String(36), ForeignKey("treatments.id"), nullable=True)
    description = Column(Text, nullable=False)
    due_on = Column(Date, nullable=True)
    estimated_cost_inr = Column(Float, default=0.0, nullable=True)
    requires_expert = Column(Boolean, default=False, nullable=False)
    done_at = Column(DateTime, nullable=True)

    plan = relationship("TreatmentPlan", back_populates="steps")
    treatment = relationship("Treatment")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    soil_moisture_pct = Column(Float, nullable=True)
    leaf_wetness_pct = Column(Float, nullable=True)
    air_temp_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    is_simulated = Column(Boolean, default=True, nullable=False)

class DroneSurvey(Base):
    __tablename__ = "drone_surveys"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    surveyed_on = Column(Date, nullable=False)
    image_url = Column(String(256), nullable=False)
    ndvi_overlay_url = Column(String(256), nullable=True)
    flagged_zones = Column(JSON, nullable=True)
    is_simulated = Column(Boolean, default=True, nullable=False)

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    disease_id = Column(String(36), ForeignKey("diseases.id"), nullable=False)
    score = Column(Integer, nullable=False)
    level = Column(String(32), nullable=False)
    factors = Column(JSON, nullable=False)
    inputs_snapshot = Column(JSON, nullable=True)
    is_what_if = Column(Boolean, default=False, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    disease = relationship("Disease")

class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    kind = Column(String(32), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    parameters = Column(JSON, nullable=False)
    results = Column(JSON, nullable=True)
    is_simulated = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class LossScenario(Base):
    __tablename__ = "loss_scenarios"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_value_inr = Column(Float, nullable=False)
    treatment_cost_inr = Column(Float, nullable=False)
    loss_pct_if_early = Column(Float, nullable=False)
    loss_pct_if_delayed = Column(Float, nullable=False)
    delay_days = Column(Integer, nullable=False)
    estimated_difference_inr = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CommunityReport(Base):
    __tablename__ = "community_reports"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=True)
    symptoms_text = Column(Text, nullable=True)
    status = Column(String(32), default="open", nullable=False)
    verified_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_simulated = Column(Boolean, default=False, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    scan = relationship("Scan")
    verifier = relationship("User", foreign_keys=[verified_by])
    solutions = relationship("CommunitySolution", back_populates="report", cascade="all, delete-orphan")

class CommunitySolution(Base):
    __tablename__ = "community_solutions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    report_id = Column(String(36), ForeignKey("community_reports.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    treatment_id = Column(String(36), ForeignKey("treatments.id"), nullable=True)
    is_expert_verified = Column(Boolean, default=False, nullable=False)
    improved_count = Column(Integer, default=0, nullable=False)
    no_change_count = Column(Integer, default=0, nullable=False)
    worse_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    report = relationship("CommunityReport", back_populates="solutions")
    author = relationship("User")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    field_id = Column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    reminder_type = Column(String(32), nullable=False)
    due_on = Column(Date, nullable=False)
    status = Column(String(32), default="pending", nullable=False)


class VoiceReport(Base):
    __tablename__ = "voice_reports"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String(36), ForeignKey("fields.id"), nullable=True)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=True)
    language = Column(String(8), default="hi", nullable=False)
    audio_url = Column(String(256), nullable=True)
    transcript = Column(Text, nullable=True)
    extracted = Column(JSON, nullable=True)
    followups = Column(JSON, nullable=True)
    sync_status = Column(String(32), default="synced", nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=True)
