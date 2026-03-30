# Project Report — Multimodal Crime / Incident Report Analyzer
**Course:** AI for Engineers | **Type:** Group Assignment | **Total Marks:** 100

---

## 1. Introduction

Emergency response departments receive incident data from many different sources — phone calls, documents, images, video feeds, and social media. Reviewing all of this manually is slow and error-prone. The goal of this project is to build an AI pipeline that reads unstructured data from five different modalities and converts it into one structured incident report. Each team member handled one data type end to end, and the outputs were merged in a final integration step.

---

## 2. Student 1 — Audio Analysis

### Approach
The task was to transcribe emergency audio calls and extract structured information from the spoken content.

Speech-to-text transcription was done using OpenAI Whisper. The transcript was then passed through a spaCy NER pipeline to extract location mentions. Incident type was classified using keyword matching against a predefined set of categories (fire, robbery, assault, etc.). Sentiment and urgency scoring used a HuggingFace DistilBERT model fine-tuned on SST-2, combined with a keyword hit count to produce a 0–1 urgency score.

### Tools Used
- `openai-whisper` — speech-to-text transcription
- `spaCy (en_core_web_sm)` — named entity recognition for locations
- `transformers (distilbert-base-uncased-finetuned-sst-2-english)` — sentiment analysis

### Dataset
Five synthetic 911 call audio files were generated using gTTS to simulate real emergency scenarios (fire, road accident, robbery, assault, warehouse fire). The Kaggle 911 Calls + Wav2Vec2 notebook was used as the base reference.

### Challenges
- Whisper occasionally dropped short words, requiring transcript post-processing.
- Location extraction from brief calls was limited — spaCy sometimes missed informal location references like "near the docks."
- Urgency scoring required combining model confidence with keyword counts because the sentiment model alone could not distinguish urgency from general negativity.

### Results
Five calls were processed and output to `audio_output.csv`. All five had Distressed sentiment. Urgency scores ranged from 0.20 (calm witness report) to 0.89 (active assault). Call C004 had the highest urgency score.

| Call_ID | Extracted_Event | Urgency_Score |
|---------|-----------------|--------------|
| C001 | Fire, Medical Emergency | 0.80 |
| C002 | Road Accident, Medical Emergency | 0.20 |
| C003 | Robbery/Theft | 0.60 |
| C004 | Assault / Fight | 0.89 |
| C005 | Fire / Building fire | 0.52 |

---

## 3. Student 2 — Document Analysis

### Approach
The task was to extract structured information from a multi-page police PDF document.

The PDF was first tested with `pdfplumber`, which is recommended for text-based PDFs. The document turned out to be mostly scanned pages, so `PyMuPDF (fitz)` was used as a fallback, which extracted text from 14 out of 75 pages. `pytesseract` was set up as a further fallback for any fully scanned pages that neither tool could read. The extracted text was passed through spaCy NER to identify organizations, persons, dates, and locations. Document type was classified using rule-based keyword matching.

### Tools Used
- `pdfplumber` — primary text extraction (text-based PDFs)
- `PyMuPDF (fitz)` — fallback for mixed PDFs
- `pytesseract` — OCR fallback for fully scanned pages
- `spaCy` — NER for dates, organizations, officer names

### Dataset
Arkansas Police Department 1033 Training Plan Proposals (LESO2.pdf) — a real FOIA-released document from MuckRock. The PDF contains 75 pages covering MRAP vehicle training proposals from five Arkansas police departments.

### Challenges
- The document was described as text-based in the assignment, but most pages were scanned images with no text layer. PyMuPDF was used as the primary workaround.
- spaCy NER often confused organization names with person names in dense bureaucratic text.
- Date formats varied across documents (MM/DD/YY, "January 19, 2015", "1 December 2015"), requiring custom regex normalization.

### Results
Five reports were extracted from the PDF and saved to `pdf_output.csv`, one per police department. Dates were normalized to YYYY-MM-DD format.

| Report_ID | Department | Doc_Type | Date |
|-----------|-----------|---------|------|
| RPT_001 | Fort Smith Police Department | 1033 MRAP Training Proposal | 2015-01-19 |
| RPT_002 | Hot Springs Police Department | 1033 MRAP Training Proposal | 2015-05-05 |
| RPT_003 | Jacksonville AR Police Department | 1033 MRAP Training Proposal | 2015-01-14 |
| RPT_004 | Jefferson County Sheriff's Office | Standard Operating Procedure (SOP) | 2015-01-13 |
| RPT_005 | Lonoke County Sheriff's Office | 1033 MRAP Training Proposal | 2015-12-01 |

