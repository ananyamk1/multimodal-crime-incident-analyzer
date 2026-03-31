# Multimodal Crime / Incident Report Analyzer
**AI for Engineers | Spring 2026 | Group Project**

---

## 1. Overview and Pipeline Architecture

Emergency response departments receive incident data from phone calls, documents, images, video feeds, and social media all at once. Reviewing all of it manually is slow and inconsistent. We built a pipeline that ingests unstructured data from five different modalities and merges them into one structured incident report that can be filtered and queried by severity, event type, or location.

Each modality runs as an independent pipeline and writes a clean CSV with standardized columns. The integration step joins all five outputs on a shared `Incident_ID` key and computes a final severity rating per incident.

```
Audio (.wav)        ──┐
PDF Reports         ──┤
Incident Images     ──┼──► Modality CSVs ──► Integration ──► final_incident_report.csv
CCTV Video Clips    ──┤
Social Media Text   ──┘
```

---

## 2. Modality Pipelines

### Audio Analysis

The audio pipeline transcribes emergency calls and extracts structured fields from the spoken content. Speech-to-text was handled by OpenAI Whisper. The transcript was then passed through spaCy NER to pick out location mentions, and incident type was classified using keyword matching against a predefined category list (fire, robbery, assault, etc.). Urgency scoring combined DistilBERT sentiment confidence with a weighted keyword hit count to produce a 0–1 score — the sentiment model alone couldn't distinguish urgency from general negativity, so the hybrid approach was necessary.

**Tools:** `openai-whisper`, `spaCy (en_core_web_sm)`, `transformers (distilbert-base-uncased-finetuned-sst-2-english)`

**Dataset:** Five synthetic 911 call audio files generated with gTTS (fire, road accident, robbery, assault, warehouse fire). The Kaggle 911 Calls + Wav2Vec2 notebook was used as a reference baseline.

Whisper occasionally dropped short words and needed transcript post-processing. spaCy also struggled with informal location references like "near the docks" — a known limitation of the `sm` model on short conversational text.

---

### Document Analysis

The PDF pipeline extracts structured fields from multi-page police documents. We started with `pdfplumber`, which is the standard choice for text-based PDFs, but the document turned out to be mostly scanned pages. `PyMuPDF (fitz)` recovered usable text from 14 of 75 pages, with `pytesseract` set up as a further OCR fallback. Extracted text went through spaCy NER to identify organizations, persons, dates, and locations. Document type was classified using rule-based keyword matching. Date formats varied across the document and required a custom regex normalization pass before any downstream processing.

**Tools:** `pdfplumber`, `PyMuPDF (fitz)`, `pytesseract`, `spaCy`

**Dataset:** Arkansas Police Department 1033 Training Plan Proposals (`LESO2.pdf`) — a real FOIA-released document from MuckRock, 75 pages covering MRAP vehicle training proposals from five Arkansas police departments.

spaCy regularly confused organization names with person names in dense bureaucratic text. Three different date formats in the same document (`MM/DD/YY`, `January 19, 2015`, `1 December 2015`) also made normalization more involved than expected.

---

### Image Analysis

The image pipeline detects objects in crime and incident scene images, classifies the scene type, and pulls any visible text. YOLOv8 nano (`yolov8n.pt`) handles object detection on images preprocessed with OpenCV — resized to 640×640, denoised with `fastNlMeansDenoisingColored`, and contrast-enhanced using CLAHE on the LAB color space. Scene type is assigned through rule-based mapping of detected COCO classes. `pytesseract` was added for OCR on any visible text like street signs or license plates.

**Tools:** `ultralytics (YOLOv8n)`, `opencv-python`, `pytesseract`, `roboflow`

**Dataset:** Roboflow Fire Detection dataset (1000+ labeled images). For local testing, two bundled ultralytics test images were used: `bus.jpg` and `zidane.jpg`.

The YOLOv8n COCO model has no fire or smoke classes — a Roboflow fine-tuned model is needed for fire-specific detection in a real deployment. OCR on low-resolution images also returned noisy output and isn't reliable below a certain image quality threshold.

---

### Video Analysis

The video pipeline extracts frames from CCTV footage, detects motion, identifies objects, and produces a timestamped event log. OpenCV handles frame extraction at one frame every 15 frames (~0.6s at 25fps). Motion is detected by computing pixel-wise frame differences with Gaussian blur and thresholding. YOLOv8n runs on each sampled frame, and events are classified by combining the clip label with the computed motion score.

**Tools:** `opencv-python`, `ultralytics (YOLOv8n)`, `moviepy / imageio`, `PyTorch`

