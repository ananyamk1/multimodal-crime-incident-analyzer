# Multimodal Crime / Incident Report Analyzer

**Assignment - Group 9**

---


## AI Pipeline Architecture


An AI-powered pipeline that automatically ingests unstructured data from five modalities: audio, documents, images, video, and text ; and converts them into a unified structured incident report that investigators can query and analyze.


```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNSTRUCTURED DATA INGESTION                          │
│  Audio (.mp3) │ PDF (.pdf) │ Images (.jpg) │ Video (.mpg) │ Text (.txt) │
└──────┬────────┴─────┬──────┴──────┬────────┴──────┬───────┴──────┬──────┘
       │              │             │               │              │
       ▼              ▼             ▼               ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐
│   STUDENT 1  │ │STUDENT 2 │ │STUDENT 3 │ │ STUDENT 4 │ │  STUDENT 5   │
│    Audio     │ │   PDF    │ │  Image   │ │   Video   │ │    Text      │
│  Analyst     │ │ Analyst  │ │ Analyst  │ │  Analyst  │ │  Analyst     │
│              │ │          │ │          │ │           │ │              │
│ Whisper STT  │ │pdfplumber│ │ YOLOv8   │ │  OpenCV   │ │   spaCy      │
│ spaCy NER    │ │PyMuPDF   │ │ OpenCV   │ │  YOLOv8   │ │transformers  │
│ Sentiment    │ │Tesseract │ │Tesseract │ │  Motion   │ │   NLTK       │
│ HuggingFace  │ │ spaCy    │ │ Roboflow │ │ Detection │ │  Sentiment   │
└──────┬───────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘ └──────┬───────┘
       │              │             │              │              │
       ▼              ▼             ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐
│audio_output  │ │pdf_output│ │image_    │ │video_     │ │text_output   │
│    .csv      │ │  .csv    │ │output.csv│ │output.csv │ │   .csv       │
│ 5 rows       │ │ 5 rows   │ │ 2 rows   │ │ 136 rows  │ │ 115 rows     │
└──────┬───────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘ └──────┬───────┘
       │              │             │              │              │
       └──────────────┴─────────────┴──────────────┴──────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │   FINAL INTEGRATION      │
                      │  (integration/ folder)   │
                      │                          │
                      │ 1. Define Incident_ID    │
                      │ 2. Merge 5 DataFrames    │
                      │ 3. Handle missing values │
                      │ 4. Severity scoring      │
                      │ 5. Query interface       │
                      └────────────┬────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   final_incident_report.csv   │
                    │   5 incidents x 25 columns    │
                    │                               │
                    │ Incident_ID | Audio_Event     │
                    │ PDF_Doc_Type | Image_Objects  │
                    │ Video_Event | Text_Crime_Type │
                    │ Severity (Low/Medium/High)    │
                    └──────────────────────────────┘
```

---



## Repository Structure

```
multimodal-crime-incident-analyzer/
│
├── audio/
│   ├── audio_processing_complete.ipynb   # Whisper STT + spaCy NER + sentiment
│   └── audio_output.csv                  # 5 emergency call records
│
├── pdf/
│   ├── pdf_processing.ipynb              # pdfplumber + PyMuPDF + spaCy NER
│   ├── LESO2.pdf                         # Arkansas Police 1033 Training Plans
│   └── pdf_output.csv                    # 5 police department reports
│
├── images/
│   ├── image_processing.ipynb            # YOLOv8 + OpenCV + pytesseract OCR
│   ├── IMG_001.jpg                        # Road incident scene
│   ├── IMG_002.jpg                        # Public disturbance scene
│   └── image_output.csv                  # 2 detected scenes
│
├── video/
│   ├── video_processing.ipynb            # OpenCV frame extraction + YOLOv8
│   ├── Fight_Chase.mpg                   # CAVIAR fight/chase clip
│   ├── Fight_RunAway1.mpg                # CAVIAR runaway clip
│   ├── Browse1.mpg                       # CAVIAR browsing clip
│   └── video_output.csv                  # 136 frame-level detections
│
├── text/
│   ├── text_processing.ipynb             # spaCy NER + HuggingFace sentiment
│   ├── CrimeReport (1).txt               # 115 crime-related tweets (JSON Lines)
│   └── text_output.csv                   # 115 NLP-processed records
│
├── integration/
│   ├── integration.ipynb                 # 5-step final integration pipeline
│   └── final_incident_report.csv         # Unified 5-incident dataset (25 cols)
│
├── requirements.txt                      # All Python dependencies
└── README.md                             # This file
```

---

## Individual Roles

| Student | Modality | AI Tools | Dataset | Output |
|---------|----------|----------|---------|--------|
| 1 — Audio Analyst | Emergency audio calls | Whisper, spaCy, HuggingFace | 911 Calls / synthetic WAV | `audio_output.csv` (5 rows) |
| 2 — Document Analyst | Police PDFs | pdfplumber, PyMuPDF, pytesseract, spaCy | Arkansas PD 1033 LESO2.pdf | `pdf_output.csv` (5 rows) |
| 3 — Image Analyst | Crime scene photos | YOLOv8, OpenCV, pytesseract | Roboflow Fire Detection | `image_output.csv` (2 rows) |
| 4 — Video Analyst | CCTV surveillance | OpenCV, YOLOv8, moviepy | CAVIAR CCTV Dataset | `video_output.csv` (136 rows) |
| 5 — Text Analyst | Social media posts | spaCy, transformers, NLTK | CrimeReport tweets | `text_output.csv` (115 rows) |

---

## Final Integrated Dataset

| Incident_ID | Audio_Event | PDF_Doc_Type | Image_Objects | Video_Event | Text_Crime_Type | Severity |
|-------------|-------------|--------------|---------------|-------------|-----------------|----------|
| INC_001 | Fire, Medical Emergency | 1033 MRAP Training Proposal | No data | Person browsing | Fire / Arson | High |
| INC_002 | Road Accident, Medical Emergency | 1033 MRAP Training Proposal | bus, person, stop sign | No data | Shooting | High |
| INC_003 | Robbery/Theft | 1033 MRAP Training Proposal | No data | Suspicious movement | Robbery / Theft | Medium |
| INC_004 | Assault / Fight | Standard Operating Procedure (SOP) | person, tie | Suspicious movement | Assault | High |
| INC_005 | Fire / Building fire | 1033 MRAP Training Proposal | No data | No data | Fire / Arson | High |

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run each modality notebook
Open and run notebooks in order: `audio/` → `pdf/` → `images/` → `video/` → `text/`

### 3. Run the final integration
```bash
cd integration/
jupyter notebook integration.ipynb
```

### 4. Query the final dataset
```python
import pandas as pd
df = pd.read_csv('integration/final_incident_report.csv')

# Filter by severity
high = df[df['Severity'] == 'High']

# Filter by event type
fires = df[df['Audio_Event'].str.contains('fire', case=False)]
```

---

## Datasets Used

| Modality | Dataset | Source |
|----------|---------|--------|
| Audio | 911 Calls + Wav2Vec2 | Kaggle |
| PDF | Arkansas PD 1033 Training Plans (LESO2.pdf) | MuckRock FOIA |
| Images | Roboflow Fire Detection (1000+ images) | Roboflow Universe |
| Video | CAVIAR CCTV Dataset (.mpg clips) | University of Edinburgh |
| Text | CrimeReport (115 crime tweets) | Kaggle |
