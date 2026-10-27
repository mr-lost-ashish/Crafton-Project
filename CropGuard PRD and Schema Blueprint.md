# CropGuard: PRD and Schema Blueprint

*Early detection and management of crop diseases and pest infestations. Prototype version 0.1 (working name: CropGuard)*

---

## 1. Overview

### 1.1 Problem

Smallholder farmers lose a large share of yield to crop diseases and pests, mostly because problems are identified late, misdiagnosed, or treated with the wrong or excess pesticide. Expert advice (agri-officers, KVKs) is hard to reach quickly, and warnings about regional outbreaks rarely arrive in time.

### 1.2 Vision

A farmer photographs a sick leaf or pest and gets a diagnosis, severity, and verified treatment advice in their own language within seconds. The app also warns the farmer before an outbreak, using weather conditions and nearby reports.

### 1.3 Goals (prototype)

- Diagnose diseases and pests for 2 to 3 crops from a photo, with a confidence score.
- Tell the farmer how severe the problem is and what to do.
- Predict disease risk from weather and crop stage, and alert the farmer.
- Show nearby outbreaks on a community map.
- Work in Hindi and English with voice support.
- Demonstrate the full product vision, with every feature visible in the demo (real, partial, or simulated, as labelled in section 3).

### 1.4 Non-goals (prototype)

- Production-grade accuracy across dozens of crops.
- Real payments, real supplier inventory, or real drone/IoT hardware integration.
- Regulatory approval of pesticide recommendations (advice is sourced from published guidelines, not certified).
- Native iOS/Android store release.

### 1.5 Assumptions

- Target region: India (initial crops to be confirmed, for example tomato, potato, wheat or cotton).
- Users have an Android phone, intermittent connectivity, and limited literacy in text-heavy interfaces.
- Prototype is delivered as a responsive web app (PWA) so it works on phones without app-store distribution.

---

## 2. Users and Personas

| Persona | Description | Key needs |
| --- | --- | --- |
| **Farmer (primary)** | Smallholder, 1 to 5 acres, regional language, basic smartphone | Fast diagnosis, simple advice, voice, low data use |
| **Agri-expert / extension officer** | Government or NGO advisor | Review escalated cases, see outbreak trends |
| **Admin** | Project team | Manage crops, diseases, treatments, content |
| **Supplier (mock)** | Local input shop | Listed in marketplace (static in prototype) |

---

## 3. Feature Scope and Implementation Level

| ID | Feature | Priority | Level |
| --- | --- | --- | --- |
| F1 | Image-based disease/pest diagnosis | P0 | Real |
| F2 | Severity estimate | P0 | Real |
| F3 | Treatment advice (organic and chemical) | P0 | Real |
| F4 | Hindi + English, voice input/output | P0 | Real |
| F5 | Scan history per field | P0 | Real |
| F6 | Weather-based risk alerts | P1 | Real |
| F7 | Community outbreak map | P1 | Real (seeded data) |
| F8 | Scheduled scan reminders | P1 | Real |
| F9 | Spray records / IPM tracking | P1 | Real (basic) |
| F10 | Offline mode with on-device model | P2 | Partial |
| F11 | Expert escalation | P2 | Simulated |
| F12 | Supplier marketplace link | P2 | Mocked |
| F13 | Drone/satellite whole-field view | P3 | Mocked (sample image, NDVI-style heatmap) |
| F14 | IoT sensor dashboard | P3 | Simulated (generated readings) |

**Priority key:** P0 = must work end to end; P1 = should work; P2 = demo-able; P3 = demo-only.

### 3.1 Innovation features added in v0.2

Ten features move the prototype from "diagnose a leaf" to "prevent crop loss". Most extend an existing feature (see Builds on) rather than adding a new module, so scope grows less than the count suggests.

| ID | Feature | What it adds | Builds on | Priority | Level |
| --- | --- | --- | --- | --- | --- |
| F15 | Disease Outbreak Radar | Green, amber and red risk zones; confirmed and suspected reports shown separately; a risk trend (rising, steady, falling) | F7, F6 | P0 | Real (seeded data) |
| F16 | Early Risk Predictor | Risk score with the factors behind it, plus a what-if simulator for humidity and rainfall; labelled as a risk estimate, never a diagnosis | F6 | P0 | Real |
| F17 | AI Second Opinion | When confidence is low: ask for a photo of the leaf underside, the crop and growth stage; compare candidate causes; recommend expert verification | F1 | P0 | Real |
| F18 | Kisan Voice SOS | Farmer describes the problem by voice in Hindi, app asks short follow-up questions, analyses the photo and explains by voice; reports queue offline | F4, F10 | P1 | Partial |
| F19 | Farm Digital Twin | Field model showing health now and scenarios for the next few days (risk keeps rising, rain forecast); ranks which field to inspect first | F5, F6 | P2 | Simulated |
| F20 | Community Crop Rescue Network | Farmers report symptoms and ask for help; experts verify reports; verified solutions are shared; outcomes are tracked | F7, F11 | P1 | Simulated (staged expert replies) |
| F21 | Smart Treatment Planner | Prevention-first plan: inspect, sanitise, cultural steps, organic, then chemical; flags when an expert is needed; tracks cost and actions | F3, F9 | P1 | Real |
| F22 | Crop Health Passport | Per-field timeline of photos, symptoms, weather, risk changes and actions taken | F5 | P1 | Real |
| F23 | Village Outbreak Simulation | Judge-facing mode: inject a simulated report in one village and watch the map and nearby alerts update | F15 | P0 for demo | Simulated, labelled |
| F24 | Loss-Avoidance Calculator | Compares early versus delayed response using editable crop value, treatment cost and loss assumptions | F9, F21 | P2 | Real (estimates only) |

### 3.2 Honesty rules for the new features

- Risk scores and digital-twin scenarios are labelled **estimates**, not confirmed diagnoses or forecasts.
- Simulated outbreaks, expert replies, and drone/sensor data carry a visible "Simulated" tag in the UI and in the database.
- The loss calculator shows estimates from editable assumptions, never promised savings.
- The differentiation claim is about the combination of features. Existing Indian initiatives already offer AI pest identification and crop-risk advisories, so the pitch should not say no one else does any of this.

