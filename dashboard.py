"""
Multimodal Crime / Incident Report Analyzer — Streamlit Dashboard
AI for Engineers Group Assignment

Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Incident Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# DATA COLORS — Wong palette (color-blind friendly)
# Only used for data/chart coloring, not UI backgrounds
# ─────────────────────────────────────────────────────────────────
C = {
    "High":   "#D55E00",   # Vermillion
    "Medium": "#E69F00",   # Amber
    "Low":    "#009E73",   # Bluish green
    "blue":   "#0072B2",   # Blue
    "sky":    "#56B4E9",   # Sky blue
    "purple": "#CC79A7",   # Reddish purple
}

SEV_ORDER  = ["High", "Medium", "Low"]
SEV_COLORS = [C["High"], C["Medium"], C["Low"]]

# ─────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    final = pd.read_csv(os.path.join(BASE, "integration", "final_incident_report.csv"))
    audio = pd.read_csv(os.path.join(BASE, "audio",       "audio_output.csv"))
    pdf   = pd.read_csv(os.path.join(BASE, "pdf",         "pdf_output.csv"))
    image = pd.read_csv(os.path.join(BASE, "images",      "image_output.csv"))
    video = pd.read_csv(os.path.join(BASE, "video",       "video_output.csv"))
    text  = pd.read_csv(os.path.join(BASE, "text",        "text_output.csv"))
    return final, audio, pdf, image, video, text

final_df, audio_df, pdf_df, image_df, video_df, text_df = load_data()

# ─────────────────────────────────────────────────────────────────
# SIDEBAR — FILTERS
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Incident Filters")
    st.markdown("---")

    severity_filter = st.multiselect(
        "Severity",
        options=SEV_ORDER,
        default=SEV_ORDER,
    )

    event_search = st.text_input("Search event keyword", placeholder="e.g. fire, robbery")

# ─────────────────────────────────────────────────────────────────
# APPLY FILTERS → filtered = subset of final_df
# ─────────────────────────────────────────────────────────────────
filtered = final_df[final_df["Severity"].isin(severity_filter)].copy()
if event_search.strip():
    mask = (
        filtered["Audio_Event"].str.contains(event_search, case=False, na=False)
        | filtered["Text_Crime_Type"].str.contains(event_search, case=False, na=False)
        | filtered["Video_Event"].str.contains(event_search, case=False, na=False)
        | filtered["Image_Scene_Type"].str.contains(event_search, case=False, na=False)
    )
    filtered = filtered[mask]

# Derive per-modality filtered subsets from the filtered incident list
filtered_audio = audio_df[audio_df["Call_ID"].isin(filtered["Audio_Source"])]
filtered_text  = text_df[text_df["Text_ID"].isin(filtered["Text_Source"])]

# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────
st.title("Multimodal Crime / Incident Report Analyzer")
st.caption(
    f"AI for Engineers — Group 9 Assignment  |  "
    f"Showing **{len(filtered)}** of **{len(final_df)}** incidents"
)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────
# KPI CARDS — always show totals from full dataset
# ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Incidents",  len(final_df))
k2.metric("High Severity",    int((final_df["Severity"] == "High").sum()))
k3.metric("Medium Severity",  int((final_df["Severity"] == "Medium").sum()))
k4.metric("Low Severity",     int((final_df["Severity"] == "Low").sum()))

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Audio",
    "PDFs",
    "Image & Video",
    "Text",
    "Full Integrated Report",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW  (uses filtered)
# ════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1.2, 1])

    # ── Severity distribution — FILTERED ────────────────────────
    with col_left:
        st.subheader("Severity Distribution")
        sev_counts = (
            filtered["Severity"]
            .value_counts()
            .reindex(SEV_ORDER, fill_value=0)
            .reset_index()
        )
        sev_counts.columns = ["Severity", "Count"]
        fig_sev = px.bar(
            sev_counts, x="Severity", y="Count",
            color="Severity",
            color_discrete_map={s: c for s, c in zip(SEV_ORDER, SEV_COLORS)},
            text="Count",
            template="simple_white",
        )
        fig_sev.update_traces(textposition="outside", marker_line_width=0)
        fig_sev.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="",
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    # ── Modality coverage — FILTERED ────────────────────────────
    with col_right:
        st.subheader("Modality Coverage")
        coverage = filtered[["Incident_ID", "Audio_Source", "PDF_Source",
                              "Image_Source", "Video_Source", "Text_Source"]].copy()
        for col in ["Audio_Source", "PDF_Source", "Image_Source", "Video_Source", "Text_Source"]:
            coverage[col] = coverage[col].apply(lambda x: "✓" if x != "No data" else "✗")
        coverage.columns = ["Incident", "Audio", "PDF", "Image", "Video", "Text"]
        coverage = coverage.set_index("Incident")

        cov_num = coverage.replace({"✓": 1, "✗": 0})
        if not cov_num.empty:
            fig_heat = go.Figure(data=go.Heatmap(
                z=cov_num.values,
                x=list(cov_num.columns),
                y=list(cov_num.index),
                colorscale=[[0, "#E0E0E0"], [1, C["blue"]]],
                showscale=False,
                text=coverage.values,
                texttemplate="%{text}",
                textfont={"size": 18},
            ))
            fig_heat.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(side="top"),
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("No incidents match the current filters.")

    st.markdown("---")

    # ── Incident summary cards — FILTERED ───────────────────────
    st.subheader(f"Incident Summary ({len(filtered)} shown)")

    if filtered.empty:
        st.info("No incidents match the current filters.")
    else:
        for _, row in filtered.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{row['Incident_ID']}**")
                sev = row["Severity"]
                color = C.get(sev, "#888")
                c2.markdown(
                    f"<span style='background:{color};color:#fff;"
                    f"padding:2px 12px;border-radius:12px;font-size:0.85rem;"
                    f"font-weight:600'>{sev}</span>",
                    unsafe_allow_html=True,
                )
                cols = st.columns(3)
                cols[0].caption(f"**Audio:** {row['Audio_Event']}")
                cols[1].caption(f"**PDF:** {row['PDF_Doc_Type']}")
                cols[2].caption(f"**Image:** {row['Image_Objects']}")
                cols[0].caption(f"**Video:** {row['Video_Event']}")
                cols[1].caption(f"**Text:** {row['Text_Crime_Type']}")
                cols[2].caption(f"**Location:** {row['Audio_Location']}")


# ════════════════════════════════════════════════════════════════
# TAB 2 — AUDIO  (uses filtered_audio)
# ════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Emergency Call Audio Analysis")
    st.caption("Tools: OpenAI Whisper · spaCy NER · HuggingFace DistilBERT · Dataset: Kaggle 911 Calls (real audio)")
    st.markdown("<br>", unsafe_allow_html=True)

    if filtered_audio.empty:
        st.info("No audio records match the current filters.")
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Urgency Score per Call")
            fig_urg = px.bar(
                filtered_audio, x="Call_ID", y="Urgency_Score",
                color="Urgency_Score",
                color_continuous_scale=[[0, C["Low"]], [0.5, C["Medium"]], [1.0, C["High"]]],
                text="Urgency_Score",
                template="simple_white",
                range_y=[0, 1.1],
            )
            fig_urg.update_traces(textposition="outside", marker_line_width=0)
            fig_urg.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis_title="", yaxis_title="Urgency Score (0–1)",
            )
            st.plotly_chart(fig_urg, use_container_width=True)

        with col_b:
            st.subheader("Sentiment Distribution")
            sent_counts = filtered_audio["Sentiment"].value_counts().reset_index()
            sent_counts.columns = ["Sentiment", "Count"]
            fig_sent = px.pie(
                sent_counts, names="Sentiment", values="Count",
                color="Sentiment",
                color_discrete_map={"Distressed": C["High"], "Calm": C["Low"], "Neutral": C["Medium"]},
                template="simple_white",
            )
            fig_sent.update_traces(textposition="inside", textinfo="percent+label")
            fig_sent.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
            )
            st.plotly_chart(fig_sent, use_container_width=True)

        st.markdown("---")
        st.subheader("Call Details")
        st.dataframe(
            filtered_audio.style.background_gradient(subset=["Urgency_Score"], cmap="Oranges"),
            use_container_width=True,
        )


# ════════════════════════════════════════════════════════════════
# TAB 3 — DOCUMENTS  (full pdf_df — only 5 rows, not severity-linked)
# ════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Police PDF Document Extraction")
    st.caption("Tools: pdfplumber · PyMuPDF · pytesseract OCR · spaCy NER · Dataset: Arkansas PD LESO2.pdf (75 pages)")
    st.markdown("<br>", unsafe_allow_html=True)

    col_d1, col_d2 = st.columns([1.5, 1])

    with col_d1:
        st.subheader("Extracted Reports")
        st.dataframe(pdf_df, use_container_width=True)

    with col_d2:
        st.subheader("Document Types")
        doc_type_counts = pdf_df["Doc_Type"].value_counts().reset_index()
        doc_type_counts.columns = ["Doc_Type", "Count"]
        fig_doc = px.bar(
            doc_type_counts, x="Count", y="Doc_Type",
            orientation="h",
            color_discrete_sequence=[C["blue"]],
            text="Count",
            template="simple_white",
        )
        fig_doc.update_traces(textposition="outside", marker_line_width=0)
        fig_doc.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="",
            showlegend=False,
        )
        st.plotly_chart(fig_doc, use_container_width=True)

    st.markdown("---")
    st.subheader("Program Distribution")
    prog_counts = pdf_df["Program"].value_counts().reset_index()
    prog_counts.columns = ["Program", "Count"]
    fig_prog = px.bar(
        prog_counts, x="Program", y="Count",
        color_discrete_sequence=[C["sky"]],
        text="Count",
        template="simple_white",
    )
    fig_prog.update_traces(textposition="outside", marker_line_width=0)
    fig_prog.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="", yaxis_title="",
    )
    st.plotly_chart(fig_prog, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# TAB 4 — IMAGE & VIDEO  (full image_df / video_df)
# ════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Visual Analysis Image and Video")

    img_col, vid_col = st.columns(2)

    with img_col:
        st.subheader("Image — Fire Detection (YOLOv8)")
        st.caption("Tools: YOLOv8 · OpenCV · pytesseract · Dataset: Roboflow Fire Detection (741 images)")
        st.markdown("<br>", unsafe_allow_html=True)

        scene_counts = image_df["Scene_Type"].value_counts().reset_index()
        scene_counts.columns = ["Scene_Type", "Count"]
        fig_scene = px.pie(
            scene_counts, names="Scene_Type", values="Count",
            color_discrete_sequence=[C["High"], C["blue"], C["sky"]],
            template="simple_white",
        )
        fig_scene.update_traces(textposition="inside", textinfo="percent+label")
        fig_scene.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig_scene, use_container_width=True)

        st.subheader("Detection Confidence (first 10 images)")
        fig_img = px.bar(
            image_df.head(10), x="Image_ID", y="Confidence",
            color="Scene_Type",
            color_discrete_sequence=[C["High"], C["blue"]],
            text="Confidence",
            template="simple_white",
            range_y=[0, 1.1],
        )
        fig_img.update_traces(textposition="outside")
        fig_img.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="Confidence",
            xaxis_tickangle=45,
            legend_title="Scene Type",
        )
        st.plotly_chart(fig_img, use_container_width=True)

    with vid_col:
        st.subheader("Video — Event Timeline (OpenCV + YOLOv8)")
        st.caption("Tools: OpenCV · YOLOv8 · moviepy · Dataset: CAVIAR CCTV (3 clips, 136 frames)")
        st.markdown("<br>", unsafe_allow_html=True)

        event_counts = video_df.groupby(["Clip_ID", "Event_Detected"]).size().reset_index(name="Frames")
        fig_vid = px.bar(
            event_counts, x="Clip_ID", y="Frames",
            color="Event_Detected",
            color_discrete_sequence=[C["blue"], C["sky"], C["purple"], C["Medium"]],
            template="simple_white",
            text="Frames",
        )
        fig_vid.update_traces(textposition="inside")
        fig_vid.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="Frames",
            legend_title="Event",
            barmode="stack",
        )
        st.plotly_chart(fig_vid, use_container_width=True)

        st.subheader("Person Count Over Time (CAVIAR_03)")
        c3 = video_df[video_df["Clip_ID"] == "CAVIAR_03"].copy()
        c3["Frame_Num"] = c3["Frame_ID"].str.extract(r"(\d+)").astype(int)
        fig_persons = px.area(
            c3, x="Frame_Num", y="Persons_Count",
            color_discrete_sequence=[C["blue"]],
            template="simple_white",
        )
        fig_persons.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Frame", yaxis_title="Persons Detected",
        )
        st.plotly_chart(fig_persons, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# TAB 5 — TEXT / SOCIAL MEDIA  (uses filtered_text)
# ════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Text Analysis")
    st.caption("Tools: spaCy · NLTK · HuggingFace DistilBERT · Dataset: CrimeReport (115 tweets)")
    st.markdown("<br>", unsafe_allow_html=True)

    if filtered_text.empty:
        st.info("No text records match the current filters.")
    else:
        tc1, tc2, tc3 = st.columns(3)

        with tc1:
            st.subheader("Crime Type")
            ct = filtered_text["Crime_Type"].value_counts().reset_index()
            ct.columns = ["Crime_Type", "Count"]
            fig_ct = px.bar(
                ct, x="Count", y="Crime_Type",
                orientation="h",
                color="Count",
                color_continuous_scale=[[0, C["sky"]], [1, C["blue"]]],
                text="Count",
                template="simple_white",
            )
            fig_ct.update_traces(textposition="outside")
            fig_ct.update_layout(
                coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis_title="", yaxis_title="",
            )
            st.plotly_chart(fig_ct, use_container_width=True)

        with tc2:
            st.subheader("Sentiment")
            sent = filtered_text["Sentiment"].value_counts().reset_index()
            sent.columns = ["Sentiment", "Count"]
            fig_s = px.pie(
                sent, names="Sentiment", values="Count",
                color="Sentiment",
                color_discrete_map={
                    "Negative": C["High"],
                    "Positive": C["Low"],
                    "Neutral":  C["Medium"],
                },
                template="simple_white",
            )
            fig_s.update_traces(textposition="inside", textinfo="percent+label")
            fig_s.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
            st.plotly_chart(fig_s, use_container_width=True)

        with tc3:
            st.subheader("Severity Label")
            sev = (
                filtered_text["Severity_Label"]
                .value_counts()
                .reindex(SEV_ORDER, fill_value=0)
                .reset_index()
            )
            sev.columns = ["Severity", "Count"]
            fig_sv = px.bar(
                sev, x="Severity", y="Count",
                color="Severity",
                color_discrete_map={s: c for s, c in zip(SEV_ORDER, SEV_COLORS)},
                text="Count",
                template="simple_white",
            )
            fig_sv.update_traces(textposition="outside", marker_line_width=0)
            fig_sv.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis_title="", yaxis_title="",
            )
            st.plotly_chart(fig_sv, use_container_width=True)

        st.markdown("---")
        st.subheader("Topic Distribution")
        topic = filtered_text["Topic"].value_counts().reset_index()
        topic.columns = ["Topic", "Count"]
        fig_topic = px.bar(
            topic, x="Topic", y="Count",
            color="Topic",
            color_discrete_sequence=[C["blue"], C["High"], C["Medium"], C["Low"],
                                      C["sky"], C["purple"]],
            text="Count",
            template="simple_white",
        )
        fig_topic.update_traces(textposition="outside", marker_line_width=0)
        fig_topic.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="Count",
        )
        st.plotly_chart(fig_topic, use_container_width=True)

        st.markdown("---")
        st.subheader("Sample Records")
        st.dataframe(filtered_text.head(20), use_container_width=True)


# ════════════════════════════════════════════════════════════════
# TAB 6 — FULL INTEGRATED REPORT  (uses filtered)
# ════════════════════════════════════════════════════════════════
with tab6:
    st.subheader("Integrated Incident Report")
    st.caption(
        f"5 incidents × {len(final_df.columns)} columns — "
        "all 5 modalities merged on Incident_ID · missing data filled with 'No data'"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Urgency scatter — FILTERED ───────────────────────────────
    if not filtered.empty:
        scatter_df = filtered.copy()
        scatter_df["Audio_Urgency_num"] = pd.to_numeric(scatter_df["Audio_Urgency"], errors="coerce").fillna(0)

        fig_scatter = px.scatter(
            scatter_df,
            x="Incident_ID",
            y="Audio_Urgency_num",
            color="Severity",
            size="Audio_Urgency_num",
            color_discrete_map={s: c for s, c in zip(SEV_ORDER, SEV_COLORS)},
            text="Incident_ID",
            template="simple_white",
            size_max=40,
            title="Urgency Score by Incident (sized by urgency, colored by severity)",
        )
        fig_scatter.update_traces(textposition="top center")
        fig_scatter.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis_title="", yaxis_title="Audio Urgency Score",
            yaxis=dict(range=[0, 1.2]),
            legend_title="Severity",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No incidents match the current filters.")

    st.markdown("---")
    st.subheader(f"Full Dataset ({len(filtered)} incident(s) after filters)")

    def color_severity(val):
        colors_map = {"High": "#FDECEA", "Medium": "#FFF8E1", "Low": "#E8F5E9"}
        return f"background-color: {colors_map.get(val, '')}"

    if not filtered.empty:
        display_cols = [
            "Incident_ID", "Audio_Event", "Audio_Location", "Audio_Urgency",
            "PDF_Department", "PDF_Doc_Type",
            "Image_Scene_Type", "Image_Objects",
            "Video_Event", "Video_Max_Persons",
            "Text_Crime_Type", "Text_Sentiment",
            "Severity",
        ]
        styled = filtered[display_cols].style.applymap(color_severity, subset=["Severity"])
        st.dataframe(styled, use_container_width=True)
    else:
        st.info("No incidents match the current filters.")

    st.markdown("<br>", unsafe_allow_html=True)
    csv_bytes = final_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download final_incident_report.csv",
        data=csv_bytes,
        file_name="final_incident_report.csv",
        mime="text/csv",
    )
