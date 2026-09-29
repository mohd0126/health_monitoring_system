/**
 * script.js
 * Dashboard JavaScript for Smart Community Health Monitoring System
 * BTech Mini Project — Rural Northeast India
 */

// ─────────────────────────────────────────────
// Chart instances (stored so they can be updated)
// ─────────────────────────────────────────────
let turbidityChart = null;
let phTempChart    = null;
let patientChart   = null;
let leafletMap     = null;

// ─────────────────────────────────────────────
// Initialize on page load
// ─────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  initMap();
  refreshAll();
  // Auto-refresh every 5 seconds
  setInterval(refreshAll, 5000);
});

// ─────────────────────────────────────────────
// Master refresh function
// ─────────────────────────────────────────────
async function refreshAll() {
  await Promise.all([
    loadStats(),
    loadCharts(),
    loadTableData(),
    loadMapData()
  ]);
  document.getElementById("lastUpdated").textContent =
    "Last updated: " + new Date().toLocaleTimeString();
}

// ─────────────────────────────────────────────
// Load summary stat cards
// ─────────────────────────────────────────────
async function loadStats() {
  try {
    const res  = await fetch("/latest_stats");
    const data = await res.json();

    document.getElementById("statPH").textContent       = data.ph      ?? "—";
    document.getElementById("statTurb").textContent     = data.turbidity ?? "—";
    document.getElementById("statTemp").textContent     = data.temp    ?? "—";
    document.getElementById("statPatients").textContent = data.patients ?? "—";
    document.getElementById("statVillage").textContent  = data.village ?? "—";
    document.getElementById("statTotalWater").textContent  = data.total_water + " readings";
    document.getElementById("statTotalReports").textContent = data.total_reports + " health reports";

    // Color code turbidity card
    const turbCard = document.getElementById("cardTurb");
    turbCard.classList.remove("danger", "warning");
    if (data.turbidity > 10) turbCard.classList.add("danger");
    else if (data.turbidity > 7) turbCard.classList.add("warning");

  } catch (err) {
    console.error("loadStats error:", err);
  }
}

// ─────────────────────────────────────────────
// Check Risk (button handler)
// ─────────────────────────────────────────────
async function checkRisk() {
  try {
    const res  = await fetch("/risk");
    const data = await res.json();

    updateRiskUI(data);

    // Show alert modal for HIGH RISK
    if (data.risk === "HIGH RISK") {
      document.getElementById("riskModal").classList.remove("hidden");
      document.getElementById("alertBanner").classList.remove("hidden");
    } else {
      document.getElementById("alertBanner").classList.add("hidden");
    }
  } catch (err) {
    console.error("checkRisk error:", err);
  }
}

function updateRiskUI(data) {
  const badge = document.getElementById("riskBadge");

  if (data.risk === "NO DATA") {
    badge.textContent = "NO DATA";
    badge.className   = "risk-badge badge-unknown";
  } else if (data.risk === "HIGH RISK") {
    badge.textContent = "🚨 HIGH RISK";
    badge.className   = "risk-badge badge-highrisk";
  } else {
    badge.textContent = "✅ SAFE";
    badge.className   = "risk-badge badge-safe";
  }

  // Sub-badges
  const ruleEl = document.getElementById("ruleRisk");
  const mlEl   = document.getElementById("mlRisk");

  ruleEl.textContent = data.rule_risk ?? "—";
  mlEl.textContent   = data.ml_risk   ?? "—";

  ruleEl.className = "badge-sm " + ((data.rule_risk === "HIGH RISK") ? "high" : "safe");
  mlEl.className   = "badge-sm " + ((data.ml_risk   === "HIGH RISK") ? "high" : "safe");

  document.getElementById("riskTurb").textContent    = data.turbidity != null ? data.turbidity + " NTU" : "—";
  document.getElementById("riskPatients").textContent = data.patients  != null ? data.patients + " patients" : "—";
}

function closeModal()    { document.getElementById("riskModal").classList.add("hidden"); }
function dismissAlert()  { document.getElementById("alertBanner").classList.add("hidden"); }

// ─────────────────────────────────────────────
// Add Simulated Water Data
// ─────────────────────────────────────────────
async function addWaterSimulated() {
  try {
    const res  = await fetch("/add_water");
    const data = await res.json();

    const msgEl = document.getElementById("sensorMsg");
    msgEl.classList.remove("hidden");
    msgEl.innerHTML =
      `✅ Sensor reading added: pH <b>${data.ph}</b> | Turbidity <b>${data.turbidity} NTU</b> | Temp <b>${data.temp}°C</b>`;

    await refreshAll();
    setTimeout(() => msgEl.classList.add("hidden"), 5000);
  } catch (err) {
    console.error("addWaterSimulated error:", err);
  }
}