### 3.3 Differentiation for the pitch

| Typical crop app | CropGuard |
| --- | --- |
| Detects a disease from a photo | Detects a possible disease and estimates future risk |
| Helps one farmer at a time | Connects field reports across a community |
| Gives a generic treatment | Gives crop-specific, prevention-first next steps in the local language |
| Shows a one-time result | Tracks crop health over time (Crop Health Passport) |
| Always gives an answer | Flags uncertainty and asks for verification |

---

## 4. Functional Requirements

### 4.1 Onboarding and Profile

- **FR-1.1** User signs up with phone number and OTP (mock OTP acceptable in prototype).
- **FR-1.2** User selects language (Hindi or English) at first launch; changeable anytime.
- **FR-1.3** User sets location (GPS or village/district search).
- **FR-1.4** User can add one or more fields with crop, variety (optional), area, sowing date, and location.

### 4.2 Scan and Diagnosis (F1, F2, F3)

- **FR-2.1** User captures a photo or uploads from the gallery, and selects the field.
- **FR-2.2** The system returns the top 3 predictions with confidence scores.
- **FR-2.3** If top confidence is below the threshold (default 60%), the app shows "Not sure, please consult an expert" and offers escalation instead of a definitive answer.
- **FR-2.4** The system estimates severity (mild, moderate, severe) from the proportion of affected leaf area.
- **FR-2.5** The result screen shows the disease/pest name, a reference image, symptoms, severity, and urgency.
- **FR-2.6** The result shows treatment options split into **organic**, **chemical**, and **preventive**, with dosage, timing, and safety notes, and a source reference (for example ICAR or a state agriculture university).
- **FR-2.7** Each treatment screen can be read aloud in the selected language.
- **FR-2.8** The user can confirm or correct the diagnosis (feedback loop for model improvement).
- **FR-2.9** Every scan is saved with image, location, timestamp, and prediction.

### 4.3 Language and Voice (F4)

- **FR-3.1** All UI strings and treatment content are available in Hindi and English.
- **FR-3.2** Text-to-speech reads results aloud; speech-to-text allows voice search or voice notes.
- **FR-3.3** Icons and colour coding (green, amber, red) convey severity without needing to read.

### 4.4 My Fields and History (F5, F9)

- **FR-4.1** List all fields with latest health status.
- **FR-4.2** Field detail shows a timeline of scans, treatments applied, and alerts.
- **FR-4.3** User logs a spray/treatment record: product, dose, date, linked scan, and cost (optional).
- **FR-4.4** System warns about repeated chemical use (for example the same active ingredient used more than the recommended number of times per season).
- **FR-4.5** Follow-up prompt: after a treatment, the app asks the user to re-scan after N days to check recovery.

### 4.5 Risk Alerts (F6) and Reminders (F8)

- **FR-5.1** The system fetches weather forecasts for each field location daily.
- **FR-5.2** A rules engine computes a risk level (low, medium, high) per disease from temperature, humidity, rainfall, leaf wetness, and crop growth stage.
- **FR-5.3** High-risk conditions trigger an in-app alert (and push/SMS where available) with preventive steps.
- **FR-5.4** Scan reminders are scheduled from the crop stage (for example weekly scans during flowering for blight-prone crops).
- **FR-5.5** Alerts can be snoozed or dismissed, and each alert records whether the user acted.

### 4.6 Community Outbreak Map (F7)

- **FR-6.1** Confirmed scans are anonymized (location rounded to roughly 1 km grid) and shown as pins or heat cells.
- **FR-6.2** The user can filter by crop, disease, and time window (7, 14, or 30 days).
- **FR-6.3** If a cluster of the same disease appears within a defined radius, nearby farmers receive an outbreak alert.
- **FR-6.4** Prototype data: seed with synthetic reports so the map is populated for demos.

### 4.7 Offline Mode (F10)

- **FR-7.1** A compressed on-device model (TFLite/ONNX) runs a basic diagnosis without a network.
- **FR-7.2** Offline scans are queued and synced when connectivity returns.
- **FR-7.3** Treatment content for supported crops is cached locally.

### 4.8 Expert Escalation (F11, simulated)

- **FR-8.1** The user taps "Ask an expert" and the scan is sent as a ticket with notes.
- **FR-8.2** An expert dashboard lists open tickets, and the expert can reply with a diagnosis and advice.
- **FR-8.3** The farmer is notified of the response. In the prototype, replies are staged by the team during the demo.

### 4.9 Marketplace (F12, mocked)

- **FR-9.1** A static list of nearby suppliers with name, distance, contact, and products. Treatment screens link recommended products to suppliers.

### 4.10 Whole-field and Sensor Views (F13, F14, simulated)

- **FR-10.1** The drone view shows a sample aerial image with an NDVI-style health heatmap and flagged zones.
- **FR-10.2** The sensor view shows soil moisture, leaf wetness, and temperature charts from a data generator, feeding the risk engine as an extra input.

### 4.11 Admin Console

- **FR-11.1** CRUD for crops, diseases/pests, treatments, translations, and supplier entries.
- **FR-11.2** Review user-corrected scans and export them as retraining data.

### 4.12 Disease Outbreak Radar (F15)

- **FR-12.1** The map shades areas green, amber or red from nearby report density, weather risk and crop overlap (only farmers growing the same crop are alerted).
- **FR-12.2** Confirmed reports (expert- or user-confirmed) and suspected reports (model prediction only) are drawn with different markers and counted separately.
- **FR-12.3** Each zone shows a trend: rising, steady or falling, compared with the previous 7 days.
- **FR-12.4** Tapping a zone shows the disease, report counts, the first and last report dates, and preventive steps.

### 4.13 Early Risk Predictor (F16)

- **FR-13.1** Each field shows a risk score (0 to 100) and level per disease, with the top contributing factors listed (for example humidity, rainfall, crop age).
- **FR-13.2** A what-if simulator lets the user change humidity, temperature and rainfall sliders and see the estimated risk change.
- **FR-13.3** Every risk screen carries the label "Risk estimate, not a diagnosis".
- **FR-13.4** Preventive reminders are generated before the risk reaches high, not only after.

