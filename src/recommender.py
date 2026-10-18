
from pathlib import Path
import re

import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler


DATA_PATH = Path("data/processed/spotify_tracks.parquet")

AUDIO_FEATURES = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "duration_ms",
    "key",
    "mode",
    "time_signature",
]

DEFAULT_WEIGHTS = {
    "audio": 0.82,
    "genre": 0.15,
    "popularity": 0.03,
}

# Common edition labels that should not make the seed song
# reappear as a recommendation.
EDITION_SUFFIXES = [
    r"\s*-\s*remastered(?:\s+\d{4})?$",
    r"\s*\(remastered(?:\s+\d{4})?\)$",
    r"\s*-\s*radio edit$",
    r"\s*\(radio edit\)$",
    r"\s*-\s*single edit$",
    r"\s*\(single edit\)$",
    r"\s*-\s*remaster$",
    r"\s*\(remaster\)$",
]


class SongRecommender:
    """Content-based music recommender with hybrid ranking."""

    def __init__(self, data_path=DATA_PATH):
        data_path = Path(data_path)

        if not data_path.exists():
            raise FileNotFoundError(
                f"Processed catalogue not found: {data_path.resolve()}"
            )

        print("Loading processed Spotify catalogue...")
        songs = pd.read_parquet(data_path)

        required = {
            "track_id",
            "artists",
            "track_name",
            "popularity",
            "track_genre",
            *AUDIO_FEATURES,
        }
        missing = required - set(songs.columns)

        if missing:
            raise ValueError(
                f"Dataset is missing columns: {sorted(missing)}"
            )

        for column in AUDIO_FEATURES + ["popularity"]:
            songs[column] = pd.to_numeric(
                songs[column], errors="coerce"
            )

        valid = (
            songs["track_id"].notna()
            & songs["track_id"].astype(str).str.strip().ne("")
            & songs["artists"].fillna("").astype(str).str.strip().ne("")
            & songs["track_name"].fillna("").astype(str).str.strip().ne("")
            & songs[AUDIO_FEATURES].notna().all(axis=1)
            & songs["popularity"].notna()
        )

        self.songs = songs.loc[valid].reset_index(drop=True)

        if self.songs["track_id"].duplicated().any():
            raise ValueError("Catalogue contains duplicate track IDs.")

        self.songs["track_name"] = (
            self.songs["track_name"].astype(str).str.strip()
        )
        self.songs["artists"] = (
            self.songs["artists"].astype(str).str.strip()
        )

        self.genre_sets = [
            self._normalise_genres(value)
            for value in self.songs["track_genre"]
        ]

        print("Standardizing audio features...")
        self.scaler = StandardScaler()
        self.standardized_audio = self.scaler.fit_transform(
            self.songs[AUDIO_FEATURES].to_numpy(dtype=np.float32)
        )

        # Cosine similarity is useful as a ranking signal, but its
        # transformed score is not a probability of musical similarity.
        norms = np.linalg.norm(
            self.standardized_audio, axis=1, keepdims=True
        )
        norms[norms == 0] = 1.0
        self.cosine_audio = self.standardized_audio / norms

        self.popularity = (
            self.songs["popularity"].to_numpy(dtype=np.float32) / 100.0
        )

        self.normalized_titles = (
            self.songs["track_name"].map(self._normalise_text).to_numpy()
        )
        self.canonical_titles = (
            self.songs["track_name"].map(self._canonical_title).to_numpy()
        )
        self.normalized_artists = (
            self.songs["artists"].map(self._normalise_text).to_numpy()
        )

        print(f"Ready: {len(self.songs):,} tracks")
        print(f"Audio features: {len(AUDIO_FEATURES)}")
        print("Recommendation engine initialized.")

    @staticmethod
    def _normalise_text(value):
        return str(value).strip().casefold()

    @classmethod
    def _canonical_title(cls, value):
        title = cls._normalise_text(value)

        # Repeatedly remove known edition suffixes.
        changed = True
        while changed:
            changed = False
            for pattern in EDITION_SUFFIXES:
                cleaned = re.sub(pattern, "", title).strip()
                if cleaned != title:
                    title = cleaned
                    changed = True

        # Ignore punctuation differences for comparison.
        title = re.sub(r"[^\w\s]", " ", title)
        return " ".join(title.split())

    @staticmethod
    def _normalise_genres(value):
        if isinstance(value, (list, tuple, set, np.ndarray)):
            values = value
        elif isinstance(value, str):
            values = [value]
        else:
            values = []

        return {
            str(item).strip().casefold()
            for item in values
            if str(item).strip()
        }

    def search_songs(self, query, limit=20):
        if limit < 1:
            raise ValueError("limit must be at least 1.")

        query = self._normalise_text(query)

        if not query:
            return self.songs.iloc[0:0].copy()

        title = self.songs["track_name"].str.casefold()
        artist = self.songs["artists"].str.casefold()

        matches = (
            title.str.contains(query, regex=False)
            | artist.str.contains(query, regex=False)
        )
        return self.songs.loc[matches].head(limit)

    def get_song(self, song_index):
        if not isinstance(song_index, (int, np.integer)):
            raise TypeError("song_index must be an integer.")

        if not 0 <= song_index < len(self.songs):
            raise IndexError("song_index is outside the catalogue.")

        return self.songs.iloc[int(song_index)]

    def _audio_scores(self, song_index, method):
        if method == "audio_cosine":
            cosine_scores = (
                self.cosine_audio @ self.cosine_audio[song_index]
            )
            # Preserve the cosine ranking while keeping scores bounded.
            return np.clip(cosine_scores, -1.0, 1.0)

        if method == "audio_euclidean":
            distances = euclidean_distances(
                self.standardized_audio[
                    song_index:song_index + 1
                ],
                self.standardized_audio,
            ).ravel()

            return np.exp(
                -distances / np.sqrt(len(AUDIO_FEATURES))
            )

        raise ValueError(f"Unsupported audio method: {method}")

    def _genre_scores(self, song_index):
        source_genres = self.genre_sets[song_index]
        scores = np.zeros(len(self.songs), dtype=np.float32)

        if not source_genres:
            return scores

        for index, candidate_genres in enumerate(self.genre_sets):
            union = source_genres | candidate_genres

            if union:
                scores[index] = (
                    len(source_genres & candidate_genres) / len(union)
                )

        return scores

    def recommend_songs(
        self,
        song_index,
        top_n=10,
        method="hybrid",
        exclude_same_artist=False,
    ):
        if not isinstance(song_index, (int, np.integer)):
            raise TypeError("song_index must be an integer.")

        if not 0 <= song_index < len(self.songs):
            raise IndexError("song_index is outside the catalogue.")

        if top_n < 1:
            raise ValueError("top_n must be at least 1.")

        valid_methods = {
            "hybrid",
            "audio_cosine",
            "audio_euclidean",
            "genre_filtered",
        }
        if method not in valid_methods:
            raise ValueError(
                f"method must be one of {sorted(valid_methods)}"
            )

        source_index = int(song_index)
        source_title = self.canonical_titles[source_index]
        source_artist = self.normalized_artists[source_index]
        source_genres = self.genre_sets[source_index]

        audio_method = (
            "audio_euclidean"
            if method == "audio_euclidean"
            else "audio_cosine"
        )
        audio_scores = self._audio_scores(
            source_index, audio_method
        )
        genre_scores = self._genre_scores(source_index)

        if method == "hybrid":
            # Cosine is now on its native [-1, 1] scale.
            # Map it to [0, 1] before combining the components.
            normalized_audio = np.clip(
                (audio_scores + 1.0) / 2.0, 0.0, 1.0
            )
            scores = (
                DEFAULT_WEIGHTS["audio"] * normalized_audio
                + DEFAULT_WEIGHTS["genre"] * genre_scores
                + DEFAULT_WEIGHTS["popularity"] * self.popularity
            )
        else:
            scores = audio_scores.copy()

        results = self.songs[
            [
                "track_id",
                "track_name",
                "artists",
                "album_name",
                "popularity",
                "track_genre",
            ]
        ].copy()

        results["catalogue_index"] = np.arange(len(results))
        results["audio_similarity"] = audio_scores
        results["genre_similarity"] = genre_scores
        results["popularity_score"] = self.popularity
        results["recommendation_score"] = scores

        candidate_indices = results["catalogue_index"].to_numpy()

        # Exclude the seed and common alternate editions of that song.
        same_title = (
            self.canonical_titles[candidate_indices] == source_title
        )
        same_artist = (
            self.normalized_artists[candidate_indices] == source_artist
        )

        results = results.loc[
            (candidate_indices != source_index)
            & ~(same_title & same_artist)
        ].copy()

        if exclude_same_artist:
            candidate_indices = results["catalogue_index"].to_numpy()
            results = results.loc[
                self.normalized_artists[candidate_indices] != source_artist
            ].copy()

        # Restrict the candidate pool to songs sharing a genre.
        if method == "genre_filtered":
            if not source_genres:
                raise ValueError(
                    "The selected song has no genre labels; "
                    "genre-filtered recommendations are unavailable."
                )

            candidate_indices = results["catalogue_index"].to_numpy()
            shares_genre = np.array([
                bool(source_genres & self.genre_sets[int(index)])
                for index in candidate_indices
            ])
            results = results.loc[shares_genre].copy()

        results["_normalized_title"] = results["track_name"].map(
            self._canonical_title
        )
        results["_normalized_artist"] = results["artists"].map(
            self._normalise_text
        )

        results = results.sort_values(
            "recommendation_score",
            ascending=False,
            kind="stable",
        )

        results = results.drop_duplicates(
            subset=["_normalized_title", "_normalized_artist"],
            keep="first",
        )

        return (
            results.head(top_n)
            .drop(columns=["_normalized_title", "_normalized_artist"])
            .reset_index(drop=True)
        )
