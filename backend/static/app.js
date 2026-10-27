/**
 * CropGuard Frontend Client Application
 * Implements Features F1 through F24 as specified in CropGuard PRD v0.1 / v0.2
 */

// ================= GLOBAL STATE =================
let currentLang = 'hi'; // 'hi' or 'en'
let activeTab = 'scan';
let activeFieldId = null;
let currentScanId = null;
let currentScanData = null;
let selectedSampleType = 'tomato_early_blight';
let currentVoiceSpokenReply = '';
let leafletMap = null;
let zonesLayerGroup = null;
let pointsLayerGroup = null;
let recognition = null;
let isRecordingVoice = false;
let allFields = [];
let allDiseases = [];
let currentUserLat = 19.9975;
let currentUserLng = 73.7898;
let currentUserDistrict = "Nashik";
let currentUserState = "Maharashtra";
let currentUserVillage = "";

// ================= LOCALIZATION DICTIONARY (F4) =================
const I18N = {
  hi: {
    appName: "CropGuard",
    appSubtitle: "फसल रोग व कीट प्रारंभिक पहचान एवं नुकसान रोकथाम",
    langBtn: "English (EN)",
    tabScan: "रोग जांच व स्कैन (F1-F3)",
    tabRadar: "प्रकोप रडार (F15)",
    tabRisk: "मौसम जोखिम व सिमुलेटर (F16)",
    tabFields: "मेरे खेत व ट्विन (F19, F22)",
    tabCommunity: "किसान सहायता व विशेषज्ञ (F20)",
    tabMarket: "कृषि बाजार व सेंसर (F12-F14)",
    voiceSosTitle: "किसान वॉइस सहायता (Kisan Voice SOS)",
    voiceSosDesc: "हिंदी में अपनी फसल की समस्या बोलकर बताएं। तुरंत सलाह प्राप्त करें।",
    openVoiceBtn: "बोलकर पूछें (Voice Search)",
    leafPhotoTitle: "रोगग्रस्त पत्ती की फोटो लें",
    coreFlowTag: "3-टैप त्वरित जांच",
    uploadBtn: "गैलरी से चुनें",
    takePhotoBtn: "कैमरे से फोटो लें",
    quickSamplesTitle: "या वास्तविक कृषि परीक्षण सैंपल चुनें:",
    analyzeBtn: "समस्या व समाधान जानें (Detect Problem)",
    severityHeader: "गंभीरता स्तर (Severity)",
    confidenceHeader: "AI सटीकता (Confidence)",
    followupHeader: "अनुवर्ती जांच (Follow-up)",
    symptomsTitle: "पहचाने गए लक्षण: ",
    readAloudBtn: "बोलकर सुनें",
    treatmentsTitle: "प्रमाणित कृषि उपचार (ICAR दिशानिर्देश)",
    feedbackAsk: "क्या यह जांच सही है?",
    btnPlan: "स्मार्ट योजना (F21)",
    btnSpray: "स्प्रे दर्ज करें (F9)",
    radarTitle: "सामुदायिक प्रकोप रडार (1 km ग्रिड)",
    demoStatus: "विलेज आउटब्रेक सिमुलेटर (F23) तैयार है। रडार अपडेट देखने के लिए रिपोर्ट इंजेक्ट करें।",
    injectBtn: "⚡ आउटब्रेक इंजेक्ट करें",
    riskMeterTitle: "खेत मौसम जोखिम स्कोर",
    factorsTitle: "जोखिम के मुख्य मौसम कारक",
    whatIfTitle: "मौसम जोखिम सिमुलेटर (What-If)",
    twinTitle: "फसल मौसम परिदृश्य सिम्युलेटर: खेत निरीक्षण प्राथमिकता (F19 - सिम्युलेटेड)",
    passportTitle: "फसल स्वास्थ्य पासपोर्ट (Crop Health Passport)"
  },
  en: {
    appName: "CropGuard",
    appSubtitle: "AI Early Detection & Crop Loss Prevention",
    langBtn: "हिंदी (HI)",
    tabScan: "Diagnose & Scan (F1-F3)",
    tabRadar: "Outbreak Radar (F15)",
    tabRisk: "Weather Risk & What-If (F16)",
    tabFields: "My Fields & Scenarios (F19, F22)",
    tabCommunity: "Crop Rescue & Expert (F20)",
    tabMarket: "Market & Sensors (F12-F14)",
    voiceSosTitle: "Kisan Voice SOS (F18)",
    voiceSosDesc: "Speak your crop problem in Hindi or English. Get voice diagnosis & advice.",
    openVoiceBtn: "Voice Search (बोलें)",
    leafPhotoTitle: "Photograph Sick Leaf",
    coreFlowTag: "Flow A: 3-Tap Scan",
    uploadBtn: "Upload Photo",
    takePhotoBtn: "Take Photo",
    quickSamplesTitle: "Or Select Real Agronomic Test Sample:",
    analyzeBtn: "Detect Problem & Get Solution",
    severityHeader: "Severity Level",
    confidenceHeader: "AI Confidence",
    followupHeader: "Follow-up Scan",
    symptomsTitle: "Identified Symptoms: ",
    readAloudBtn: "Read Aloud",
    treatmentsTitle: "Verified Agronomic Treatments (ICAR Guidelines)",
    feedbackAsk: "Confirm Diagnosis:",
    btnPlan: "Smart Plan (F21)",
    btnSpray: "Log Spray (F9)",
    radarTitle: "Community Outbreak Radar (1 km Grid Snapped)",
    demoStatus: "Village Outbreak Simulator (F23) is ready. Inject a report to observe real-time map recoloring.",
    injectBtn: "⚡ Inject Outbreak",
    riskMeterTitle: "Field Weather Risk Score",
    factorsTitle: "Top Contributing Factors Behind Risk",
    whatIfTitle: "Early Risk Predictor: What-If Simulator",
    twinTitle: "Crop Weather Scenario Simulator: Field Inspection Priority (F19 - Simulated)",
    passportTitle: "Crop Health Passport (Field Timeline)"
  }
};

// ================= APP INITIALIZATION =================
document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) lucide.createIcons();
  
  // Set default sowing date in modal
  const dtInput = document.getElementById('new-field-date');
  if (dtInput) dtInput.value = new Date().toISOString().split('T')[0];

  // Register Service Worker for PWA (F10)
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js').catch(err => console.log('SW reg error:', err));
  }

  // Load baseline reference data
  await loadFields();
  await loadDiseases();
  await loadAlerts();
  
  // Initialize Leaflet map
  initOutbreakRadarMap();

  // Check user session & prompt login if not authenticated
  const savedUserStr = localStorage.getItem('cropguard_user');
  if (savedUserStr) {
    try {
      const savedUser = JSON.parse(savedUserStr);
      currentUserLat = savedUser.latitude || 19.9975;
      currentUserLng = savedUser.longitude || 73.7898;
      currentUserDistrict = savedUser.district || "Nashik";
      currentUserState = savedUser.state || "Maharashtra";
      updateUserInterface(savedUser);
    } catch (e) {
      console.warn("User restore error:", e);
      openLoginModal();
    }
  } else {
    // Open login modal on first visit to detect location
    openLoginModal();
  }
});

// ================= FARMER LOGIN & LOCATION SERVICE =================
function openLoginModal() {
  const modal = document.getElementById('modal-login');
  if (modal) modal.classList.remove('hidden');
  detectUserLocation();
  if (window.lucide) lucide.createIcons();
}

function closeLoginModal() {
  const modal = document.getElementById('modal-login');
  if (modal) modal.classList.add('hidden');
}