// ─────────────────────────────────────────────
// Add Manual Water Data
// ─────────────────────────────────────────────
async function addWaterManual() {
  const ph   = document.getElementById("mph").value;
  const turb = document.getElementById("mturb").value;
  const temp = document.getElementById("mtemp").value;

  if (!ph || !turb || !temp) {
    alert("Please fill in all three fields.");
    return;
  }

  try {
    await fetch("/add_water_manual", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ ph: parseFloat(ph), turbidity: parseFloat(turb), temp: parseFloat(temp) })
    });

    const msgEl = document.getElementById("sensorMsg");
    msgEl.classList.remove("hidden");
    msgEl.innerHTML = `✅ Manual water reading added successfully.`;

    document.getElementById("mph").value   = "";
    document.getElementById("mturb").value = "";
    document.getElementById("mtemp").value = "";

    await refreshAll();
    setTimeout(() => msgEl.classList.add("hidden"), 4000);
  } catch (err) {
    console.error("addWaterManual error:", err);
  }
}

// ─────────────────────────────────────────────
// Chart.js — Load / Update Charts
// ─────────────────────────────────────────────
async function loadCharts() {
  try {
    const res  = await fetch("/chart_data");
    const data = await res.json();

    renderTurbidityChart(data);
    renderPhTempChart(data);
    renderPatientChart(data);
  } catch (err) {
    console.error("loadCharts error:", err);
  }
}

/** Line chart: Turbidity over time with danger threshold */
function renderTurbidityChart(data) {
  const ctx = document.getElementById("turbidityChart").getContext("2d");
  const labels = data.water_labels.length ? data.water_labels : ["No data"];
  const vals   = data.turbidity.length    ? data.turbidity    : [0];

  // Threshold line at 10 NTU
  const thresholdData = new Array(labels.length).fill(10);

  if (turbidityChart) {
    turbidityChart.data.labels              = labels;
    turbidityChart.data.datasets[0].data   = vals;
    turbidityChart.data.datasets[1].data   = thresholdData;
    turbidityChart.update();
    return;
  }

  turbidityChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label:           "Turbidity (NTU)",
          data:            vals,
          borderColor:     "#2563ab",
          backgroundColor: "rgba(37,99,171,0.1)",
          fill:            true,
          tension:         0.4,
          pointRadius:     4,
          pointBackgroundColor: vals.map(v => v > 10 ? "#e53e3e" : "#2563ab")
        },
        {
          label:       "Safe Threshold (10 NTU)",
          data:        thresholdData,
          borderColor: "#e53e3e",
          borderDash:  [6, 4],
          borderWidth: 2,
          pointRadius: 0,
          fill:        false
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "top" },
        tooltip: { mode: "index", intersect: false }
      },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: "NTU" } }
      }
    }
  });
}

/** Dual-axis line chart: pH and Temperature */
function renderPhTempChart(data) {
  const ctx = document.getElementById("phTempChart").getContext("2d");
  const labels = data.water_labels.length ? data.water_labels : ["No data"];

  if (phTempChart) {
    phTempChart.data.labels            = labels;
    phTempChart.data.datasets[0].data  = data.ph;
    phTempChart.data.datasets[1].data  = data.temp;
    phTempChart.update();
    return;
  }

  phTempChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label:           "pH Level",
          data:            data.ph,
          borderColor:     "#38a169",
          backgroundColor: "rgba(56,161,105,0.08)",
          fill:            true,
          tension:         0.4,
          yAxisID:         "yPH"
        },
        {
          label:       "Temperature (°C)",
          data:        data.temp,
          borderColor: "#ed8936",
          borderDash:  [4, 3],
          fill:        false,
          tension:     0.4,
          yAxisID:     "yTemp"
        }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "top" } },
      scales: {
        yPH: {
          type:     "linear",
          position: "left",
          title:    { display: true, text: "pH" },
          min: 4, max: 10
        },
        yTemp: {
          type:     "linear",
          position: "right",
          title:    { display: true, text: "°C" },
          grid:     { drawOnChartArea: false }
        }
      }
    }
  });
}

/** Bar chart: Patients per report */
function renderPatientChart(data) {
  const ctx = document.getElementById("patientChart").getContext("2d");
  const labels = data.health_labels.length ? data.health_labels : ["No data"];
  const vals   = data.patients.length      ? data.patients      : [0];

  const colors = vals.map(v => v > 5 ? "rgba(229,62,62,0.7)" : "rgba(37,99,171,0.7)");

  if (patientChart) {
    patientChart.data.labels                        = labels;
    patientChart.data.datasets[0].data              = vals;
    patientChart.data.datasets[0].backgroundColor   = colors;
    patientChart.update();
    return;
  }

  patientChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label:           "Patients Reported",
        data:            vals,
        backgroundColor: colors,
        borderColor:     colors.map(c => c.replace("0.7", "1")),
        borderWidth:     1,
        borderRadius:    6
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "top" },
        tooltip: { callbacks: {
          label: ctx => `${ctx.raw} patient${ctx.raw !== 1 ? "s" : ""}`
        }}
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: "No. of Patients" }
        }
      }
    }
  });
}

