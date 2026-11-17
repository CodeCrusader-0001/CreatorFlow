"""
CreatorFlow – AI-Powered Content Production & Optimization Platform.
Main Streamlit application entrypoint.
"""

import streamlit as st
import os

# Set page config as the very first Streamlit call
st.set_page_config(
    page_title="CreatorFlow | AI Content Production Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

import config
import database
import gemini_service
from ui.theme import apply_theme
from ui.dashboard import render_dashboard
from ui.content_studio import render_content_studio
from ui.repurpose_studio import render_repurpose_studio
from ui.translation_studio import render_translation_studio
from ui.evaluator import render_evaluator
from ui.ab_testing import render_ab_testing
from ui.library import render_content_library


def main():
    # 1. Initialize SQLite Database automatically on startup
    database.init_db()

    # 2. Apply Custom Modern SaaS Dark Navy Theme
    apply_theme()

    # 3. Sidebar Brand & Navigation
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">⚡</div>
                <div>
                    <div class="sidebar-brand-title">{config.APP_NAME}</div>
                    <div style="font-size: 0.72rem; color: #64748b;">Production Assistant</div>
                </div>
                <div class="sidebar-brand-badge">v{config.APP_VERSION}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_options = [
            "Dashboard",
            "Content Studio",
            "Repurpose Studio",
            "Translation Studio",
            "Content Evaluator",
            "A/B Hook Testing",
            "Content Library",
        ]

        # Handle page navigation sync with session state (for quick links)
        if "nav_selection" not in st.session_state:
            st.session_state["nav_selection"] = "Dashboard"

        try:
            current_index = nav_options.index(st.session_state["nav_selection"])
        except ValueError:
            current_index = 0

        selected_page = st.radio(
            "Navigation",
            nav_options,
            index=current_index,
            label_visibility="collapsed",
            key="sidebar_nav_radio",
        )

        # Update if changed via radio
        if selected_page != st.session_state["nav_selection"]:
            st.session_state["nav_selection"] = selected_page
            st.rerun()

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # 4. Engine & API Configuration in Sidebar
        st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;'>Engine Settings</div>", unsafe_allow_html=True)

        env_key_available = bool(config.GEMINI_API_KEY)
        session_key = st.session_state.get("custom_api_key", "")
        has_active_key = env_key_available or bool(session_key)

        if has_active_key:
            source = "Environment (.env)" if env_key_available and not session_key else "Session Override"
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="height: 8px; width: 8px; border-radius: 50%; background-color: #10b981; display: inline-block;"></span>
                    <span style="font-size: 0.8rem; color: #34d399; font-weight: 500;">Gemini API Connected</span>
                </div>
                <div style="font-size: 0.72rem; color: #64748b; margin-top: -0.5rem; margin-bottom: 0.75rem;">
                    Source: {source}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="height: 8px; width: 8px; border-radius: 50%; background-color: #f59e0b; display: inline-block;"></span>
                    <span style="font-size: 0.8rem; color: #fbbf24; font-weight: 500;">API Key Required</span>
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; line-height: 1.4; margin-bottom: 0.5rem;">
                    Add <code>GEMINI_API_KEY</code> to <code>.env</code> or enter an API key below:
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("⚙️ Configure API & Model", expanded=(not has_active_key)):
            user_key_input = st.text_input(
                "Gemini API Key",
                type="password",
                value=st.session_state.get("custom_api_key", ""),
                help="Enter your Google Gemini API key. Never shared or hardcoded.",
                placeholder="AIzaSy...",
                key="api_key_sidebar_input",
            )
            if user_key_input:
                st.session_state["custom_api_key"] = user_key_input.strip()

            model_choices = [
                "gemini-3.8-flash",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
            ]
            current_default_model = config.GEMINI_MODEL
            try:
                model_idx = model_choices.index(current_default_model)
            except ValueError:
                model_choices.insert(0, current_default_model)
                model_idx = 0

            selected_model = st.selectbox(
                "Active Model",
                model_choices,
                index=model_idx,
                help="Configurable via GEMINI_MODEL env var.",
            )
            st.session_state["custom_model"] = selected_model

            st.markdown(
                """
                <div style="font-size: 0.72rem; color: #64748b; margin-top: 0.5rem;">
                    Get an API key from <a href="https://aistudio.google.com/" target="_blank" style="color: #60a5fa;">Google AI Studio</a>.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Database info
        st.markdown(
            f"""
            <div style="border-top: 1px solid #1e293b; padding-top: 0.75rem; margin-top: 1rem; font-size: 0.72rem; color: #64748b;">
                💾 <strong>Database:</strong> SQLite (WAL Enabled)<br/>
                📁 <code>creatorflow.db</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5. Route to Selected Page
    active_page = st.session_state["nav_selection"]

    if active_page == "Dashboard":
        render_dashboard()
    elif active_page == "Content Studio":
        render_content_studio()
    elif active_page == "Repurpose Studio":
        render_repurpose_studio()
    elif active_page == "Translation Studio":
        render_translation_studio()
    elif active_page == "Content Evaluator":
        render_evaluator()
    elif active_page == "A/B Hook Testing":
        render_ab_testing()
    elif active_page == "Content Library":
        render_content_library()


if __name__ == "__main__":
    main()

