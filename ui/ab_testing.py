"""
CreatorFlow A/B Hook Testing View.
Generates 3 distinct promotional hooks based on different psychological frameworks,
evaluates each under the 5-pillar rubric, and presents a competitive scorecard.
"""

import streamlit as st
import pandas as pd
import json
import config
import database
import gemini_service


def render_ab_testing():
    """Render the A/B Hook Testing interface."""
    st.markdown('<div class="page-title">A/B Hook Testing Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Generate 3 psychologically distinct promotional hooks, benchmark them under the 5-pillar rubric, and surface the strongest candidate.</div>',
        unsafe_allow_html=True,
    )

    # Disclaimer
    st.markdown(
        """
        <div class="cf-disclaimer">
            ⚖️ <strong>Testing Disclaimer:</strong> The candidate with the highest rubric score is structurally and editorially superior according to quality benchmarks.
            However, real-world audience engagement and CTR also depend on thumbnail visual resonance, posting timing, and distribution algorithms.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        story_input = st.text_area(
            "Source Story / Script",
            value=st.session_state.get("ab_prefill", ""),
            height=150,
            placeholder="Paste your story concept, script, or pitch to generate and test 3 competing hooks...",
            key="ab_story_input",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            genre = st.selectbox("Genre", config.GENRES, index=0, key="ab_genre")
        with col2:
            audience = st.selectbox("Target Audience", config.AUDIENCES, index=0, key="ab_aud")
        with col3:
            tone = st.selectbox("Tone", config.TONES, index=0, key="ab_tone")

        run_ab_btn = st.button("⚔️ Generate & Compare 3 Hooks", type="primary", use_container_width=True)

    if run_ab_btn:
        if not story_input.strip():
            st.warning("⚠️ Please provide a story or script to generate hooks.")
            return

        with st.spinner("Generating 3 distinct psychological hooks and executing competitive rubric evaluations..."):
            try:
                results = gemini_service.ab_hook_test(
                    story_text=story_input,
                    genre=genre,
                    audience=audience,
                    tone=tone,
                    api_key=st.session_state.get("custom_api_key"),
                    model=st.session_state.get("custom_model"),
                )

                st.session_state["ab_results"] = results
                st.session_state["ab_last_input"] = story_input
                st.session_state["ab_meta"] = {"genre": genre, "audience": audience, "tone": tone}

                # Save test to DB for metrics
                database.save_content(
                    original_input=story_input,
                    generated_output=json.dumps(results, ensure_ascii=False),
                    content_type="ab_hook_test",
                    language="English",
                    evaluation_score=results.get("winner", {}).get("overall_score"),
                    metadata=st.session_state["ab_meta"],
                    is_saved=0,
                )

                st.success("✅ A/B Hook comparison generated successfully!")

            except gemini_service.GeminiConfigError as e:
                st.error(f"🔑 Configuration Error: {e}")
            except gemini_service.GeminiQuotaError as e:
                st.error(f"⏳ Rate Limit Exceeded: {e}")
            except Exception as e:
                st.error(f"❌ A/B Test Error: {e}")

    # Render results
    if "ab_results" in st.session_state:
        ab_data = st.session_state["ab_results"]
        last_input = st.session_state.get("ab_last_input", "")
        meta = st.session_state.get("ab_meta", {})
        hooks = ab_data.get("hooks", [])
        winner = ab_data.get("winner", {})
        summary = ab_data.get("comparison_summary", "")

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # Winner Spotlight Banner
        if winner:
            w_id = winner.get("hook_id", "A")
            w_text = winner.get("hook_text", "")
            w_framework = winner.get("framework", "")
            w_score = winner.get("overall_score", 0.0)
            w_reason = winner.get("winning_reason", "")

            st.markdown(
                f"""
                <div class="cf-card-highlight" style="border: 2px solid #3b82f6;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span class="cf-badge cf-badge-green" style="font-size: 0.85rem;">🏆 Strongest Candidate: Hook {w_id}</span>
                        <span class="cf-badge cf-badge-blue">{w_framework}</span>
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff; line-height: 1.4; margin: 0.75rem 0;">
                        "{w_text}"
                    </div>
                    <div style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 0.75rem;">
                        <strong>Rubric Score:</strong> <span style="color: #60a5fa; font-weight: 700;">{w_score}/100</span> — {w_reason}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Winner Save action
            w_col1, w_col2 = st.columns([1, 3])
            with w_col1:
                if st.button("💾 Save Winning Hook", key="save_winner_btn"):
                    cid = database.save_content(
                        original_input=last_input,
                        generated_output=w_text,
                        content_type="hook",
                        language="English",
                        evaluation_score=w_score,
                        metadata={"framework": w_framework, "is_winner": True, **meta},
                        is_saved=1,
                    )
                    st.success(f"Winning Hook saved to Library! (ID: {cid})")

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # 3 Competing Cards
        st.markdown("### 🥊 Candidate Breakdown")
        hook_cols = st.columns(3)

        for idx, h in enumerate(hooks):
            with hook_cols[idx]:
                h_id = h.get("id", chr(65 + idx))
                h_text = h.get("hook_text", "")
                h_frame = h.get("framework", "")
                h_score = h.get("overall_score", 0.0)
                h_rat = h.get("rationale", "")
                scores = h.get("scores", {})

                is_this_winner = (h_id == winner.get("hook_id"))
                card_class = "cf-card-highlight" if is_this_winner else "cf-card"

                st.markdown(
                    f"""
                    <div class="{card_class}" style="min-height: 290px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <span style="font-size: 1.1rem; font-weight: 700; color: #f8fafc;">Hook {h_id}</span>
                                <span class="cf-badge cf-badge-purple">{h_frame}</span>
                            </div>
                            <div style="font-size: 0.95rem; font-style: italic; color: #38bdf8; margin: 0.6rem 0; line-height: 1.4;">
                                "{h_text}"
                            </div>
                            <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.75rem;">
                                {h_rat}
                            </div>
                        </div>
                        <div style="border-top: 1px solid #1e293b; padding-top: 0.5rem;">
                            <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff;">
                                Score: {h_score}<span style="font-size: 0.8rem; color: #64748b;">/100</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.code(h_text, language=None)
                if st.button(f"💾 Save Hook {h_id}", key=f"save_cand_{h_id}"):
                    cid = database.save_content(
                        original_input=last_input,
                        generated_output=h_text,
                        content_type="hook",
                        language="English",
                        evaluation_score=h_score,
                        metadata={"framework": h_frame, "scores": scores, **meta},
                        is_saved=1,
                    )
                    st.toast(f"Saved Hook {h_id} to Library! (ID: {cid})")

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Comparative Scoring Table
        st.markdown("### 📊 Side-by-Side Rubric Scorecard")
        table_rows = []
        for h in hooks:
            s = h.get("scores", {})
            table_rows.append({
                "Candidate": f"Hook {h.get('id')} ({h.get('framework')})",
                "Clarity (0-10)": s.get("clarity", 0.0),
                "Emotional Appeal (0-10)": s.get("emotional_appeal", 0.0),
                "Audience Relevance (0-10)": s.get("audience_relevance", 0.0),
                "Originality (0-10)": s.get("originality", 0.0),
                "Promotional Pull (0-10)": s.get("promotional_effectiveness", 0.0),
                "Overall Score (0-100)": h.get("overall_score", 0.0),
            })

        df_table = pd.DataFrame(table_rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

        if summary:
            st.info(f"💡 **Takeaway:** {summary}")

