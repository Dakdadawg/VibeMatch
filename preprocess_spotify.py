
from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw/spotify_tracks.csv")
OUTPUT_PATH = Path("data/processed/spotify_tracks.parquet")

REQUIRED_COLUMNS = [
    "track_id",
    "artists",
    "track_name",
    "popularity",
    "track_genre",
]

NUMERIC_FEATURES = [
    "popularity",
    "duration_ms",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature",
]


def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_PATH.resolve()}"
        )

    print("Loading raw Spotify dataset...")
    df = pd.read_csv(RAW_PATH, low_memory=False)

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    original_rows = len(df)

    # Normalize essential identity fields.
    for column in ["track_id", "artists", "track_name", "track_genre"]:
        df[column] = df[column].fillna("").astype(str).str.strip()

    # Rows without a track ID, artist, or title cannot reliably
    # identify a recommendation candidate.
    valid_identity = (
        df["track_id"].ne("")
        & df["artists"].ne("")
        & df["track_name"].ne("")
    )
    df = df.loc[valid_identity].copy()

    # Convert numerical fields safely.
    for column in NUMERIC_FEATURES:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Reject impossible values in fields with known valid ranges.
    bounded_features = {
        "popularity": (0, 100),
        "danceability": (0, 1),
        "energy": (0, 1),
        "mode": (0, 1),
        "speechiness": (0, 1),
        "acousticness": (0, 1),
        "instrumentalness": (0, 1),
        "liveness": (0, 1),
        "valence": (0, 1),
    }

    for column, (minimum, maximum) in bounded_features.items():
        if column in df.columns:
            invalid = (
                df[column].notna()
                & ~df[column].between(minimum, maximum)
            )
            df.loc[invalid, column] = float("nan")

    # Require usable core features for the initial recommender.
    core_features = [
        "popularity",
        "danceability",
        "energy",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]

    existing_core = [
        column for column in core_features if column in df.columns
    ]

    before_feature_filter = len(df)
    df = df.dropna(subset=existing_core).copy()

    # Keep the original genre labels before aggregating repeated IDs.
    df["track_genre"] = df["track_genre"].replace("", pd.NA)

    print(f"Raw rows: {original_rows:,}")
    print(f"Rows with valid track identity: {len(df):,}")
    print(
        "Rows removed for missing core features: "
        f"{before_feature_filter - len(df):,}"
    )

    # Duplicate IDs can represent the same track tagged under
    # different genres. Aggregate genre labels rather than discarding them.
    print("Aggregating repeated track IDs and genre labels...")

    aggregation = {}

    for column in df.columns:
        if column == "track_id":
            continue
        elif column == "track_genre":
            aggregation[column] = lambda values: sorted(
                set(values.dropna().astype(str).str.strip()) - {""}
            )
        elif column in NUMERIC_FEATURES:
            aggregation[column] = "median"
        else:
            aggregation[column] = "first"

    processed = (
        df.groupby("track_id", as_index=False, sort=False)
        .agg(aggregation)
    )

    # Remove records that have no genre information at all.
    processed = processed.loc[
        processed["track_genre"].map(bool)
    ].reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(OUTPUT_PATH, index=False)

    print("\nPREPROCESSING SUMMARY")
    print("=" * 50)
    print(f"Original rows: {original_rows:,}")
    print(f"Processed unique tracks: {len(processed):,}")
    print(
        "Repeated-ID rows consolidated: "
        f"{len(df) - len(processed):,}"
    )
    print(
        "Unique artists: "
        f"{processed['artists'].nunique():,}"
    )
    print(
        "Distinct genre labels across catalogue: "
        f"{len(set(g for genres in processed['track_genre'] for g in genres)):,}"
    )
    print(f"Output: {OUTPUT_PATH.resolve()}")
    print("\nPreview:")
    print(
        processed[
            ["track_id", "artists", "track_name", "popularity", "track_genre"]
        ].head(5).to_string(index=False)
    )
    print("\nPREPROCESSING COMPLETE")


if __name__ == "__main__":
    main()
