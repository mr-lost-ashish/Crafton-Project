import hashlib
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from .models import (
    User, ExpertProfile, Crop, CropStage, Disease, Treatment, Field, Scan, ScanPrediction,
    TreatmentLog, WeatherSnapshot, OutbreakEvent, Alert, Supplier, SupplierProduct
)

SALT = "CropGuard_India_DPDP_Salt_2026"

def hash_phone(phone: str) -> str:
    return hashlib.sha256((phone.strip() + SALT).encode("utf-8")).hexdigest()

def seed_database(db: Session):
    if db.query(Crop).first():
        return

    print("Seeding CropGuard database with hardened agronomic reference data...")

    # 1. USERS (DPDP Act 2023 Compliant)
    farmer = User(
        phone_lookup_hash=hash_phone("9876543210"),
        encrypted_phone="ENC:3210",
        name="Ramesh Patel",
        role="farmer",
        language="hi",
        latitude=19.9975,
        longitude=73.7898,
        district="Nashik",
        state="Maharashtra",
        share_scans=True
    )
    db.add(farmer)
    db.flush()

    expert = User(
        phone_lookup_hash=hash_phone("9123456789"),
        encrypted_phone="ENC:6789",
        name="Dr. Sunita Sharma",
        role="expert",
        language="en",
        latitude=19.9850,
        longitude=73.7780,
        district="Nashik",
        state="Maharashtra"
    )
    db.add(expert)
    db.flush()

    expert_profile = ExpertProfile(
        user_id=expert.id,
        organization="ICAR - Krishi Vigyan Kendra (KVK, Nashik)",
        specialization=["Plant Pathology", "Horticultural Crops", "CIBRC Compliance"],
        regions_covered=["Nashik", "Pune", "Ahmednagar"]
    )
    db.add(expert_profile)

    # 2. CROPS
    tomato = Crop(code="tomato", name_en="Tomato", name_hi="टमाटर", icon_url="/static/icons/tomato.svg")
    potato = Crop(code="potato", name_en="Potato", name_hi="आलू", icon_url="/static/icons/potato.svg")
    cotton = Crop(code="cotton", name_en="Cotton", name_hi="कपास", icon_url="/static/icons/cotton.svg")
    wheat = Crop(code="wheat", name_en="Wheat", name_hi="गेहूं", icon_url="/static/icons/wheat.svg")
    db.add_all([tomato, potato, cotton, wheat])
    db.flush()

    stages = [
        CropStage(crop_id=tomato.id, stage_name="Seedling / नर्सरी", start_day=0, end_day=20, scan_interval_days=5),
        CropStage(crop_id=tomato.id, stage_name="Vegetative / वानस्पतिक", start_day=21, end_day=45, scan_interval_days=7),
        CropStage(crop_id=tomato.id, stage_name="Flowering / फूल आना", start_day=46, end_day=70, scan_interval_days=5),
        CropStage(crop_id=tomato.id, stage_name="Fruiting & Harvest / फलन", start_day=71, end_day=120, scan_interval_days=7),
    ]
    db.add_all(stages)

    # 3. DISEASES (Includes Abiotic / Nutrient Disorders to handle look-alikes!)
    d_early_blight = Disease(
        crop_id=tomato.id,
        model_label="tomato_early_blight",
        category="fungal",
        scientific_name="Alternaria solani",
        name_en="Tomato Early Blight",
        name_hi="टमाटर अगेती झुलसा",
        symptoms_en="Concentric dark brown target-like rings on older leaves, surrounded by yellow chlorotic halo. Causes premature leaf fall.",
        symptoms_hi="पुरानी निचली पत्तियों पर काले-भूरे रंग के गोल छल्लेदार धब्बे, जिसके चारों ओर पीलापन दिखाई देता है।",
        reference_image_url="/sample_images/tomato_early_blight.jpg"
    )

    d_late_blight = Disease(
        crop_id=tomato.id,
        model_label="tomato_late_blight",
        category="fungal",
        scientific_name="Phytophthora infestans",
        name_en="Tomato Late Blight",
        name_hi="टमाटर पछेती झुलसा",
        symptoms_en="Large, irregular, water-soaked dark purplish lesions on leaves and stems. White downy fungal mold develops on leaf underside.",
        symptoms_hi="पत्तियों और तनों पर बड़े गहरे पानी जैसे भीगे धब्बे, तथा ठंडे व नम मौसम में पत्तियों की निचली सतह पर सफेद फफूंद जम जाती है।",
        reference_image_url="/sample_images/tomato_late_blight.jpg"
    )

    d_leaf_curl = Disease(
        crop_id=tomato.id,
        model_label="tomato_leaf_curl",
        category="viral",
        scientific_name="Tomato leaf curl New Delhi virus (ToLCNDV)",
        name_en="Tomato Leaf Curl Virus",
        name_hi="टमाटर पर्ण कुंचन रोग (मरोड़िया)",
        symptoms_en="Upward curling and crinkling of leaves, severe stunting of plants, yellowing between veins, transmitted by whiteflies.",
        symptoms_hi="पत्तियां ऊपर की ओर मुड़कर कटोरी जैसी हो जाती हैं, पौधे बौने रह जाते हैं और शिराओं के बीच पीलापन आ जाता है।",
        reference_image_url="/sample_images/tomato_leaf_curl.jpg"
    )

    # Abiotic look-alike (Nutrient Deficiency & Sunburn)
    d_abiotic_chlorosis = Disease(
        crop_id=tomato.id,
        model_label="nutrient_deficiency",
        category="nutrient_abiotic",
        scientific_name="Non-pathogenic / Physiological Disorder",
        name_en="Potassium/Nitrogen Chlorosis (Non-Infectious)",
        name_hi="पोषक तत्व की कमी (गैर-संक्रामक पीलापन)",
        symptoms_en="Interveinal chlorosis and marginal leaf scorch without fungal spores or concentric target rings. DO NOT spray chemical fungicides.",
        symptoms_hi="पत्तियों की शिराओं के बीच पीलापन और किनारों का सूखना। यह फफूंद रोग नहीं है, रासायनिक कीटनाशक का छिड़काव न करें।",
        reference_image_url="/sample_images/tomato_healthy.jpg"
    )

    d_healthy = Disease(
        crop_id=tomato.id,
        model_label="tomato_healthy",
        category="healthy",
        scientific_name="Solanum lycopersicum",
        name_en="Healthy Tomato Plant",
        name_hi="स्वस्थ टमाटर का पौधा",
        symptoms_en="Vibrant green leaves without discoloration, vigorous foliage.",
        symptoms_hi="स्वस्थ हरी पत्तियां, कोई रोग के लक्षण नहीं।",
        reference_image_url="/sample_images/tomato_healthy.jpg"
    )

    d_potato_late_blight = Disease(
        crop_id=potato.id,
        model_label="potato_late_blight",
        category="fungal",
        scientific_name="Phytophthora infestans",
        name_en="Potato Late Blight",
        name_hi="आलू पछेती झुलसा",
        symptoms_en="Water-soaked spots at leaf tips and margins spreading rapidly into brown-black necrotic tissue.",
        symptoms_hi="आलू की पत्तियों के किनारों पर गहरे पानी से भीगे धब्बे जो तेजी से भूरे-काले होकर सड़ने लगते हैं।",
        reference_image_url="/sample_images/potato_late_blight.jpg"
    )

    db.add_all([d_early_blight, d_late_blight, d_leaf_curl, d_abiotic_chlorosis, d_healthy, d_potato_late_blight])
    db.flush()

    # 4. TREATMENTS (With CIBRC India Registration Status and Safety Precaution Intervals)
    treatments = [
        # Early Blight Organic
        Treatment(
            disease_id=d_early_blight.id,
            type="organic",
            min_severity="mild",
            title_en="Neem Seed Kernel Extract (NSKE 5%) or Azadirachtin Spray",
            title_hi="नीम का काढ़ा (एनएसकेई 5%) या एजाडिराक्टिन 1500 पीपीएम का छिड़काव",
            instructions_en="Mix Azadirachtin 1500 ppm @ 3-4 ml per liter of water. Spray thoroughly on both sides of foliage in early morning.",
            instructions_hi="एजाडिराक्टिन 1500 पीपीएम 3-4 मिली प्रति लीटर पानी में मिलाकर पत्तियों के दोनों ओर सुबह या शाम छिड़कें।",
            active_ingredient="Azadirachtin 1500 ppm",
            dosage="3-4 ml / liter of water",
            timing="At first appearance of concentric spots on lower leaves",
            pre_harvest_interval_days=0,
            max_applications_per_season=4,
            safety_notes_en="Safe for non-target beneficial insects when sprayed outside bee foraging hours.",
            safety_notes_hi="मधुमक्खियों के लिए सुरक्षित। सुबह या शाम को छिड़कें।",
            cibrc_status="CIBRC Approved Bio-Pesticide (Schedule II)",
            is_banned_in_india=False,
            source_name="ICAR - Indian Institute of Horticultural Research (IIHR)",
            source_url="https://iihr.res.in",
            reviewed_by="Dr. S. K. Singh (ICAR Panel)",
            last_reviewed_at=datetime.utcnow()
        ),
        # Early Blight Cultural / Preventive
        Treatment(
            disease_id=d_early_blight.id,
            type="cultural",
            min_severity="mild",
            title_en="Lower Canopy Pruning & Drip Aeration",
            title_hi="निचली पत्तियों की छंटाई व ड्रिप सिंचाई",
            instructions_en="Prune off lower leaves touching the soil and destroy outside the field. Avoid overhead sprinkler wetting.",
            instructions_hi="जमीन को छूने वाली निचली पत्तियों को काटकर खेत से दूर नष्ट करें। ऊपर से पानी छिड़कने से बचें।",
            active_ingredient="Canopy Aeration & Hygiene",
            dosage="Manual operation",
            timing="Morning on sunny days",
            pre_harvest_interval_days=0,
            max_applications_per_season=10,
            safety_notes_en="Clean pruning shears in 5% bleach between rows.",
            safety_notes_hi="कैंची को साफ रखें।",
            cibrc_status="Cultural Sanitation (Good Agricultural Practice)",
            is_banned_in_india=False,
            source_name="ICAR-CISH Central Institute for Subtropical Horticulture",
            source_url="https://cish.icar.gov.in",
            reviewed_by="ICAR Agronomy Panel",
            last_reviewed_at=datetime.utcnow()
        ),
        # Early Blight Chemical
        Treatment(
            disease_id=d_early_blight.id,
            type="chemical",
            min_severity="moderate",
            title_en="Mancozeb 75% WP (Contact Fungicide)",
            title_hi="मैनकोजेब 75% डब्लूपी का छिड़काव",
            instructions_en="Dissolve Mancozeb 75% WP @ 2.5 g per liter of water (500 g in 200 L per acre). Ensure thorough coverage of lower canopy.",
            instructions_hi="मैनकोजेब 75% डब्लूपी 2.5 ग्राम प्रति लीटर पानी में घोलकर पौधे के निचले हिस्से पर अच्छी तरह छिड़कें।",
            active_ingredient="Mancozeb 75% WP",
            dosage="2.5 g / liter of water",
            timing="Repeat after 10-12 days if disease progression continues",
            pre_harvest_interval_days=7,
            max_applications_per_season=3,
            safety_notes_en="Wear chemical-resistant nitrile gloves, eye goggles and face mask. Observe mandatory 7-day pre-harvest waiting interval.",
            safety_notes_hi="दस्ताने और मास्क पहनें। तुड़ाई से कम से कम 7 दिन पहले छिड़काव बंद करें।",
            cibrc_status="CIBRC Approved for Tomato Early Blight (Reg No. CIR-2918)",
            is_banned_in_india=False,
            source_name="ICAR-IARI Package of Practices / Central Insecticides Board",
            source_url="http://cibrc.gov.in",
            reviewed_by="Dr. Sunita Sharma (KVK)",
            last_reviewed_at=datetime.utcnow()
        ),
        # Late Blight Chemical
        Treatment(
            disease_id=d_late_blight.id,
            type="chemical",
            min_severity="moderate",
            title_en="Metalaxyl-M 4% + Mancozeb 64% WP",
            title_hi="मेटालेक्सिल-एम 4% + मैनकोजेब 64% डब्लूपी",
            instructions_en="Mix Metalaxyl-M + Mancozeb @ 2.0 g per liter of water. Halts both internal mycelial spread and secondary spore germination.",
            instructions_hi="मेटालेक्सिल + मैनकोजेब 2.0 ग्राम प्रति लीटर पानी में मिलाकर तुरंत छिड़कें।",
            active_ingredient="Metalaxyl-M 4% + Mancozeb 64% WP",
            dosage="2.0 g / liter of water",
            timing="Immediate intervention at first detection of water-soaked lesions",
            pre_harvest_interval_days=10,
            max_applications_per_season=2,
            safety_notes_en="Rotate with non-phenylamide fungicides to prevent fungal resistance. Strict 10-day PHI.",
            safety_notes_hi="रोग प्रतिरोधक क्षमता (रेजिस्टेंस) से बचने के लिए इसे 2 बार से अधिक न छिड़कें। तुड़ाई से 10 दिन पहले बंद करें।",
            cibrc_status="CIBRC Approved for Tomato & Potato Late Blight",
            is_banned_in_india=False,
            source_name="ICAR - Central Potato Research Institute (CPRI)",
            source_url="https://cpri.icar.gov.in",
            reviewed_by="Dr. Sunita Sharma (KVK)",
            last_reviewed_at=datetime.utcnow()
        ),
        # Abiotic treatment (Fertilizer balance, NO pesticides)
        Treatment(
            disease_id=d_abiotic_chlorosis.id,
            type="cultural",
            min_severity="mild",
            title_en="Foliar Micronutrient & Potassium Nitrate (13-0-45) Spray",
            title_hi="पोटेशियम नाइट्रेट (13-0-45) व सूक्ष्म पोषक तत्वों का छिड़काव",
            instructions_en="Apply Potassium Nitrate (13-0-45) @ 5 g/L + Chelated Micronutrient mixture @ 1 g/L. Do NOT apply fungicides.",
            instructions_hi="13-0-45 5 ग्राम प्रति लीटर पानी में मिलाकर छिड़कें। किसी भी फफूंदनाशक का प्रयोग न करें।",
            active_ingredient="Potassium Nitrate & Chelated Zinc/Iron",
            dosage="5 g / liter",
            timing="During cool early morning hours",
            pre_harvest_interval_days=0,
            max_applications_per_season=4,
            safety_notes_en="Non-toxic plant nutrient fertilizer.",
            safety_notes_hi="पोषक तत्व स्प्रे, पर्यावरण के लिए पूर्णतः सुरक्षित।",
            cibrc_status="Fertilizer Control Order (FCO) Approved",
            is_banned_in_india=False,
            source_name="ICAR-Indian Institute of Soil Science (IISS)",
            source_url="https://iiss.icar.gov.in",
            reviewed_by="ICAR Agronomy Panel",
            last_reviewed_at=datetime.utcnow()
        )
    ]
    db.add_all(treatments)
    db.flush()

    # 5. FIELDS
    f1 = Field(
        user_id=farmer.id,
        crop_id=tomato.id,
        name="Shivaji Nagar Plot (Tomato / टमाटर)",
        variety="Abhinav (Syngenta)",
        area_acres=2.5,
        sowing_date=date.today() - timedelta(days=38),
        latitude=19.9975,
        longitude=73.7898,
        status="watch"
    )
    f2 = Field(
        user_id=farmer.id,
        crop_id=potato.id,
        name="Godavari Canal Plot (Potato / आलू)",
        variety="Kufri Jyoti",
        area_acres=1.8,
        sowing_date=date.today() - timedelta(days=52),
        latitude=20.0150,
        longitude=73.8050,
        status="healthy"
    )
    f3 = Field(
        user_id=farmer.id,
        crop_id=tomato.id,
        name="Dindori Road Field (Tomato / टमाटर)",
        variety="US-440",
        area_acres=3.2,
        sowing_date=date.today() - timedelta(days=28),
        latitude=20.0520,
        longitude=73.8410,
        status="infected"
    )
    db.add_all([f1, f2, f3])
    db.flush()

    # 6. HISTORICAL SCANS (Unified State)
    s1 = Scan(
        field_id=f1.id,
        user_id=farmer.id,
        image_url="/sample_images/tomato_early_blight.jpg",
        captured_at=datetime.utcnow() - timedelta(days=6),
        latitude=19.9975,
        longitude=73.7898,
        top_disease_id=d_early_blight.id,
        calibrated_confidence=0.88,
        severity="moderate",
        severity_pct=18.4,
        is_leaf_valid=True,
        lifecycle_status="farmer_verified",
        user_confirmed_disease_id=d_early_blight.id,
        notes="Spotted on lower leaves"
    )
    db.add(s1)
    db.flush()

    sp1 = ScanPrediction(scan_id=s1.id, rank=1, disease_id=d_early_blight.id, confidence=0.88)
    sp2 = ScanPrediction(scan_id=s1.id, rank=2, disease_id=d_abiotic_chlorosis.id, confidence=0.08)
    sp3 = ScanPrediction(scan_id=s1.id, rank=3, disease_id=d_healthy.id, confidence=0.04)
    db.add_all([sp1, sp2, sp3])

    # 7. OUTBREAK EVENT (Unified Source of Truth, Gated Threshold)
    ob1 = OutbreakEvent(
        disease_id=d_late_blight.id,
        crop_id=tomato.id,
        center_lat=19.9975,
        center_lng=73.7898,
        radius_km=12.0,
        confirmed_count=14, # Exceeds minimum threshold of 3
        suspected_count=8,
        min_cluster_threshold=3,
        trend="rising",
        risk_level="red",
        first_reported=datetime.utcnow() - timedelta(days=4),
        last_reported=datetime.utcnow(),
        is_synthetic=False
    )
    db.add(ob1)
    db.flush()

    # 8. ALERTS
    alert1 = Alert(
        user_id=farmer.id,
        field_id=f1.id,
        type="outbreak",
        outbreak_id=ob1.id,
        severity="critical",
        title="प्रकोप चेतावनी: 14 सत्यापित मामलों के साथ टमाटर पछेती झुलसा का प्रकोप (Red Zone)",
        body="नासिक क्षेत्र में क्लस्टर थ्रेशोल्ड (>3 सत्यापित रिपोर्ट) पार हो गया है। 14 सत्यापित खेतों में पछेती झुलसा की पुष्टि हुई है।",
        language="hi"
    )
    db.add(alert1)

    # 9. SUPPLIERS
    s_shop1 = Supplier(
        name="Kisan Seva Kendra (किसान सेवा केंद्र - नासिक)",
        latitude=19.9920,
        longitude=73.7810,
        address="Shop 14, APMC Market Yard, Nashik",
        phone="+91 253-2591024",
        is_mock=True
    )
    db.add(s_shop1)
    db.flush()

    sp_prod1 = SupplierProduct(
        supplier_id=s_shop1.id,
        treatment_id=treatments[1].id,
        product_name="Indofil M-45 (Mancozeb 75% WP - CIBRC Approved)",
        price_inr=380.0,
        in_stock=True
    )
    db.add(sp_prod1)

    db.commit()
    print("CropGuard database seeded with safety, CIBRC India compliance, and gated cluster rules.")