### 4.14 AI Second Opinion (F17)

- **FR-14.1** If top confidence is below the threshold, or the top two predictions are close, the app starts a Second Opinion flow instead of showing a single answer.
- **FR-14.2** The flow asks for: a photo of the leaf underside, the crop and growth stage (pre-filled from the field), and which symptoms are present (yellowing, spots, curling, insects).
- **FR-14.3** The app re-scores the candidates using the extra photo and answers, and shows a side-by-side comparison of the likely causes and their symptoms.
- **FR-14.4** If confidence is still low, the app recommends expert verification and offers escalation (F11 or F20).
- **FR-14.5** The app never presents a treatment as definitive for a result in the uncertain state.

### 4.15 Kisan Voice SOS (F18)

- **FR-15.1** The user holds one button and describes the problem in Hindi or English (for example, tomato leaves turning yellow).
- **FR-15.2** The system transcribes the speech, extracts crop and symptoms, and asks up to 3 short follow-up questions by voice.
- **FR-15.3** The user adds a photo; the system combines voice and image evidence and replies by voice and text.
- **FR-15.4** In low connectivity the report is saved on the device and synced when the network returns, with a visible "waiting to send" status.

### 4.16 Farm Digital Twin (F19)

- **FR-16.1** Each field has a status view with current health, latest scan, current risk and recent weather.
- **FR-16.2** The user can run scenarios for the next 3 to 7 days: risk keeps rising, rain is forecast tomorrow, or treatment is applied.
- **FR-16.3** The view ranks the user's fields by inspection priority.
- **FR-16.4** Scenario outputs are labelled "Simulated estimate" and list the assumptions used.

### 4.17 Community Crop Rescue Network (F20)

- **FR-17.1** A farmer posts a rescue request with a scan, symptoms and optional voice note.
- **FR-17.2** Experts mark a report as verified, needs more info, or rejected, with a short comment.
- **FR-17.3** Other users can suggest solutions; only expert-verified solutions are shown as "Verified".
- **FR-17.4** After acting on advice, the farmer records the outcome (improved, no change, worse), which feeds the outcome statistics shown on each solution.
- **FR-17.5** In the prototype, expert replies are staged by the team and flagged as simulated.

### 4.18 Smart Treatment Planner (F21)

- **FR-18.1** For each diagnosis, the app builds a stepwise plan in this order: inspect, sanitise, cultural practices, organic option, then chemical option only if severity or spread warrants it.
- **FR-18.2** Each step shows who should do it, when, an estimated cost and a done checkbox.
- **FR-18.3** Steps where an expert should be consulted (severe cases, unknown product choice, restricted chemicals) are flagged.
- **FR-18.4** The planner shows estimated total cost and actual cost recorded so far, using the spray records from F9.

### 4.19 Crop Health Passport (F22)

- **FR-19.1** Each field has a single timeline combining scans, symptoms, weather events, risk changes, alerts and treatments.
- **FR-19.2** The user can filter by event type and date range and compare two scans side by side.
- **FR-19.3** The passport can be exported as a PDF to share with an expert or a lender.

### 4.20 Village Outbreak Simulation (F23)

- **FR-20.1** A demo-mode switch lets the presenter pick a village, disease and crop, and inject a simulated report.
- **FR-20.2** The radar recolours nearby zones, and simulated alerts appear for fields within the chosen radius.
- **FR-20.3** All simulated data is tagged and removable with a single reset button.

### 4.21 Loss-Avoidance Calculator (F24)

- **FR-21.1** The user enters or edits crop value, expected loss percentage if untreated, treatment cost, and delay days.
- **FR-21.2** The tool compares an early-intervention scenario and a delayed-response scenario, and shows the difference as an estimate.
- **FR-21.3** The assumptions are shown beside the result, and the result is labelled "Estimate, not a guaranteed saving".

---

## 5. Non-Functional Requirements

| Area | Requirement |
| --- | --- |
| **Performance** | Diagnosis response under 3 seconds on 4G; image upload compressed to under 500 KB |
| **Accuracy (target)** | At least 85% top-1 on a held-out set that includes real-field photos for chosen crops; to be measured, not assumed |
| **Usability** | Core scan flow in 3 taps or fewer; usable with large touch targets and minimal text |
| **Availability** | Prototype target: 95% during the demo period |
| **Privacy** | Phone number stored hashed or encrypted; location anonymized on the public map; user consent captured for sharing scans |
| **Safety** | Pesticide advice must cite a source and include safety text (PPE, pre-harvest interval); low-confidence results never show a treatment as definitive |
| **Compatibility** | Chrome on Android 8+, responsive down to 360 px width |
| **Data usage** | Offline-capable screens and compressed images for low-bandwidth areas |

---

## 6. Key User Flows

**Flow A: Diagnose a problem**

1. Open the app and tap Scan.
2. Choose a field and take a photo.
3. App uploads the image and runs the model.
4. High confidence: show the disease, severity, and treatments. Low confidence: show a "not sure" message with the escalation option.
5. The user confirms or corrects the result and optionally logs a spray record.
6. The app schedules a follow-up scan reminder.

**Flow B: Receive a risk alert**

1. Daily job fetches weather per field.
2. Rules engine scores risk.
3. A high score creates an alert and sends a notification.
4. The user opens the alert, reads preventive steps, and taps "Scan now" or "Mark done".

**Flow C: Outbreak awareness**

1. Several users in an area submit scans for the same disease.
2. The cluster job detects the pattern and creates an outbreak event.
3. Nearby users get an alert and can view the event on the map.

**Flow D: Live demo (hackathon version)**

1. Upload a leaf photo; the app shows a possible disease with its confidence. If confidence is low, the Second Opinion flow asks for the leaf underside and growth stage.
2. Open the field's risk screen; change humidity and rainfall in the simulator and show the estimate move.
3. Open the Outbreak Radar; use demo mode to inject a simulated report in a village and watch nearby zones turn amber or red.
4. Press the voice button and describe the problem in Hindi; the assistant asks short questions and answers by voice.
5. Open the Treatment Planner and Loss-Avoidance Calculator, then record a follow-up photo and mark whether symptoms improved; the Crop Health Passport shows the whole timeline.

