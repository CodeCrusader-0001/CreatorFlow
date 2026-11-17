"""
CreatorFlow Translation Studio View.
Translates and transcreates storytelling content into Hindi, English, Tamil, Telugu,
Bengali, and Spanish while preserving tone, emotion, and character nuances.
"""

import streamlit as st
import json
import config
import database
import gemini_service


def render_translation_studio():
    """Render the Translation Studio interface."""
    st.markdown('<div class="page-title">Translation & Localization Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Transcreate content across 6 major regional and global languages while preserving dramatic cadence, emotion, and storytelling voice.</div>',
        unsafe_allow_html=True,
    )

    # Prominent disclaimer notice
    st.markdown(
        """
        <div class="cf-disclaimer">
            ⚖️ <strong>Editorial Disclaimer:</strong> AI-powered localization preserves dramatic tone, character names, and cultural idioms.
            However, these outputs are algorithmic transcreations and have <em>not</em> been verified by a certified human native speaker.
            Human review is recommended prior to formal broadcast or publication.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        input_text = st.text_area(
            "Content to Localize (Story, Script, Hook, or Post)",
            value=st.session_state.get("trans_prefill", ""),
            height=160,
            placeholder="Enter the English or source text you want to translate and transcreate...",
            key="trans_input_text",
        )

        col1, col2 = st.columns(2)
        with col1:
            source_lang = st.selectbox("Source Language", config.SUPPORTED_LANGUAGES, index=0)
        with col2:
            target_options = [l for l in config.SUPPORTED_LANGUAGES if l != source_lang]
            target_options.append("🌍 All Regional Indian Languages (Hindi, Tamil, Telugu, Bengali)")
            target_lang_choice = st.selectbox("Target Language", target_options, index=0)

        translate_btn = st.button("🌐 Transcreate Content", type="primary", use_container_width=True)

    if translate_btn:
        if not input_text.strip():
            st.warning("⚠️ Please provide text to translate.")
            return

        with st.spinner("Transcreating narrative with cultural nuances and emotion retention..."):
            try:
                results_bundle = {}
                if "All Regional" in target_lang_choice:
                    languages_to_process = ["Hindi", "Tamil", "Telugu", "Bengali"]
                    for lang in languages_to_process:
                        res = gemini_service.translate_content(
                            text=input_text,
                            target_language=lang,
                            source_language=source_lang,
                            api_key=st.session_state.get("custom_api_key"),
                            model=st.session_state.get("custom_model"),
                        )
                        results_bundle[lang] = res
                    st.session_state["trans_results"] = {"type": "multi", "data": results_bundle}
                else:
                    res = gemini_service.translate_content(
                        text=input_text,
                        target_language=target_lang_choice,
                        source_language=source_lang,
                        api_key=st.session_state.get("custom_api_key"),
                        model=st.session_state.get("custom_model"),
                    )
                    st.session_state["trans_results"] = {
                        "type": "single",
                        "target_lang": target_lang_choice,
                        "data": res,
                    }

                st.session_state["trans_last_input"] = input_text
                st.session_state["trans_source_lang"] = source_lang

                # Log to DB for metrics
                database.save_content(
                    original_input=input_text,
                    generated_output=json.dumps(st.session_state["trans_results"], ensure_ascii=False),
                    content_type="translation",
                    language=target_lang_choice if "All Regional" not in target_lang_choice else "Multilingual",
                    metadata={"source_lang": source_lang},
                    is_saved=0,
                )

                st.success("✅ Content transcreated successfully!")

            except gemini_service.GeminiConfigError as e:
                st.error(f"🔑 Configuration Error: {e}")
            except gemini_service.GeminiQuotaError as e:
                st.error(f"⏳ Rate Limit Exceeded: {e}")
            except Exception as e:
                st.error(f"❌ Translation Error: {e}")

    # Render results
    if "trans_results" in st.session_state:
        res_data = st.session_state["trans_results"]
        last_input = st.session_state.get("trans_last_input", "")

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 🈳 Localized Content")

        if res_data["type"] == "single":
            _render_single_translation_card(
                res_data["data"], res_data["target_lang"], last_input
            )
        else:
            lang_tabs = st.tabs(list(res_data["data"].keys()))
            for idx, (lang_name, trans_item) in enumerate(res_data["data"].items()):
                with lang_tabs[idx]:
                    _render_single_translation_card(
                        trans_item, lang_name, last_input
                    )


def _render_single_translation_card(trans_item: dict, target_lang: str, source_input: str):
    """Render localized text card with cultural notes and save options."""
    translated_text = trans_item.get("translated_text", "")
    cultural_notes = trans_item.get("cultural_adaptation_notes", "")
    disclaimer = trans_item.get("disclaimer", "")

    st.markdown(
        f"""
        <div class="cf-card-highlight">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span class="cf-badge cf-badge-blue">{target_lang} Localization</span>
                <span class="cf-badge cf-badge-purple">Cultural Transcreation</span>
            </div>
            <div style="font-size: 1.05rem; line-height: 1.6; color: #f8fafc; white-space: pre-wrap;">
                {translated_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if cultural_notes:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; color: #94a3b8; background: #111827; border: 1px solid #1e293b; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
                💡 <strong>Cultural Adaptation Notes:</strong> {cultural_notes}
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2, c3 = st.columns([2, 1, 3])
    with c1:
        st.code(translated_text, language=None)
    with c2:
        btn_key = f"save_trans_{target_lang}_{abs(hash(translated_text[:20]))}"
        if st.button(f"💾 Save {target_lang}", key=btn_key):
            cid = database.save_content(
                original_input=source_input,
                generated_output=translated_text,
                content_type="translation",
                language=target_lang,
                metadata={"cultural_notes": cultural_notes, "disclaimer": disclaimer},
                is_saved=1,
            )
            st.success(f"Saved {target_lang} version to Library! (ID: {cid})")

