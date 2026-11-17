"""
CreatorFlow Theme & Styling Module.
Provides CSS rules for a sleek, modern enterprise dark-navy SaaS aesthetic.
"""

import streamlit as st


def apply_theme():
    """Inject custom CSS for dark navy and subtle blue SaaS aesthetic."""
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography and Base */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Top padding adjustment */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1250px !important;
    }

    /* Main background accents */
    .stApp {
        background-color: #090d16;
        color: #e2e8f0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1322 !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Brand Logo / Header in Sidebar */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0 1.25rem 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 1rem;
    }
    .sidebar-brand-icon {
        background: linear-gradient(135deg, #2563eb 0%, #38bdf8 100%);
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #ffffff;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    .sidebar-brand-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.02em;
    }
    .sidebar-brand-badge {
        font-size: 0.65rem;
        background: rgba(37, 99, 235, 0.2);
        color: #60a5fa;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin-left: auto;
        font-weight: 600;
    }

    /* Card Containers */
    .cf-card {
        background-color: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .cf-card:hover {
        border-color: #334155;
    }

    .cf-card-highlight {
        background: linear-gradient(180deg, #131c31 0%, #111827 100%);
        border: 1px solid #2563eb;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.15);
    }

    /* Metric Cards */
    .metric-card {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        display: flex;
        flex-direction: column;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .metric-hint {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }

    /* Badges */
    .cf-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .cf-badge-blue {
        background: rgba(37, 99, 235, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .cf-badge-green {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .cf-badge-purple {
        background: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    .cf-badge-amber {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    /* Disclaimer Callout */
    .cf-disclaimer {
        background-color: rgba(30, 41, 59, 0.4);
        border-left: 3px solid #64748b;
        padding: 0.65rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.8rem;
        color: #94a3b8;
        margin: 1rem 0;
        line-height: 1.4;
    }

    /* Page Titles & Headers */
    .page-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .page-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.75rem;
    }

    /* Form Fields Styling */
    .stTextArea textarea {
        background-color: #0d1322 !important;
        color: #f1f5f9 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        font-size: 0.92rem !important;
        line-height: 1.5 !important;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }

    .stTextInput input {
        background-color: #0d1322 !important;
        color: #f1f5f9 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }

    .stSelectbox > div > div {
        background-color: #0d1322 !important;
        border: 1px solid #1e293b !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #273549;
        border-color: #475569;
        color: #ffffff;
    }

    /* Primary Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: 1px solid #3b82f6 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(180deg, #1d4ed8 0%, #1e40af 100%) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
    }

    /* Code blocks */
    pre, code {
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: 6px !important;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #111827 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }

    /* Radio button pills */
    div[role="radiogroup"] {
        gap: 0.5rem;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

