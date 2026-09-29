# 💧 Smart Community Health Monitoring and Early Warning System
### for Water-Borne Diseases in Rural Northeast India

**BTech 3rd Year Mini Project** | Department of Computer Science

---

## 📌 Project Description

This web-based system monitors water quality and community health data in real time to detect the early onset of water-borne disease outbreaks (cholera, typhoid, dysentery) in rural Northeast India.

It simulates IoT water sensors, collects community health reports, applies machine learning risk prediction, and visualizes data on an interactive dashboard with a Leaflet map.

---

## 🔧 Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python Flask                      |
| Database   | SQLite                            |
| Frontend   | HTML5, CSS3, JavaScript (ES6+)    |
| Charts     | Chart.js 4                        |
| ML Model   | Scikit-learn (Decision Tree)      |
| Map        | Leaflet.js + OpenStreetMap        |

---

## 📁 Project Structure

```
health_monitoring_system/
│
├── app.py              ← Flask backend (all API routes)
├── ml_model.py         ← Decision Tree ML model
├── database.db         ← SQLite database (auto-created)
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
│
├── templates/
│     ├── dashboard.html   ← Main dashboard page
│     └── form.html        ← Community health report form
│
└── static/
      ├── style.css        ← Full stylesheet
      └── script.js        ← Dashboard JavaScript (charts, map, API calls)
```

---

## 🚀 How to Install & Run

### Step 1: Install Python 3.8+
Make sure Python is installed:
```bash
python --version
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the App
```bash
python app.py
```

### Step 4: Open in Browser
```
http://localhost:5000
```

---

## 📡 API Endpoints

| Method | Endpoint           | Description                              |
|--------|--------------------|------------------------------------------|
| GET    | `/`                | Redirect to dashboard                    |
| GET    | `/dashboard`       | Main dashboard page                      |
| GET    | `/form`            | Health report form                       |
| GET    | `/add_water`       | Simulate IoT sensor reading              |
| POST   | `/add_water_manual`| Add manual water reading (JSON body)     |
| POST   | `/add_health`      | Submit community health report           |
| GET    | `/risk`            | Get risk prediction (rule + ML)          |
| GET    | `/chart_data`      | Get all chart data (water + health)      |
| GET    | `/latest_stats`    | Get latest summary stats for cards       |
| GET    | `/village_data`    | Get village data for map                 |

---

## 🧠 ML Model Details

- **Algorithm:** Decision Tree Classifier (max_depth=5)
- **Library:** Scikit-learn
- **Training data:** 50-row synthetic dataset simulating NE India conditions
- **Features used:** pH, turbidity, temperature, patient count, fever, diarrhea, vomiting
- **Label:** 0 = SAFE, 1 = HIGH RISK
- **Accuracy:** ~90%+ on test split

### Risk Logic:
| Method      | Condition                                |
|-------------|------------------------------------------|
| Rule-Based  | turbidity > 10 AND patients > 5 = HIGH RISK |
| ML Model    | Decision Tree prediction on all features |
| Final Result| HIGH RISK if **either** method says HIGH |

---

## 📊 Dashboard Features

- **5 Summary Cards** — pH, turbidity, temperature, patient count, total readings
- **Risk Badge** — Color-coded: ✅ SAFE (green) / 🚨 HIGH RISK (red blinking)
- **Rule-Based + ML Risk** — Shown separately with color-coded badges
- **Turbidity Line Chart** — With 10 NTU danger threshold line
- **pH & Temperature Dual-Axis Chart** — Overlay of both readings
- **Patient Bar Chart** — Bars turn red when patient count > 5
- **Leaflet Map** — Color-coded markers for all NE India villages
- **Alert Popup Modal** — Triggered automatically on HIGH RISK
- **Top Alert Banner** — Red banner for HIGH RISK condition
- **Auto Refresh** — Dashboard updates every 5 seconds

---

## 🏘️ Covered Villages (Northeast India)

Majuli, Sibsagar, Dibrugarh, Tezpur, Jorhat, Nagaon, Silchar, Imphal, Kohima, Agartala, Itanagar, Aizawl, Gangtok, Shillong, Bongaigaon

---

## 📸 Screenshots Description

1. **Dashboard** — Overview with stat cards, risk badge, IoT controls, and charts
2. **Risk Alert Modal** — Red popup when HIGH RISK is detected
3. **Water Charts** — Turbidity line chart with threshold + pH/temp dual chart
4. **Patient Bar Chart** — Community health data per village
5. **Leaflet Map** — Color-coded village outbreak map of NE India
6. **Health Form** — Checkbox symptom cards and village selector

---

## 👨‍💻 How to Test

1. Open dashboard at `http://localhost:5000`
2. Click **"Simulate Sensor Reading"** a few times to add water data
3. Go to `/form` and submit a health report with >5 patients
4. Come back to dashboard and click **"Check Risk Now"**
5. If turbidity > 10 AND patients > 5 → see the HIGH RISK alert!
6. Watch the map update with the village you selected

---

## 📝 Academic Details

- **Subject:** Mini Project / Software Engineering Lab
- **Focus Area:** Health Informatics, IoT Simulation, ML Integration
- **Target Region:** Rural communities in Assam, Manipur, Nagaland, Meghalaya, Tripura, Arunachal Pradesh, Mizoram, Sikkim
- **Problem Statement:** High incidence of water-borne diseases due to contaminated water sources in flood-prone rural areas of Northeast India

---

*Built with ❤️ for BTech Mini Project Submission*