Simulated data is labelled on screen throughout.

---

## 7. ML and Data Requirements

| Item | Specification |
| --- | --- |
| **Task** | Multi-class image classification (disease/pest/healthy per crop); optional segmentation or heuristic for severity |
| **Base model** | MobileNetV3 or EfficientNet-Lite, fine-tuned (transfer learning) |
| **Datasets** | PlantVillage (baseline), PlantDoc and field images (robustness), IP102 (pests) |
| **Augmentation** | Rotation, brightness, background variation, blur, to bridge the lab-to-field gap |
| **Severity** | Prototype: ratio of diseased pixels (colour or segmentation mask) mapped to thresholds (under 10% mild, 10 to 30% moderate, over 30% severe; thresholds tunable per disease) |
| **Uncertainty** | Softmax confidence threshold plus an "unknown/other" fallback |
| **Serving** | FastAPI endpoint for the server model; TFLite/ONNX build for offline |
| **Feedback loop** | User corrections stored with the image and exported for periodic retraining |
| **Evaluation** | Per-class precision/recall, a confusion matrix, and a separate real-field test set |

**Risk engine (prototype rules, examples)**

- Late blight (potato/tomato): average temperature 10 to 24 C with relative humidity above 90% for 2 or more days gives HIGH risk.
- Powdery mildew: moderate temperature and high humidity without rain raises risk.
- Aphids and whitefly: warm, dry spells raise risk.

Rules are stored as data (see `risk_rules`), so they can be edited without code changes and later replaced by an ML model. Thresholds above are illustrative and must be verified against agronomy sources before use.

---

## 8. System Architecture

```
[PWA frontend: React]  <-->  [API: FastAPI]  <-->  [PostgreSQL + PostGIS]
        |                        |  |
   TFLite/ONNX (offline)         |  +--> [Object storage: images]
                                 +--> [ML service: classifier + severity]
                                 +--> [Weather API: OpenWeatherMap]
                                 +--> [Scheduler: alerts, reminders, cluster detection]
                                 +--> [Notifications: web push / SMS]
```

| Layer | Choice |
| --- | --- |
| Frontend | React PWA, i18n (react-i18next), Web Speech API, Leaflet for maps |
| Backend | FastAPI (Python) |
| Database | PostgreSQL with PostGIS (spatial queries for the outbreak map) |
| Storage | S3-compatible bucket or Firebase Storage |
| Jobs | Celery or APScheduler for daily weather, risk scoring, reminders, and clustering |
| ML | TensorFlow or PyTorch; export to TFLite/ONNX |
| Hosting | Any free or low-cost tier for the demo |

---

## 9. Data Schema Blueprint

PostgreSQL with the PostGIS extension. All tables use `uuid` primary keys and `created_at` / `updated_at` timestamps unless noted.

### 9.1 Entity Overview

| Domain | Tables |
| --- | --- |
| Users | `users`, `expert_profiles` |
| Reference data | `crops`, `crop_stages`, `diseases`, `treatments`, `disease_translations`, `treatment_translations` |
| Farm data | `fields`, `scans`, `scan_predictions`, `treatment_logs` |
| Early detection | `weather_snapshots`, `risk_rules`, `alerts`, `outbreak_events`, `reminders` |
| Support | `expert_tickets`, `suppliers`, `supplier_products` |
| Simulated | `sensor_readings`, `drone_surveys` |

### 9.2 Relationships

- A **user** has many **fields**; a **field** belongs to one **crop** and has many **scans**.
- A **scan** has many **scan\_predictions** (top-N results), each pointing to a **disease**.
- A **disease** belongs to one **crop** (or is a multi-crop pest) and has many **treatments**.
- A **treatment\_log** links a **field**, optionally a **scan**, and optionally a **treatment**.
- **Alerts** belong to a user and field, and reference a **risk\_rule** or an **outbreak\_event**.
- **Expert\_tickets** link a **scan**, the requesting **user**, and an assigned **expert**.

