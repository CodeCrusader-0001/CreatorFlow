"""
CreatorFlow Content Studio View.
Handles creation of 5 catchy titles, 1 engaging description, and 3 promotional hooks
with individual copy and save-to-library functionality.
"""

import streamlit as st
import json
import config
import database
import gemini_service

SAMPLE_STORIES = {
    "The Autonomous Glitch (Sci-Fi / Thriller)": (
        "In 2038, Maya Vance builds Chronos, an AI that predicts subway infrastructure failures in New York. "
        "During a routine nocturnal diagnostic, Chronos flags a catastrophic derailment scheduled to happen in 14 minutes—"
        "on a decommissioned express line that hasn't carried passengers since 1984. When Maya descends into the abandoned "
        "tunnels to investigate, she discovers the train isn't carrying cargo; it's transporting 200 high-profile citizens "
        "who officially died five years ago. Now, she has less than ten minutes to decide whether to trigger the emergency "
        "brakes and expose an underground global conspiracy, or let the train vanish into the Hudson deep tunnels forever."
    ),
    "Bootstrapped to Billions (Business / Tech)": (
        "After getting rejected by 42 Silicon Valley venture capitalists for being 'too practical,' two aerospace engineers "
        "started building commercial micro-satellites from an abandoned warehouse in Detroit using repurposed automotive robotics. "
        "With only $12,000 left on their maxed-out credit cards and four days before their landlord changed the locks, they received "
        "an unsolicited encrypted transmission offering a $50 million government contract—with one impossible condition."
    ),
    "The 4:00 AM Habit That Stole My Life (Self-Improvement / Drama)": (
        "I followed the extreme productivity gospel for three years: cold showers, 4:00 AM alarms, ruthless time-blocking, "
        "and zero social distractions. I built two seven-figure digital companies, got in peak physical shape, and amassed "
        "half a million followers. But on a Tuesday afternoon during my quarterly review, I realized I hadn't laughed, cried, "
        "or spoken to anyone without an agenda in 1,000 days. This is the confession of what happens when optimization kills "
        "your humanity."
    ),
}


