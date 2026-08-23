import streamlit as st


def inject_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: -0.02em;
        }

        .stApp {
            background: radial-gradient(circle at 20% 0%, #131C2E 0%, #0B1220 55%);
        }

        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace;
            color: #E8A33D;
        }

        .stTextInput input {
            background-color: #131C2E !important;
            border: 1px solid #2A3550 !important;
            border-radius: 10px !important;
            color: #E7ECF3 !important;
        }

        .stButton button {
            background: linear-gradient(135deg, #E8A33D 0%, #C97F1F 100%) !important;
            color: #0B1220 !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 10px !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(232, 163, 61, 0.35);
        }

        .pipeline {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 1.2rem 0 1.8rem 0;
            padding: 14px 18px;
            background: #131C2E;
            border: 1px solid #2A3550;
            border-radius: 14px;
        }

        .pipeline-node {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            color: #8792A6;
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid #2A3550;
            animation: pulseGlow 6s ease-in-out infinite;
        }

        .pipeline-node:nth-child(1) { animation-delay: 0s; }
        .pipeline-node:nth-child(3) { animation-delay: 1.5s; }
        .pipeline-node:nth-child(5) { animation-delay: 3s; }
        .pipeline-node:nth-child(7) { animation-delay: 4.5s; }

        .pipeline-arrow {
            color: #2A3550;
            font-size: 0.9rem;
        }

        @keyframes pulseGlow {
            0%, 70%, 100% { border-color: #2A3550; color: #8792A6; box-shadow: none; }
            15% { border-color: #E8A33D; color: #E8A33D; box-shadow: 0 0 12px rgba(232, 163, 61, 0.4); }
        }

        .report-card {
            background: #131C2E;
            border: 1px solid #2A3550;
            border-left: 3px solid #4FD1C5;
            border-radius: 12px;
            padding: 20px 24px;
            animation: fadeIn 0.5s ease;
        }

        .approval-card {
            background: #131C2E;
            border: 1px solid #2A3550;
            border-left: 3px solid #E8A33D;
            border-radius: 12px;
            padding: 20px 24px;
            animation: fadeIn 0.5s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        [data-testid="stSidebar"] {
            background-color: #0E1526;
            border-right: 1px solid #2A3550;
        }
        </style>
    """, unsafe_allow_html=True)


def render_pipeline():
    st.markdown("""
        <div class="pipeline">
            <span class="pipeline-node">RESEARCHER</span>
            <span class="pipeline-arrow">→</span>
            <span class="pipeline-node">CRITIC</span>
            <span class="pipeline-arrow">→</span>
            <span class="pipeline-node">WRITER</span>
            <span class="pipeline-arrow">→</span>
            <span class="pipeline-node">EDITOR</span>
        </div>
    """, unsafe_allow_html=True)