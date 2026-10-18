
from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/raw/spotify_tracks.csv")

FAMOUS_ARTISTS = [
    "Radiohead",
    "Tame Impala",
    "Arctic Monkeys",
    "The Beatles",
    "Nirvana",
    "Pink Floyd",
    "Queen",
    "David Bowie",
    "Kendrick Lamar",
    "Kanye West",
    "Taylor Swift",
    "Billie Eilish",
    "Lana Del Rey",
    "Frank Ocean",
    "The Weeknd",
    "Daft Punk",
    "Gorillaz",
    "Coldplay",
    "Muse",
    "The Strokes",
    "Fleetwood Mac",
    "Led Zeppelin",
    "Metallica",
    "Linkin Park",
    "Eminem",
    "Drake",
    "Adele",
    "Oasis",
    "Mac DeMarco",
    "Joji",
    "Cigarettes After Sex",
    "The Killers",
    "Paramore",
    "The Cure",
    "Red Hot Chili Peppers",
    "Kendrick Lamar",
    "Lorde",
    "Laufey",
    "Tyler, The Creator",
    "Childish Gambino",
]


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH.resolve()}"
        )

    print("Reading dataset...")
    df = pd.read_csv(DATA_PATH, low_memory=False)

    print("\nDATASET OVERVIEW")
    print("=" * 60)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"File size: {DATA_PATH.stat().st_size / (1024 * 1024):.2f} MB")

    print("\nCOLUMNS AND DATA TYPES")
    print(df.dtypes.to_string())

    print("\nFIRST FIVE ROWS")
    print(df.head().to_string(max_cols=12))

    print("\nMISSING VALUES")
    missing = df.isna().sum().sort_values(ascending=False)
    print(missing[missing > 0].to_string() or "No missing values")

    print("\nDUPLICATE TRACK IDS")
    if "track_id" in df.columns:
        print(int(df["track_id"].duplicated().sum()))
    else:
        print("No track_id column found")

    print("\nPOPULARITY DISTRIBUTION")
    if "popularity" in df.columns:
        print(df["popularity"].describe().round(2).to_string())
    else:
        print("No popularity column found")

    print("\nGENRE SUMMARY")
    if "track_genre" in df.columns:
        print(f"Unique genres: {df['track_genre'].nunique(dropna=True)}")
        print(df["track_genre"].value_counts().head(15).to_string())
    else:
        print("No track_genre column found")

    print("\nFAMOUS ARTIST COVERAGE")
    print("=" * 60)

    if "artists" not in df.columns:
        print("No artists column found.")
    else:
        artists = df["artists"].fillna("").astype(str)

        for artist in FAMOUS_ARTISTS:
            # Exact artist-name matching within the dataset's
            # semicolon-separated artist field.
            count = artists.apply(
                lambda value: artist.casefold()
                in {
                    part.strip().strip("'\"").casefold()
                    for part in value.split(";")
                }
            ).sum()

            print(f"{artist:<28} {int(count):>5} tracks")

    print("\nNUMERICAL AUDIO FEATURES")
    audio_features = [
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
        "duration_ms",
        "popularity",
    ]

    present = [col for col in audio_features if col in df.columns]
    if present:
        print(df[present].describe().round(2).to_string())
    else:
        print("No expected numerical audio features found.")

    print("\nAUDIT COMPLETE")


if __name__ == "__main__":
    main()