function detectUserLocation() {
  const placeLbl = document.getElementById('lbl-detected-place');
  const coordsLbl = document.getElementById('lbl-detected-coords');
  const badge = document.getElementById('badge-gps-verified');

  if (placeLbl) placeLbl.innerHTML = '<i data-lucide="map-pin" class="w-4 h-4 text-amber-500 animate-pulse"></i><span>Acquiring GPS farm coordinates...</span>';
  if (window.lucide) lucide.createIcons();

  if (!navigator.geolocation) {
    applyFallbackLocation("Geolocation not supported by this browser.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      currentUserLat = position.coords.latitude;
      currentUserLng = position.coords.longitude;

      if (coordsLbl) coordsLbl.innerText = `Lat: ${currentUserLat.toFixed(4)}, Lng: ${currentUserLng.toFixed(4)}`;

      try {
        const res = await fetch(`/auth/location/reverse?lat=${currentUserLat}&lng=${currentUserLng}`);
        const data = await res.json();
        currentUserDistrict = data.district || "Nashik";
        currentUserState = data.state || "Maharashtra";
        currentUserVillage = data.village || "";

        if (placeLbl) {
          placeLbl.innerHTML = `<i data-lucide="map-pin" class="w-4 h-4 text-emerald-600"></i><span>${data.display_name}</span>`;
        }
        if (badge) badge.classList.remove('hidden');
      } catch (err) {
        if (placeLbl) placeLbl.innerHTML = `<i data-lucide="map-pin" class="w-4 h-4 text-emerald-600"></i><span>GPS Fix Active (${currentUserLat.toFixed(3)}, ${currentUserLng.toFixed(3)})</span>`;
        if (badge) badge.classList.remove('hidden');
      }
      if (window.lucide) lucide.createIcons();
    },
    (err) => {
      console.warn("Geolocation warning:", err.message);
      applyFallbackLocation("Location permission denied/unavailable. Using Nashik (MH) baseline.");
    },
    { enableHighAccuracy: true, timeout: 8000, maximumAge: 60000 }
  );
}

function applyFallbackLocation(message) {
  currentUserLat = 19.9975;
  currentUserLng = 73.7898;
  currentUserDistrict = "Nashik";
  currentUserState = "Maharashtra";

  const placeLbl = document.getElementById('lbl-detected-place');
  const coordsLbl = document.getElementById('lbl-detected-coords');
  if (placeLbl) placeLbl.innerHTML = `<i data-lucide="map-pin" class="w-4 h-4 text-slate-500"></i><span>Nashik, Maharashtra</span>`;
  if (coordsLbl) coordsLbl.innerText = `Lat: 19.9975, Lng: 73.7898 (${message})`;
  if (window.lucide) lucide.createIcons();
}

async function requestLoginOtp() {
  const phone = document.getElementById('login-phone').value.trim();
  if (!phone || phone.length < 10) {
    alert("Please enter a valid 10-digit mobile number.");
    return;
  }
  const btn = document.getElementById('btn-request-otp');
  if (btn) btn.innerText = "Sending...";
  try {
    const res = await fetch('/auth/otp/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const data = await res.json();
    alert(`📲 OTP Sent successfully to +91 ${phone}!\n\nFor prototype demo, enter Demo OTP: ${data.mock_otp || '123456'}`);
  } catch (err) {
    alert("Error sending OTP: " + err.message);
  } finally {
    if (btn) btn.innerText = "Send OTP";
  }
}

async function submitLogin() {
  const phone = document.getElementById('login-phone').value.trim();
  const otp = document.getElementById('login-otp').value.trim();
  const name = document.getElementById('login-farmer-name').value.trim();
  const consent = document.getElementById('login-consent-check')?.checked;

  if (!phone || phone.length < 10) {
    alert("Please enter a valid 10-digit mobile number.");
    return;
  }
  if (!otp) {
    alert("Please enter the 6-digit OTP (use 123456).");
    return;
  }
  if (!consent) {
    alert("Please consent to the location & privacy policy under DPDP Act 2023 to proceed.");
    return;
  }

  const btn = document.getElementById('btn-submit-login');
  if (btn) btn.innerText = "Verifying...";

  try {
    const res = await fetch('/auth/otp/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone: phone,
        otp: otp,
        name: name || "Farmer",
        latitude: currentUserLat,
        longitude: currentUserLng,
        district: currentUserDistrict,
        state: currentUserState
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Authentication failed");
    }

    const data = await res.json();
    localStorage.setItem('cropguard_user', JSON.stringify(data.user));
    localStorage.setItem('cropguard_token', data.token);

    updateUserInterface(data.user);
    closeLoginModal();

    // Re-center radar map on farmer's GPS coordinates
    if (leafletMap && data.user.latitude && data.user.longitude) {
      leafletMap.setView([data.user.latitude, data.user.longitude], 12);
    }

    alert(`🌾 Welcome, ${data.user.name}!\n\nYour farm location is set to ${data.user.district}, ${data.user.state} (${data.user.latitude.toFixed(3)}, ${data.user.longitude.toFixed(3)}). Real-time weather alerts and outbreak radar are now synchronized.`);
  } catch (err) {
    alert("Login failed: " + err.message);
  } finally {
    if (btn) btn.innerHTML = '<i data-lucide="log-in" class="w-4 h-4"></i><span>Verify & Enter Farm Dashboard (लॉगिन करें)</span>';
    if (window.lucide) lucide.createIcons();
  }
}

function updateUserInterface(user) {
  if (!user) return;
  const nameElem = document.getElementById('user-header-name');
  const distElem = document.getElementById('user-header-district');
  const initialsElem = document.getElementById('user-initials-badge');

  if (nameElem) nameElem.innerText = user.name || "Farmer";
  if (distElem) distElem.innerText = `${user.district || 'Nashik'}, ${user.state ? user.state.slice(0, 2).toUpperCase() : 'MH'}`;
  if (initialsElem && user.name) initialsElem.innerText = user.name.charAt(0).toUpperCase();
}

// ================= LANGUAGE TOGGLE (F4) =================
function toggleLanguage() {
  currentLang = currentLang === 'hi' ? 'en' : 'hi';
  document.getElementById('lang-btn-text').innerText = I18N[currentLang].langBtn;
  applyLocalization();
  if (currentScanData) renderDiagnosisResult(currentScanData);
}

function applyLocalization() {
  const dict = I18N[currentLang];
  const mapping = {
    'tab-txt-scan': dict.tabScan,
    'tab-txt-radar': dict.tabRadar,
    'tab-txt-risk': dict.tabRisk,
    'tab-txt-fields': dict.tabFields,
    'tab-txt-community': dict.tabCommunity,
    'tab-txt-market': dict.tabMarket,
    'lbl-voice-sos-title': dict.voiceSosTitle,
    'lbl-voice-sos-desc': dict.voiceSosDesc,
    'btn-open-voice': dict.openVoiceBtn,
    'lbl-leaf-photo': dict.leafPhotoTitle,
    'lbl-core-flow': dict.coreFlowTag,
    'btn-upload-leaf': dict.uploadBtn,
    'btn-take-leaf': dict.takePhotoBtn,
    'lbl-quick-samples': dict.quickSamplesTitle,
    'btn-text-analyze': dict.analyzeBtn,
    'lbl-severity-header': dict.severityHeader,
    'lbl-confidence-header': dict.confidenceHeader,
    'lbl-followup-header': dict.followupHeader,
    'btn-read-aloud': dict.readAloudBtn,
    'lbl-treatments-title': dict.treatmentsTitle,
    'lbl-feedback-ask': dict.feedbackAsk,
    'btn-create-plan': dict.btnPlan,
    'btn-log-spray': dict.btnSpray,
    'lbl-radar-title': dict.radarTitle,
    'txt-demo-status': dict.demoStatus,
    'lbl-risk-meter-title': dict.riskMeterTitle,
    'lbl-factors-title': dict.factorsTitle,
    'lbl-whatif-title': dict.whatIfTitle,
    'lbl-twin-title': dict.twinTitle,
  };

  for (const [id, text] of Object.entries(mapping)) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
  }
}