def render_content_studio():
    """Render the Content Studio interface."""
    st.markdown('<div class="page-title">Content Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Transform raw story concepts and scripts into high-converting titles, descriptions, and scroll-stopping hooks.</div>',
        unsafe_allow_html=True,
    )

    # Sample loader toolbar
    with st.expander("💡 Need inspiration? Load a production-ready sample story", expanded=False):
        sample_choice = st.selectbox("Choose a sample scenario:", list(SAMPLE_STORIES.keys()))
        if st.button("Load Selected Sample into Editor"):
            st.session_state["cs_story_input"] = SAMPLE_STORIES[sample_choice]
            st.rerun()

    # Main Input Form
    with st.container():
        story_input = st.text_area(
            "Story / Script Concept",
            value=st.session_state.get("cs_story_input", ""),
            height=180,
            placeholder="Paste your story synopsis, script draft, podcast concept, or video pitch here...",
            key="cs_story_input_area",
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            genre = st.selectbox("Genre", config.GENRES, index=0)
        with col2:
            audience = st.selectbox("Target Audience", config.AUDIENCES, index=0)
        with col3:
            language = st.selectbox("Language", config.SUPPORTED_LANGUAGES, index=0)
        with col4:
            tone = st.selectbox("Narrative Tone", config.TONES, index=0)

        generate_clicked = st.button("⚡ Generate Production Bundle", type="primary", use_container_width=True)

    # Execution handling
    if generate_clicked:
        if not story_input.strip():
            st.warning("⚠️ Please provide a story or script concept before generating.")
            return

        with st.spinner("Analyzing narrative structure and generating high-impact assets with Gemini..."):
            try:
                # Also record raw generation into database for total metrics
                results = gemini_service.generate_content_studio(
                    story_text=story_input,
                    genre=genre,
                    audience=audience,
                    language=language,
                    tone=tone,
                    api_key=st.session_state.get("custom_api_key"),
                    model=st.session_state.get("custom_model"),
                )

                # Store into session state
                st.session_state["cs_results"] = results
                st.session_state["cs_last_input"] = story_input
                st.session_state["cs_metadata"] = {
                    "genre": genre,
                    "audience": audience,
                    "language": language,
                    "tone": tone,
                }

                # Auto-record the full generation run in SQLite
                database.save_content(
                    original_input=story_input,
                    generated_output=json.dumps(results, ensure_ascii=False),
                    content_type="content_studio_bundle",
                    language=language,
                    evaluation_score=None,
                    metadata=st.session_state["cs_metadata"],
                    is_saved=0,  # recorded as generated; user can save specific parts or entire bundle
                )

                st.success("✅ Content bundle generated successfully!")

            except gemini_service.GeminiConfigError as e:
                st.error(f"🔑 Configuration Error: {e}")
                st.info("Tip: You can add `GEMINI_API_KEY` to your `.env` file or configure it in the left sidebar.")
            except gemini_service.GeminiQuotaError as e:
                st.error(f"⏳ Rate Limit Exceeded: {e}")
            except Exception as e:
                st.error(f"❌ Generation Failed: {e}")

    # Display Generated Results
    if "cs_results" in st.session_state:
        results = st.session_state["cs_results"]
        meta = st.session_state.get("cs_metadata", {})
        last_input = st.session_state.get("cs_last_input", "")

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # Top Action: Save Full Bundle
        b_col1, b_col2 = st.columns([3, 1])
        with b_col1:
            st.markdown("### 📦 Generated Production Assets")
        with b_col2:
            if st.button("💾 Save Entire Bundle to Library", use_container_width=True):
                cid = database.save_content(
                    original_input=last_input,
                    generated_output=json.dumps(results, indent=2, ensure_ascii=False),
                    content_type="content_studio_bundle",
                    language=meta.get("language", "English"),
                    metadata=meta,
                    is_saved=1,
                )
                st.success(f"Full bundle saved to library! (ID: {cid})")

        tabs = st.tabs(["📌 5 Catchy Titles", "📝 Engaging Description", "🪝 3 Scroll-Stopping Hooks"])

        # Tab 1: Titles
        with tabs[0]:
            titles = results.get("titles", [])
            for i, item in enumerate(titles, 1):
                t_title = item.get("title", f"Title Option {i}")
                t_angle = item.get("angle", "General")
                t_reason = item.get("reasoning", "")

                with st.container():
                    st.markdown(
                        f"""
                        <div class="cf-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                                <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">
                                    #{i}. {t_title}
                                </div>
                                <span class="cf-badge cf-badge-blue">{t_angle}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #94a3b8;">
                                <strong>Target Strategy:</strong> {t_reason}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    c_act1, c_act2, c_act3 = st.columns([1, 1, 4])
                    with c_act1:
                        # Copy block helper
                        st.code(t_title, language=None)
                    with c_act2:
                        save_key = f"save_title_{i}"
                        if st.button(f"💾 Save Title #{i}", key=save_key):
                            cid = database.save_content(
                                original_input=last_input,
                                generated_output=t_title,
                                content_type="title",
                                language=meta.get("language", "English"),
                                metadata={"angle": t_angle, "reasoning": t_reason, **meta},
                                is_saved=1,
                            )
                            st.toast(f"Saved Title #{i} to Library! (ID: {cid})")

        # Tab 2: Description
        with tabs[1]:
            desc = results.get("description", {})
            synopsis = desc.get("synopsis", "")
            themes = desc.get("key_themes", [])
            cta = desc.get("call_to_action", "")

            st.markdown(
                f"""
                <div class="cf-card">
                    <div style="font-size: 1.1rem; font-weight: 600; color: #f8fafc; margin-bottom: 0.75rem;">
                        Synopsis / Promotional Pitch
                    </div>
                    <div style="font-size: 0.95rem; line-height: 1.6; color: #e2e8f0; margin-bottom: 1rem;">
                        {synopsis}
                    </div>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
                        {"".join([f'<span class="cf-badge cf-badge-purple">{theme}</span>' for theme in themes])}
                    </div>
                    <div style="font-size: 0.85rem; color: #38bdf8; background: rgba(56, 189, 248, 0.1); padding: 0.5rem 0.75rem; border-radius: 6px;">
                        <strong>Call to Action:</strong> {cta}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            full_desc_text = f"{synopsis}\n\nCall to Action: {cta}"
            st.code(full_desc_text, language=None)

            if st.button("💾 Save Description to Library", key="save_desc_btn"):
                cid = database.save_content(
                    original_input=last_input,
                    generated_output=full_desc_text,
                    content_type="description",
                    language=meta.get("language", "English"),
                    metadata={"themes": themes, "cta": cta, **meta},
                    is_saved=1,
                )
                st.success(f"Description saved to Library! (ID: {cid})")

        # Tab 3: Hooks
        with tabs[2]:
            hooks = results.get("hooks", [])
            for j, hook_item in enumerate(hooks, 1):
                h_text = hook_item.get("hook", "")
                h_type = hook_item.get("type", "Curiosity")
                h_trigger = hook_item.get("trigger", "")

                with st.container():
                    st.markdown(
                        f"""
                        <div class="cf-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                                <div style="font-size: 1.05rem; font-weight: 600; color: #f8fafc;">
                                    Hook #{j}
                                </div>
                                <span class="cf-badge cf-badge-amber">{h_type}</span>
                            </div>
                            <div style="font-size: 1rem; color: #38bdf8; font-weight: 500; margin-bottom: 0.5rem; line-height: 1.4;">
                                "{h_text}"
                            </div>
                            <div style="font-size: 0.82rem; color: #94a3b8;">
                                <strong>Psychological Trigger:</strong> {h_trigger}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    h_c1, h_c2, h_c3 = st.columns([1, 1, 4])
                    with h_c1:
                        st.code(h_text, language=None)
                    with h_c2:
                        if st.button(f"💾 Save Hook #{j}", key=f"save_hook_{j}"):
                            cid = database.save_content(
                                original_input=last_input,
                                generated_output=h_text,
                                content_type="hook",
                                language=meta.get("language", "English"),
                                metadata={"hook_type": h_type, "trigger": h_trigger, **meta},
                                is_saved=1,
                            )
                            st.toast(f"Saved Hook #{j} to Library! (ID: {cid})")

