"""
AquaGuard Nepal — AI-Powered Hydropower ESG Monitoring Dashboard
Streamlit frontend for the Smart-Nepal-Hydro FastAPI backend.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import glob
import time

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
API_BASE = "http://localhost:8000"
CHISAPANI_DIR = "chisapani_yearly_csv"
MASTER_CSV = os.path.join(CHISAPANI_DIR, "chisapani_master_cleaned.csv")

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AquaGuard Nepal",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS — Premium Dark Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global ─────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0e17 0%, #0f1923 40%, #0a1628 100%);
}

/* Hide default Streamlit header/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Hero Header ────────────────────────── */
.hero-container {
    background: linear-gradient(135deg, rgba(0,212,170,0.08) 0%, rgba(0,120,255,0.06) 50%, rgba(220,40,60,0.05) 100%);
    border: 1px solid rgba(0,212,170,0.15);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(0,212,170,0.06) 0%, transparent 50%),
                radial-gradient(circle at 70% 50%, rgba(0,120,255,0.04) 0%, transparent 50%);
    animation: shimmer 8s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { transform: translateX(-5%) translateY(-5%); }
    50% { transform: translateX(5%) translateY(5%); }
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00D4AA, #0078FF, #DC283C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
    position: relative;
    z-index: 1;
}
.hero-sub {
    color: #8892a4;
    font-size: 1.05rem;
    font-weight: 400;
    position: relative;
    z-index: 1;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,212,170,0.12);
    border: 1px solid rgba(0,212,170,0.25);
    padding: 5px 14px;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #00D4AA;
    margin-top: 0.8rem;
    position: relative;
    z-index: 1;
}
.pulse-dot {
    width: 8px;
    height: 8px;
    background: #00D4AA;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0,212,170,0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 8px rgba(0,212,170,0); }
}

/* ── Section Headers ────────────────────── */
.section-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: #e8eaed;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(0,212,170,0.2);
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ── Metric Cards ───────────────────────── */
.metric-card {
    background: linear-gradient(145deg, rgba(26,31,46,0.9), rgba(18,24,38,0.95));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.metric-card:hover {
    border-color: rgba(0,212,170,0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,212,170,0.08);
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.metric-card.teal::after { background: linear-gradient(90deg, #00D4AA, #00B894); }
.metric-card.blue::after { background: linear-gradient(90deg, #0078FF, #00B4D8); }
.metric-card.crimson::after { background: linear-gradient(90deg, #DC283C, #FF6B6B); }
.metric-card.amber::after { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
.metric-card.purple::after { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }

.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0.5rem 0 0.2rem;
}
.metric-label {
    font-size: 0.82rem;
    color: #8892a4;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.metric-icon {
    font-size: 1.8rem;
}

/* ── Status Badges ──────────────────────── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 16px;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 600;
}
.status-compliant {
    background: rgba(0,212,170,0.12);
    border: 1px solid rgba(0,212,170,0.3);
    color: #00D4AA;
}
.status-warning {
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.3);
    color: #F59E0B;
}
.status-violation {
    background: rgba(220,40,60,0.12);
    border: 1px solid rgba(220,40,60,0.3);
    color: #DC283C;
}

/* ── Alert Cards ────────────────────────── */
.alert-card {
    background: linear-gradient(145deg, rgba(220,40,60,0.06), rgba(255,107,107,0.03));
    border: 1px solid rgba(220,40,60,0.2);
    border-left: 4px solid #DC283C;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    color: #e8eaed;
    font-size: 0.92rem;
}
.alert-card.safe {
    background: linear-gradient(145deg, rgba(0,212,170,0.06), rgba(0,184,148,0.03));
    border: 1px solid rgba(0,212,170,0.2);
    border-left: 4px solid #00D4AA;
}

/* ── AI Summary Box ─────────────────────── */
.ai-summary {
    background: linear-gradient(145deg, rgba(0,120,255,0.06), rgba(139,92,246,0.04));
    border: 1px solid rgba(0,120,255,0.15);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    color: #c8cdd5;
    line-height: 1.7;
    font-size: 0.92rem;
    position: relative;
}
.ai-summary::before {
    content: '✨ AI Analysis';
    display: block;
    font-size: 0.75rem;
    font-weight: 700;
    color: #8B5CF6;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.8rem;
}

/* ── Gauge Container ────────────────────── */
.gauge-container {
    background: linear-gradient(145deg, rgba(26,31,46,0.9), rgba(18,24,38,0.95));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1rem;
}

/* ── Sidebar Styling ────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1320 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.04);
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e8eaed;
}

/* ── Streamlit widget overrides ─────────── */
.stSlider > div > div > div {
    background: rgba(0,212,170,0.3) !important;
}
div[data-baseweb="select"] > div {
    background: rgba(26,31,46,0.9) !important;
    border-color: rgba(255,255,255,0.08) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #00D4AA, #0078FF) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(0,212,170,0.25) !important;
}

/* ── Divider ────────────────────────────── */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,170,0.15), transparent);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────
def call_api(endpoint, payload):
    """Call the FastAPI backend. Returns None on failure."""
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None


def risk_color(score):
    """Return a color based on risk score (0-100)."""
    if score >= 70:
        return "#DC283C"
    elif score >= 40:
        return "#F59E0B"
    return "#00D4AA"


def compliance_badge(status):
    """Return styled HTML badge for compliance status."""
    class_map = {
        "Compliant": "status-compliant",
        "Warning": "status-warning",
        "Violation": "status-violation",
    }
    icons = {"Compliant": "✅", "Warning": "⚠️", "Violation": "🚨"}
    cls = class_map.get(status, "status-warning")
    icon = icons.get(status, "❓")
    return f'<span class="status-badge {cls}">{icon} {status}</span>'


def make_gauge(value, title, max_val=100, color="#00D4AA"):
    """Create a Plotly gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14, "color": "#8892a4"}},
        number={"font": {"size": 36, "color": "#e8eaed"}},
        gauge={
            "axis": {"range": [0, max_val], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)",
                     "tickfont": {"color": "#555"}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(26,31,46,0.5)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, max_val * 0.33], "color": "rgba(0,212,170,0.08)"},
                {"range": [max_val * 0.33, max_val * 0.66], "color": "rgba(245,158,11,0.08)"},
                {"range": [max_val * 0.66, max_val], "color": "rgba(220,40,60,0.08)"},
            ],
            "threshold": {
                "line": {"color": "#e8eaed", "width": 2},
                "thickness": 0.8,
                "value": value,
            },
        },
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter"},
    )
    return fig


