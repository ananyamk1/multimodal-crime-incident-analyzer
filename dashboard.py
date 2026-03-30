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
# COLOR SCHEME — Wong palette (color-blind friendly), light theme
# ─────────────────────────────────────────────────────────────────
C = {
    "High":      "#D55E00",   # Vermillion
    "Medium":    "#E69F00",   # Amber
    "Low":       "#009E73",   # Bluish green
    "blue":      "#0072B2",   # Blue
    "sky":       "#56B4E9",   # Sky blue
    "purple":    "#CC79A7",   # Reddish purple
    "bg":        "#F5F5F5",
    "card":      "#FFFFFF",
    "border":    "#E0E0E0",
    "text":      "#222222",
    "subtext":   "#555555",
    "sidebar_bg":"#FFFFFF",
}

# ─────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── App background ───────────────────────────────── */
.stApp {{
    background-color: {C['bg']};
    color: {C['text']};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

/* ── Sidebar ──────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background-color: {C['sidebar_bg']};
    border-right: 1.5px solid {C['border']};
}}
section[data-testid="stSidebar"] * {{
    color: {C['text']} !important;
}}

/* ── Metric cards ─────────────────────────────────── */
div[data-testid="metric-container"] {{
    background-color: {C['card']};
    border: 1.5px solid {C['border']};
    border-radius: 10px;
    padding: 18px 22px;
}}

/* ── Tab bar ──────────────────────────────────────── */
div[data-testid="stTabs"] button {{
    font-weight: 600;
    color: {C['subtext']};
    border-radius: 6px 6px 0 0;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {C['blue']} !important;
    border-bottom: 3px solid {C['blue']};
}}

/* ── Dataframe ────────────────────────────────────── */
div[data-testid="stDataFrame"] {{
    border: 1.5px solid {C['border']};
    border-radius: 8px;
    overflow: hidden;
}}

/* ── Card helper ──────────────────────────────────── */
.incident-card {{
    background: {C['card']};
    border: 1.5px solid {C['border']};
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
}}
.section-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {C['blue']};
    margin-bottom: 4px;
    letter-spacing: 0.02em;
}}
.badge-high   {{ background:{C['High']};   color:#fff; padding:2px 10px; border-radius:12px; font-size:0.82rem; font-weight:600; }}
.badge-medium {{ background:{C['Medium']}; color:#fff; padding:2px 10px; border-radius:12px; font-size:0.82rem; font-weight:600; }}
.badge-low    {{ background:{C['Low']};    color:#fff; padding:2px 10px; border-radius:12px; font-size:0.82rem; font-weight:600; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    final  = pd.read_csv(os.path.join(BASE, "integration", "final_incident_report.csv"))
    audio  = pd.read_csv(os.path.join(BASE, "audio",       "audio_output.csv"))
    pdf    = pd.read_csv(os.path.join(BASE, "pdf",         "pdf_output.csv"))
    image  = pd.read_csv(os.path.join(BASE, "images",      "image_output.csv"))
    video  = pd.read_csv(os.path.join(BASE, "video",       "video_output.csv"))
    text   = pd.read_csv(os.path.join(BASE, "text",        "text_output.csv"))
    return final, audio, pdf, image, video, text

final_df, audio_df, pdf_df, image_df, video_df, text_df = load_data()

SEV_ORDER  = ["High", "Medium", "Low"]
SEV_COLORS = [C["High"], C["Medium"], C["Low"]]

# ─────────────────────────────────────────────────────────────────
# SIDEBAR — FILTERS
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div class='section-title'>🔍 Incident Filters</div>", unsafe_allow_html=True)
    st.markdown("---")

    severity_filter = st.multiselect(
        "Severity",
        options=SEV_ORDER,
        default=SEV_ORDER,
    )

    event_search = st.text_input("Search event keyword", placeholder="e.g. fire, robbery")

    st.markdown("---")
    st.markdown(f"<div class='section-title'>ℹ About</div>", unsafe_allow_html=True)
    st.caption(
        "AI-powered pipeline that ingests audio, PDF, image, "
        "video, and text data and converts them into a unified "
        "structured incident report."
    )
    st.caption("Course: AI for Engineers")

# ─────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────
filtered = final_df[final_df["Severity"].isin(severity_filter)]
if event_search.strip():
    mask = (
        filtered["Audio_Event"].str.contains(event_search, case=False, na=False)
        | filtered["Text_Crime_Type"].str.contains(event_search, case=False, na=False)
        | filtered["Video_Event"].str.contains(event_search, case=False, na=False)
    )
    filtered = filtered[mask]

# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────
st.markdown(
    f"<h1 style='color:{C['blue']};margin-bottom:0;'>Multimodal Crime / Incident Report Analyzer</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='color:{C['subtext']};margin-top:4px;font-size:1rem;'>"
    "AI for Engineers — Group Assignment &nbsp;|&nbsp; "
    f"Showing <b>{len(filtered)}</b> of <b>{len(final_df)}</b> incidents</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Incidents",  len(final_df))
k2.metric("High Severity",    int((final_df["Severity"] == "High").sum()),   delta=None)
k3.metric("Medium Severity",  int((final_df["Severity"] == "Medium").sum()), delta=None)
k4.metric("Low Severity",     int((final_df["Severity"] == "Low").sum()),    delta=None)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Overview",
    "🔊 Audio",
    "📄 Documents",
    "🖼️ Image & Video",
    "📝 Text / Social Media",
    "🔗 Full Integrated Report",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1.2, 1])

    # ── Severity distribution chart ──────────────────────────────
    with col_left:
        st.markdown(f"<div class='section-title'>Severity Distribution</div>", unsafe_allow_html=True)
        sev_counts = final_df["Severity"].value_counts().reindex(SEV_ORDER, fill_value=0).reset_index()
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
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="",
            yaxis=dict(showgrid=True, gridcolor=C["border"]),
            font=dict(color=C["text"]),
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    # ── Modality coverage matrix ─────────────────────────────────
    with col_right:
        st.markdown(f"<div class='section-title'>Modality Coverage per Incident</div>", unsafe_allow_html=True)

        coverage = final_df[["Incident_ID", "Audio_Source", "PDF_Source",
                              "Image_Source", "Video_Source", "Text_Source"]].copy()
        for col in ["Audio_Source", "PDF_Source", "Image_Source", "Video_Source", "Text_Source"]:
            coverage[col] = coverage[col].apply(lambda x: "✓" if x != "No data" else "✗")
        coverage.columns = ["Incident", "Audio", "PDF", "Image", "Video", "Text"]
        coverage = coverage.set_index("Incident")

        # Convert to numeric for heatmap
        cov_num = coverage.replace({"✓": 1, "✗": 0})
        fig_heat = go.Figure(data=go.Heatmap(
            z=cov_num.values,
            x=list(cov_num.columns),
            y=list(cov_num.index),
            colorscale=[[0, C["border"]], [1, C["blue"]]],
            showscale=False,
            text=coverage.values,
            texttemplate="%{text}",
            textfont={"size": 18, "color": C["text"]},
        ))
        fig_heat.update_layout(
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(side="top"),
            font=dict(color=C["text"]),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # ── Filtered incident summary cards ─────────────────────────
    st.markdown(f"<div class='section-title'>Incident Summary ({len(filtered)} shown)</div>",
                unsafe_allow_html=True)

    if filtered.empty:
        st.info("No incidents match the current filters.")
    else:
        for _, row in filtered.iterrows():
            badge_cls = f"badge-{row['Severity'].lower()}"
            st.markdown(f"""
            <div class='incident-card'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                    <span style='font-weight:700;font-size:1.05rem;color:{C["blue"]};'>{row['Incident_ID']}</span>
                    <span class='{badge_cls}'>{row['Severity']}</span>
                </div>
                <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.88rem;color:{C["subtext"]};'>
                    <div><b>Audio:</b> {row['Audio_Event']}</div>
                    <div><b>PDF:</b> {row['PDF_Doc_Type']}</div>
                    <div><b>Image:</b> {row['Image_Objects']}</div>
                    <div><b>Video:</b> {row['Video_Event']}</div>
                    <div><b>Text:</b> {row['Text_Crime_Type']}</div>
                    <div><b>Location:</b> {row['Audio_Location']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 2 — AUDIO
# ════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"<div class='section-title'>Emergency Call Analysis — Student 1 (Audio Analyst)</div>",
                unsafe_allow_html=True)
    st.caption("Tools: OpenAI Whisper · spaCy NER · HuggingFace DistilBERT · Dataset: 911 Calls (real audio, first 6 seconds)")
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1.3])

    with col_a:
        st.markdown(f"<div class='section-title'>Urgency Score per Call</div>", unsafe_allow_html=True)
        fig_urg = px.bar(
            audio_df, x="Call_ID", y="Urgency_Score",
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
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="Urgency Score (0–1)",
            font=dict(color=C["text"]),
        )
        st.plotly_chart(fig_urg, use_container_width=True)

    with col_b:
        st.markdown(f"<div class='section-title'>Sentiment Distribution</div>", unsafe_allow_html=True)
        sent_counts = audio_df["Sentiment"].value_counts().reset_index()
        sent_counts.columns = ["Sentiment", "Count"]
        fig_sent = px.pie(
            sent_counts, names="Sentiment", values="Count",
            color="Sentiment",
            color_discrete_map={"Distressed": C["High"], "Calm": C["Low"], "Neutral": C["Medium"]},
            template="simple_white",
        )
        fig_sent.update_traces(textposition="inside", textinfo="percent+label")
        fig_sent.update_layout(
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(color=C["text"]),
            showlegend=False,
        )
        st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>Call Details</div>", unsafe_allow_html=True)
    st.dataframe(
        audio_df.style.background_gradient(subset=["Urgency_Score"], cmap="Oranges"),
        use_container_width=True,
    )


# ════════════════════════════════════════════════════════════════
# TAB 3 — DOCUMENTS
# ════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"<div class='section-title'>Police PDF Document Extraction — Student 2 (Document Analyst)</div>",
                unsafe_allow_html=True)
    st.caption("Tools: pdfplumber · PyMuPDF · pytesseract OCR · spaCy NER · Dataset: Arkansas PD LESO2.pdf (75 pages)")
    st.markdown("<br>", unsafe_allow_html=True)

    col_d1, col_d2 = st.columns([1.5, 1])

    with col_d1:
        st.markdown(f"<div class='section-title'>Extracted Reports</div>", unsafe_allow_html=True)
        st.dataframe(pdf_df, use_container_width=True)

    with col_d2:
        st.markdown(f"<div class='section-title'>Document Types</div>", unsafe_allow_html=True)
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
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="",
            font=dict(color=C["text"]),
            showlegend=False,
        )
        st.plotly_chart(fig_doc, use_container_width=True)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>Program Distribution</div>", unsafe_allow_html=True)
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
        plot_bgcolor=C["card"],
        paper_bgcolor=C["bg"],
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="", yaxis_title="",
        font=dict(color=C["text"]),
    )
    st.plotly_chart(fig_prog, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# TAB 4 — IMAGE & VIDEO
# ════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"<div class='section-title'>Visual Analysis — Student 3 (Image) & Student 4 (Video)</div>",
                unsafe_allow_html=True)

    img_col, vid_col = st.columns(2)

    # ── Image ────────────────────────────────────────────────────
    with img_col:
        st.markdown(f"<div class='section-title'>Image — Object Detection (YOLOv8)</div>",
                    unsafe_allow_html=True)
        st.caption("Tools: YOLOv8 · OpenCV · pytesseract · Dataset: Roboflow Fire Detection")
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(image_df, use_container_width=True)

        fig_img = px.bar(
            image_df, x="Image_ID", y="Confidence",
            color="Scene_Type",
            color_discrete_sequence=[C["blue"], C["sky"]],
            text="Confidence",
            template="simple_white",
            range_y=[0, 1.1],
        )
        fig_img.update_traces(textposition="outside")
        fig_img.update_layout(
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="Confidence",
            font=dict(color=C["text"]),
            legend_title="Scene Type",
        )
        st.plotly_chart(fig_img, use_container_width=True)

    # ── Video ────────────────────────────────────────────────────
    with vid_col:
        st.markdown(f"<div class='section-title'>Video — Event Timeline (OpenCV + YOLOv8)</div>",
                    unsafe_allow_html=True)
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
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="Frames",
            font=dict(color=C["text"]),
            legend_title="Event",
            barmode="stack",
        )
        st.plotly_chart(fig_vid, use_container_width=True)

        st.markdown(f"<div class='section-title'>Person Count Over Time (CAVIAR_03)</div>",
                    unsafe_allow_html=True)
        c3 = video_df[video_df["Clip_ID"] == "CAVIAR_03"].copy()
        c3["Frame_Num"] = c3["Frame_ID"].str.extract(r"(\d+)").astype(int)
        fig_persons = px.area(
            c3, x="Frame_Num", y="Persons_Count",
            color_discrete_sequence=[C["blue"]],
            template="simple_white",
        )
        fig_persons.update_layout(
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Frame", yaxis_title="Persons Detected",
            font=dict(color=C["text"]),
        )
        st.plotly_chart(fig_persons, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# TAB 5 — TEXT / SOCIAL MEDIA
# ════════════════════════════════════════════════════════════════
with tab5:
    st.markdown(f"<div class='section-title'>Text / Social Media Analysis — Student 5 (Text Analyst)</div>",
                unsafe_allow_html=True)
    st.caption("Tools: spaCy · NLTK · HuggingFace DistilBERT · Dataset: CrimeReport (115 tweets)")
    st.markdown("<br>", unsafe_allow_html=True)

    tc1, tc2, tc3 = st.columns(3)

    # Crime type
    with tc1:
        st.markdown(f"<div class='section-title'>Crime Type</div>", unsafe_allow_html=True)
        ct = text_df["Crime_Type"].value_counts().reset_index()
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
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="",
            font=dict(color=C["text"]),
        )
        st.plotly_chart(fig_ct, use_container_width=True)

    # Sentiment
    with tc2:
        st.markdown(f"<div class='section-title'>Sentiment</div>", unsafe_allow_html=True)
        sent = text_df["Sentiment"].value_counts().reset_index()
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
        fig_s.update_layout(
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            font=dict(color=C["text"]),
        )
        st.plotly_chart(fig_s, use_container_width=True)

    # Severity
    with tc3:
        st.markdown(f"<div class='section-title'>Severity Label</div>", unsafe_allow_html=True)
        sev = text_df["Severity_Label"].value_counts().reindex(SEV_ORDER, fill_value=0).reset_index()
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
            plot_bgcolor=C["card"],
            paper_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="", yaxis_title="",
            font=dict(color=C["text"]),
        )
        st.plotly_chart(fig_sv, use_container_width=True)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>Topic Distribution</div>", unsafe_allow_html=True)
    topic = text_df["Topic"].value_counts().reset_index()
    topic.columns = ["Topic", "Count"]
    fig_topic = px.bar(
        topic, x="Topic", y="Count",
        color="Topic",
        color_discrete_sequence=[C["blue"], C["High"], C["Medium"], C["Low"],
                                  C["sky"], C["purple"], C["Medium"], C["sky"]],
        text="Count",
        template="simple_white",
    )
    fig_topic.update_traces(textposition="outside", marker_line_width=0)
    fig_topic.update_layout(
        showlegend=False,
        plot_bgcolor=C["card"],
        paper_bgcolor=C["bg"],
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="", yaxis_title="Count",
        font=dict(color=C["text"]),
    )
    st.plotly_chart(fig_topic, use_container_width=True)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>Sample Records</div>", unsafe_allow_html=True)
    st.dataframe(text_df.head(20), use_container_width=True)


# ════════════════════════════════════════════════════════════════
# TAB 6 — FULL INTEGRATED REPORT
# ════════════════════════════════════════════════════════════════
with tab6:
    st.markdown(f"<div class='section-title'>Final Integrated Incident Report</div>",
                unsafe_allow_html=True)
    st.caption(
        f"5 incidents × {len(final_df.columns)} columns — "
        "all 5 modalities merged on Incident_ID · missing data filled with 'No data'"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Audio urgency vs severity scatter
    scatter_df = final_df.copy()
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
    )
    fig_scatter.update_traces(textposition="top center")
    fig_scatter.update_layout(
        plot_bgcolor=C["card"],
        paper_bgcolor=C["bg"],
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="", yaxis_title="Audio Urgency Score",
        yaxis=dict(range=[0, 1.15]),
        font=dict(color=C["text"]),
        legend_title="Severity",
        title="Urgency Score by Incident (sized by urgency, colored by severity)",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.markdown(f"<div class='section-title'>Full Dataset ({len(filtered)} incident(s) after filters)</div>",
                unsafe_allow_html=True)

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
        label="Download full_incident_report.csv",
        data=csv_bytes,
        file_name="final_incident_report.csv",
        mime="text/csv",
    )