// ================= TAB SWITCHING =================
function switchTab(tabId) {
  activeTab = tabId;
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.remove('active', 'border-brand-600', 'text-brand-700', 'font-semibold');
    b.classList.add('border-transparent', 'text-slate-600');
  });
  document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));

  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  const activeContent = document.getElementById(`tab-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.add('active', 'border-brand-600', 'text-brand-700', 'font-semibold');
    activeBtn.classList.remove('border-transparent', 'text-slate-600');
  }
  if (activeContent) activeContent.classList.remove('hidden');

  if (window.lucide) lucide.createIcons();

  // Tab specific refreshes
  if (tabId === 'radar') {
    setTimeout(() => {
      if (leafletMap) {
        leafletMap.invalidateSize();
        loadOutbreakRadar();
      }
    }, 200);
  } else if (tabId === 'risk') {
    loadFieldRisk();
  } else if (tabId === 'fields') {
    loadFieldPriority();
    loadTreatmentPlan();
    loadPassportTimeline();
  } else if (tabId === 'community') {
    loadCommunityReports();
  } else if (tabId === 'market') {
    loadSuppliers();
  }
}

// ================= FIELD MANAGEMENT =================
async function loadFields() {
  try {
    const res = await fetch('/fields');
    allFields = await res.json();
    const selector = document.getElementById('field-selector');
    selector.innerHTML = '';

    allFields.forEach((f, idx) => {
      const opt = document.createElement('option');
      opt.value = f.id;
      opt.innerText = `${f.name} (${f.area_acres} Ac)`;
      if (idx === 0) {
        opt.selected = true;
        activeFieldId = f.id;
      }
      selector.appendChild(opt);
    });

    // Populate modal crop choices
    const cropSel = document.getElementById('new-field-crop');
    if (cropSel && allFields.length > 0) {
      cropSel.innerHTML = `
        <option value="${allFields[0].crop_id}">Tomato (टमाटर)</option>
        <option value="${allFields[1] ? allFields[1].crop_id : allFields[0].crop_id}">Potato (आलू)</option>
      `;
    }

    updateFieldStatusBadge();
  } catch (err) {
    console.error('Failed to load fields:', err);
  }
}

function onFieldChange() {
  const sel = document.getElementById('field-selector');
  activeFieldId = sel.value;
  updateFieldStatusBadge();
  if (activeTab === 'fields') {
    loadPassportTimeline();
    loadTreatmentPlan();
  } else if (activeTab === 'risk') {
    loadFieldRisk();
  }
}

function updateFieldStatusBadge() {
  const field = allFields.find(f => f.id === activeFieldId);
  const badge = document.getElementById('field-status-badge');
  if (!field || !badge) return;

  badge.innerText = field.status.toUpperCase();
  if (field.status === 'infected') {
    badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-600 text-white';
  } else if (field.status === 'watch') {
    badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500 text-white';
  } else if (field.status === 'recovering') {
    badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-indigo-500 text-white';
  } else {
    badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-600 text-white';
  }
}

async function submitNewField() {
  const name = document.getElementById('new-field-name').value.trim();
  const cropId = document.getElementById('new-field-crop').value;
  const area = parseFloat(document.getElementById('new-field-area').value) || 1.5;
  const variety = document.getElementById('new-field-variety').value.trim();
  const sowingDate = document.getElementById('new-field-date').value;

  if (!name || !sowingDate) {
    alert('Please enter field name and sowing date.');
    return;
  }

  try {
    const res = await fetch('/fields', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        crop_id: cropId,
        name: name,
        variety: variety,
        area_acres: area,
        sowing_date: sowingDate,
        latitude: 20.012 + (Math.random() * 0.04),
        longitude: 73.810 + (Math.random() * 0.04)
      })
    });
    if (res.ok) {
      closeModal('modal-new-field');
      await loadFields();
      alert('Field created successfully!');
    }
  } catch (err) {
    alert('Failed to create field: ' + err.message);
  }
}

// ================= LEAF SAMPLE SELECTION & FILE UPLOAD =================
function selectSampleLeaf(sampleKey, displayName) {
  selectedSampleType = sampleKey;
  const preview = document.getElementById('leaf-preview');
  preview.src = `/sample_images/${sampleKey}.jpg`;
  preview.classList.remove('hidden');
  document.getElementById('leaf-placeholder').classList.add('hidden');
  const badge = document.getElementById('preview-tag-badge');
  if (badge) badge.classList.remove('hidden');
  document.getElementById('preview-tag').innerText = `Sample: ${displayName}`;
  document.getElementById('leaf-file-input').value = '';
  // Automatically trigger diagnosis for instant results
  runDiagnosis();
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    const preview = document.getElementById('leaf-preview');
    preview.src = e.target.result;
    preview.classList.remove('hidden');
    document.getElementById('leaf-placeholder').classList.add('hidden');
    const badge = document.getElementById('preview-tag-badge');
    if (badge) badge.classList.remove('hidden');
    document.getElementById('preview-tag').innerText = `Uploaded: ${file.name.slice(0, 16)}...`;
    selectedSampleType = null; // Use uploaded file
    // Automatically trigger real-time Gemini diagnosis upon image upload!
    runDiagnosis();
  };
  reader.readAsDataURL(file);
}

function triggerCameraCapture() {
  const input = document.getElementById('leaf-file-input');
  input.setAttribute('capture', 'environment');
  input.click();
}

// ================= RUN AI DIAGNOSIS (F1, F2, F3) =================
async function runDiagnosis() {
  const fileInput = document.getElementById('leaf-file-input');
  if (fileInput.files.length === 0 && !selectedSampleType) {
    document.getElementById('leaf-file-input').click();
    return;
  }

  const btn = document.getElementById('btn-run-diagnosis');
  const btnText = document.getElementById('btn-text-analyze');
  const forceUncertain = document.getElementById('check-force-uncertain')?.checked || false;

  btn.disabled = true;
  btnText.innerText = currentLang === 'hi' ? 'Google Gemini जांच रहा है...' : 'Gemini AI Detecting Problem...';

  // Show loading card, hide empty state and result card
  const emptyState = document.getElementById('diagnosis-empty-state');
  const loadingState = document.getElementById('diagnosis-loading-state');
  const resultCard = document.getElementById('diagnosis-result-card');

  if (emptyState) emptyState.classList.add('hidden');
  if (loadingState) loadingState.classList.remove('hidden');
  if (resultCard) resultCard.classList.add('hidden');

  try {
    const formData = new FormData();
    formData.append('field_id', activeFieldId || allFields[0]?.id || 'default');
    
    if (fileInput.files.length > 0) {
      formData.append('image', fileInput.files[0]);
    } else {
      formData.append('sample_type', selectedSampleType);
    }

    if (forceUncertain) {
      formData.append('force_uncertain', 'true');
    }

    const res = await fetch('/scans', {
      method: 'POST',
      body: formData
    });

    if (res.status === 422) {
      const errData = await res.json();
      const msg = errData.detail?.message || "Invalid image. Please photograph an active crop leaf.";
      const guidance = errData.detail?.guidance || "Ensure the camera is focused on a leaf against a neutral background.";
      
      if (loadingState) loadingState.classList.add('hidden');
      if (emptyState) emptyState.classList.remove('hidden');

      alert(`⚠️ Not a Crop Leaf:\n\n${msg}\n\nTip: ${guidance}`);
      return;
    }

    if (!res.ok) throw new Error('Diagnosis failed');
    const data = await res.json();
    currentScanId = data.scan_id;
    currentScanData = data;

    renderDiagnosisResult(data);

    // Show result card, hide loading
    if (loadingState) loadingState.classList.add('hidden');
    if (resultCard) resultCard.classList.remove('hidden');

    // Scroll to results smoothly
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // If uncertain, show second opinion banner
    const soBanner = document.getElementById('banner-second-opinion');
    if (data.requires_second_opinion) {
      soBanner.classList.remove('hidden');
    } else {
      soBanner.classList.add('hidden');
    }

  } catch (err) {
    if (loadingState) loadingState.classList.add('hidden');
    if (emptyState) emptyState.classList.remove('hidden');
    alert('Diagnosis error: ' + err.message);
  } finally {
    btn.disabled = false;
    btnText.innerText = (currentLang === 'hi') ? 'समस्या व समाधान जानें (Detect Problem)' : 'Detect Problem & Get Solution';
    if (window.lucide) lucide.createIcons();
  }
}

function renderDiagnosisResult(data) {
  const disease = data.top_disease;
  const isHi = (currentLang === 'hi');

  // Disease Names
  document.getElementById('diag-disease-name').innerText = disease ? disease.name_en : 'Unknown';
  document.getElementById('diag-disease-scientific').innerText = disease?.scientific_name || '';
  document.getElementById('diag-disease-hindi').innerText = disease?.name_hi || '';

  // Severity & Confidence
  const sevBadge = document.getElementById('diag-severity-badge');
  sevBadge.innerText = data.severity.toUpperCase();
  document.getElementById('diag-severity-pct').innerText = `${data.severity_pct}% Leaf Area Affected`;

  const sevBar = document.getElementById('severity-bar');
  sevBar.style.width = `${Math.min(data.severity_pct * 2, 100)}%`;

  if (data.severity === 'severe') {
    sevBadge.className = 'text-base font-black px-2 py-0.5 rounded uppercase bg-red-600 text-white';
    sevBar.className = 'bg-red-600 h-full rounded-full transition-all duration-700';
  } else if (data.severity === 'moderate') {
    sevBadge.className = 'text-base font-black px-2 py-0.5 rounded uppercase bg-amber-500 text-white';
    sevBar.className = 'bg-amber-500 h-full rounded-full transition-all duration-700';
  } else {
    sevBadge.className = 'text-base font-black px-2 py-0.5 rounded uppercase bg-emerald-600 text-white';
    sevBar.className = 'bg-emerald-600 h-full rounded-full transition-all duration-700';
  }

  const confVal = Math.round(data.top_confidence * 100);
  document.getElementById('diag-confidence-pct').innerText = `${confVal}%`;
  document.getElementById('confidence-bar').style.width = `${confVal}%`;

  // Symptoms
  document.getElementById('diag-symptoms-text').innerText = (isHi && disease?.symptoms_hi) ? disease.symptoms_hi : (disease?.symptoms_en || '');

  // Render Multi-Tier Treatments (F3)
  const container = document.getElementById('treatment-cards-container');
  container.innerHTML = '';

  data.treatments.forEach(t => {
    const card = document.createElement('div');
    const title = isHi ? t.title_hi : t.title_en;
    const instructions = isHi ? t.instructions_hi : t.instructions_en;
    const safety = isHi ? t.safety_notes_hi : t.safety_notes_en;

    let typeColor = 'bg-emerald-50 border-emerald-200 text-emerald-900';
    let typeTag = '🍃 Organic (जैविक)';
    if (t.type === 'chemical') {
      typeColor = 'bg-red-50 border-red-200 text-red-900';
      typeTag = '🧪 Chemical (रासायनिक)';
    } else if (t.type === 'cultural') {
      typeColor = 'bg-blue-50 border-blue-200 text-blue-900';
      typeTag = '🛡️ Cultural / Preventive';
    }

    card.className = `p-3.5 rounded-xl border ${typeColor} text-xs space-y-1.5 transition`;
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-[11px] uppercase tracking-wider">${typeTag}</span>
        <div class="flex items-center space-x-1">
          ${t.cibrc_status ? `<span class="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[9px] border border-emerald-300">✓ ${t.cibrc_status}</span>` : ''}
          ${t.pre_harvest_interval_days ? `<span class="bg-white/80 text-slate-800 font-bold px-2 py-0.5 rounded text-[10px] border border-slate-300">PHI: ${t.pre_harvest_interval_days}d</span>` : ''}
        </div>
      </div>
      <h5 class="font-bold text-sm text-slate-900">${title}</h5>
      <p class="text-slate-700 leading-relaxed">${instructions}</p>
      ${t.dosage ? `<div class="font-semibold text-[11px] text-slate-800"><b>Dosage:</b> ${t.dosage}</div>` : ''}
      ${safety ? `<div class="text-[10px] text-amber-900 bg-amber-500/10 p-1.5 rounded border border-amber-300/40">⚠️ <b>Safety Note:</b> ${safety}</div>` : ''}
      <div class="text-[10px] text-slate-500 italic pt-1 border-t border-black/5 flex items-center justify-between">
        <span>Source: ${t.source_name} • Audit: ${t.reviewed_by || 'ICAR Panel'}</span>
        <button onclick="speakText('${title.replace(/'/g, "")}')" class="text-slate-600 hover:text-slate-900"><i data-lucide="volume-2" class="w-3.5 h-3.5"></i></button>
      </div>
    `;
    container.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

// ================= TEXT-TO-SPEECH (TTS) (F4, FR-2.7) =================
function speakDiagnosisAdvice() {
  if (!currentScanData || !currentScanData.top_disease) return;
  const isHi = (currentLang === 'hi');
  const d = currentScanData.top_disease;
  
  let speechText = '';
  if (isHi) {
    speechText = `फसल जांच परिणाम: ${d.name_hi || d.name_en}। रोग की गंभीरता ${currentScanData.severity === 'severe' ? 'गंभीर' : 'मध्यम'} है और पत्तियों का लगभग ${Math.round(currentScanData.severity_pct)} प्रतिशत हिस्सा प्रभावित है। अनुशंसित उपचार: ${currentScanData.treatments[0]?.title_hi || currentScanData.treatments[0]?.title_en || 'जैविक नीम का छिड़काव करें।'}`;
  } else {
    speechText = `Diagnosis result: ${d.name_en}. Severity is ${currentScanData.severity} with ${Math.round(currentScanData.severity_pct)} percent leaf area affected. Recommended treatment: ${currentScanData.treatments[0]?.title_en || 'Apply recommended bio-spray.'}`;
  }

  speakText(speechText);
}

function speakText(text) {
  if (!window.speechSynthesis) {
    alert('Speech Synthesis not supported in this browser.');
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = (currentLang === 'hi') ? 'hi-IN' : 'en-IN';
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}

// ================= FEEDBACK LOOP (FR-2.8) =================
async function submitFeedback(status) {
  if (!currentScanId) return;
  try {
    const res = await fetch(`/scans/${currentScanId}/feedback`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_feedback: status })
    });
    if (res.ok) {
      alert(currentLang === 'hi' ? 'धन्यवाद! आपकी प्रतिक्रिया मॉडल सुधार के लिए दर्ज कर ली गई है।' : 'Thank you! Your feedback has been recorded for model improvement.');
    }
  } catch (err) {
    console.error(err);
  }
}