# ─────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🏔️ AquaGuard Nepal</div>
    <div class="hero-sub">AI-Powered Hydropower ESG Monitoring &amp; IFC PS4 Compliance Dashboard</div>
    <div class="hero-badge"><div class="pulse-dot"></div> System Online — Real-time Monitoring Active</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar — Sensor Input Panel
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📡 Sensor Inputs")
    st.markdown("Configure environmental parameters for analysis.")
    st.markdown("---")

    st.markdown("### 🌡️ Weather Conditions")
    temperature = st.slider("Temperature (°C)", min_value=-10.0, max_value=50.0, value=25.0, step=0.5,
                            help="Current ambient temperature")
    rainfall = st.slider("Rainfall (mm)", min_value=0.0, max_value=100.0, value=15.0, step=0.5,
                         help="Current rainfall measurement")
    humidity = st.slider("Relative Humidity (%)", min_value=0.0, max_value=100.0, value=65.0, step=1.0,
                         help="Current relative humidity")

    st.markdown("---")
    st.markdown("### 🌊 River Hydrology")
    river_flow = st.slider("River Flow (m³/s)", min_value=0.0, max_value=1000.0, value=350.0, step=5.0,
                           help="Current river discharge")
    rolling_flow = st.slider("Rolling Avg Flow (m³/s)", min_value=0.0, max_value=1000.0, value=300.0, step=5.0,
                             help="7-day rolling average flow")
    eco_threshold = st.slider("Eco Threshold (m³/s)", min_value=0.0, max_value=500.0, value=200.0, step=5.0,
                              help="Minimum ecological flow requirement")

    st.markdown("---")
    st.markdown("### 📊 Compliance Inputs")
    compliance_score_input = st.slider("Current Compliance Score", min_value=0, max_value=100, value=85, step=1)
    anomaly_flag = st.checkbox("Anomaly Detected", value=False)

    st.markdown("---")
    analyze = st.button("🔍 Run Full Analysis", use_container_width=True)