---

## 4. Student 3 — Image Analysis

### Approach
The task was to detect objects in crime or incident scene images, classify the scene type, and extract any visible text.

YOLOv8 nano (`yolov8n.pt`) was used for object detection. Images were preprocessed with OpenCV: resized to 640×640, denoised using `fastNlMeansDenoisingColored`, and contrast-enhanced using CLAHE on the LAB color space. Scene type was classified using rule-based mapping from detected COCO classes. `pytesseract` was integrated for OCR to detect visible text such as street signs or license plates.

### Tools Used
- `ultralytics (YOLOv8n)` — object detection, COCO pretrained
- `opencv-python` — preprocessing (resize, denoise, CLAHE)
- `pytesseract` — OCR for text in images
- `roboflow` — dataset download (Roboflow Fire Detection, for fire/smoke specific detection)

### Dataset
Roboflow Fire Detection dataset (1000+ labeled fire and smoke images in YOLOv8 format). For local testing, two bundled ultralytics test images were used (bus.jpg → road incident scene, zidane.jpg → public disturbance scene).

### Challenges
- The YOLOv8n COCO model does not include fire or smoke as classes. A Roboflow fine-tuned fire detection model would be needed for fire-specific detection in production.
- OCR on low-quality or small images produced noisy output.
- The available test images were general scenes, not crime scenes — results reflect what a pipeline run on real incident images would produce.

### Results
Two images were processed and saved to `image_output.csv`. Both produced real bounding box coordinates and confidence scores.

| Image_ID | Scene_Type | Objects_Detected | Confidence |
|----------|-----------|-----------------|------------|
| IMG_001 | Road Incident Scene | bus, person, stop sign | 0.66 |
| IMG_002 | Public Disturbance Scene | person, tie | 0.65 |

---

## 5. Student 4 — Video Analysis

### Approach
The task was to extract frames from CCTV footage, detect motion, identify objects and activities, and produce a timestamped event log.

Three video clips were downloaded from the CAVIAR dataset (.mpg format). OpenCV was used to extract one frame every 15 frames (~0.6 seconds at 25fps). Motion was detected by computing pixel-wise frame differences with Gaussian blur and thresholding. YOLOv8n was run on each sampled frame to detect objects. Events were classified using a combination of the clip name (fight/browse/collapse) and the motion score.

### Tools Used
- `opencv-python` — frame extraction and motion detection (frame differencing)
- `ultralytics (YOLOv8n)` — per-frame object detection
- `moviepy / imageio` — video loading and manipulation
- `PyTorch` — backend for YOLOv8

### Dataset
CAVIAR CCTV Dataset from the University of Edinburgh. Three clips were used:
- `Fight_Chase.mpg` (5MB, 437 frames) — chase scenario
- `Fight_RunAway1.mpg` (6MB, 556 frames) — fight/run scenario
- `Browse1.mpg` (12MB, 1050 frames) — person browsing

### Challenges
- CAVIAR footage is old low-resolution MPEG video from the early 2000s. YOLOv8 confidence scores were low (0.2–0.7) because the model was not trained on this footage style.
- The CAVIAR fight scenarios involve close-together people, which YOLOv8 sometimes detected as a single large blob rather than separate persons.
- Motion detection thresholding required tuning — too low and empty frames flagged motion, too high and slow movements were missed.

### Results
136 frame-level rows across three clips were saved to `video_output.csv`. CAVIAR_01 and CAVIAR_02 produced "Suspicious movement" events. CAVIAR_03 produced "Person browsing."

| Clip_ID | Frames Sampled | Dominant Event |
|---------|---------------|----------------|
| CAVIAR_01 | 29 | Suspicious movement |
| CAVIAR_02 | 37 | Suspicious movement |
| CAVIAR_03 | 70 | Person browsing |

---

## 6. Student 5 — Text Analysis

### Approach
The task was to process crime-related social media posts, extract entities, classify the crime type and topic, and determine sentiment.