**Dataset:** CAVIAR CCTV Dataset (University of Edinburgh). Three clips were used — `Fight_Chase.mpg` (437 frames), `Fight_RunAway1.mpg` (556 frames), and `Browse1.mpg` (1050 frames).

CAVIAR is old low-resolution MPEG footage from the early 2000s, and YOLOv8 confidence scores stayed between 0.2–0.7 throughout because the model was never trained on this footage style. Close-together people in fight clips were sometimes merged into a single detection blob. Motion detection thresholding also needed manual tuning — the default values flagged empty frames as motion.

---

### Text Analysis

The text pipeline processes crime-related social media posts, extracts entities, classifies crime type, and scores sentiment. Input is JSON Lines format, one post per line. Text is cleaned with regex (URLs, @mentions, special characters removed). NLTK handles tokenization, stopword removal, and lemmatization. spaCy NER extracts locations, persons, and organizations. DistilBERT handles sentiment classification. Crime type and severity are assigned through keyword matching — `fire`, `murder`, `shooting` map to High; `robbery`, `arrest` to Medium; everything else to Low.

**Tools:** `nltk`, `spaCy (en_core_web_sm)`, `transformers (distilbert-base-uncased-finetuned-sst-2-english)`, `pandas`

**Dataset:** CrimeReport — 115 real crime-related tweets in JSON Lines format from Kaggle, covering shootings, robberies, assaults, arrests, and fire incidents across US cities.

Most tweets had no location tag, so location extraction relied entirely on NER, which returned "Unknown" frequently on short informal text. 82 of 115 posts fell into "General Crime" because tweets about police policy or news coverage don't carry specific crime-type keywords.

---

## 3. Results

**Audio** — Five calls processed. All five returned Distressed sentiment. Urgency scores ranged from 0.20 (calm witness report) to 0.89 (active assault).

| Call_ID | Extracted_Event | Urgency_Score |
|---------|----------------|---------------|
| C001 | Fire, Medical Emergency | 0.80 |
| C002 | Road Accident, Medical Emergency | 0.20 |
| C003 | Robbery/Theft | 0.60 |
| C004 | Assault / Fight | 0.89 |
| C005 | Fire / Building fire | 0.52 |

**PDF** — Five reports extracted, one per police department. All dates normalized to `YYYY-MM-DD`.

| Report_ID | Department | Doc_Type | Date |
|-----------|-----------|---------|------|
| RPT_001 | Fort Smith Police Department | 1033 MRAP Training Proposal | 2015-01-19 |
| RPT_002 | Hot Springs Police Department | 1033 MRAP Training Proposal | 2015-05-05 |
| RPT_003 | Jacksonville AR Police Department | 1033 MRAP Training Proposal | 2015-01-14 |
| RPT_004 | Jefferson County Sheriff's Office | Standard Operating Procedure (SOP) | 2015-01-13 |
| RPT_005 | Lonoke County Sheriff's Office | 1033 MRAP Training Proposal | 2015-12-01 |

**Image** — Two images processed with real bounding box coordinates and confidence scores.

| Image_ID | Scene_Type | Objects_Detected | Confidence |
|----------|-----------|-----------------|------------|
| IMG_001 | Road Incident Scene | bus, person, stop sign | 0.66 |
| IMG_002 | Public Disturbance Scene | person, tie | 0.65 |

**Video** — 136 frame-level rows across three clips. CAVIAR_01 and CAVIAR_02 flagged suspicious movement; CAVIAR_03 was uneventful.

| Clip_ID | Frames Sampled | Dominant Event |
|---------|---------------|----------------|
| CAVIAR_01 | 29 | Suspicious movement |
| CAVIAR_02 | 37 | Suspicious movement |
| CAVIAR_03 | 70 | Person browsing |

**Text** — 115 posts processed. Most were Negative sentiment. Severity breakdown: 18 High, 10 Medium, 87 Low.

| Crime_Type | Count |
|-----------|-------|
| General Crime | 82 |
| Shooting | 10 |
| Arrest | 7 |
| Homicide | 5 |
| Assault | 5 |
| Fire / Arson | 3 |

---

## 4. Integration

The five CSVs were merged into a single dataset in five steps. First, five incidents (`INC_001`–`INC_005`) were defined and anchored on the audio calls. Each modality's records were mapped to the closest matching incident by crime type and scene context — there is no shared key across the five source datasets, so this alignment was done manually. A base DataFrame of five incident IDs was created, and all five modality DataFrames were joined using left merges. Missing string fields were filled with `"No data"`; missing numerics with `0`. Severity was computed by scanning combined text fields from all modalities for keyword signals, with the audio urgency score as a tiebreaker. A `query_incidents()` function was built on top of the final dataset to filter by severity, keyword, or location.

