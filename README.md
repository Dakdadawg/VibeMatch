# VibeMatch 🎵

A content-based music recommendation system built with Python, Streamlit, pandas, and scikit-learn.

## Overview

VibeMatch recommends similar tracks by analyzing audio features and genre information. It combines feature-based similarity with genre overlap and popularity to rank recommendations.

The current implementation uses a predefined hybrid scoring approach rather than a supervised model trained on user preferences.

## Features

- Music recommendations based on audio-feature similarity
- Genre-overlap analysis
- Popularity-aware ranking
- Interactive Streamlit interface
- Spotify track data preprocessing
- Docker containerization
- AWS EC2 deployment

## Technology Stack

- Python
- Streamlit
- pandas and PyArrow
- scikit-learn
- Docker
- AWS EC2

## Project Structure

```text
VibeMatch/
├── app.py
├── src/
│   └── recommender.py
├── scripts/
│   └── evaluate_recommender.py
├── data/
│   └── processed/
│       └── spotify_tracks.parquet
├── preprocess_spotify.py
├── download_dataset.py
├── audit_dataset.py
├── verify_spotify.py
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

## Run Locally

### Prerequisites

- Python 3.11 recommended
- Git
- The processed dataset file: `data/processed/spotify_tracks.parquet`

### 1. Clone the repository

```bash
git clone https://github.com/Dakdadawg/VibeMatch.git
cd VibeMatch
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Prepare the dataset

The application requires `data/processed/spotify_tracks.parquet`.

If this file is not included in your checkout, follow the dataset download and preprocessing workflow in `download_dataset.py` and `preprocess_spotify.py`. Review those scripts and the dataset's license before downloading or redistributing data.

### 5. Launch the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## Recommendation Method

The system standardizes numerical audio features and uses similarity-based ranking, supplemented by genre overlap and popularity.

The current hybrid scoring weights are predefined. This is a content-based recommendation system, not a supervised model trained on listener ratings or personal preferences.

## Dataset

The project uses the [Spotify Tracks Dataset on Hugging Face](https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset).

Dataset attribution and license terms should be checked before redistributing the dataset.

## Limitations and Future Work

- Evaluate recommendations using broader, user-centered metrics.
- Tune scoring weights using systematic experiments.
- Improve reproducibility and dataset setup.
- Explore personalized recommendations in future versions.

## Author

**Dakdadawg**

GitHub: [@Dakdadawg](https://github.com/Dakdadawg)
