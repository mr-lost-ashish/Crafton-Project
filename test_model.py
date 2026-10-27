"""
Automated end-to-end test suite for CropGuard Working Model
"""
import sys
import io
import os

# Ensure UTF-8 output on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi.testclient import TestClient
from backend.app.main import app

def test_full_model():
    print("Testing CropGuard API Endpoints...")
    with TestClient(app) as client:
        # 1. Root & Static
        res = client.get("/")
        assert res.status_code == 200, f"Root failed: {res.status_code}"
        print("[PASS] GET /: HTML Served successfully")

        # 1b. Farmer Location & Auth (Current Location & DPDP Login)
        res_loc = client.get("/auth/location/reverse?lat=19.9975&lng=73.7898")
        assert res_loc.status_code == 200
        loc_data = res_loc.json()
        assert "district" in loc_data and "state" in loc_data
        print(f"[PASS] GET /auth/location/reverse: GPS Geocoded to '{loc_data['display_name']}'")

        res_otp_req = client.post("/auth/otp/request", json={"phone": "9822099999"})
        assert res_otp_req.status_code == 200
        print("[PASS] POST /auth/otp/request: OTP dispatched")

        res_login = client.post(
            "/auth/otp/verify",
            json={
                "phone": "9822099999",
                "otp": "123456",
                "name": "Kisan Demo User",
                "latitude": 19.9975,
                "longitude": 73.7898,
                "district": "Nashik",
                "state": "Maharashtra"
            }
        )
        assert res_login.status_code == 200
        login_res = res_login.json()
        assert login_res["user"]["name"] == "Kisan Demo User"
        assert login_res["user"]["latitude"] == 19.9975
        print(f"[PASS] POST /auth/otp/verify: User logged in with GPS coords ({login_res['user']['latitude']}, {login_res['user']['longitude']})")

        # 2. User & Fields
        res = client.get("/me")
        assert res.status_code == 200
        user_data = res.json()
        print(f"[PASS] GET /me: User {user_data['name']} ({user_data['district']})")

        res = client.get("/fields")
        assert res.status_code == 200
        fields = res.json()
        assert len(fields) >= 3
        field_id = fields[0]["id"]
        print(f"[PASS] GET /fields: Found {len(fields)} fields. Selected: {fields[0]['name']}")

        # 3. Scan & Diagnosis (F1, F2, F3)
        res = client.post(
            "/scans",
            data={"field_id": field_id, "sample_type": "tomato_early_blight"}
        )
        assert res.status_code == 200
        scan_res = res.json()
        scan_id = scan_res["scan_id"]
        assert scan_res["result_status"] == "confident"
        assert scan_res["top_disease"]["name_en"] == "Tomato Early Blight"
        assert len(scan_res["treatments"]) >= 3
        print(f"[PASS] POST /scans: Diagnosis '{scan_res['top_disease']['name_en']}', Severity: {scan_res['severity']} ({scan_res['severity_pct']}%), Treatments: {len(scan_res['treatments'])}")

        # 4. Feedback loop (FR-2.8)
        res = client.patch(f"/scans/{scan_id}/feedback", json={"user_feedback": "correct"})
        assert res.status_code == 200
        print("[PASS] PATCH /scans/{id}/feedback: Confirmed diagnosis")

        # 5. Low Confidence & AI Second Opinion (F17)
        res = client.post(
            "/scans",
            data={"field_id": field_id, "sample_type": "tomato_early_blight", "force_uncertain": "true"}
        )
        assert res.status_code == 200
        so_scan = res.json()
        assert so_scan["requires_second_opinion"] == True
        assert so_scan["result_status"] == "uncertain"
        print("[PASS] POST /scans (force_uncertain): Flagged uncertain, triggered Second Opinion")

        # Submit second opinion
        res = client.post(
            f"/scans/{so_scan['scan_id']}/second-opinion",
            json={
                "growth_stage": "Vegetative",
                "symptoms_reported": ["concentric rings", "yellow halo"],
                "leaf_underside_url": "/sample_images/tomato_early_blight.jpg"
            }
        )
        assert res.status_code == 200
        so_res = res.json()
        print(f"[PASS] POST /scans/{so_scan['scan_id']}/second-opinion: Outcome '{so_res['outcome']}', Top: {so_res['rescored_predictions'][0]['disease_name']} ({so_res['final_confidence']})")

        # 6. Outbreak Radar & Map (F15)
        res = client.get("/radar?crop=tomato&days=14")
        assert res.status_code == 200
        radar = res.json()
        assert len(radar["zones"]) >= 1
        print(f"[PASS] GET /radar: {len(radar['zones'])} Gated Outbreak Zones loaded. Total confirmed: {radar['summary']['total_confirmed_cases']}")

        # 7. Early Risk & What-If Simulator (F16)
        res = client.get(f"/fields/{field_id}/risk")
        assert res.status_code == 200
        risk_data = res.json()
        print(f"[PASS] GET /fields/{field_id}/risk: Ambient score {risk_data['risk_assessment']['score']}/100 ({risk_data['risk_assessment']['level']})")

        res = client.post(
            f"/fields/{field_id}/risk-assessments/what-if",
            json={"temperature_c": 22.0, "humidity_pct": 94.0, "rainfall_mm": 20.0}
        )
        assert res.status_code == 200
        whatif = res.json()
        assert whatif["is_what_if"] == True
        print(f"[PASS] POST /fields/{field_id}/risk-assessments/what-if: High moisture simulated score: {whatif['score']}/100 ({whatif['level']})")

        # 8. Judge Village Outbreak Simulation (F23)
        res = client.post(
            "/admin/simulations/village",
            json={
                "village_name": "Nashik Rural",
                "center_lat": 20.015,
                "center_lng": 73.805,
                "crop_id": fields[0]["crop_id"],
                "disease_id": scan_res["top_disease"]["id"],
                "intensity": 5
            }
        )
        assert res.status_code == 200
        sim_data = res.json()
        print(f"[PASS] POST /admin/simulations/village: Outbreak injected into {sim_data['village']}, {sim_data['alerts_generated']} emergency alerts fired.")

        # 9. Smart Treatment Planner (F21)
        res = client.post(f"/scans/{scan_id}/treatment-plan")
        assert res.status_code == 200
        plan_data = res.json()
        print(f"[PASS] POST /scans/{scan_id}/treatment-plan: Plan created with {plan_data['steps_count']} steps. Est Cost: ₹{plan_data['estimated_total_cost_inr']}")

        # 10. Loss-Avoidance Calculator (F24)
        res = client.post(
            f"/fields/{field_id}/loss-scenarios",
            json={
                "crop_value_inr": 150000.0,
                "treatment_cost_inr": 1800.0,
                "loss_pct_if_early": 5.0,
                "loss_pct_if_delayed": 28.0,
                "delay_days": 6
            }
        )
        assert res.status_code == 200
        loss_data = res.json()
        print(f"[PASS] POST /fields/{field_id}/loss-scenarios: Delayed Loss: ₹{loss_data['delayed_loss_inr']}, Savings: ₹{loss_data['estimated_difference_inr']}")

        # 11. Kisan Voice SOS (F18)
        res = client.post(
            "/voice-reports",
            json={"language": "hi", "transcript": "मेरे टमाटर के पत्तों पर गोल छल्लेदार काले धब्बे बन रहे हैं"}
        )
        assert res.status_code == 200
        voice_res = res.json()
        print(f"[PASS] POST /voice-reports: Voice SOS processed: '{voice_res['spoken_reply'][:65]}...'")

        # 12. Crop Health Passport PDF Export (F22)
        res = client.get(f"/fields/{field_id}/passport/export")
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/pdf"
        print(f"[PASS] GET /fields/{field_id}/passport/export: PDF report generated ({len(res.content)} bytes)")

        # 13. Safety Gatekeeper: Test that non-leaf / skin image is rejected (422)
        # Create a small blank non-leaf image
        from PIL import Image
        import tempfile
        blank_img_path = os.path.join(tempfile.gettempdir(), "test_non_leaf.jpg")
        Image.new("RGB", (200, 200), (220, 180, 150)).save(blank_img_path) # skin-tone blank
        with open(blank_img_path, "rb") as f:
            res_bad = client.post(
                "/scans",
                data={"field_id": field_id},
                files={"image": ("test_non_leaf.jpg", f, "image/jpeg")}
            )
        assert res_bad.status_code == 422
        print(f"[PASS] OOD Gatekeeper: Non-leaf image correctly rejected with HTTP 422: '{res_bad.json()['detail']['message']}'")

    print("\n>>> ALL 12 END-TO-END TESTS PASSED WITH 100% SUCCESS! <<<")

if __name__ == "__main__":
    test_full_model()
