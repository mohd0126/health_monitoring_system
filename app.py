"""
Smart Community Health Monitoring and Early Warning System
for Water-Borne Diseases in Rural Northeast India

BTech 3rd Year Mini Project
Backend: Flask + SQLite + Scikit-learn ML
"""

import sqlite3
import random
from flask import Flask, request, jsonify, render_template
from ml_model import predict_risk_ml

app = Flask(__name__)
DB = "database.db"

# ─────────────────────────────────────────────
# Database Initialization
# ─────────────────────────────────────────────

def init_db():
    """Create tables if they do not exist."""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS WaterData (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ph         REAL,
            turbidity  REAL,
            temp       REAL,
            date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS HealthReports (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            village   TEXT,
            fever     INTEGER,
            diarrhea  INTEGER,
            vomiting  INTEGER,
            patients  INTEGER,
            date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────

@app.route("/")
def home():
    """Redirect root to dashboard."""
    return render_template("dashboard.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/form")
def form():
    return render_template("form.html")


# ─────────────────────────────────────────────
# API: Water Data (Simulated IoT Sensor)
# ─────────────────────────────────────────────

@app.route("/add_water")
def add_water():
    """
    Simulate an IoT sensor reading.
    Randomly generates pH, turbidity, and temperature values.
    """
    ph        = round(random.uniform(5.5, 9.5), 2)
    turbidity = round(random.uniform(1.0, 25.0), 1)
    temp      = round(random.uniform(18.0, 38.0), 1)

    conn = get_db()
    conn.execute(
        "INSERT INTO WaterData(ph, turbidity, temp) VALUES (?, ?, ?)",
        (ph, turbidity, temp)
    )
    conn.commit()
    conn.close()

    return jsonify({"msg": "Water data added", "ph": ph, "turbidity": turbidity, "temp": temp})


@app.route("/add_water_manual", methods=["POST"])
def add_water_manual():
    """Manually insert a water reading (from dashboard form)."""
    data = request.get_json()
    conn = get_db()
    conn.execute(
        "INSERT INTO WaterData(ph, turbidity, temp) VALUES (?, ?, ?)",
        (data["ph"], data["turbidity"], data["temp"])
    )
    conn.commit()
    conn.close()
    return jsonify({"msg": "Manual water data added"})


# ─────────────────────────────────────────────
# API: Health Reports
# ─────────────────────────────────────────────

@app.route("/add_health", methods=["POST"])
def add_health():
    """Submit a community health report from the form."""
    data = request.get_json()
    conn = get_db()
    conn.execute(
        """INSERT INTO HealthReports(village, fever, diarrhea, vomiting, patients)
           VALUES (?, ?, ?, ?, ?)""",
        (
            data["village"],
            int(data["fever"]),
            int(data["diarrhea"]),
            int(data["vomiting"]),
            int(data["patients"]),
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"msg": "Health report saved successfully"})


# ─────────────────────────────────────────────
# API: Risk Prediction
# ─────────────────────────────────────────────

@app.route("/risk")
def risk():
    """
    Dual risk assessment:
    1. Rule-based: turbidity > 10 AND patients > 5 → HIGH RISK
    2. ML model  : Decision Tree trained on dummy dataset
    """
    conn = get_db()

    # Latest water reading
    water_row = conn.execute(
        "SELECT ph, turbidity, temp FROM WaterData ORDER BY id DESC LIMIT 1"
    ).fetchone()

    # Latest health report
    health_row = conn.execute(
        "SELECT fever, diarrhea, vomiting, patients FROM HealthReports ORDER BY id DESC LIMIT 1"
    ).fetchone()

    conn.close()

    if water_row is None or health_row is None:
        return jsonify({
            "risk": "NO DATA",
            "rule_risk": "NO DATA",
            "ml_risk": "NO DATA",
            "turbidity": None,
            "patients": None
        })

    turbidity = water_row["turbidity"]
    ph        = water_row["ph"]
    temp      = water_row["temp"]
    patients  = health_row["patients"]
    fever     = health_row["fever"]
    diarrhea  = health_row["diarrhea"]
    vomiting  = health_row["vomiting"]

    # Rule-based assessment
    rule_risk = "HIGH RISK" if (turbidity > 10 and patients > 5) else "SAFE"

    # ML-based assessment
    ml_risk = predict_risk_ml(ph, turbidity, temp, patients, fever, diarrhea, vomiting)

    # Final combined result (either HIGH → alert)
    final_risk = "HIGH RISK" if ("HIGH" in rule_risk or "HIGH" in ml_risk) else "SAFE"

    return jsonify({
        "risk":      final_risk,
        "rule_risk": rule_risk,
        "ml_risk":   ml_risk,
        "turbidity": turbidity,
        "patients":  patients,
        "ph":        ph,
        "temp":      temp
    })


# ─────────────────────────────────────────────
# API: Chart Data
# ─────────────────────────────────────────────

@app.route("/chart_data")
def chart_data():
    """Return all water and patient data for Chart.js graphs."""
    conn = get_db()

    water_rows = conn.execute(
        "SELECT ph, turbidity, temp, date FROM WaterData ORDER BY id ASC LIMIT 30"
    ).fetchall()

    health_rows = conn.execute(
        "SELECT village, patients, fever, diarrhea, vomiting, date FROM HealthReports ORDER BY id ASC LIMIT 30"
    ).fetchall()

    conn.close()

    water_labels    = [r["date"][:16] for r in water_rows]
    turbidity_vals  = [r["turbidity"] for r in water_rows]
    ph_vals         = [r["ph"] for r in water_rows]
    temp_vals       = [r["temp"] for r in water_rows]

    health_labels   = [r["village"] for r in health_rows]
    patient_vals    = [r["patients"] for r in health_rows]

    return jsonify({
        "water_labels":   water_labels,
        "turbidity":      turbidity_vals,
        "ph":             ph_vals,
        "temp":           temp_vals,
        "health_labels":  health_labels,
        "patients":       patient_vals
    })


# ─────────────────────────────────────────────
# API: Latest Stats (for summary cards)
# ─────────────────────────────────────────────

@app.route("/latest_stats")
def latest_stats():
    """Return latest readings for the summary cards on the dashboard."""
    conn = get_db()

    w = conn.execute(
        "SELECT ph, turbidity, temp FROM WaterData ORDER BY id DESC LIMIT 1"
    ).fetchone()

    h = conn.execute(
        "SELECT village, patients FROM HealthReports ORDER BY id DESC LIMIT 1"
    ).fetchone()

    total_water   = conn.execute("SELECT COUNT(*) FROM WaterData").fetchone()[0]
    total_reports = conn.execute("SELECT COUNT(*) FROM HealthReports").fetchone()[0]

    conn.close()

    return jsonify({
        "ph":           w["ph"]         if w else "--",
        "turbidity":    w["turbidity"]  if w else "--",
        "temp":         w["temp"]       if w else "--",
        "village":      h["village"]    if h else "--",
        "patients":     h["patients"]   if h else "--",
        "total_water":  total_water,
        "total_reports": total_reports
    })


# ─────────────────────────────────────────────
# API: Village map pins
# ─────────────────────────────────────────────

# Northeast India village coordinates (sample data)
VILLAGE_COORDS = {
    "Majuli":       [27.0041, 94.5916],
    "Sibsagar":     [26.9834, 94.6418],
    "Dibrugarh":    [27.4728, 94.9119],
    "Tezpur":       [26.6338, 92.7957],
    "Jorhat":       [26.7509, 94.2037],
    "Nagaon":       [26.3488, 92.6841],
    "Silchar":      [24.8333, 92.7789],
    "Imphal":       [24.8170, 93.9368],
    "Kohima":       [25.6751, 94.1086],
    "Agartala":     [23.8315, 91.2868],
    "Itanagar":     [27.0844, 93.6053],
    "Aizawl":       [23.7307, 92.7173],
    "Gangtok":      [27.3389, 88.6065],
    "Shillong":     [25.5788, 91.8933],
    "Bongaigaon":   [26.4765, 90.5584],
}

@app.route("/village_data")
def village_data():
    """Return village health data for the Leaflet map."""
    conn = get_db()
    rows = conn.execute(
        """SELECT village, SUM(patients) as total_patients,
                  AVG(fever) as avg_fever,
                  COUNT(*) as reports
           FROM HealthReports
           GROUP BY village"""
    ).fetchall()
    conn.close()

    result = []
    for r in rows:
        coords = VILLAGE_COORDS.get(r["village"], [26.5, 93.0])  # default: Assam center
        result.append({
            "village":  r["village"],
            "patients": r["total_patients"],
            "reports":  r["reports"],
            "lat":      coords[0],
            "lng":      coords[1],
        })

    return jsonify(result)


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
