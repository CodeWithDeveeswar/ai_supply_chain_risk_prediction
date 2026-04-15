import joblib
import os

# ---------------- LOAD MODEL ----------------
MODEL_PATH = os.path.join("model", "risk_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("❌ Model not found. Train the model first.")

model = joblib.load(MODEL_PATH)


# ---------------- FUEL COST ----------------
def calculate_fuel_cost(delay):
    return round(1.5 + (delay * 0.2), 2)


# ---------------- EXPLANATION ENGINE ----------------
def generate_explanation(data, risk):
    reasons = []

    delay = float(data.get("delay", 0))
    traffic = int(data.get("traffic", 0))
    weather = int(data.get("weather", 0))
    inventory = int(data.get("inventory", 0))
    order_value = float(data.get("order_value", 0))
    port_delay = int(data.get("port_delay", 0))

    # 🔥 RULE-BASED EXPLANATION
    if delay > 7:
        reasons.append("High delivery delay")

    if traffic == 2:
        reasons.append("Heavy traffic conditions")

    if weather == 2:
        reasons.append("Severe weather conditions")

    if inventory < 20:
        reasons.append("Low inventory level")

    if port_delay == 1:
        reasons.append("Port delay detected")

    if order_value > 3000:
        reasons.append("High-value order (higher risk impact)")

    # fallback
    if not reasons:
        if risk == "Low":
            reasons.append("Stable supply conditions with low delay and good inventory")
        else:
            reasons.append("Moderate operating conditions affecting supply chain")

    return reasons


# ---------------- MAIN PREDICTION ----------------
def run_prediction(data):

    try:
        features = [[
            float(data.get("delay", 0)),
            int(data.get("traffic", 0)),
            int(data.get("weather", 0)),
            int(data.get("inventory", 0)),
            float(data.get("order_value", 0)),
            int(data.get("port_delay", 0))
        ]]

        # 🔥 PREDICTION
        prediction = model.predict(features)[0]

        # 🔥 CONFIDENCE
        probs = model.predict_proba(features)[0]
        confidence = round(max(probs) * 100, 2)

        # 🔥 FUEL COST
        fuel_cost = calculate_fuel_cost(features[0][0])

        # 🔥 EXPLANATION
        explanation = generate_explanation(data, prediction)

        return {
            "risk": prediction,
            "confidence": confidence,
            "fuel_cost": fuel_cost,
            "explanation": explanation   # 🔥 NEW
        }

    except Exception as e:
        print("❌ Prediction Error:", e)

        return {
            "risk": "Error",
            "confidence": 0,
            "fuel_cost": 0,
            "explanation": []
        }