"""
CreatorFlow Repurpose Studio View.
Converts stories/scripts into Instagram Captions, YouTube Descriptions,
Short Video Scripts (Reels/TikTok/Shorts), and WhatsApp Promotional Broadcasts.
"""

import streamlit as st
import json
import config
import database
import gemini_service


def render_repurpose_studio():
    """Render the Repurpose Studio interface."""
    st.markdown('<div class="page-title">Repurpose Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Instantly adapt scripts and narratives into platform-native formats: Instagram, YouTube, Short Video, and WhatsApp.</div>',
        unsafe_allow_html=True,
    )

    # Check if coming with pre-filled content from session
    default_text = st.session_state.get("repurpose_prefill", "")

    with st.container():
        input_text = st.text_area(
            "Source Story / Script / Content",
            value=default_text,
            height=160,
            placeholder="Paste the story, script draft, or core concept to repurpose across social channels...",
            key="rp_input_text",
        )

        col1, col2 = st.columns(2)
        with col1:
            format_display_names = list(config.REPURPOSE_FORMATS.keys())
            format_display_names.append("🚀 Multi-Format Omnichannel (All 4 Formats)")
            chosen_format_label = st.selectbox("Target Platform / Format", format_display_names, index=0)

        with col2:
            tone = st.selectbox("Target Tone", config.TONES, index=2)  # Default Casual/Conversational

        repurpose_btn = st.button("🔄 Adapt & Repurpose Content", type="primary", use_container_width=True)

    if repurpose_btn:
        if not input_text.strip():
            st.warning("⚠️ Please provide source content before repurposing.")
            return

        with st.spinner("Refactoring narrative structure for native platform algorithms..."):
            try:
                if "Omnichannel" in chosen_format_label:
                    # Run batch for all 4 formats
                    all_results = {}
                    for label, fmt_key in config.REPURPOSE_FORMATS.items():
                        res = gemini_service.repurpose_content(
                            story_text=input_text,
                            target_format=fmt_key,
                            tone=tone,
                            api_key=st.session_state.get("custom_api_key"),
                            model=st.session_state.get("custom_model"),
                        )
                        all_results[fmt_key] = res
                    st.session_state["rp_results"] = {"type": "omnichannel", "data": all_results}
                else:
                    target_fmt_key = config.REPURPOSE_FORMATS[chosen_format_label]
                    res = gemini_service.repurpose_content(
                        story_text=input_text,
                        target_format=target_fmt_key,
                        tone=tone,
                        api_key=st.session_state.get("custom_api_key"),
                        model=st.session_state.get("custom_model"),
                    )
                    st.session_state["rp_results"] = {
                        "type": "single",
                        "format_key": target_fmt_key,
                        "format_label": chosen_format_label,
                        "data": res,
                    }

                st.session_state["rp_last_input"] = input_text
                st.session_state["rp_tone"] = tone

                # Save record to database for metrics tracking
                database.save_content(
                    original_input=input_text,
                    generated_output=json.dumps(st.session_state["rp_results"], ensure_ascii=False),
                    content_type="repurpose_batch" if "Omnichannel" in chosen_format_label else config.REPURPOSE_FORMATS.get(chosen_format_label, "repurpose"),
                    language="English",
                    metadata={"tone": tone, "format_label": chosen_format_label},
                    is_saved=0,
                )

                st.success("✅ Content successfully repurposed!")

            except gemini_service.GeminiConfigError as e:
                st.error(f"🔑 Configuration Error: {e}")
            except gemini_service.GeminiQuotaError as e:
                st.error(f"⏳ Rate Limit Exceeded: {e}")
            except Exception as e:
                st.error(f"❌ Repurposing Error: {e}")

    # Render results
    if "rp_results" in st.session_state:
        rp_state = st.session_state["rp_results"]
        last_input = st.session_state.get("rp_last_input", "")
        tone_used = st.session_state.get("rp_tone", "Engaging")

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("---")

        if rp_state["type"] == "single":
            _render_single_repurpose_result(
                rp_state["data"],
                rp_state["format_key"],
                rp_state["format_label"],
                last_input,
                tone_used,
            )
        else:
            # Omnichannel tabs
            omni_tabs = st.tabs([
                "📸 Instagram Caption",
                "▶️ YouTube Description",
                "🎬 Short Video Script",
                "💬 WhatsApp Broadcast",
            ])
            formats_mapping = [
                ("repurpose_instagram", "Instagram Caption", omni_tabs[0]),
                ("repurpose_youtube", "YouTube Description", omni_tabs[1]),
                ("repurpose_video_script", "Short Video Script", omni_tabs[2]),
                ("repurpose_whatsapp", "WhatsApp Broadcast", omni_tabs[3]),
            ]
            for fmt_key, label, tab in formats_mapping:
                with tab:
                    item_data = rp_state["data"].get(fmt_key, {})
                    _render_single_repurpose_result(
                        item_data,
                        fmt_key,
                        label,
                        last_input,
                        tone_used,
                    )


def _render_single_repurpose_result(
    data: dict, format_key: str, format_label: str, source_input: str, tone: str
):
    """Render a single repurposed asset card with copy and save tools."""
    headline = data.get("headline_or_title", f"Repurposed for {format_label}")
    formatted_content = data.get("formatted_content", "")
    tips = data.get("production_tips", "")
    components = data.get("components", {})

    st.markdown(
        f"""
        <div class="cf-card-highlight">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span class="cf-badge cf-badge-blue">{format_label}</span>
                <span style="font-size: 0.8rem; color: #94a3b8;">Tone: {tone}</span>
            </div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-bottom: 0.75rem;">
                {headline}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.markdown("**📋 Ready-to-Publish Copy:**")
        st.code(formatted_content, language=None)

        if tips:
            st.markdown(
                f"""
                <div class="cf-disclaimer">
                    💡 <strong>Production Tip:</strong> {tips}
                </div>
                """,
                unsafe_allow_html=True,
            )

        btn_key = f"save_{format_key}_{abs(hash(formatted_content[:20]))}"
        if st.button(f"💾 Save {format_label} to Library", key=btn_key):
            cid = database.save_content(
                original_input=source_input,
                generated_output=formatted_content,
                content_type=format_key,
                language="English",
                metadata={"format": format_label, "headline": headline, "tone": tone, "tips": tips},
                is_saved=1,
            )
            st.success(f"Saved to Library! (ID: {cid})")

    with c_right:
        st.markdown("**🧩 Structural Breakdown:**")
        if components:
            for comp_key, comp_val in components.items():
                label_formatted = comp_key.replace("_", " ").title()
                st.markdown(
                    f"""
                    <div class="cf-card" style="padding: 0.65rem 0.85rem; margin-bottom: 0.5rem;">
                        <div style="font-size: 0.75rem; color: #60a5fa; font-weight: 600; text-transform: uppercase;">
                            {label_formatted}
                        </div>
                        <div style="font-size: 0.85rem; color: #cbd5e1; margin-top: 0.2rem; white-space: pre-wrap;">
                            {comp_val}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No sub-components extracted.")