# ─────────────────────────────────────────────
# Main Content — Top Metrics Row
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Current Conditions Overview</div>', unsafe_allow_html=True)

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(f"""
    <div class="metric-card teal">
        <div class="metric-icon">🌡️</div>
        <div class="metric-value" style="color:#00D4AA;">{temperature}°</div>
        <div class="metric-label">Temperature</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card blue">
        <div class="metric-icon">🌧️</div>
        <div class="metric-value" style="color:#0078FF;">{rainfall}</div>
        <div class="metric-label">Rainfall (mm)</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card purple">
        <div class="metric-icon">💧</div>
        <div class="metric-value" style="color:#A78BFA;">{humidity}%</div>
        <div class="metric-label">Humidity</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card amber">
        <div class="metric-icon">🌊</div>
        <div class="metric-value" style="color:#FBBF24;">{river_flow}</div>
        <div class="metric-label">River Flow (m³/s)</div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    eco_status = "✅" if river_flow >= eco_threshold else "⚠️"
    eco_color = "#00D4AA" if river_flow >= eco_threshold else "#F59E0B"
    st.markdown(f"""
    <div class="metric-card crimson">
        <div class="metric-icon">{eco_status}</div>
        <div class="metric-value" style="color:{eco_color};">{eco_threshold}</div>
        <div class="metric-label">Eco Threshold</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Analysis Results (shown when button is clicked)
# ─────────────────────────────────────────────
if analyze:
    with st.spinner("🔄 Running AI analysis across all modules..."):
        # ── 1. Flood Risk Prediction ────────
        predict_payload = {
            "temperature": temperature,
            "rainfall": rainfall,
            "humidity": humidity,
            "river_flow": river_flow,
        }
        prediction_result = call_api("/predict", predict_payload)

        # ── 2. IFC Compliance ───────────────
        compliance_payload = {
            "current_flow": river_flow,
            "eco_threshold": eco_threshold,
        }
        compliance_result = call_api("/compliance", compliance_payload)

        # ── 3. Anomaly Alerts ───────────────
        alerts_payload = {
            "rainfall": rainfall,
            "river_flow": river_flow,
            "rolling_flow": rolling_flow,
        }
        alerts_result = call_api("/alerts", alerts_payload)

        # ── 4. Analytics (ESG + Forecast + AI Summary)
        analytics_payload = {
            "rainfall": rainfall,
            "humidity": humidity,
            "temperature": temperature,
            "compliance_score": compliance_score_input,
            "anomaly_detected": anomaly_flag,
            "river_flow": river_flow,
        }
        analytics_result = call_api("/analytics", analytics_payload)

    # ── Display Results ─────────────────────
    st.markdown('<div class="section-header">🌊 Flood Risk Prediction</div>', unsafe_allow_html=True)

    if prediction_result:
        risk_val = prediction_result.get("predicted_risk", 0)
        risk_pct = min(abs(risk_val) * 100, 100)
        r_color = risk_color(risk_pct)

        col_gauge, col_info = st.columns([1, 1])
        with col_gauge:
            st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
            fig = make_gauge(risk_pct, "Flood Risk Score", color=r_color)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_info:
            if risk_pct >= 70:
                level, desc, icon = "HIGH", "Immediate action required. Conditions indicate elevated flood probability.", "🔴"
            elif risk_pct >= 40:
                level, desc, icon = "MODERATE", "Monitor closely. Current parameters suggest possible risk escalation.", "🟡"
            else:
                level, desc, icon = "LOW", "Conditions are within safe parameters. Continue routine monitoring.", "🟢"

            st.markdown(f"""
            <div class="metric-card {'crimson' if risk_pct >= 70 else 'amber' if risk_pct >= 40 else 'teal'}">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value" style="color:{r_color};">{level}</div>
                <div class="metric-label">Risk Level</div>
                <p style="color:#8892a4; font-size:0.85rem; margin-top:0.8rem;">{desc}</p>
                <p style="color:#555; font-size:0.75rem; margin-top:0.5rem;">Raw model output: {risk_val:.4f}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Could not reach the Prediction API. Make sure the FastAPI backend is running on port 8000.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── IFC PS4 Compliance ──────────────────
    st.markdown('<div class="section-header">✅ IFC PS4 Compliance Status</div>', unsafe_allow_html=True)

    if compliance_result:
        ps4_status = compliance_result.get("ps4_status", "Unknown")
        comp_score = compliance_result.get("compliance_score", 0)

        cc1, cc2 = st.columns([1, 1])
        with cc1:
            badge_color = "#00D4AA" if ps4_status == "Compliant" else "#F59E0B" if ps4_status == "Warning" else "#DC283C"
            st.markdown(f"""
            <div class="metric-card {'teal' if ps4_status == 'Compliant' else 'amber' if ps4_status == 'Warning' else 'crimson'}">
                <div style="margin-bottom:1rem;">{compliance_badge(ps4_status)}</div>
                <div class="metric-value" style="color:{badge_color};">{comp_score}</div>
                <div class="metric-label">Compliance Score</div>
                <p style="color:#8892a4; font-size:0.82rem; margin-top:0.8rem;">
                    Current Flow: {river_flow} m³/s &nbsp;|&nbsp; Eco Threshold: {eco_threshold} m³/s
                </p>
            </div>
            """, unsafe_allow_html=True)

        with cc2:
            st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
            comp_gauge = make_gauge(comp_score, "Compliance Rating", color=badge_color)
            st.plotly_chart(comp_gauge, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Could not reach the Compliance API.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Anomaly Alerts ──────────────────────
    st.markdown('<div class="section-header">⚠️ Anomaly Detection & Alerts</div>', unsafe_allow_html=True)

    if alerts_result:
        alert_list = alerts_result.get("alerts", [])
        if alert_list:
            for alert_msg in alert_list:
                st.markdown(f"""
                <div class="alert-card">
                    <strong>🚨 ALERT:</strong> {alert_msg}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-card safe">
                <strong>✅ All Clear:</strong> No anomalies detected. River system operating within expected parameters.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Could not reach the Alerts API.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Analytics Dashboard ─────────────────
    st.markdown('<div class="section-header">📈 Analytics & ESG Dashboard</div>', unsafe_allow_html=True)

    if analytics_result:
        forecast = analytics_result.get("forecast", {})
        esg = analytics_result.get("esg_score", 0)
        ai_summary_data = analytics_result.get("ai_summary", {})

        ac1, ac2, ac3 = st.columns(3)

        with ac1:
            f_level = forecast.get("forecast_risk", "N/A")
            f_score = forecast.get("risk_score", 0)
            f_color = "#DC283C" if f_level == "High" else "#F59E0B" if f_level == "Moderate" else "#00D4AA"
            st.markdown(f"""
            <div class="metric-card {'crimson' if f_level == 'High' else 'amber' if f_level == 'Moderate' else 'teal'}">
                <div class="metric-icon">📊</div>
                <div class="metric-value" style="color:{f_color};">{f_level}</div>
                <div class="metric-label">Risk Forecast</div>
                <p style="color:#555; font-size:0.78rem; margin-top:0.5rem;">Score: {f_score}%</p>
            </div>
            """, unsafe_allow_html=True)

        with ac2:
            esg_color = "#00D4AA" if esg >= 70 else "#F59E0B" if esg >= 40 else "#DC283C"
            st.markdown(f"""
            <div class="metric-card {'teal' if esg >= 70 else 'amber' if esg >= 40 else 'crimson'}">
                <div class="metric-icon">🌿</div>
                <div class="metric-value" style="color:{esg_color};">{esg}</div>
                <div class="metric-label">ESG Score</div>
                <p style="color:#555; font-size:0.78rem; margin-top:0.5rem;">{"Anomaly penalty applied" if anomaly_flag else "No anomaly penalty"}</p>
            </div>
            """, unsafe_allow_html=True)

        with ac3:
            st.markdown(f"""
            <div class="metric-card purple">
                <div class="metric-icon">🤖</div>
                <div class="metric-value" style="color:#A78BFA;">Gemini</div>
                <div class="metric-label">AI Engine</div>
                <p style="color:#555; font-size:0.78rem; margin-top:0.5rem;">Gemini 1.5 Flash</p>
            </div>
            """, unsafe_allow_html=True)

        # AI Summary
        if ai_summary_data:
            summary_text = ai_summary_data.get("summary", "") if isinstance(ai_summary_data, dict) else str(ai_summary_data)
            audio_path = ai_summary_data.get("audio_file", "") if isinstance(ai_summary_data, dict) else ""

            st.markdown(f"""
            <div class="ai-summary">
                {summary_text}
            </div>
            """, unsafe_allow_html=True)

            # Voice Alert Audio Player
            if audio_path:
                st.markdown('<div class="section-header" style="margin-top:1.5rem;">🔊 Voice Alert</div>',
                            unsafe_allow_html=True)
                audio_url = f"{API_BASE}{audio_path}"
                st.audio(audio_url, format="audio/mp3")
    else:
        st.warning("⚠️ Could not reach the Analytics API. Ensure the FastAPI backend is running and GEMINI_API_KEY is set.")


# ─────────────────────────────────────────────
# Historical Discharge Data (always visible)
# ─────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">📉 Historical Chisapani River Discharge</div>', unsafe_allow_html=True)

@st.cache_data
def load_master_discharge():
    """Load the master Chisapani discharge CSV."""
    if os.path.exists(MASTER_CSV):
        df = pd.read_csv(MASTER_CSV, parse_dates=["datetime"])
        return df
    return None

discharge_df = load_master_discharge()

if discharge_df is not None and not discharge_df.empty:
    # Year range selector
    min_year = int(discharge_df["datetime"].dt.year.min())
    max_year = int(discharge_df["datetime"].dt.year.max())

    yr_col1, yr_col2 = st.columns([1, 3])
    with yr_col1:
        year_range = st.slider(
            "Select Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(max(min_year, 2015), max_year),
        )

    filtered = discharge_df[
        (discharge_df["datetime"].dt.year >= year_range[0])
        & (discharge_df["datetime"].dt.year <= year_range[1])
    ]

    # Main discharge time series
    fig_discharge = go.Figure()
    fig_discharge.add_trace(go.Scatter(
        x=filtered["datetime"],
        y=filtered["discharge_cms"],
        mode="lines",
        name="Discharge",
        line=dict(color="#0078FF", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(0,120,255,0.08)",
    ))

    # Add rolling average
    if len(filtered) > 30:
        filtered = filtered.copy()
        filtered["rolling_30d"] = filtered["discharge_cms"].rolling(window=30, min_periods=1).mean()
        fig_discharge.add_trace(go.Scatter(
            x=filtered["datetime"],
            y=filtered["rolling_30d"],
            mode="lines",
            name="30-Day Average",
            line=dict(color="#00D4AA", width=2, dash="dot"),
        ))

    fig_discharge.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#8892a4"),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.03)",
            showgrid=True,
            title=None,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            showgrid=True,
            title="Discharge (m³/s)",
            titlefont=dict(size=12),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig_discharge, use_container_width=True)

    # Monthly distribution box plot
    st.markdown("#### Monthly Discharge Distribution")
    filtered_box = filtered.copy()
    filtered_box["month"] = filtered_box["datetime"].dt.month
    month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                   7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
    filtered_box["month_name"] = filtered_box["month"].map(month_names)

    fig_box = go.Figure()
    colors = ["#00D4AA", "#00B894", "#00A896", "#0078FF", "#00B4D8", "#48CAE4",
              "#F59E0B", "#FBBF24", "#DC283C", "#FF6B6B", "#8B5CF6", "#A78BFA"]

    for i, m in enumerate(range(1, 13)):
        month_data = filtered_box[filtered_box["month"] == m]["discharge_cms"]
        if not month_data.empty:
            fig_box.add_trace(go.Box(
                y=month_data,
                name=month_names[m],
                marker_color=colors[i],
                line_color=colors[i],
                fillcolor=f"rgba({int(colors[i][1:3],16)},{int(colors[i][3:5],16)},{int(colors[i][5:7],16)},0.15)",
            ))

    fig_box.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#8892a4"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.03)"),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            title="Discharge (m³/s)",
            titlefont=dict(size=12),
        ),
        showlegend=False,
    )
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.info("📂 No historical discharge data found. Place `chisapani_master_cleaned.csv` in the `chisapani_yearly_csv/` directory.")


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:1.5rem 0 2rem; color:#4a5568;">
    <div style="font-size:0.85rem; font-weight:600; color:#8892a4;">
        🏔️ AquaGuard Nepal &nbsp;·&nbsp; AI-Powered Hydropower ESG Monitoring
    </div>
    <div style="font-size:0.72rem; margin-top:0.4rem; color:#4a5568;">
        Built with Streamlit &nbsp;·&nbsp; PyTorch &nbsp;·&nbsp; Gemini AI &nbsp;·&nbsp; FastAPI
    </div>
</div>
""", unsafe_allow_html=True)
