# Demonstration Script — Multimodal Crime / Incident Report Analyzer

> **Estimated duration:** 8–10 minutes
> **Format:** Screen share, walk through the repo and notebooks live
> **Tip:** Have all five output CSVs and the final_incident_report.csv open in a spreadsheet app side by side before you start.

---

## [INTRO — 30 seconds]

> *"We built an AI pipeline that takes raw unstructured data — audio calls, PDFs, images, video, and social media posts — and converts all of it into one structured incident report. I'll walk through each modality, show the raw input, show what the AI extracts, and then show how everything gets merged at the end."*

---

## [PART 1 — Audio Modality — 1.5 minutes]

**Show:** Open `audio/` folder. Show the notebook `audio_processing_complete.ipynb`.

> *"Student 1 handled audio. The raw input here is emergency call audio files. These are MP3 files — just voice recordings of someone reporting an incident."*

**Show:** Run or scroll through Cell 3 (Whisper transcription output).

> *"We pass the audio through OpenAI's Whisper model, which converts speech to text. So this call — 'There is a fire, people are trapped on the second floor' — gets transcribed automatically."*

**Show:** Scroll to Cell A (spaCy extraction).

> *"We then run spaCy NER on the transcript to pull out the location — here it finds 'Avenue' — and keyword matching to classify the event as Fire and Medical Emergency."*

**Show:** Open `audio_output.csv`.

> *"The output is this CSV. Five calls, each with a transcript, event type, location, sentiment, and an urgency score from 0 to 1. C004 scored 0.89 — that's the assault call with 'immediately' and 'attacking' in it."*

---

## [PART 2 — PDF Modality — 1.5 minutes]

**Show:** Open `pdf/` folder. Open `pdf_processing.ipynb`.

> *"Student 2 handled police PDF documents. The raw input is LESO2.pdf — a 75-page FOIA-released police document from Arkansas."*

**Show:** Briefly open the PDF — show it's dense pages of police training proposals.

> *"When we run pdfplumber on it, most pages return nothing — they're scanned images. So the notebook falls back to PyMuPDF, which manages to extract text from 14 pages. For anything still unreadable, pytesseract would run OCR."*

**Show:** Open `pdf_output.csv`.

> *"The output is five rows — one per police department. We extracted the department name, document type, date, and the LESO program it belongs to. The dates were in three different formats across the document — January 19 2015, 5/5/15, 1 December 2015 — so we normalized all of them to YYYY-MM-DD."*

---

## [PART 3 — Image Modality — 1 minute]

**Show:** Open `images/` folder. Show IMG_001.jpg and IMG_002.jpg side by side.

> *"Student 3 handled images. The raw input is photographs of scenes — in a real deployment these would be CCTV stills or scene photos. We used two test images here."*

**Show:** Open `image_processing.ipynb`, scroll to the YOLOv8 cell.

> *"We run each image through YOLOv8, which gives us bounding boxes and confidence scores for every object it detects. This image here — it detects a bus, three people, and a stop sign. That maps to a Road Incident scene type."*

**Show:** Open `image_output.csv`.

> *"Output is this CSV. Image ID, scene type, objects detected, bounding box coordinates, and average confidence score."*

---

## [PART 4 — Video Modality — 1.5 minutes]

**Show:** Open `video/` folder. Briefly play a few seconds of `Fight_Chase.mpg`.

> *"Student 4 handled CCTV video. This is a clip from the CAVIAR surveillance dataset — simulated indoor footage of people in a shopping corridor. Three clips were downloaded: two fight scenarios and a browsing scenario."*

**Show:** Open `video_processing.ipynb`, scroll to the frame extraction cell.

> *"OpenCV extracts one frame every 15 frames — so about 0.6 seconds of real time. We then compute a motion score per frame by diffing consecutive grayscale frames. High pixel change means high motion."*

**Show:** Scroll to the YOLOv8 inference cell.

> *"YOLOv8 runs on each extracted frame and tells us what objects are present — mostly people. Combined with the motion score and the clip name, we classify the event. Fight clips get 'Suspicious movement'. The browse clip gets 'Person browsing'."*

**Show:** Open `video_output.csv`.

> *"136 rows — one per sampled frame across the three clips. Each row has a timestamp, frame ID, event classification, person count, and confidence."*

---

## [PART 5 — Text Modality — 1 minute]

**Show:** Open `text/` folder. Show a few lines of `CrimeReport (1).txt` — raw JSON.

> *"Student 5 handled social media text. The raw input is 115 crime-related tweets in JSON Lines format. Each line is a full tweet object with the post text, timestamp, and location if the user tagged it."*

**Show:** Open `text_processing.ipynb`, scroll through cleaning and NER cells.

> *"We clean the text first — remove URLs, mentions, hashtag symbols. Then NLTK tokenizes and removes stopwords. spaCy NER picks up any location mentions. DistilBERT gives us the sentiment. Keyword matching gives us the crime type and topic."*

**Show:** Open `text_output.csv`.

> *"115 rows. Each tweet is now a structured record with crime type, location, sentiment, topic, and severity label."*

---

## [PART 6 — Final Integration — 2 minutes]

**Show:** Open `integration/integration.ipynb`.

> *"Now the final integration. We have five separate CSV outputs. The goal is to merge them into one dataset where each row represents a single incident."*

**Show:** Scroll to Step 1 cell.

> *"Step 1 is defining a shared Incident_ID. We define five incidents — INC_001 through INC_005 — anchored on the audio calls, because those are the primary incident reports. Each other modality is mapped to the closest matching incident by crime type."*

**Show:** Scroll to Step 2 (merge cell).

> *"Step 2 merges all five DataFrames on Incident_ID using pandas left joins. We start with a base table of five incident IDs and join each modality's data in."*

**Show:** Scroll to Step 3 (fillna).

> *"Step 3 fills any gaps. Some incidents have no matching image or video data — those get 'No data'. Numeric columns get 0."*

**Show:** Scroll to Step 4 (severity cell).

> *"Step 4 computes a final severity rating. It scans the combined text from all five modalities — audio event, text crime type, image scene, video event — for high and medium severity keywords. Audio urgency score is also factored in. INC_004 — the assault — scores High because the audio urgency was 0.89 and 'assault' and 'fight' are both high-severity keywords."*

**Show:** Open `integration/final_incident_report.csv`.

> *"This is the final output. Five incidents, 25 columns, one row per incident. You can see all five modalities side by side — audio call type, PDF document type, image objects, video event, text crime type, and the final severity."*

**Show:** Scroll to Step 5 — run a query.

> *"Step 5 is a query interface. I can filter by severity — let me pull all High severity incidents. Or I can search by event keyword — 'fire' — and get back just the fire incidents. This is how an analyst would actually use the system to filter and review cases."*

---

## [CLOSE — 30 seconds]

> *"So to summarize: raw unstructured data comes in from five sources — audio, PDF, image, video, and text. Each AI component processes its own modality and outputs a clean structured CSV. The integration step merges all five on a shared Incident_ID, handles missing data, and computes a final severity score. The result is one unified incident report that an analyst can search and filter without having to manually review any of the raw data."*

---

> **End of demonstration.**