// ================= AI SECOND OPINION FLOW (F17) =================
function openSecondOpinionModal() {
  document.getElementById('modal-second-opinion').classList.remove('hidden');
}

async function submitSecondOpinion() {
  if (!currentScanId) {
    alert('Please execute a scan first.');
    return;
  }

  const stage = document.getElementById('so-growth-stage').value;
  const symptoms = [];
  document.querySelectorAll('input[name="so-symptom"]:checked').forEach(c => symptoms.push(c.value));

  try {
    const res = await fetch(`/scans/${currentScanId}/second-opinion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        growth_stage: stage,
        symptoms_reported: symptoms,
        leaf_underside_url: "/sample_images/tomato_late_blight.jpg"
      })
    });

    const data = await res.json();
    closeModal('modal-second-opinion');

    // Update diagnosis card with resolved opinion
    if (data.recommended_disease && currentScanData) {
      currentScanData.top_disease = data.recommended_disease;
      currentScanData.top_confidence = data.final_confidence;
      currentScanData.requires_second_opinion = false;
      renderDiagnosisResult(currentScanData);
    }

    alert(`AI Second Opinion: ${data.message}\nTop Candidate: ${data.rescored_predictions[0].disease_name} (${Math.round(data.final_confidence*100)}%)`);
  } catch (err) {
    alert('Second opinion error: ' + err.message);
  }
}

async function escalateToExpert() {
  if (!currentScanId) return;
  try {
    const res = await fetch(`/scans/${currentScanId}/escalate`, { method: 'POST' });
    const data = await res.json();
    alert(data.message);
  } catch (err) {
    alert('Escalation failed: ' + err.message);
  }
}

// ================= KISAN VOICE SOS (F18) =================
function openVoiceSosModal() {
  document.getElementById('modal-voice-sos').classList.remove('hidden');
}

function toggleVoiceRecording() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    // If not supported, simulate voice query
    simulateVoiceQuery("मेरे टमाटर के पत्तों पर काले गोल छल्लेदार धब्बे दिख रहे हैं और निचली पत्तियां सूख रही हैं");
    return;
  }

  if (!recognition) {
    recognition = new SpeechRecognition();
    recognition.lang = (currentLang === 'hi') ? 'hi-IN' : 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      isRecordingVoice = true;
      document.getElementById('voice-recording-status').innerText = (currentLang === 'hi') ? 'सुन रहा हूँ... बोलिए' : 'Listening... Speak now';
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      simulateVoiceQuery(transcript);
    };

    recognition.onerror = () => {
      isRecordingVoice = false;
      document.getElementById('voice-recording-status').innerText = 'Microphone ready. Tap to speak.';
    };

    recognition.onend = () => {
      isRecordingVoice = false;
    };
  }

  if (isRecordingVoice) {
    recognition.stop();
  } else {
    recognition.start();
  }
}

async function simulateVoiceQuery(transcriptText) {
  const statusEl = document.getElementById('voice-recording-status');
  statusEl.innerText = (currentLang === 'hi') ? `जांच: "${transcriptText.slice(0, 30)}..."` : `Processing query...`;

  try {
    const res = await fetch('/voice-reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        language: currentLang,
        transcript: transcriptText,
        field_id: activeFieldId
      })
    });

    const data = await res.json();
    currentVoiceSpokenReply = data.spoken_reply;

    const replyCard = document.getElementById('voice-reply-card');
    replyCard.classList.remove('hidden');
    document.getElementById('voice-reply-text').innerText = data.text_reply;

    // Automatically speak reply back to farmer (F18)
    speakText(data.spoken_reply);

  } catch (err) {
    alert('Voice processing failed: ' + err.message);
  }
}

// ================= OUTBREAK RADAR & LEAFLET MAP (F7, F15) =================
function initOutbreakRadarMap() {
  const mapContainer = document.getElementById('radar-map');
  if (!mapContainer || leafletMap) return;

  // Center on Nashik agricultural belt, Maharashtra
  leafletMap = L.map('radar-map', {
    center: [20.00, 73.80],
    zoom: 11,
    zoomControl: true
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors | CropGuard Radar'
  }).addTo(leafletMap);

  zonesLayerGroup = L.layerGroup().addTo(leafletMap);
  pointsLayerGroup = L.layerGroup().addTo(leafletMap);
}

async function loadOutbreakRadar() {
  if (!leafletMap) initOutbreakRadarMap();
  const crop = document.getElementById('radar-filter-crop').value;
  const days = document.getElementById('radar-filter-days').value;

  try {
    const [radarRes, pointsRes] = await Promise.all([
      fetch(`/radar?crop=${crop}&days=${days}`),
      fetch(`/outbreaks?crop=${crop}&days=${days}`)
    ]);

    const radarData = await radarRes.json();
    const pointsData = await pointsRes.json();

    // Update Counts
    document.getElementById('radar-confirmed-count').innerText = radarData.summary.total_confirmed_cases;
    document.getElementById('radar-suspected-count').innerText = radarData.summary.total_suspected_cases;
    document.getElementById('radar-alerts-count').innerText = radarData.summary.active_outbreak_alerts;

    // Clear existing
    zonesLayerGroup.clearLayers();
    pointsLayerGroup.clearLayers();

    // Render Risk Zones (F15)
    radarData.zones.forEach(z => {
      let zoneColor = '#22c55e'; // green
      if (z.risk_level === 'red') zoneColor = '#ef4444';
      else if (z.risk_level === 'amber') zoneColor = '#f59e0b';

      const circle = L.circle([z.center_lat, z.center_lng], {
        color: zoneColor,
        fillColor: zoneColor,
        fillOpacity: z.risk_level === 'red' ? 0.35 : 0.22,
        radius: (z.radius_km || 10) * 1000,
        weight: 2
      });

      const popupHtml = `
        <div class="text-xs p-1 space-y-1 font-sans">
          <div class="flex items-center justify-between">
            <span class="font-bold text-sm text-slate-900">${z.disease_name}</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold text-white uppercase" style="background:${zoneColor}">${z.risk_level} Zone</span>
          </div>
          <div class="text-slate-600 font-semibold">${z.disease_name_hi || ''}</div>
          <div class="grid grid-cols-2 gap-1 pt-1 text-[11px] border-t border-slate-100">
            <div>Confirmed: <b class="text-slate-900">${z.confirmed_count}</b></div>
            <div>Suspected: <b class="text-slate-900">${z.suspected_count}</b></div>
          </div>
          <div class="text-[11px]">7-Day Trend: <b>${z.trend.toUpperCase()}</b></div>
          <div class="text-[10px] text-amber-900 bg-amber-50 p-1.5 rounded mt-1">
            ⚠️ <b>Advisory:</b> Spores active within ${z.radius_km} km. Inspect your fields and prepare prophylactic bio-fungicide.
          </div>
        </div>
      `;
      circle.bindPopup(popupHtml);
      zonesLayerGroup.addLayer(circle);
    });

    // Render Scan Points (FR-6.1)
    pointsData.reports.forEach(p => {
      const isConfirmed = (p.report_status === 'confirmed');
      const markerColor = isConfirmed ? '#dc2626' : '#d97706';

      const marker = L.circleMarker([p.latitude, p.longitude], {
        radius: isConfirmed ? 7 : 5,
        fillColor: markerColor,
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
      });

      marker.bindPopup(`
        <div class="text-xs p-1">
          <b>${p.disease_name}</b> (${p.crop_name})<br>
          Status: <b>${p.report_status.toUpperCase()}</b><br>
          Severity: ${p.severity}<br>
          <span class="text-[10px] text-slate-400">Snapped to 1 km privacy grid</span>
        </div>
      `);
      pointsLayerGroup.addLayer(marker);
    });

  } catch (err) {
    console.error('Failed to load radar data:', err);
  }
}

// ================= VILLAGE OUTBREAK SIMULATION (F23 - JUDGE DEMO MODE) =================
function openSimulationModal() {
  document.getElementById('modal-village-sim').classList.remove('hidden');
}

async function executeVillageSimulation() {
  const selVillage = document.getElementById('sim-village');
  const selectedOpt = selVillage.options[selVillage.selectedIndex];
  const villageName = selectedOpt.value;
  const lat = parseFloat(selectedOpt.dataset.lat);
  const lng = parseFloat(selectedOpt.dataset.lng);
  const diseaseId = document.getElementById('sim-disease').value || allDiseases[1]?.id;
  const intensity = parseInt(document.getElementById('sim-intensity').value) || 6;
  const cropId = allFields[0]?.crop_id || '';

  try {
    const res = await fetch('/admin/simulations/village', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        village_name: villageName,
        center_lat: lat,
        center_lng: lng,
        crop_id: cropId,
        disease_id: diseaseId,
        intensity: intensity
      })
    });

    const data = await res.json();
    closeModal('modal-village-sim');
    alert(data.message);

    // Switch to radar map and refresh
    switchTab('radar');
    await loadOutbreakRadar();
    await loadAlerts();

  } catch (err) {
    alert('Simulation injection failed: ' + err.message);
  }
}

async function resetSimulations() {
  if (!confirm('Reset all simulated village outbreaks and restore baseline state?')) return;
  try {
    const res = await fetch('/admin/simulations', { method: 'DELETE' });
    const data = await res.json();
    alert(data.message);
    if (activeTab === 'radar') loadOutbreakRadar();
    await loadAlerts();
  } catch (err) {
    alert('Reset failed: ' + err.message);
  }
}

// ================= EARLY RISK & WHAT-IF SIMULATOR (F6, F16) =================
async function loadFieldRisk() {
  if (!activeFieldId) return;
  try {
    const res = await fetch(`/fields/${activeFieldId}/risk`);
    const data = await res.json();
    const r = data.risk_assessment;

    document.getElementById('txt-risk-score').innerText = r.score;
    document.getElementById('risk-level-badge').innerText = `${r.level.toUpperCase()} RISK`;
    document.getElementById('risk-targeted-pathogen').innerText = `Target Pathogen: ${r.disease_name}`;

    // Update gauge stroke
    const circle = document.getElementById('risk-circle-path');
    if (circle) circle.setAttribute('stroke-dasharray', `${r.score}, 100`);

    // Weather readings
    const w = data.current_weather;
    document.getElementById('txt-weather-temp').innerText = `${w.temp_c.toFixed(1)} °C`;
    document.getElementById('txt-weather-humidity').innerText = `${w.humidity_pct.toFixed(0)} %`;
    document.getElementById('txt-weather-rain').innerText = `${w.rainfall_mm.toFixed(1)} mm`;
    document.getElementById('txt-weather-wetness').innerText = `${w.leaf_wetness_hrs.toFixed(1)} Hours`;

    // Render contributing factors
    const container = document.getElementById('factors-list-container');
    container.innerHTML = '';
    r.factors.forEach(f => {
      const div = document.createElement('div');
      div.className = 'p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start space-x-3 text-xs';
      div.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-slate-800 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">${f.weight}</div>
        <div>
          <h4 class="font-bold text-slate-900">${f.factor}</h4>
          <p class="text-slate-600">${f.impact}</p>
        </div>
      `;
      container.appendChild(div);
    });

  } catch (err) {
    console.error('Failed to load risk:', err);
  }
}