The dataset is in JSON Lines format — one tweet object per line. Text was cleaned by removing URLs, @mentions, and special characters using regex. NLTK was used for tokenization, stopword removal, and lemmatization. spaCy NER extracted locations, persons, and organizations. HuggingFace DistilBERT was used for sentiment analysis. Crime type and topic were classified using keyword matching. Severity was assigned based on keyword presence (fire, murder, shooting → High; robbery, arrest → Medium; else Low).

### Tools Used
- `nltk` — tokenization, stopword removal, lemmatization
- `spaCy (en_core_web_sm)` — NER for people, locations, organizations, dates
- `transformers (distilbert-base-uncased-finetuned-sst-2-english)` — sentiment analysis
- `pandas` — structured output

### Dataset
CrimeReport — 115 real crime-related tweets in JSON Lines format from Kaggle. Topics include shootings, robberies, assaults, arrests, and fire incidents across various US cities.

### Challenges
- Most tweets had no location tag, so location extraction relied entirely on spaCy NER, which often returned "Unknown" for short informal text.
- 82 out of 115 posts were classified as "General Crime" because tweets about police policy or news coverage do not contain specific crime-type keywords.
- Twitter text is short and informal, which reduces NER precision.

### Results
115 rows saved to `text_output.csv`. Most posts were Negative sentiment. 18 were High severity, 10 Medium, 87 Low.

| Crime_Type | Count |
|-----------|-------|
| General Crime | 82 |
| Shooting | 10 |
| Arrest | 7 |
| Homicide | 5 |
| Assault | 5 |
| Fire / Arson | 3 |

---

## 7. Final Integration

### Approach
The five output CSVs were merged into a single unified incident dataset following five steps:

**Step 1 — Define Incident_ID:** Five incidents (INC_001 to INC_005) were defined, anchored on the audio calls. Each modality's records were mapped to the most semantically matching incident based on crime type and scene context.

**Step 2 — Merge DataFrames:** A base DataFrame of five incident IDs was created. All five modality DataFrames were joined to it using left merges on Incident_ID.

**Step 3 — Handle missing values:** String columns with no matching data were filled with "No data". Numeric columns were filled with 0.

**Step 4 — Severity classification:** Each incident's severity was computed by scanning combined text from Audio_Event, Text_Crime_Type, Text_Severity, Image_Scene_Type, and Video_Event for high/medium/low keyword signals. Audio urgency score was also factored in.

**Step 5 — Query interface:** A `query_incidents()` function was built that filters the final dataset by severity, event keyword, or location. A text-based dashboard prints severity counts and per-incident modality coverage.

### Tools Used
- `pandas` — merge, join, fillna, groupby operations

### Challenges
- The five datasets are from different sources and domains, so there is no natural incident key to join on. The mapping required manual semantic alignment.
- The video CSV had 136 rows (frame-level), so it needed to be aggregated to clip-level before merging.
- Some incidents had no matching image or video data, resulting in "No data" entries — this is expected and handled explicitly.

### Results
`final_incident_report.csv` — 5 incidents × 25 columns, all modalities merged.

| Incident_ID | Audio_Event | PDF_Doc_Type | Image_Objects | Video_Event | Text_Crime_Type | Severity |
|-------------|-------------|--------------|---------------|-------------|-----------------|----------|
| INC_001 | Fire, Medical Emergency | 1033 MRAP Training Proposal | No data | Person browsing | Fire / Arson | High |
| INC_002 | Road Accident, Medical Emergency | 1033 MRAP Training Proposal | bus, person, stop sign | No data | Shooting | High |
| INC_003 | Robbery/Theft | 1033 MRAP Training Proposal | No data | Suspicious movement | Robbery / Theft | Medium |
| INC_004 | Assault / Fight | Standard Operating Procedure (SOP) | person, tie | Suspicious movement | Assault | High |
| INC_005 | Fire / Building fire | 1033 MRAP Training Proposal | No data | No data | Fire / Arson | High |

---

## 8. Conclusion

The pipeline successfully converts unstructured data from five different modalities into one structured dataset that can be filtered and queried. Each modality pipeline runs independently and produces a clean CSV with standardized columns. The integration step then merges all five outputs on a shared Incident_ID key and assigns a final severity rating.

The main limitation of the current prototype is that the five datasets are from different real-world sources, so incident matching is semantic rather than exact. In a real deployment, all five modalities would feed data about the same incident at the same time, making the Incident_ID alignment automatic. The pipeline is designed to support that — each modality just needs to tag its output with a shared incident key at ingestion time.
