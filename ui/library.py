"""
CreatorFlow Content Library View.
Manages saved and generated assets in SQLite with search, filtering,
deletion, and TXT/CSV export capabilities.
"""

import streamlit as st
import pandas as pd
import json
from io import StringIO
import config
import database


def render_content_library():
    """Render the Content Library interface."""
    st.markdown('<div class="page-title">Content Library</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Search, filter, inspect, and export your curated production assets stored in SQLite.</div>',
        unsafe_allow_html=True,
    )

    # Search & Filter Toolbar
    with st.container():
        f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1, 1, 1])

        with f_col1:
            search_query = st.text_input(
                "🔍 Search Content",
                placeholder="Search keywords in prompt, output, or metadata...",
                key="lib_search_query",
            )

        with f_col2:
            all_types = ["All"] + [
                "title",
                "description",
                "hook",
                "content_studio_bundle",
                "repurpose_instagram",
                "repurpose_youtube",
                "repurpose_video_script",
                "repurpose_whatsapp",
                "translation",
                "evaluation",
                "ab_hook_test",
            ]
            filter_type = st.selectbox("Content Type", all_types, index=0, key="lib_filter_type")

        with f_col3:
            all_langs = ["All"] + config.SUPPORTED_LANGUAGES
            filter_lang = st.selectbox("Language", all_langs, index=0, key="lib_filter_lang")

        with f_col4:
            view_saved_only = st.checkbox("Saved items only", value=True, key="lib_saved_only")

    # Fetch items from SQLite
    items = database.get_content_items(
        search_query=search_query,
        content_type=filter_type,
        language=filter_lang,
        is_saved_only=view_saved_only,
        limit=150,
    )

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Results Header & Export Tools
    e_col1, e_col2, e_col3 = st.columns([2, 1, 1])
    with e_col1:
        st.markdown(f"**Found `{len(items)}` matching items**")

    if items:
        # Prepare DataFrame for export
        export_records = []
        for it in items:
            export_records.append({
                "Content ID": it["content_id"],
                "Content Type": it["content_type"],
                "Language": it["language"],
                "Created At": it["created_at"],
                "Evaluation Score": it.get("evaluation_score"),
                "Original Input": it["original_input"],
                "Generated Output": it["generated_output"],
            })
        df_export = pd.DataFrame(export_records)

        with e_col2:
            csv_data = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export as CSV",
                data=csv_data,
                file_name="creatorflow_export.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with e_col3:
            # Prepare TXT export
            txt_buffer = StringIO()
            txt_buffer.write("=== CREATORFLOW PRODUCTION ASSETS EXPORT ===\n\n")
            for it in items:
                txt_buffer.write(f"ID: {it['content_id']}\n")
                txt_buffer.write(f"Type: {it['content_type']} | Lang: {it['language']} | Created: {it['created_at']}\n")
                if it.get("evaluation_score"):
                    txt_buffer.write(f"Score: {it['evaluation_score']}/100\n")
                txt_buffer.write(f"--- SOURCE INPUT ---\n{it['original_input']}\n")
                txt_buffer.write(f"--- GENERATED OUTPUT ---\n{it['generated_output']}\n")
                txt_buffer.write("=" * 60 + "\n\n")

            st.download_button(
                label="📄 Export as TXT",
                data=txt_buffer.getvalue().encode("utf-8"),
                file_name="creatorflow_export.txt",
                mime="text/plain",
                use_container_width=True,
            )

    st.markdown("---")

    # Item Cards View
    if not items:
        st.info("No content items match your current search and filter criteria.")
        return

    for idx, item in enumerate(items):
        cid = item["content_id"]
        ctype = item["content_type"].replace("_", " ").title()
        lang = item["language"]
        created = item["created_at"]
        score = item.get("evaluation_score")
        output_text = item["generated_output"]
        input_text = item["original_input"]
        metadata = item.get("metadata", {})

        # Truncate preview
        preview_text = output_text if len(output_text) <= 220 else output_text[:220] + "..."

        score_html = ""
        if score is not None:
            score_html = f'<span class="cf-badge cf-badge-green" style="margin-left: 0.4rem;">Score: {score}/100</span>'

        with st.container():
            st.markdown(
                f"""
                <div class="cf-card" style="margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div>
                            <span class="cf-badge cf-badge-blue">{ctype}</span>
                            <span class="cf-badge cf-badge-purple" style="margin-left: 0.3rem;">{lang}</span>
                            {score_html}
                            <span style="font-size: 0.75rem; color: #64748b; margin-left: 0.5rem; font-family: monospace;">ID: {cid}</span>
                        </div>
                        <span style="font-size: 0.75rem; color: #64748b;">{created}</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #e2e8f0; line-height: 1.5; margin-bottom: 0.5rem; white-space: pre-wrap;">
                        {preview_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"🔍 Inspect Full Details & Actions for ID: {cid}", expanded=False):
                col_d1, col_d2 = st.columns([1, 1])
                with col_d1:
                    st.markdown("**Original Input:**")
                    st.text_area(f"Input_{cid}", value=input_text, height=120, disabled=True, key=f"inp_{cid}")

                with col_d2:
                    st.markdown("**Generated Output:**")
                    st.text_area(f"Output_{cid}", value=output_text, height=120, disabled=True, key=f"out_{cid}")

                if metadata:
                    st.markdown("**Metadata:**")
                    st.json(metadata)

                # Action row: Copy, Send to Evaluator, Delete
                act1, act2, act3 = st.columns([1, 1, 1])

                with act1:
                    st.code(output_text, language=None)

                with act2:
                    if st.button("📊 Send to Evaluator", key=f"eval_btn_{cid}"):
                        st.session_state["eval_prefill"] = output_text
                        st.session_state["nav_selection"] = "Content Evaluator"
                        st.rerun()

                with act3:
                    if st.button("🗑️ Delete from Library", key=f"del_btn_{cid}", type="secondary"):
                        success = database.delete_content(cid)
                        if success:
                            st.toast(f"Deleted item {cid}")
                            st.rerun()
                        else:
                            st.error("Failed to delete item.")