async function runWhatIfSimulation() {
  const temp = parseFloat(document.getElementById('slider-temp').value);
  const humidity = parseFloat(document.getElementById('slider-humidity').value);
  const rain = parseFloat(document.getElementById('slider-rain').value);

  document.getElementById('val-slider-temp').innerText = `${temp.toFixed(1)} °C`;
  document.getElementById('val-slider-humidity').innerText = `${humidity.toFixed(0)} %`;
  document.getElementById('val-slider-rain').innerText = `${rain.toFixed(1)} mm`;

  try {
    const res = await fetch(`/fields/${activeFieldId || allFields[0]?.id}/risk-assessments/what-if`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        temperature_c: temp,
        humidity_pct: humidity,
        rainfall_mm: rain
      })
    });

    const data = await res.json();
    document.getElementById('whatif-score-badge').innerText = `Simulated Risk: ${data.score} / 100 (${data.level.toUpperCase()})`;
    document.getElementById('whatif-advisory-title').innerText = `Estimated Agronomic Risk Outcome: ${data.level.toUpperCase()} (${data.score}/100)`;
    document.getElementById('whatif-advisory-desc').innerText = data.preventive_actions.join(' • ');

  } catch (err) {
    console.error('What-if error:', err);
  }
}

// ================= FARM DIGITAL TWIN & FIELD PRIORITY (F19) =================
async function loadFieldPriority() {
  try {
    const res = await fetch('/fields/priority');
    const list = await res.json();
    const tbody = document.getElementById('field-priority-tbody');
    tbody.innerHTML = '';

    list.forEach((f, idx) => {
      let badgeClass = 'bg-red-100 text-red-800 border-red-200';
      if (f.priority_score < 60) badgeClass = 'bg-emerald-100 text-emerald-800 border-emerald-200';
      else if (f.priority_score < 80) badgeClass = 'bg-amber-100 text-amber-800 border-amber-200';

      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-50 transition';
      tr.innerHTML = `
        <td class="py-3 px-3 font-bold text-slate-900">${f.field_name}</td>
        <td class="py-3 px-3 text-slate-600">${f.crop_name}</td>
        <td class="py-3 px-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${badgeClass}">
            ${f.priority_level}
          </span>
        </td>
        <td class="py-3 px-3 text-slate-700">${f.reason}</td>
        <td class="py-3 px-3 text-right">
          <button onclick="selectFieldAndScan('${f.field_id}')" class="bg-brand-50 hover:bg-brand-100 text-brand-800 font-bold px-2.5 py-1 rounded-lg text-[11px] border border-brand-200">
            Inspect Now
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Failed to load field priority:', err);
  }
}

function selectFieldAndScan(fId) {
  activeFieldId = fId;
  const sel = document.getElementById('field-selector');
  if (sel) sel.value = fId;
  updateFieldStatusBadge();
  switchTab('scan');
}

// ================= SMART TREATMENT PLANNER (F21) =================
async function generatePlanFromScan() {
  if (!currentScanId) {
    alert('Please execute a scan first.');
    return;
  }
  try {
    const res = await fetch(`/scans/${currentScanId}/treatment-plan`, { method: 'POST' });
    const data = await res.json();
    alert(`Smart Treatment Plan generated with ${data.steps_count} stepwise prevention actions!`);
    switchTab('fields');
    await loadTreatmentPlan();
  } catch (err) {
    alert('Plan generation error: ' + err.message);
  }
}

async function loadTreatmentPlan() {
  const container = document.getElementById('plan-steps-container');
  if (!container) return;

  const mockSteps = [
    { order: 1, phase: 'Inspect', desc: 'Field Scouting: Walk plot diagonals to tag initial infected clusters.', cost: '₹0', done: true },
    { order: 2, phase: 'Sanitation', desc: 'Canopy Hygiene: Prune lower leaves touching soil; burn outside field.', cost: '₹150', done: true },
    { order: 3, phase: 'Cultural', desc: 'Drip Optimization: Stop sprinkler canopy wetting; increase row airflow.', cost: '₹0', done: false },
    { order: 4, phase: 'Organic', desc: 'Bio-Fungicide: Spray Neem Azadirachtin (1500 ppm @ 3 ml/L).', cost: '₹450', done: false },
    { order: 5, phase: 'Chemical', desc: 'Targeted Intervention: If lesions exceed 20%, spray Mancozeb 75% WP @ 2.5 g/L.', cost: '₹680', done: false, expert: true }
  ];

  container.innerHTML = '';
  mockSteps.forEach(s => {
    const div = document.createElement('div');
    div.className = `p-3 rounded-xl border ${s.done ? 'bg-emerald-50 border-emerald-200' : 'bg-slate-50 border-slate-200'} flex items-start justify-between text-xs`;
    div.innerHTML = `
      <div class="flex items-start space-x-2.5">
        <input type="checkbox" ${s.done ? 'checked' : ''} class="mt-0.5 rounded text-brand-600 focus:ring-brand-500 cursor-pointer">
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-bold text-[10px] uppercase text-brand-800">Step ${s.order}: ${s.phase}</span>
            ${s.expert ? '<span class="bg-red-100 text-red-800 text-[9px] font-bold px-1.5 py-0.2 rounded">Requires Expert</span>' : ''}
          </div>
          <p class="text-slate-800 mt-0.5">${s.desc}</p>
        </div>
      </div>
      <span class="font-mono font-bold text-slate-700 ml-2">${s.cost}</span>
    `;
    container.appendChild(div);
  });
}

// ================= LOSS-AVOIDANCE CALCULATOR (F24) =================
const LOSS_BENCHMARKS = {
  tomato_early_blight: { early: 5.0, perDay: 3.5, max: 35.0, label: "Tomato Early Blight" },
  tomato_late_blight: { early: 10.0, perDay: 9.0, max: 70.0, label: "Tomato Late Blight" },
  potato_late_blight: { early: 12.0, perDay: 9.5, max: 75.0, label: "Potato Late Blight" },
  wheat_rust: { early: 8.0, perDay: 6.0, max: 50.0, label: "Wheat Yellow Rust" },
  abiotic: { early: 3.0, perDay: 2.0, max: 18.0, label: "Nutrient Deficiency" }
};

function applyLossBenchmark() {
  recalculateLossSavings();
}

async function recalculateLossSavings() {
  const cropVal = parseFloat(document.getElementById('input-crop-value').value);
  const treatCost = parseFloat(document.getElementById('input-treat-cost').value);
  const delayDays = parseInt(document.getElementById('input-delay-days').value);

  const benchSelect = document.getElementById('loss-benchmark-disease');
  const benchKey = benchSelect ? benchSelect.value : 'tomato_early_blight';
  const bench = LOSS_BENCHMARKS[benchKey] || LOSS_BENCHMARKS.tomato_early_blight;

  const earlyLossPct = bench.early;
  const delayedLossPct = Math.min(bench.early + (delayDays * bench.perDay), bench.max);

  document.getElementById('val-loss-cropval').innerText = `₹ ${cropVal.toLocaleString('en-IN')}`;
  document.getElementById('val-loss-treatcost').innerText = `₹ ${treatCost.toLocaleString('en-IN')}`;
  document.getElementById('val-loss-delay').innerText = `${delayDays} Days Delay`;

  const explElem = document.getElementById('txt-loss-explanation');
  if (explElem) {
    explElem.innerText = `Early treatment limits ${bench.label} yield loss to ${earlyLossPct}% vs ${Math.round(delayedLossPct)}% if delayed ${delayDays} days.`;
  }

  try {
    const res = await fetch(`/fields/${activeFieldId || allFields[0]?.id}/loss-scenarios`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        crop_value_inr: cropVal,
        treatment_cost_inr: treatCost,
        loss_pct_if_early: earlyLossPct,
        loss_pct_if_delayed: delayedLossPct,
        delay_days: delayDays
      })
    });

    const data = await res.json();
    document.getElementById('txt-estimated-savings').innerText = `₹ ${Math.round(data.estimated_difference_inr).toLocaleString('en-IN')}`;
  } catch (err) {
    console.error('Loss calc error:', err);
  }
}

// ================= CROP HEALTH PASSPORT (F22) =================
async function loadPassportTimeline() {
  if (!activeFieldId) return;
  try {
    const res = await fetch(`/fields/${activeFieldId}/passport`);
    const data = await res.json();
    const container = document.getElementById('passport-timeline-container');
    container.innerHTML = '';

    data.timeline.forEach(e => {
      const item = document.createElement('div');
      item.className = 'relative pl-2 text-xs space-y-1';
      
      let dotColor = 'bg-brand-600';
      if (e.event_type === 'alert') dotColor = 'bg-red-500';
      else if (e.event_type === 'treatment') dotColor = 'bg-indigo-600';

      item.innerHTML = `
        <div class="absolute -left-6 top-1 w-3 h-3 rounded-full ${dotColor} border-2 border-white shadow"></div>
        <div class="flex items-center space-x-2">
          <span class="font-bold text-slate-900">${e.title}</span>
          <span class="text-[10px] text-slate-400 font-mono">${new Date(e.timestamp).toLocaleDateString()}</span>
        </div>
        <p class="text-slate-600">${e.notes || ''}</p>
        ${e.image_url ? `<img src="${e.image_url}" class="w-16 h-16 rounded-lg object-cover border mt-1">` : ''}
      `;
      container.appendChild(item);
    });

  } catch (err) {
    console.error('Failed to load passport:', err);
  }
}

function downloadPassportPdf() {
  if (!activeFieldId) return;
  window.open(`/fields/${activeFieldId}/passport/export`, '_blank');
}

// ================= SPRAY RECORDS (F9) =================
function openSprayLogModal() {
  document.getElementById('modal-spray-log').classList.remove('hidden');
}

async function submitSprayLog() {
  if (!activeFieldId) return;
  const prod = document.getElementById('spray-product-name').value;
  const activeIng = document.getElementById('spray-active-ingredient').value;
  const dose = document.getElementById('spray-dose').value;
  const cost = parseFloat(document.getElementById('spray-cost').value) || 0;

  try {
    const res = await fetch(`/fields/${activeFieldId}/treatment-logs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_name: prod,
        active_ingredient: activeIng,
        dose_applied: dose,
        applied_on: new Date().toISOString().split('T')[0],
        cost_inr: cost
      })
    });

    const data = await res.json();
    closeModal('modal-spray-log');

    if (data.warning) {
      alert(`⚠️ ${data.warning}`);
    } else {
      alert('Spray record saved successfully to Crop Health Passport!');
    }

    if (activeTab === 'fields') loadPassportTimeline();
  } catch (err) {
    alert('Spray log error: ' + err.message);
  }
}