The video CSV required aggregation from frame-level (136 rows) to clip-level before merging — it was the only modality that produced multiple rows per incident.

**Final output — `final_incident_report.csv` (5 incidents × 25 columns)**

| Incident_ID | Audio_Event | PDF_Doc_Type | Image_Objects | Video_Event | Text_Crime_Type | Severity |
|-------------|-------------|-------------|---------------|-------------|-----------------|----------|
| INC_001 | Fire, Medical Emergency | 1033 MRAP Training Proposal | No data | Person browsing | Fire / Arson | High |
| INC_002 | Road Accident, Medical Emergency | 1033 MRAP Training Proposal | bus, person, stop sign | No data | Shooting | High |
| INC_003 | Robbery/Theft | 1033 MRAP Training Proposal | No data | Suspicious movement | Robbery / Theft | Medium |
| INC_004 | Assault / Fight | Standard Operating Procedure (SOP) | person, tie | Suspicious movement | Assault | High |
| INC_005 | Fire / Building fire | 1033 MRAP Training Proposal | No data | No data | Fire / Arson | High |

---

## 5. Ethics and Limitations

**Human oversight.** The pipeline produces a structured report and severity rating — it does not make decisions. A human dispatcher or analyst reviews every output before any action is taken. The system is a filtering and organization tool, not an automated response system.

**Transparency.** Each incident record retains the raw extracted fields from all five modalities alongside the final severity label. Reviewers can see exactly which signals drove the classification rather than trusting a black-box score.

**Dataset mismatch.** The five datasets are from different real-world sources and domains. In a real deployment, all five modalities would feed data about the same incident in real time, making the `Incident_ID` alignment automatic. The current prototype uses manual semantic matching as a stand-in for that shared key — it works for demonstration purposes but is not production-ready as-is.

**Model limitations.** YOLOv8n was not fine-tuned on crime scene imagery or CCTV-style footage. DistilBERT was fine-tuned on SST-2, a general sentiment dataset — not emergency communications. Both models produce usable results here, but neither should be treated as reliable without domain-specific fine-tuning.

---

## 6. Team Contributions

| Member | Contributions |  Modules  |
|--------|--------------|------------|
| Adi | Audio pipeline — Processed real Kaggle 911 emergency call audio using OpenAI Whisper for speech-to-text transcription; implemented spaCy NER pipeline for location extraction; built keyword-based event classifier with KEYWORD_MAP; designed hybrid urgency scoring combining DistilBERT sentiment confidence with urgency keyword hit count  | audio_processing_final_2.ipynb, audio_output.csv, audio_files/C001–C005.wav |
| Harshini | PDF pipeline — pExtracted structured data from 75-page FOIA police PDF using 3-tier fallback chain (pdfplumber → PyMuPDF → pytesseract OCR); applied spaCy NER for organization and date extraction; built custom regex normalization to standardize three date formats to YYYY-MM-DD  |   pdf_processing.ipynb, pdf_output.csv (5 rows), LESO2.pdf  |
| Ashwin | Image pipeline — Downloaded Roboflow fire-smoke detection dataset; ran OpenCV preprocessing pipeline, executed Roboflow hosted YOLOv8 fire-smoke model inference; integrated pytesseract OCR for visible text extraction; classified scene types from detected classes |  image_processing_final.ipynb, image_output.csv (20 rows, Fire Scene detections 0.76–0.97 confidence)  |
| Sahithi | Video pipeline — Downloaded 3 CAVIAR CCTV clips; built OpenCV frame extraction pipeline (1 frame per 15 frames); implemented motion detection via frame differencing with Gaussian blur and threshold; ran YOLOv8n on each sampled frame; classified events by clip name and motion score; aggregated frame-level output to clip-level  |  video_processing.ipynb, video_output.csv (136 frame-level rows across 3 clips) |
| Ananya | Text pipeline — Cleaned and processed 115 real crime tweets (regex, NLTK tokenization, stopword removal); ran spaCy NER for location extraction; applied DistilBERT sentiment analysis; built keyword classifiers for crime type, topic, and severity; built full integration pipeline, defined Incident_ID mapping, merged DataFrames, handled missing values, computed severity scores, implemented query_incidents() filter interface |  text_processing.ipynb, text_output.csv, integration.ipynb, final_incident_report.csv  |