### 9.3 Core Tables (SQL)

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============ USERS ============
CREATE TABLE users (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  phone_hash      text UNIQUE NOT NULL,
  name            text,
  role            text NOT NULL DEFAULT 'farmer'
                  CHECK (role IN ('farmer','expert','admin')),
  language        text NOT NULL DEFAULT 'hi' CHECK (language IN ('hi','en')),
  home_location   geography(Point,4326),
  district        text,
  state           text,
  share_scans     boolean NOT NULL DEFAULT true,   -- consent for community map
  push_token      text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE expert_profiles (
  user_id         uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  organization    text,
  specialization  text[],
  regions_covered text[]
);

-- ============ REFERENCE DATA ============
CREATE TABLE crops (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code            text UNIQUE NOT NULL,            -- e.g. 'tomato'
  name_en         text NOT NULL,
  name_hi         text,
  icon_url        text
);

CREATE TABLE crop_stages (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  crop_id         uuid NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
  stage_name      text NOT NULL,                   -- seedling, vegetative, flowering...
  start_day       int  NOT NULL,                   -- days after sowing
  end_day         int  NOT NULL,
  scan_interval_days int DEFAULT 7
);

CREATE TABLE diseases (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  crop_id         uuid REFERENCES crops(id),       -- NULL for multi-crop pests
  model_label     text UNIQUE NOT NULL,            -- class name used by the ML model
  category        text NOT NULL
                  CHECK (category IN ('fungal','bacterial','viral','pest','nutrient','healthy')),
  scientific_name text,
  name_en         text NOT NULL,
  symptoms_en     text,
  reference_image_url text,
  is_active       boolean NOT NULL DEFAULT true
);

CREATE TABLE treatments (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  disease_id      uuid NOT NULL REFERENCES diseases(id) ON DELETE CASCADE,
  type            text NOT NULL CHECK (type IN ('organic','chemical','preventive','cultural')),
  min_severity    text NOT NULL DEFAULT 'mild'
                  CHECK (min_severity IN ('mild','moderate','severe')),
  title_en        text NOT NULL,
  instructions_en text NOT NULL,
  active_ingredient text,
  dosage          text,
  timing          text,
  pre_harvest_interval_days int,
  max_applications_per_season int,
  safety_notes_en text,
  source_name     text NOT NULL,                   -- e.g. ICAR, state agri university
  source_url      text
);

CREATE TABLE disease_translations (
  disease_id      uuid REFERENCES diseases(id) ON DELETE CASCADE,
  language        text CHECK (language IN ('hi','en')),
  name            text NOT NULL,
  symptoms        text,
  PRIMARY KEY (disease_id, language)
);

CREATE TABLE treatment_translations (
  treatment_id    uuid REFERENCES treatments(id) ON DELETE CASCADE,
  language        text CHECK (language IN ('hi','en')),
  title           text NOT NULL,
  instructions    text NOT NULL,
  safety_notes    text,
  PRIMARY KEY (treatment_id, language)
);

-- ============ FARM DATA ============
CREATE TABLE fields (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  crop_id         uuid NOT NULL REFERENCES crops(id),
  name            text NOT NULL,
  variety         text,
  area_acres      numeric(8,2),
  sowing_date     date NOT NULL,
  location        geography(Point,4326) NOT NULL,
  boundary        geography(Polygon,4326),
  status          text NOT NULL DEFAULT 'healthy'
                  CHECK (status IN ('healthy','watch','infected','recovering')),
  is_active       boolean NOT NULL DEFAULT true,
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_fields_user ON fields(user_id);
CREATE INDEX idx_fields_loc ON fields USING GIST(location);

CREATE TABLE scans (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id        uuid NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  user_id         uuid NOT NULL REFERENCES users(id),
  image_url       text NOT NULL,
  captured_at     timestamptz NOT NULL DEFAULT now(),
  location        geography(Point,4326),
  source          text NOT NULL DEFAULT 'server'
                  CHECK (source IN ('server','offline_synced')),
  model_version   text,
  top_disease_id  uuid REFERENCES diseases(id),
  top_confidence  numeric(5,4),
  severity        text CHECK (severity IN ('mild','moderate','severe')),
  severity_pct    numeric(5,2),                    -- % leaf area affected
  result_status   text NOT NULL DEFAULT 'confident'
                  CHECK (result_status IN ('confident','uncertain','escalated')),
  user_confirmed_disease_id uuid REFERENCES diseases(id),  -- farmer/expert correction
  user_feedback   text CHECK (user_feedback IN ('correct','incorrect','unsure')),
  notes           text
);
CREATE INDEX idx_scans_field_time ON scans(field_id, captured_at DESC);
CREATE INDEX idx_scans_loc ON scans USING GIST(location);
CREATE INDEX idx_scans_disease_time ON scans(top_disease_id, captured_at);

CREATE TABLE scan_predictions (
  scan_id         uuid REFERENCES scans(id) ON DELETE CASCADE,
  rank            smallint CHECK (rank BETWEEN 1 AND 5),
  disease_id      uuid NOT NULL REFERENCES diseases(id),
  confidence      numeric(5,4) NOT NULL,
  PRIMARY KEY (scan_id, rank)
);

CREATE TABLE treatment_logs (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id        uuid NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  scan_id         uuid REFERENCES scans(id),
  treatment_id    uuid REFERENCES treatments(id),
  product_name    text,
  active_ingredient text,
  dose_applied    text,
  applied_on      date NOT NULL,
  cost_inr        numeric(10,2),
  followup_due_on date,
  outcome         text CHECK (outcome IN ('improved','no_change','worse','pending'))
                  DEFAULT 'pending',
  notes           text
);
CREATE INDEX idx_tlogs_field ON treatment_logs(field_id, applied_on DESC);
```

### 9.4 Early-Detection Tables (SQL)

```sql
CREATE TABLE weather_snapshots (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  location        geography(Point,4326) NOT NULL,   -- rounded grid point, shared across nearby fields
  observed_for    date NOT NULL,
  is_forecast     boolean NOT NULL DEFAULT false,
  temp_min_c      numeric(4,1),
  temp_max_c      numeric(4,1),
  humidity_avg    numeric(4,1),
  rainfall_mm     numeric(6,1),
  leaf_wetness_hrs numeric(4,1),                    -- from sensor or estimated
  UNIQUE (location, observed_for, is_forecast)
);

CREATE TABLE risk_rules (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  disease_id      uuid NOT NULL REFERENCES diseases(id),
  crop_stage_id   uuid REFERENCES crop_stages(id),  -- NULL = any stage
  conditions      jsonb NOT NULL,
  -- e.g. {"temp_avg":{"min":10,"max":24},"humidity_avg":{"gt":90},"consecutive_days":2}
  risk_level      text NOT NULL CHECK (risk_level IN ('medium','high')),
  advice_en       text NOT NULL,
  advice_hi       text,
  source_note     text,
  is_active       boolean NOT NULL DEFAULT true
);

CREATE TABLE outbreak_events (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  disease_id      uuid NOT NULL REFERENCES diseases(id),
  center          geography(Point,4326) NOT NULL,
  radius_km       numeric(6,2) NOT NULL,
  report_count    int NOT NULL,
  first_reported  timestamptz NOT NULL,
  last_reported   timestamptz NOT NULL,
  status          text NOT NULL DEFAULT 'active'
                  CHECK (status IN ('active','resolved')),
  is_synthetic    boolean NOT NULL DEFAULT false    -- seeded demo data
);
CREATE INDEX idx_outbreak_center ON outbreak_events USING GIST(center);

CREATE TABLE alerts (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  field_id        uuid REFERENCES fields(id) ON DELETE CASCADE,
  type            text NOT NULL CHECK (type IN ('weather_risk','outbreak','followup','reminder')),
  risk_rule_id    uuid REFERENCES risk_rules(id),
  outbreak_id     uuid REFERENCES outbreak_events(id),
  severity        text CHECK (severity IN ('info','warning','critical')),
  title           text NOT NULL,
  body            text NOT NULL,
  language        text NOT NULL,
  created_at      timestamptz NOT NULL DEFAULT now(),
  read_at         timestamptz,
  action_taken    boolean DEFAULT false,
  snoozed_until   timestamptz
);
CREATE INDEX idx_alerts_user_unread ON alerts(user_id, read_at);

CREATE TABLE reminders (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id        uuid NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  crop_stage_id   uuid REFERENCES crop_stages(id),
  reminder_type   text NOT NULL CHECK (reminder_type IN ('scan','followup_scan','spray')),
  due_on          date NOT NULL,
  repeat_every_days int,
  status          text NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','sent','done','skipped'))
);
CREATE INDEX idx_reminders_due ON reminders(due_on, status);
```

### 9.5 Support and Simulated Tables (SQL)

```sql
CREATE TABLE expert_tickets (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id         uuid NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
  requested_by    uuid NOT NULL REFERENCES users(id),
  assigned_to     uuid REFERENCES users(id),        -- expert
  farmer_note     text,
  status          text NOT NULL DEFAULT 'open'
                  CHECK (status IN ('open','in_review','answered','closed')),
  expert_diagnosis_id uuid REFERENCES diseases(id),
  expert_reply    text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  answered_at     timestamptz
);

CREATE TABLE suppliers (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name            text NOT NULL,
  location        geography(Point,4326),
  address         text,
  phone           text,
  is_mock         boolean NOT NULL DEFAULT true
);

CREATE TABLE supplier_products (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  supplier_id     uuid NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
  treatment_id    uuid REFERENCES treatments(id),
  product_name    text NOT NULL,
  price_inr       numeric(10,2),
  in_stock        boolean DEFAULT true
);

-- Simulated modules
CREATE TABLE sensor_readings (
  id              bigserial PRIMARY KEY,
  field_id        uuid NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  recorded_at     timestamptz NOT NULL,
  soil_moisture_pct numeric(5,2),
  leaf_wetness_pct  numeric(5,2),
  air_temp_c      numeric(4,1),
  humidity_pct    numeric(4,1),
  is_simulated    boolean NOT NULL DEFAULT true
);
CREATE INDEX idx_sensor_field_time ON sensor_readings(field_id, recorded_at DESC);

CREATE TABLE drone_surveys (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id        uuid NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  surveyed_on     date NOT NULL,
  image_url       text NOT NULL,
  ndvi_overlay_url text,
  flagged_zones   jsonb,        -- GeoJSON polygons with health scores
  is_simulated    boolean NOT NULL DEFAULT true
);
```

### 9.5a Schema Additions for v0.2 Features

Two existing tables gain columns, and eight tables are new.

| Feature | Schema change |
| --- | --- |
| F15 Outbreak Radar | New columns on `outbreak_events`; new `risk_zones` table |
| F16 Early Risk Predictor | New `risk_assessments` table |
| F17 AI Second Opinion | New `second_opinion_sessions` table |
| F18 Kisan Voice SOS | New `voice_reports` table |
| F19, F23, F24 Twin, simulation, calculator | New `simulation_scenarios` and `loss_scenarios` tables |
| F20 Rescue Network | New `community_reports` and `community_solutions` tables |
| F21 Treatment Planner | New `treatment_plans` and `treatment_plan_steps` tables |
| F22 Health Passport | New `field_passport_events` view (no new data) |

```sql
-- ===== F15: Outbreak Radar =====
ALTER TABLE outbreak_events
  ADD COLUMN confirmed_count  int NOT NULL DEFAULT 0,
  ADD COLUMN suspected_count  int NOT NULL DEFAULT 0,
  ADD COLUMN trend            text CHECK (trend IN ('rising','steady','falling')),
  ADD COLUMN risk_level       text CHECK (risk_level IN ('green','amber','red'));

ALTER TABLE scans
  ADD COLUMN report_status text NOT NULL DEFAULT 'suspected'
  CHECK (report_status IN ('suspected','confirmed'));   -- confirmed = user- or expert-verified

CREATE TABLE risk_zones (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  disease_id     uuid NOT NULL REFERENCES diseases(id),
  crop_id        uuid NOT NULL REFERENCES crops(id),
  zone           geography(Polygon,4326) NOT NULL,      -- grid cell or buffered cluster
  risk_level     text NOT NULL CHECK (risk_level IN ('green','amber','red')),
  confirmed_count int NOT NULL DEFAULT 0,
  suspected_count int NOT NULL DEFAULT 0,
  trend          text CHECK (trend IN ('rising','steady','falling')),
  computed_at    timestamptz NOT NULL DEFAULT now(),
  is_synthetic   boolean NOT NULL DEFAULT false
);
CREATE INDEX idx_zones_geo ON risk_zones USING GIST(zone);

-- ===== F16: Early Risk Predictor =====
CREATE TABLE risk_assessments (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id       uuid NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  disease_id     uuid NOT NULL REFERENCES diseases(id),
  risk_rule_id   uuid REFERENCES risk_rules(id),
  score          smallint NOT NULL CHECK (score BETWEEN 0 AND 100),
  level          text NOT NULL CHECK (level IN ('low','medium','high')),
  factors        jsonb NOT NULL,
  -- e.g. [{"name":"humidity_avg","value":92,"weight":0.4},{"name":"crop_age_days","value":38,"weight":0.2}]
  inputs_snapshot jsonb,                  -- weather and sensor inputs used
  is_what_if     boolean NOT NULL DEFAULT false,  -- true for simulator runs
  computed_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_risk_field_time ON risk_assessments(field_id, computed_at DESC);

-- ===== F17: AI Second Opinion =====
CREATE TABLE second_opinion_sessions (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id        uuid NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
  extra_image_urls text[],               -- e.g. leaf underside
  growth_stage   text,
  symptoms_reported text[],
  answers        jsonb,                  -- follow-up question and answer pairs
  rescored_predictions jsonb,            -- candidates with updated confidence
  final_confidence numeric(5,4),
  outcome        text CHECK (outcome IN ('resolved','still_uncertain','escalated')),
  created_at     timestamptz NOT NULL DEFAULT now()
);

-- ===== F18: Kisan Voice SOS =====
CREATE TABLE voice_reports (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  field_id       uuid REFERENCES fields(id),
  scan_id        uuid REFERENCES scans(id),
  language       text NOT NULL CHECK (language IN ('hi','en')),
  audio_url      text,
  transcript     text,
  extracted      jsonb,                  -- {"crop":"tomato","symptoms":["yellow leaves"]}
  followups      jsonb,                  -- questions asked and answers given
  sync_status    text NOT NULL DEFAULT 'synced'
                 CHECK (sync_status IN ('queued','synced','failed')),
  recorded_at    timestamptz NOT NULL,   -- device time
  synced_at      timestamptz
);

-- ===== F19, F23: Digital Twin and Village Simulation =====
CREATE TABLE simulation_scenarios (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  kind           text NOT NULL CHECK (kind IN ('digital_twin','village_outbreak')),
  field_id       uuid REFERENCES fields(id) ON DELETE CASCADE,   -- twin runs
  created_by     uuid REFERENCES users(id),
  parameters     jsonb NOT NULL,
  -- twin: {"horizon_days":5,"rain_mm":[0,12,8,0,0],"treatment_applied":false}
  -- village: {"village":"...","disease_id":"...","radius_km":5}
  results        jsonb,                  -- projected risk per day, affected zones, alerts created
  is_simulated   boolean NOT NULL DEFAULT true CHECK (is_simulated),
  created_at     timestamptz NOT NULL DEFAULT now()
);

-- ===== F24: Loss-Avoidance Calculator =====
CREATE TABLE loss_scenarios (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id       uuid NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  scan_id        uuid REFERENCES scans(id),
  crop_value_inr numeric(12,2) NOT NULL,
  treatment_cost_inr numeric(10,2) NOT NULL,
  loss_pct_if_early numeric(5,2) NOT NULL,
  loss_pct_if_delayed numeric(5,2) NOT NULL,
  delay_days     int NOT NULL,
  estimated_difference_inr numeric(12,2) NOT NULL,
  created_at     timestamptz NOT NULL DEFAULT now()
);

-- ===== F20: Community Crop Rescue Network =====
CREATE TABLE community_reports (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        uuid NOT NULL REFERENCES users(id),
  scan_id        uuid REFERENCES scans(id),
  voice_report_id uuid REFERENCES voice_reports(id),
  symptoms_text  text,
  status         text NOT NULL DEFAULT 'open'
                 CHECK (status IN ('open','needs_info','verified','rejected','resolved')),
  verified_by    uuid REFERENCES users(id),
  verified_at    timestamptz,
  created_at     timestamptz NOT NULL DEFAULT now(),
  is_simulated   boolean NOT NULL DEFAULT false
);

CREATE TABLE community_solutions (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id      uuid NOT NULL REFERENCES community_reports(id) ON DELETE CASCADE,
  author_id      uuid NOT NULL REFERENCES users(id),
  body           text NOT NULL,
  treatment_id   uuid REFERENCES treatments(id),
  is_expert_verified boolean NOT NULL DEFAULT false,
  improved_count int NOT NULL DEFAULT 0,     -- outcome tallies from farmers who tried it
  no_change_count int NOT NULL DEFAULT 0,
  worse_count    int NOT NULL DEFAULT 0,
  created_at     timestamptz NOT NULL DEFAULT now()
);

-- ===== F21: Smart Treatment Planner =====
CREATE TABLE treatment_plans (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id       uuid NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  scan_id        uuid NOT NULL REFERENCES scans(id),
  status         text NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active','completed','abandoned')),
  estimated_cost_inr numeric(10,2),
  actual_cost_inr numeric(10,2) DEFAULT 0,
  created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE treatment_plan_steps (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id        uuid NOT NULL REFERENCES treatment_plans(id) ON DELETE CASCADE,
  step_order     smallint NOT NULL,
  phase          text NOT NULL
                 CHECK (phase IN ('inspect','sanitation','cultural','organic','chemical')),
  treatment_id   uuid REFERENCES treatments(id),
  description    text NOT NULL,
  due_on         date,
  estimated_cost_inr numeric(10,2),
  requires_expert boolean NOT NULL DEFAULT false,
  done_at        timestamptz,
  treatment_log_id uuid REFERENCES treatment_logs(id),   -- links to the spray record
  UNIQUE (plan_id, step_order)
);

-- ===== F22: Crop Health Passport (derived view) =====
CREATE VIEW field_passport_events AS
  SELECT field_id, captured_at AS event_time, 'scan' AS event_type,
         id AS source_id, severity AS summary
    FROM scans
  UNION ALL
  SELECT field_id, applied_on::timestamptz, 'treatment', id, product_name
    FROM treatment_logs
  UNION ALL
  SELECT field_id, computed_at, 'risk_change', id, level
    FROM risk_assessments WHERE is_what_if = false
  UNION ALL
  SELECT field_id, created_at, 'alert', id, title
    FROM alerts WHERE field_id IS NOT NULL;
```

**Notes**

- `simulation_scenarios.is_simulated` is constrained to true, so simulated runs can never be mistaken for real data; `risk_assessments.is_what_if` separates simulator runs from real scores.
- `scans.report_status` drives the radar's confirmed versus suspected counts. A scan becomes confirmed when the farmer or an expert confirms the diagnosis.
- Weather history for the passport comes from `weather_snapshots` joined by location and date at query time, rather than copied into the view.

### 9.6 Schema Notes

- **Anonymization for the map:** the public map query should return `ST_SnapToGrid(location::geometry, 0.01)` (about 1 km) and only scans from users with `share_scans = true`.
- **Retraining data:** `scans.user_confirmed_disease_id` (or an expert diagnosis) plus `image_url` form the labelled feedback set.
- **Translations:** English text lives on the base tables; additional languages go in the `*_translations` tables so new languages need no schema change.
- **Rules as data:** `risk_rules.conditions` is JSONB so agronomists can tune thresholds from the admin console.
- **Simulated flags:** `is_synthetic` / `is_simulated` / `is_mock` columns let the team clearly separate demo data from real data.

---

## 10. API Blueprint (REST)

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/auth/otp/request`, `/auth/otp/verify` | Phone login |
| GET/PATCH | `/me` | Profile and language |
| GET/POST | `/fields` | List or create fields |
| GET/PATCH/DELETE | `/fields/{id}` | Field detail |
| POST | `/scans` | Upload image, run diagnosis, return result |
| GET | `/scans?field_id=` | Scan history |
| PATCH | `/scans/{id}/feedback` | Confirm or correct a diagnosis |
| GET | `/diseases/{id}` | Disease details with treatments (language-aware) |
| POST/GET | `/fields/{id}/treatment-logs` | Spray and treatment records |
| GET | `/alerts` | List alerts |
| PATCH | `/alerts/{id}` | Mark read, snooze, action taken |
| GET | `/fields/{id}/risk` | Current risk summary |
| GET | `/outbreaks?bbox=&crop=&days=` | Community map data |
| POST | `/scans/{id}/escalate` | Create an expert ticket |
| GET/PATCH | `/expert/tickets` | Expert dashboard |
| GET | `/suppliers?near=` | Marketplace list |
| GET | `/fields/{id}/sensors` | Simulated sensor data |
| GET | `/fields/{id}/drone` | Simulated drone survey |
| POST | `/admin/*` | Content management |

**New endpoints for v0.2 features**

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/radar?bbox=&crop=&days=` | Risk zones with confirmed and suspected counts and trend (F15) |
| GET | `/fields/{id}/risk-assessments` | Risk score with contributing factors (F16) |
| POST | `/fields/{id}/risk-assessments/what-if` | Run the humidity/rainfall simulator; not stored as a real score (F16) |
| POST | `/scans/{id}/second-opinion` | Submit extra photo and answers, get re-scored candidates (F17) |
| POST | `/voice-reports` | Upload audio, get transcript, follow-up questions and spoken reply (F18) |
| POST | `/voice-reports/sync` | Upload queued offline reports in a batch (F18) |
| POST | `/fields/{id}/twin/scenarios` | Run a digital-twin scenario (F19) |
| GET | `/fields/priority` | Fields ranked by inspection priority (F19) |
| GET/POST | `/community/reports` | List or create rescue requests (F20) |
| PATCH | `/community/reports/{id}` | Expert verification (F20) |
| POST | `/community/reports/{id}/solutions` | Add a solution; record an outcome (F20) |
| POST | `/scans/{id}/treatment-plan` | Generate a prevention-first plan (F21) |
| PATCH | `/treatment-plans/{id}/steps/{step_id}` | Mark a step done, link a spray record (F21) |
| GET | `/fields/{id}/passport?from=&to=&type=` | Timeline of events (F22) |
| GET | `/fields/{id}/passport/export` | PDF export (F22) |
| POST | `/admin/simulations/village` | Inject a simulated village report (F23) |
| DELETE | `/admin/simulations` | Reset all simulated data (F23) |
| POST | `/fields/{id}/loss-scenarios` | Compute early versus delayed loss estimate (F24) |

**Sample scan response**

```json
{
  "scan_id": "7c1e...",
  "result_status": "confident",
  "predictions": [
    {"disease": "Tomato Early Blight", "confidence": 0.91},
    {"disease": "Tomato Septoria Leaf Spot", "confidence": 0.05},
    {"disease": "Healthy", "confidence": 0.02}
  ],
  "severity": "moderate",
  "severity_pct": 18.4,
  "treatments": [
    {"type": "organic", "title": "...", "dosage": "...", "source": "..."},
    {"type": "chemical", "title": "...", "pre_harvest_interval_days": 7}
  ],
  "followup_reminder": "2026-11-03"
}
```

---

## 11. Success Metrics

| Metric | Prototype target |
| --- | --- |
| Top-1 accuracy on the real-field test set | 85% or higher (report honestly, including failures) |
| Time from photo to result | Under 3 seconds |
| Low-confidence handling | 100% of results under the threshold show the "not sure" path |
| Task success in user testing | At least 8 of 10 test users complete a scan and read the advice unaided |
| Language comprehension | Test users understand the Hindi advice without help |
| Alert logic | Risk rules fire correctly on at least 5 replayed historical weather scenarios |
| Demo completeness | All 14 features reachable in the demo, with real versus simulated clearly labelled |

---

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Lab-to-field accuracy gap | Wrong diagnoses | Add field images, heavy augmentation, a field-photo test set, and a confidence threshold |
| Incorrect or unsafe pesticide advice | Crop or health harm | Use only cited sources (ICAR, state universities), show safety notes, and have an agronomist review the content |
| Poor connectivity | Feature unusable | Image compression, offline model, and sync queue |
| Scope creep from 14 features | Nothing finished | Priority tiers P0 to P3; cut from the bottom |
| Low literacy | Low adoption | Voice, icons, colour severity, short sentences |
| Privacy of farm locations | Trust loss | Consent, grid snapping, and hashed phone numbers |
| Treatment data volume per crop | Content bottleneck | Limit to 2 to 3 crops for the prototype |

---

## 13. Suggested Milestones

| Phase | Deliverables |
| --- | --- |
| **1. Core** | Dataset prep, trained model, diagnosis API, severity, treatment content for chosen crops |
| **2. App base** | Auth, fields, scan flow, history, Hindi/English, voice |
| **3. Early detection** | Weather ingestion, risk engine, alerts, outbreak map with seeded data, reminders |
| **4. Extended** | Spray records, offline model, expert ticket flow |
| **5. Mock modules** | Marketplace, drone view, IoT simulator, admin console |
| **6. Polish** | User testing, accuracy report, demo script, documentation |

Timeline in weeks depends on team size, which is still an open question (see below).

---

## 14. Open Questions

1. Which 2 to 3 crops and which region will the prototype cover?
2. What is the context (hackathon, college project, startup pitch) and the deadline?
3. How many people are on the team, and what are their skills (ML, frontend, backend)?
4. Web app (PWA) only, or is a native mobile app required?
5. Who can review the treatment content for agronomic correctness?
6. Is SMS or WhatsApp alerting needed, or are in-app and web push enough?