// ================= COMMUNITY RESCUE NETWORK (F20) =================
function switchCommunitySubTab(sub) {
  if (sub === 'feed') {
    document.getElementById('subtab-feed').classList.remove('hidden');
    document.getElementById('subtab-expert').classList.add('hidden');
    document.getElementById('btn-sub-feed').className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-brand-600 text-white';
    document.getElementById('btn-sub-expert').className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-100 text-slate-700 hover:bg-slate-200';
    loadCommunityReports();
  } else {
    document.getElementById('subtab-feed').classList.add('hidden');
    document.getElementById('subtab-expert').classList.remove('hidden');
    document.getElementById('btn-sub-expert').className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-brand-600 text-white';
    document.getElementById('btn-sub-feed').className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-100 text-slate-700 hover:bg-slate-200';
    loadExpertTickets();
  }
}

async function loadCommunityReports() {
  try {
    const res = await fetch('/community/reports');
    const reports = await res.json();
    const container = document.getElementById('community-reports-container');
    container.innerHTML = '';

    reports.forEach(r => {
      const card = document.createElement('div');
      card.className = 'bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3 text-xs';
      
      let solHtml = '';
      r.solutions.forEach(s => {
        solHtml += `
          <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 mt-2">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-900">${s.author_name} (${s.author_role})</span>
              ${s.is_expert_verified ? '<span class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-1.5 py-0.5 rounded">✓ ICAR Expert Verified</span>' : ''}
            </div>
            <p class="text-slate-700">${s.body}</p>
            <div class="flex items-center space-x-3 text-[11px] pt-1 text-slate-500">
              <button onclick="voteSolution('${r.id}', '${s.id}', 'improved')" class="hover:text-emerald-700">👍 Improved (${s.improved_count})</button>
              <button onclick="voteSolution('${r.id}', '${s.id}', 'no_change')" class="hover:text-amber-700">😐 No Change (${s.no_change_count})</button>
              <button onclick="voteSolution('${r.id}', '${s.id}', 'worse')" class="hover:text-red-700">👎 Worse (${s.worse_count})</button>
            </div>
          </div>
        `;
      });

      card.innerHTML = `
        <div class="flex items-start justify-between">
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-full bg-brand-600 text-white font-bold flex items-center justify-center">F</div>
            <div>
              <div class="font-bold text-slate-900">${r.author_name}</div>
              <div class="text-[10px] text-slate-400">${r.author_district} • ${new Date(r.created_at).toLocaleDateString()}</div>
            </div>
          </div>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase ${r.status === 'verified' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">${r.status}</span>
        </div>
        <p class="text-slate-800 font-medium">${r.symptoms_text}</p>
        <img src="${r.scan_image_url}" class="w-full h-36 object-cover rounded-xl border">
        <div class="pt-2">
          <span class="font-bold text-slate-700 text-[11px]">Solutions & Verified Treatments (${r.solutions.length}):</span>
          ${solHtml}
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error('Failed to load community reports:', err);
  }
}

async function voteSolution(reportId, solId, outcome) {
  try {
    await fetch(`/community/reports/${reportId}/solutions?solution_id=${solId}&outcome_vote=${outcome}`, { method: 'POST' });
    loadCommunityReports();
  } catch (err) {
    console.error('Vote failed:', err);
  }
}

function openNewCommunityReportModal() {
  document.getElementById('modal-community-post').classList.remove('hidden');
}

async function submitCommunityPost() {
  const text = document.getElementById('comm-symptoms-text').value.trim();
  if (!text) return;
  try {
    await fetch('/community/reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        field_id: activeFieldId,
        symptoms_text: text
      })
    });
    closeModal('modal-community-post');
    loadCommunityReports();
  } catch (err) {
    alert('Failed to post request: ' + err.message);
  }
}

// ================= EXPERT TICKETS (F11) =================
async function loadExpertTickets() {
  try {
    const res = await fetch('/expert/tickets');
    const tickets = await res.json();
    const container = document.getElementById('expert-tickets-container');
    container.innerHTML = '';

    tickets.forEach(t => {
      const card = document.createElement('div');
      card.className = 'bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2 text-xs';
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-bold text-slate-900">${t.farmer_name} (${t.farmer_district})</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase ${t.status === 'answered' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}">${t.status}</span>
        </div>
        <p class="text-slate-600">Farmer Query: "${t.farmer_note}"</p>
        <div class="flex items-center space-x-3">
          <img src="${t.image_url}" class="w-16 h-16 rounded-lg object-cover border">
          <div>
            <div class="text-[11px] text-slate-500">Model Initial Guess: <b>${t.model_prediction}</b></div>
            ${t.expert_reply ? `<div class="text-emerald-800 font-bold mt-1">Verified Diagnosis: ${t.expert_reply}</div>` : ''}
          </div>
        </div>
        ${t.status === 'open' ? `
          <div class="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <input type="text" id="expert-reply-${t.id}" placeholder="Type verified diagnosis & treatment advice..." class="flex-1 p-2 bg-slate-50 border rounded-lg text-xs">
            <button onclick="draftWithGemini('${t.id}')" id="btn-draft-${t.id}" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-3 py-2 rounded-lg whitespace-nowrap shadow-sm flex items-center justify-center space-x-1">
              <span>✨ Gemini Draft</span>
            </button>
            <button onclick="submitExpertAnswer('${t.id}')" class="bg-brand-600 hover:bg-brand-700 text-white font-bold px-3 py-2 rounded-lg whitespace-nowrap">Submit Advice</button>
          </div>
        ` : ''}
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error('Failed to load expert tickets:', err);
  }
}

async function draftWithGemini(ticketId) {
  const btn = document.getElementById(`btn-draft-${ticketId}`);
  if (btn) btn.innerText = "Drafting...";
  try {
    const res = await fetch(`/expert/tickets/${ticketId}/gemini-draft`, { method: 'POST' });
    const data = await res.json();
    const input = document.getElementById(`expert-reply-${ticketId}`);
    if (input) {
      input.value = (currentLang === 'hi') ? data.expert_reply_hi : data.expert_reply_en;
    }
  } catch (err) {
    alert("Gemini Auto-Draft failed: " + err.message);
  } finally {
    if (btn) btn.innerHTML = "<span>✨ Gemini Draft</span>";
  }
}

async function submitExpertAnswer(ticketId) {
  const reply = document.getElementById(`expert-reply-${ticketId}`).value.trim();
  if (!reply) return;
  try {
    await fetch(`/expert/tickets/${ticketId}?diagnosis_id=${allDiseases[0]?.id || ''}&reply_text=${encodeURIComponent(reply)}`, { method: 'PATCH' });
    alert('Expert reply submitted to farmer!');
    loadExpertTickets();
  } catch (err) {
    alert('Failed to submit advice: ' + err.message);
  }
}

// ================= SUPPLIERS (F12) =================
async function loadSuppliers() {
  try {
    const res = await fetch('/suppliers');
    const list = await res.json();
    const container = document.getElementById('suppliers-container');
    container.innerHTML = '';

    list.forEach(s => {
      const card = document.createElement('div');
      card.className = 'bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2 text-xs';
      
      let prodHtml = '';
      s.products.forEach(p => {
        prodHtml += `<li class="flex justify-between"><span>${p.name}</span><b class="text-slate-800">₹${p.price_inr}</b></li>`;
      });

      card.innerHTML = `
        <div class="flex items-start justify-between">
          <h4 class="font-bold text-slate-900 text-sm">${s.name}</h4>
          <span class="bg-brand-50 text-brand-800 font-bold px-2 py-0.5 rounded text-[10px] border border-brand-200">${s.distance_km} km away</span>
        </div>
        <p class="text-slate-500">${s.address} • 📞 ${s.phone}</p>
        <div class="pt-1 border-t border-slate-100">
          <span class="font-bold text-slate-700 text-[11px]">Recommended Stock Available:</span>
          <ul class="space-y-1 text-slate-600 mt-1">${prodHtml}</ul>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error('Failed to load suppliers:', err);
  }
}

// ================= ALERTS DRAWER =================
function toggleAlertsDrawer() {
  const drawer = document.getElementById('alerts-drawer');
  drawer.classList.toggle('hidden');
}

async function loadAlerts() {
  try {
    const res = await fetch('/alerts');
    const alerts = await res.json();
    const list = document.getElementById('alerts-list');
    list.innerHTML = '';

    document.getElementById('alert-badge').innerText = alerts.length;

    alerts.forEach(a => {
      const card = document.createElement('div');
      card.className = `p-3.5 rounded-xl border ${a.severity === 'critical' ? 'bg-red-50 border-red-200 text-red-950' : 'bg-amber-50 border-amber-200 text-amber-950'} space-y-1 text-xs`;
      card.innerHTML = `
        <div class="flex items-center justify-between font-bold">
          <span>${a.title}</span>
          <span class="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded ${a.severity === 'critical' ? 'bg-red-600 text-white' : 'bg-amber-500 text-white'}">${a.severity}</span>
        </div>
        <p class="text-slate-700">${a.body}</p>
        <div class="flex justify-between items-center pt-1 text-[10px] text-slate-400">
          <span>${new Date(a.created_at).toLocaleTimeString()}</span>
          <button onclick="dismissAlert('${a.id}')" class="text-slate-600 hover:text-slate-900 font-semibold underline">Mark Action Taken</button>
        </div>
      `;
      list.appendChild(card);
    });
  } catch (err) {
    console.error('Failed to load alerts:', err);
  }
}

async function dismissAlert(alertId) {
  try {
    await fetch(`/alerts/${alertId}?action_taken=true`, { method: 'PATCH' });
    await loadAlerts();
  } catch (err) {
    console.error(err);
  }
}

// ================= REFERENCE DATA =================
async function loadDiseases() {
  try {
    const res = await fetch('/admin/feedback'); // or diseases
    const simDiseaseSel = document.getElementById('sim-disease');
    if (simDiseaseSel) {
      simDiseaseSel.innerHTML = `
        <option value="d_late_blight">Tomato Late Blight (टमाटर पछेती झुलसा)</option>
        <option value="d_early_blight">Tomato Early Blight (टमाटर अगेती झुलसा)</option>
        <option value="d_leaf_curl">Tomato Leaf Curl Virus (मरोड़िया रोग)</option>
        <option value="d_potato_late">Potato Late Blight (आलू पछेती झुलसा)</option>
      `;
    }
  } catch (err) {}
}

// ================= MODAL HELPERS =================
function closeModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
}
function openNewFieldModal() {
  document.getElementById('modal-new-field').classList.remove('hidden');
}
