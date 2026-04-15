from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime
from config import *
from utils.excel_export import export_excel
from utils.predictor import run_prediction
from werkzeug.utils import secure_filename
import os
import subprocess
import pandas as pd


app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ---------------- DB CONNECT ----------------
def get_db():
    return sqlite3.connect(DB_PATH)


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            flash("Login successful!", "success") 
            return redirect("/dashboard")
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    # ================= KPI =================
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT supplier) FROM predictions")
    total_suppliers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk='High'")
    high_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk='Medium'")
    medium_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk='Low'")
    low_risk = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(delay) FROM predictions")
    avg_delay = round(cursor.fetchone()[0] or 0, 2)

    cursor.execute("SELECT SUM(order_value) FROM predictions")
    total_value_raw = cursor.fetchone()[0] or 0
    total_value = f"{total_value_raw:,.0f}"

    cursor.execute("SELECT AVG(fuel_cost) FROM predictions")
    avg_fuel_raw = cursor.fetchone()[0] or 0
    avg_fuel = f"{avg_fuel_raw:.2f}"

    # ================= REGION =================
    regionData = [0,0,0,0,0]
    cursor.execute("SELECT region, COUNT(*) FROM predictions GROUP BY region")
    for r,c in cursor.fetchall():
        if r < 5:
            regionData[r] = c

    # ================= TRANSPORT =================
    transportData = [0,0,0,0]
    cursor.execute("SELECT transport, COUNT(*) FROM predictions GROUP BY transport")
    for t,c in cursor.fetchall():
        if t < 4:
            transportData[t] = c

    # ================= WEATHER =================
    weatherData = {
        0: {"Low":0,"Medium":0,"High":0},
        1: {"Low":0,"Medium":0,"High":0},
        2: {"Low":0,"Medium":0,"High":0},
        3: {"Low":0,"Medium":0,"High":0}
    }

    cursor.execute("SELECT weather, risk, COUNT(*) FROM predictions GROUP BY weather, risk")
    for w,r,c in cursor.fetchall():
        if w in weatherData:
            weatherData[w][r] = c

    # ================= TRAFFIC =================
    trafficData = [0,0,0]
    cursor.execute("SELECT traffic, AVG(delay) FROM predictions GROUP BY traffic")
    for t,a in cursor.fetchall():
        if t < 3:
            trafficData[t] = round(a,2)

    # ================= DEMAND =================
    demandData = [0,0,0]
    cursor.execute("SELECT demand, COUNT(*) FROM predictions GROUP BY demand")
    for d,c in cursor.fetchall():
        if d < 3:
            demandData[d] = c

    # ================= STOCK =================
    stockData = {
        "Sufficient":{"Low":0,"Medium":0,"High":0},
        "Low":{"Low":0,"Medium":0,"High":0},
        "Out":{"Low":0,"Medium":0,"High":0}
    }

    cursor.execute("SELECT inventory, risk FROM predictions")
    for inv,risk in cursor.fetchall():
        if inv > 50:
            stockData["Sufficient"][risk] += 1
        elif inv > 20:
            stockData["Low"][risk] += 1
        else:
            stockData["Out"][risk] += 1

    # ================= VALUE TREND =================
    valueData = [0]*7
    cursor.execute("""
        SELECT strftime('%w', date), SUM(order_value)
        FROM predictions
        GROUP BY strftime('%w', date)
    """)
    for d,v in cursor.fetchall():
        valueData[int(d)] = v or 0

    # ================= FUEL =================
    cursor.execute("""
        SELECT delay, fuel_cost, risk
        FROM predictions
        WHERE fuel_cost IS NOT NULL
        LIMIT 100
    """)

    fuelData = [list(row) for row in cursor.fetchall()]

    # ================= ALERT TABLE =================
    cursor.execute("""
        SELECT supplier, region, delay, weather, risk
        FROM predictions
        WHERE risk='High'
        ORDER BY delay DESC
        LIMIT 5
    """)
    alerts = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",

        total_predictions=total_predictions,
        total_suppliers=total_suppliers,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        avg_delay=avg_delay,
        total_value=total_value,
        avg_fuel=avg_fuel,

        regionData=regionData,
        transportData=transportData,
        weatherData=weatherData,
        trafficData=trafficData,
        demandData=demandData,
        stockData=stockData,
        valueData=valueData,
        fuelData=fuelData,

        alerts=alerts
    )
