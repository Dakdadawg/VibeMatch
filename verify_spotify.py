
from pathlib import Path

import pandas as pd

PATH = Path("data/processed/spotify_tracks.parquet")


def main():
    if not PATH.exists():
        raise FileNotFoundError(f"Not found: {PATH.resolve()}")

    df = pd.read_parquet(PATH)

    print("PROCESSED DATASET VERIFICATION")
    print("=" * 55)
    print(f"Tracks: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Unique track IDs: {df['track_id'].nunique():,}")
    print(f"Duplicate track IDs: {df['track_id'].duplicated().sum():,}")
    print(f"Unique artist entries: {df['artists'].nunique():,}")

    print("\nGENRE COVERAGE")
    genre_counts = df["track_genre"].explode().value_counts()
    print(f"Unique genres: {len(genre_counts):,}")
    print(genre_counts.head(10).to_string())

    print("\nPOPULARITY")
    print(df["popularity"].describe().round(2).to_string())

    print("\nFAMOUS ARTIST COVERAGE")
    artist_names = [
        "Radiohead",
        "Tame Impala",
        "Arctic Monkeys",
        "The Beatles",
        "Nirvana",
        "Pink Floyd",
        "Billie Eilish",
        "The Weeknd",
        "Linkin Park",
        "Taylor Swift",
        "Daft Punk",
    ]

    for name in artist_names:
        matching = df["artists"].fillna("").str.contains(
            name, case=False, regex=False
        )
        print(f"{name:<22} {int(matching.sum()):>5} tracks")

    print("\nMISSING VALUES IN CORE FIELDS")
    columns = [
        "track_id",
        "artists",
        "track_name",
        "popularity",
        "danceability",
        "energy",
        "valence",
        "tempo",
        "track_genre",
    ]
    print(df[columns].isna().sum().to_string())

    print("\nVERIFICATION COMPLETE")


if __name__ == "__main__":
    main()
