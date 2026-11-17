"""
CreatorFlow Content Evaluator View.
Evaluates creative assets and scripts across a 5-pillar rubric:
Clarity, Emotional Appeal, Audience Relevance, Originality, and Promotional Effectiveness.
Provides 0-100 overall score, score tiers, strengths, weaknesses, and actionable recommendations.
"""

import streamlit as st
import json
import database
import gemini_service


def render_evaluator():
    """Render the Content Evaluator interface."""
    st.markdown('<div class="page-title">Content Evaluator & Quality Rubric</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Objective, AI-powered editorial critique across 5 core storytelling and conversion dimensions.</div>',
        unsafe_allow_html=True,
    )

    # Prominent estimation disclaimer
    st.markdown(
        """
        <div class="cf-disclaimer">
            ⚖️ <strong>Benchmarking Notice:</strong> Evaluator scores are heuristic estimates based on editorial craft, clarity, and structural hooks.
            They are not guaranteed predictions of real-world algorithm distribution, virality, or audience metrics.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        content_to_eval = st.text_area(
            "Draft Content to Evaluate",
            value=st.session_state.get("eval_prefill", ""),
            height=160,
            placeholder="Paste your title, hook, script excerpt, description, or social caption to evaluate...",
            key="eval_content_input",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            content_type_choice = st.selectbox(
                "Content Format / Intent",
                [
                    "Promotional Hook",
                    "Story / Script Concept",
                    "YouTube Description",
                    "Instagram Caption",
                    "Short Video Script",
                    "Ad Copy",
                    "General Creative Content",
                ],
                index=0,
            )

        with col2:
            st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
            eval_btn = st.button("📊 Run Deep Rubric Evaluation", type="primary", use_container_width=True)

    if eval_btn:
        if not content_to_eval.strip():
            st.warning("⚠️ Please provide content to evaluate.")
            return

        with st.spinner("Scoring content against 5-pillar editorial rubric with Gemini..."):
            try:
                results = gemini_service.evaluate_content(
                    content_text=content_to_eval,
                    content_type=content_type_choice,
                    api_key=st.session_state.get("custom_api_key"),
                    model=st.session_state.get("custom_model"),
                )

                st.session_state["eval_results"] = results
                st.session_state["eval_last_input"] = content_to_eval
                st.session_state["eval_content_type"] = content_type_choice

                # Log evaluation run to database
                database.save_content(
                    original_input=content_to_eval,
                    generated_output=json.dumps(results, ensure_ascii=False),
                    content_type="evaluation",
                    language="English",
                    evaluation_score=results.get("overall_score"),
                    metadata={"content_format": content_type_choice},
                    is_saved=0,
                )

                st.success("✅ Evaluation complete!")

            except gemini_service.GeminiConfigError as e:
                st.error(f"🔑 Configuration Error: {e}")
            except gemini_service.GeminiQuotaError as e:
                st.error(f"⏳ Rate Limit Exceeded: {e}")
            except Exception as e:
                st.error(f"❌ Evaluation Error: {e}")

    # Render results
    if "eval_results" in st.session_state:
        eval_data = st.session_state["eval_results"]
        last_input = st.session_state.get("eval_last_input", "")
        format_used = st.session_state.get("eval_content_type", "Content")

        overall_score = eval_data.get("overall_score", 0.0)
        criteria = eval_data.get("criteria_scores", {})
        tier = eval_data.get("score_tier", "Strong")
        strengths = eval_data.get("strengths", [])
        weaknesses = eval_data.get("weaknesses", [])
        suggestions = eval_data.get("actionable_suggestions", [])

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # Top Score Banner
        b1, b2 = st.columns([1, 2])
        with b1:
            tier_badge = "cf-badge-blue"
            if overall_score >= 85:
                tier_badge = "cf-badge-green"
            elif overall_score < 70:
                tier_badge = "cf-badge-amber"

            st.markdown(
                f"""
                <div class="cf-card-highlight" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">
                        Cumulative Quality Score
                    </div>
                    <div style="font-size: 3.5rem; font-weight: 800; color: #ffffff; line-height: 1.1; margin: 0.5rem 0;">
                        {overall_score}<span style="font-size: 1.5rem; color: #60a5fa;">/100</span>
                    </div>
                    <span class="cf-badge {tier_badge}" style="font-size: 0.85rem; padding: 4px 10px;">
                        {tier}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with b2:
            st.markdown("### 🎯 Criteria Breakdown (0–10 Scale)")
            criteria_names = [
                ("clarity", "Clarity & Readability"),
                ("emotional_appeal", "Emotional Appeal & Tension"),
                ("audience_relevance", "Audience Relevance & Value"),
                ("originality", "Originality & Distinctive Voice"),
                ("promotional_effectiveness", "Promotional / Conversion Pull"),
            ]

            for key, display_name in criteria_names:
                val = float(criteria.get(key, 0.0))
                c_lbl, c_prog = st.columns([2, 3])
                with c_lbl:
                    st.markdown(f"**{display_name}**: `{val}/10`")
                with c_prog:
                    st.progress(min(val / 10.0, 1.0))

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # Strengths, Weaknesses, and Actionable Suggestions
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("### ✅ Key Strengths")
            for s in strengths:
                st.markdown(
                    f"""
                    <div class="cf-card" style="padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-left: 3px solid #10b981;">
                        <span style="color: #34d399; font-weight: 600;">•</span> {s}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col_w:
            st.markdown("### ⚠️ Areas for Improvement")
            for w in weaknesses:
                st.markdown(
                    f"""
                    <div class="cf-card" style="padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-left: 3px solid #f59e0b;">
                        <span style="color: #fbbf24; font-weight: 600;">•</span> {w}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("### 💡 Actionable Editorial Recommendations")
        for idx, rec in enumerate(suggestions, 1):
            st.markdown(
                f"""
                <div class="cf-card" style="padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-left: 3px solid #3b82f6;">
                    <strong>Step {idx}:</strong> {rec}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Save Evaluation Report Button
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("💾 Save Evaluation Report to Library", use_container_width=True):
            eval_summary = (
                f"Overall Score: {overall_score}/100 ({tier})\n\n"
                f"Criteria: {json.dumps(criteria)}\n\n"
                f"Strengths: {', '.join(strengths)}\n\n"
                f"Weaknesses: {', '.join(weaknesses)}\n\n"
                f"Recommendations: {', '.join(suggestions)}"
            )
            cid = database.save_content(
                original_input=last_input,
                generated_output=eval_summary,
                content_type="evaluation",
                language="English",
                evaluation_score=overall_score,
                metadata={
                    "format": format_used,
                    "criteria": criteria,
                    "tier": tier,
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "suggestions": suggestions,
                },
                is_saved=1,
            )
            st.success(f"Evaluation report permanently saved to Library! (ID: {cid})")