@app.route("/dashboard-data")
def dashboard_data():
    if "user" not in session:
        return {}

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT supplier) FROM predictions")
    total_suppliers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk='High'")
    high_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk='Medium'")
    medium_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk='Low'")
    low_risk = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(delay) FROM predictions")
    avg_delay = round(cursor.fetchone()[0] or 0, 2)

    cursor.execute("SELECT SUM(order_value) FROM predictions")
    total_value_raw = cursor.fetchone()[0] or 0
    total_value = f"{total_value_raw:,.0f}"

    cursor.execute("SELECT AVG(fuel_cost) FROM predictions")
    avg_fuel_raw = cursor.fetchone()[0] or 0
    avg_fuel = f"{avg_fuel_raw:.2f}"

    cursor.execute("""
        SELECT supplier, region, delay, weather, risk
        FROM predictions
        WHERE risk='High'
        ORDER BY delay DESC
        LIMIT 5
    """)
    alerts = cursor.fetchall()

    conn.close()

    return {
        "total_predictions": total_predictions,
        "total_suppliers": total_suppliers,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "avg_delay": avg_delay,
        "total_value": total_value,
        "avg_fuel": avg_fuel,
        "alerts": alerts
    }

# ---------------- PREDICT ----------------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        conn = get_db()
        cursor = conn.cursor()

        # ================= MAPPING =================
        region_map = {
            "asia": 0,
            "europe": 1,
            "north america": 2,
            "south america": 3,
            "africa": 4
        }

        transport_map = {
            "truck": 0,
            "rail": 1,
            "ship": 2,
            "air": 3
        }

        weather_map = {
            "clear": 0,
            "rain": 1,
            "storm": 2,
            "fog": 3
        }

        traffic_map = {
            "low": 0,
            "medium": 1,
            "high": 2
        }

        demand_map = {
            "low": 0,
            "medium": 1,
            "high": 2
        }

        # ================= FILE UPLOAD =================
        file = request.files.get("file")

        if file and file.filename != "":

            upload_folder = os.path.join(os.getcwd(), "uploads")

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            file_path = os.path.join(upload_folder, filename)

            file.save(file_path)

            if filename.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            inserted = 0

            for _, row in df.iterrows():
                try:
                    supplier = str(row.get("supplier", "Unknown"))

                    # 🔥 SMART CONVERSION FUNCTION
                    def convert(value, mapping):
                        if isinstance(value, str):
                            return mapping.get(value.strip().lower(), 0)
                        return int(value)

                    region = convert(row.get("region", 0), region_map)
                    transport = convert(row.get("transport", 0), transport_map)
                    weather = convert(row.get("weather", 0), weather_map)
                    traffic = convert(row.get("traffic", 0), traffic_map)
                    demand = convert(row.get("demand", 0), demand_map)

                    delay = float(row.get("delay", 0))
                    inventory = int(row.get("inventory", 0))
                    port_delay = int(row.get("port_delay", 0))
                    order_value = float(row.get("order_value", 0))

                    # ================= PREDICTION =================
                    result = run_prediction({
                        "delay": delay,
                        "traffic": traffic,
                        "weather": weather,
                        "inventory": inventory,
                        "order_value": order_value,
                        "port_delay": port_delay
                    })

                    risk = result.get("risk", "Unknown")
                    fuel_cost = result.get("fuel_cost", 0)

                    date = datetime.now().strftime("%Y-%m-%d %H:%M")

                    cursor.execute("""
                        INSERT INTO predictions (
                            date, supplier, region, transport, delay,
                            weather, demand, inventory, traffic,
                            port_delay, order_value, fuel_cost, risk
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date, supplier, region, transport, delay,
                        weather, demand, inventory, traffic,
                        port_delay, order_value, fuel_cost, risk
                    ))

                    inserted += 1

                except Exception as e:
                    print("Row skipped:", e)

            conn.commit()
            conn.close()

            subprocess.Popen(["python", "model/train_model.py"])

            flash(f"{inserted} records uploaded & predicted successfully", "success")
            return redirect("/dashboard")

        # ================= MANUAL FORM =================
        def convert_form(value, mapping):
            if isinstance(value, str) and not value.isdigit():
                return mapping.get(value.lower(), 0)
            return int(value)

        supplier = request.form.get("supplier")

        region = convert_form(request.form.get("region"), region_map)
        transport = convert_form(request.form.get("transport"), transport_map)
        weather = convert_form(request.form.get("weather"), weather_map)
        traffic = convert_form(request.form.get("traffic"), traffic_map)
        demand = convert_form(request.form.get("demand"), demand_map)

        delay = float(request.form.get("delay"))
        inventory = int(request.form.get("inventory"))
        port_delay = int(request.form.get("port_delay"))
        order_value = float(request.form.get("order_value"))

        result = run_prediction({
            "delay": delay,
            "traffic": traffic,
            "weather": weather,
            "inventory": inventory,
            "order_value": order_value,
            "port_delay": port_delay
        })

        risk = result.get("risk", "Unknown")
        fuel_cost = result.get("fuel_cost", 0)
        confidence = result.get("confidence", 0)
        explanation = result.get("explanation", [])

        date = datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
            INSERT INTO predictions (
                date, supplier, region, transport, delay,
                weather, demand, inventory, traffic,
                port_delay, order_value, fuel_cost, risk
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, supplier, region, transport, delay,
            weather, demand, inventory, traffic,
            port_delay, order_value, fuel_cost, risk
        ))

        conn.commit()
        conn.close()

        flash(f"Prediction completed: {risk} Risk", "success")

        return render_template(
            "result.html",
            risk=risk,
            confidence=confidence,
            explanation=explanation,
            fuel_cost=fuel_cost,
            data={
                "supplier": supplier,
                "region": region,
                "transport": transport,
                "delay": delay,
                "weather": weather,
                "demand": demand,
                "inventory": inventory,
                "traffic": traffic,
                "port_delay": port_delay,
                "order_value": order_value
            }
        )

    return render_template("predict.html")

# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    # convert to dict for Jinja
    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "date": r[1],
            "supplier": r[2],
            "region": r[3],
            "transport": r[4],
            "delay": r[5],
            "weather": r[6],
            "demand": r[7],
            "inventory": r[8],
            "traffic": r[9],
            "port_delay": r[10],
            "order_value": r[11],
            "fuel_cost": r[12],
            "risk_level": r[13]
        })

    return render_template("history.html", data=data)

@app.route("/export_excel")
def export_excel_route():
    if "user" not in session:
        return redirect("/")

    return export_excel("database/database.db")

@app.route("/delete/<int:id>", methods=["POST"])
def delete_single(id):
    if "user" not in session:
        return {"status": "unauthorized"}, 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM predictions WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return {"status": "success"}

@app.route("/delete_all", methods=["POST"])
def delete_all():
    if "user" not in session:
        return {"status": "unauthorized"}, 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()

    return {"status": "success"}

@app.route("/save-dashboard-image", methods=["POST"])
def save_dashboard_image():
    import os, base64
    from flask import request, jsonify

    data = request.json
    image_data = data["image"].split(",")[1]
    filename = data.get("filename", "dashboard.png")

    downloads_path = os.path.join(os.path.expanduser(""), "Downloads")

    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)

    file_path = os.path.join(downloads_path, filename)

    with open(file_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    return jsonify({"status": "saved", "path": file_path})

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)