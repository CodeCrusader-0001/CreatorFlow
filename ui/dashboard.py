"""
CreatorFlow Dashboard View.
Renders analytics, generation distribution charts, recent SQLite activity,
and quick tool launchers.
"""

import streamlit as st
import pandas as pd
import database


def render_dashboard():
    """Render the main analytics dashboard."""
    st.markdown('<div class="page-title">Executive Content Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Real-time production metrics, asset distributions, and workflow activity from SQLite.</div>',
        unsafe_allow_html=True,
    )

    # Fetch live metrics from SQLite database
    metrics = database.get_dashboard_metrics()
    total_generated = metrics["total_generated"]
    total_saved = metrics["total_saved"]
    avg_score = metrics["avg_evaluation_score"]
    type_distribution = metrics["type_distribution"]
    recent_items = metrics["recent_items"]

    # 1. Top Metrics Bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Generated Assets</div>
                <div class="metric-value">{total_generated}</div>
                <div class="metric-hint">Cumulative AI production items</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Saved to Library</div>
                <div class="metric-value">{total_saved}</div>
                <div class="metric-hint">Curated production assets</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        score_display = f"{avg_score}/100" if avg_score > 0 else "N/A"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Avg Quality Score</div>
                <div class="metric-value">{score_display}</div>
                <div class="metric-hint">5-Pillar Rubric Benchmark</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        active_channels = len(type_distribution)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Active Formats</div>
                <div class="metric-value">{active_channels}</div>
                <div class="metric-hint">Cross-platform channels</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 2. Quick Navigation Section
    st.markdown("### ⚡ Quick Tool Launchers")
    q_col1, q_col2, q_col3, q_col4, q_col5 = st.columns(5)

    with q_col1:
        if st.button("🚀 Content Studio", use_container_width=True):
            st.session_state["nav_selection"] = "Content Studio"
            st.rerun()
    with q_col2:
        if st.button("🔄 Repurpose Studio", use_container_width=True):
            st.session_state["nav_selection"] = "Repurpose Studio"
            st.rerun()
    with q_col3:
        if st.button("🌐 Translation Studio", use_container_width=True):
            st.session_state["nav_selection"] = "Translation Studio"
            st.rerun()
    with q_col4:
        if st.button("📊 Content Evaluator", use_container_width=True):
            st.session_state["nav_selection"] = "Content Evaluator"
            st.rerun()
    with q_col5:
        if st.button("⚔️ A/B Hook Testing", use_container_width=True):
            st.session_state["nav_selection"] = "A/B Hook Testing"
            st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Analytics Distribution & Recent Activity
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown("### 📈 Asset Type Distribution")
        if type_distribution:
            df_dist = pd.DataFrame(type_distribution)
            # Make label user friendly
            df_dist["Display Type"] = df_dist["content_type"].apply(
                lambda x: x.replace("_", " ").title()
            )
            chart_df = df_dist.set_index("Display Type")[["count"]]
            st.bar_chart(chart_df, color="#3b82f6", use_container_width=True)
        else:
            st.info("No content items generated yet. Generate your first piece in the Content Studio to populate analytics.")

    with c_right:
        st.markdown("### 🕒 Recent Production Activity")
        if recent_items:
            for item in recent_items:
                cid = item["content_id"]
                ctype = item["content_type"].replace("_", " ").title()
                created = item["created_at"]
                output_snip = item["generated_output"][:110] + "..." if len(item["generated_output"]) > 110 else item["generated_output"]
                score_badge = ""
                if item["evaluation_score"]:
                    score_badge = f'<span class="cf-badge cf-badge-green" style="margin-left: 0.5rem;">Score: {item["evaluation_score"]}</span>'

                st.markdown(
                    f"""
                    <div class="cf-card" style="padding: 0.85rem 1rem; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                            <div>
                                <span class="cf-badge cf-badge-blue">{ctype}</span>
                                {score_badge}
                            </div>
                            <span style="font-size: 0.75rem; color: #64748b;">{created}</span>
                        </div>
                        <div style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.4;">
                            {output_snip}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="cf-card" style="text-align: center; padding: 2rem 1rem;">
                    <div style="color: #64748b; font-size: 0.9rem;">No generation history found in SQLite database.</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem;">
                        Use the sidebar or quick launchers above to start generating content.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