// ─────────────────────────────────────────────
// Table Data
// ─────────────────────────────────────────────
async function loadTableData() {
  try {
    const res  = await fetch("/chart_data");
    const data = await res.json();

    // Water table
    const waterTbody = document.getElementById("waterTbody");
    if (waterTbody) {
      const waterRows = data.water_labels.map((date, i) => ({
        date,
        ph:        data.ph[i],
        turbidity: data.turbidity[i],
        temp:      data.temp[i]
      })).reverse().slice(0, 10);

      waterTbody.innerHTML = waterRows.map((r, i) => `
        <tr>
          <td>${i + 1}</td>
          <td>${r.ph}</td>
          <td class="${r.turbidity > 10 ? 'badge-yes' : ''}">${r.turbidity}</td>
          <td>${r.temp}</td>
          <td style="font-size:0.75rem;color:#a0aec0">${r.date}</td>
        </tr>
      `).join("") || `<tr><td colspan="5" style="text-align:center;color:#a0aec0">No data yet</td></tr>`;
    }

    // Health table
    const healthTbody = document.getElementById("healthTbody");
    if (healthTbody) {
      // We'll load from a separate endpoint if available; otherwise show placeholder
      const hRes  = await fetch("/village_data");
      const hData = await hRes.json();

      healthTbody.innerHTML = hData.length
        ? hData.map(r => `
            <tr>
              <td>${r.village}</td>
              <td class="${r.patients > 5 ? 'badge-yes' : ''}">${r.patients}</td>
              <td>—</td><td>—</td><td>—</td>
            </tr>
          `).join("")
        : `<tr><td colspan="5" style="text-align:center;color:#a0aec0">No reports yet</td></tr>`;
    }
  } catch (err) {
    console.error("loadTableData error:", err);
  }
}

// ─────────────────────────────────────────────
// Leaflet Map — Northeast India
// ─────────────────────────────────────────────
function initMap() {
  const mapEl = document.getElementById("map");
  if (!mapEl || leafletMap) return;

  // Centre on Assam/NE India
  leafletMap = L.map("map").setView([25.5, 92.5], 6);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
    maxZoom: 18
  }).addTo(leafletMap);

  // Add a legend
  const legend = L.control({ position: "bottomright" });
  legend.onAdd = () => {
    const div = L.DomUtil.create("div", "");
    div.style.cssText = "background:white;padding:10px;border-radius:8px;font-size:12px;box-shadow:0 2px 8px rgba(0,0,0,0.2)";
    div.innerHTML = `
      <strong>Patient Count</strong><br>
      🔴 High (&gt;10)<br>
      🟡 Moderate (6–10)<br>
      🟢 Low (≤5)
    `;
    return div;
  };
  legend.addTo(leafletMap);
}

async function loadMapData() {
  if (!leafletMap) return;

  try {
    const res  = await fetch("/village_data");
    const data = await res.json();

    // Remove existing markers
    leafletMap.eachLayer(layer => {
      if (layer instanceof L.CircleMarker) leafletMap.removeLayer(layer);
    });

    data.forEach(v => {
      const color  = v.patients > 10 ? "#e53e3e" : v.patients > 5 ? "#ed8936" : "#38a169";
      const radius = Math.min(8 + v.patients * 1.5, 30);

      L.circleMarker([v.lat, v.lng], {
        radius,
        fillColor:   color,
        color:       color,
        fillOpacity: 0.7,
        weight:      2
      })
      .bindPopup(`
        <div style="font-family:sans-serif;min-width:140px">
          <strong style="font-size:1rem">🏘️ ${v.village}</strong><br>
          <span style="color:#718096">Patients:</span> <b style="color:${color}">${v.patients}</b><br>
          <span style="color:#718096">Reports:</span>  ${v.reports}
        </div>
      `)
      .addTo(leafletMap);
    });

    // Add default pins for villages with no data
    const DEFAULT_VILLAGES = {
      "Majuli":    [27.0041, 94.5916],
      "Sibsagar":  [26.9834, 94.6418],
      "Tezpur":    [26.6338, 92.7957],
      "Jorhat":    [26.7509, 94.2037],
      "Imphal":    [24.8170, 93.9368],
      "Shillong":  [25.5788, 91.8933],
      "Kohima":    [25.6751, 94.1086],
      "Agartala":  [23.8315, 91.2868],
    };

    const reportedVillages = new Set(data.map(v => v.village));
    Object.entries(DEFAULT_VILLAGES).forEach(([name, coords]) => {
      if (!reportedVillages.has(name)) {
        L.circleMarker(coords, {
          radius: 6, fillColor: "#a0aec0", color: "#718096",
          fillOpacity: 0.5, weight: 1
        })
        .bindPopup(`<strong>${name}</strong><br><i>No reports yet</i>`)
        .addTo(leafletMap);
      }
    });

  } catch (err) {
    console.error("loadMapData error:", err);
  }
}
