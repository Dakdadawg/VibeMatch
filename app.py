
import html

import streamlit as st

from src.recommender import SongRecommender


# ============================================================
# Configuration
# ============================================================

st.set_page_config(
    page_title="VibeMatch",
    page_icon="♫",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --background: #000000;
        --panel: #0b0b0b;
        --surface: #171717;
        --border: #303030;
        --text: #f5f5f5;
        --muted: #a7a7a7;
        --green: #1ed760;
        --green-hover: #3be477;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--background);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1200px;
        padding: 0.5rem 1.25rem 2.5rem;
        background: var(--panel);
        border-radius: 14px 14px 0 0;
        min-height: 100vh;
    }

    /* Header */

    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 12px 0 20px;
        border-bottom: 1px solid #292929;
        margin-bottom: 3.1rem;
    }

    .brand-icon {
        width: 46px;
        height: 46px;
        flex: 0 0 46px;
        border-radius: 50%;
        background: var(--green);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000000;
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 29px;
        font-weight: 700;
        line-height: 1;
    }

    .brand-name {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 23px;
        font-weight: 700;
        letter-spacing: -0.7px;
    }

    .brand-caption {
        margin-left: auto;
        color: var(--muted);
        font-size: 12px;
        letter-spacing: 0.2px;
    }

    /* Intro */

    .hero {
        text-align: center;
        margin: 0 auto 2.3rem;
        max-width: 720px;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--text);
        font-size: clamp(31px, 4.5vw, 43px);
        font-weight: 600;
        letter-spacing: -1.5px;
        line-height: 1.2;
        margin: 0 0 12px;
    }

    .hero-description {
        color: var(--muted);
        font-size: 17px;
        line-height: 1.6;
        margin: 0;
    }

    /* Search */

    .stTextInput label,
    .stSelectbox label {
        color: var(--muted) !important;
        font-size: 13px !important;
    }

    .stTextInput input,
    .stSelectbox [data-baseweb="select"] > div {
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        min-height: 46px;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stTextInput input:focus {
        border-color: var(--green) !important;
        box-shadow: 0 0 0 1px var(--green) !important;
    }

    /* Settings panel */

    .settings-panel {
        background: var(--surface);
        border: 1px solid #353535;
        border-radius: 11px;
        padding: 15px 16px 4px;
        margin: 16px 0 20px;
    }

    .settings-heading {
        color: var(--muted);
        font-size: 12px;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .setting-label {
        color: var(--text);
        font-size: 15px;
        padding-top: 11px;
    }

    .setting-divider {
        height: 1px;
        background: #303030;
        margin: 7px 0 11px;
    }

    .stCheckbox label {
        color: var(--muted) !important;
        font-size: 13px !important;
    }

    /* Primary action */

    div[data-testid="stButton"] button {
        background: var(--green);
        color: #000000;
        border: 1px solid var(--green);
        border-radius: 10px;
        min-height: 50px;
        font-size: 15px;
        font-weight: 600;
        transition: background 0.15s ease;
    }

    div[data-testid="stButton"] button:hover {
        background: var(--green-hover);
        border-color: var(--green-hover);
        color: #000000;
    }

    /* Results */

    .results-heading {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 600;
        margin: 2.2rem 0 13px;
    }

    .result-row {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 12px;
        border-bottom: 1px solid #292929;
        border-radius: 7px;
    }

    .result-row:hover {
        background: #171717;
    }

    .result-rank {
        flex: 0 0 25px;
        color: var(--muted);
        font-size: 13px;
    }

    .result-main {
        flex: 1;
        min-width: 0;
    }

    .result-title {
        color: var(--text);
        font-size: 14px;
        font-weight: 600;
        overflow-wrap: anywhere;
    }

    .result-artist {
        color: var(--muted);
        font-size: 12px;
        margin-top: 4px;
        overflow-wrap: anywhere;
    }

    .result-genres {
        color: #858585;
        font-size: 11px;
        margin-top: 5px;
        line-height: 1.5;
        overflow-wrap: anywhere;
    }

    .result-side {
        text-align: right;
        flex: 0 0 auto;
    }

    .result-score {
        color: var(--green);
        font-size: 14px;
        font-weight: 600;
    }

    .result-score-label,
    .result-popularity {
        color: var(--muted);
        font-size: 10px;
        margin-top: 4px;
    }

    .method-note {
        color: var(--muted);
        font-size: 11px;
        line-height: 1.7;
        margin-top: 13px;
    }

    .footer {
        border-top: 1px solid #292929;
        margin-top: 2.7rem;
        padding-top: 16px;
        display: flex;
        justify-content: space-between;
        gap: 10px;
        color: #777777;
        font-size: 11px;
    }

    #MainMenu,
    footer,
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        visibility: hidden;
    }

    @media (max-width: 600px) {
        .block-container {
            padding: 0.5rem 0.85rem 2rem;
        }

        .brand {
            margin-bottom: 2.4rem;
        }

        .brand-icon {
            width: 40px;
            height: 40px;
            flex-basis: 40px;
        }

        .brand-name {
            font-size: 21px;
        }

        .brand-caption {
            display: none;
        }

        .hero-description {
            font-size: 14px;
        }

        .result-row {
            gap: 8px;
            padding: 12px 4px;
        }

        .result-rank {
            flex-basis: 19px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Recommendation engine
# ============================================================

@st.cache_resource
def load_recommender():
    return SongRecommender()


def display_genres(value):
    if isinstance(value, (list, tuple, set)):
        values = value
    elif hasattr(value, "tolist"):
        values = value.tolist()
    elif isinstance(value, str):
        values = [value]
    else:
        values = []

    return ", ".join(
        str(item).strip()
        for item in values
        if str(item).strip()
    ) or "Unknown"


def track_label(row):
    return f"{row['track_name']} — {row['artists']}"


try:
    recommender = load_recommender()
except Exception as exc:
    st.error("VibeMatch could not load the music catalogue.")
    st.exception(exc)
    st.stop()


# ============================================================
# Header
# ============================================================

st.markdown(
    """
    <div class="brand">
        <div class="brand-icon">♫</div>
        <div class="brand-name">VibeMatch</div>
        <div class="brand-caption">MUSIC DISCOVERY</div>
    </div>

    <div class="hero">
        <div class="hero-title">Your next favourite song.</div>
        <div class="hero-description">
            Find something new from something you love.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Search
# ============================================================

query = st.text_input(
    "Search songs or artists",
    placeholder="⌕   Search songs or artists...",
    label_visibility="collapsed",
)

if not query.strip():
    st.stop()

matches = recommender.search_songs(query, limit=50)

if matches.empty:
    st.warning("No matching tracks found. Try another search.")
    st.stop()

selected_index = st.selectbox(
    "Matching tracks",
    options=matches.index.tolist(),
    format_func=lambda index: track_label(
        recommender.get_song(index)
    ),
    label_visibility="collapsed",
)

seed = recommender.get_song(selected_index)


# ============================================================
# Discovery settings
# ============================================================

method_labels = {
    "Hybrid": "hybrid",
    "Audio cosine": "audio_cosine",
    "Audio Euclidean": "audio_euclidean",
    "Genre filtered": "genre_filtered",
}

st.markdown(
    """
    <div style="
        color: #1ED760;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin: 22px 0 12px;
    ">
        DISCOVERY SETTINGS
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([3, 1])

with left:
    st.markdown(
        '<div class="setting-label">Recommendation method</div>',
        unsafe_allow_html=True,
    )

with right:
    method_label = st.selectbox(
        "Recommendation method",
        options=list(method_labels.keys()),
        index=0,
        label_visibility="collapsed",
    )

method = method_labels[method_label]

st.markdown('<div class="setting-divider"></div>', unsafe_allow_html=True)

left, right = st.columns([3, 1])

with left:
    st.markdown(
        '<div class="setting-label">Number of tracks</div>',
        unsafe_allow_html=True,
    )

with right:
    top_n = st.selectbox(
        "Number of tracks",
        options=[5, 10, 15, 20],
        index=1,
        label_visibility="collapsed",
    )

exclude_same_artist = st.checkbox(
    "Explore different artists",
    value=False,
)

generate = st.button(
    "Find recommendations  →",
    type="primary",
    use_container_width=True,
)


# ============================================================
# Generate recommendations
# ============================================================

if generate:
    try:
        with st.spinner("Finding recommendations..."):
            results = recommender.recommend_songs(
                int(selected_index),
                top_n=int(top_n),
                method=method,
                exclude_same_artist=exclude_same_artist,
            )

        st.session_state["vm_results"] = results
        st.session_state["vm_seed"] = int(selected_index)
        st.session_state["vm_method"] = method
        st.session_state["vm_top_n"] = int(top_n)
        st.session_state["vm_exclude_artist"] = exclude_same_artist

    except Exception as exc:
        st.error(f"Could not generate recommendations: {exc}")


# ============================================================
# Results
# ============================================================

results = st.session_state.get("vm_results")

settings_match = (
    st.session_state.get("vm_seed") == int(selected_index)
    and st.session_state.get("vm_method") == method
    and st.session_state.get("vm_top_n") == int(top_n)
    and st.session_state.get("vm_exclude_artist") == exclude_same_artist
)

if results is not None and settings_match:
    st.markdown(
        '<div class="results-heading">Recommendations</div>',
        unsafe_allow_html=True,
    )

    if results.empty:
        st.info("No recommendations found. Try another method.")
    else:
        score_labels = {
            "hybrid": "HYBRID SCORE",
            "audio_cosine": "COSINE SCORE",
            "audio_euclidean": "AUDIO SCORE",
            "genre_filtered": "AUDIO SCORE",
        }

        for rank, (_, row) in enumerate(results.iterrows(), start=1):
            title = html.escape(str(row["track_name"]))
            artists = html.escape(str(row["artists"]))
            genres = html.escape(display_genres(row["track_genre"]))
            score = float(row["recommendation_score"])
            popularity = float(row["popularity"])

            st.markdown(
                f"""
                <div class="result-row">
                    <div class="result-rank">{rank:02d}</div>
                    <div class="result-main">
                        <div class="result-title">{title}</div>
                        <div class="result-artist">{artists}</div>
                        <div class="result-genres">{genres}</div>
                    </div>
                    <div class="result-side">
                        <div class="result-score">{score:.3f}</div>
                        <div class="result-score-label">
                            {score_labels[method]}
                        </div>
                        <div class="result-popularity">
                            POP {popularity:.0f}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        notes = {
            "hybrid": (
                "Combines audio similarity, genre overlap, and popularity. "
                "Scores are not probabilities."
            ),
            "audio_cosine": (
                "Ranks tracks by cosine similarity across audio features. "
                "Scores are not probabilities."
            ),
            "audio_euclidean": (
                "Ranks tracks using a transformation of audio-feature distance."
            ),
            "genre_filtered": (
                "Restricts candidates to shared genres, then ranks by audio similarity."
            ),
        }

        st.markdown(
            f'<div class="method-note">{html.escape(notes[method])}</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# Footer
# ============================================================

st.markdown(
    """
    <div class="footer">
        <span>VibeMatch</span>
        <span>CONTENT-BASED MUSIC DISCOVERY</span>
    </div>
    """,
    unsafe_allow_html=True,
)
