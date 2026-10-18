
from itertools import combinations

import numpy as np

from src.recommender import SongRecommender


SEEDS = [
    ("Radiohead", "Creep"),
    ("Arctic Monkeys", "Do I Wanna Know"),
    ("The Beatles", "Come Together"),
    ("Linkin Park", "Numb"),
    ("Billie Eilish", "bad guy"),
    ("The Weeknd", "Blinding Lights"),
    ("Nirvana", "Smells Like Teen Spirit"),
    ("Daft Punk", "Get Lucky"),
    ("Adele", "Rolling in the Deep"),
    ("Pink Floyd", "Wish You Were Here"),
]

METHODS = ["audio_cosine", "hybrid", "genre_filtered"]
TOP_N = 5


def normalize_text(value):
    return str(value).strip().casefold()


def normalize_genres(value):
    """Convert a genre field into a normalized set of labels."""
    if isinstance(value, (list, tuple, set, np.ndarray)):
        values = value
    elif isinstance(value, str):
        values = [value]
    else:
        values = []

    return {
        normalize_text(item)
        for item in values
        if str(item).strip()
    }


def normalize_artists(value):
    """Split semicolon-separated artist credits into individual names."""
    if isinstance(value, (list, tuple, set, np.ndarray)):
        values = value
    elif isinstance(value, str):
        values = value.split(";")
    else:
        values = []

    return {
        normalize_text(item)
        for item in values
        if str(item).strip()
    }


def find_seed(recommender, artist, title):
    songs = recommender.songs

    title_matches = songs["track_name"].str.casefold().str.contains(
        title.casefold(), regex=False
    )
    artist_matches = songs["artists"].str.casefold().str.contains(
        artist.casefold(), regex=False
    )

    candidates = songs.loc[title_matches & artist_matches].copy()

    if candidates.empty:
        return None

    # Choose the most popular matching version for reproducibility.
    return int(candidates["popularity"].idxmax())


def calculate_metrics(seed, recommendations):
    """Calculate descriptive metrics for one recommendation list."""
    seed_artists = normalize_artists(seed["artists"])
    seed_genres = normalize_genres(seed["track_genre"])

    artist_overlap_count = 0
    genre_overlap_count = 0
    genre_jaccard_scores = []

    seen_pairs = set()
    duplicate_count = 0

    for _, row in recommendations.iterrows():
        candidate_artists = normalize_artists(row["artists"])
        candidate_genres = normalize_genres(row["track_genre"])

        if seed_artists & candidate_artists:
            artist_overlap_count += 1

        if seed_genres & candidate_genres:
            genre_overlap_count += 1

        union = seed_genres | candidate_genres
        if union:
            genre_jaccard_scores.append(
                len(seed_genres & candidate_genres) / len(union)
            )

        pair = (
            normalize_text(row["track_name"]),
            normalize_text(row["artists"]),
        )

        if pair in seen_pairs:
            duplicate_count += 1
        seen_pairs.add(pair)

    count = len(recommendations)

    return {
        "count": count,
        "same_artist_rate": (
            artist_overlap_count / count if count else 0.0
        ),
        "shared_genre_rate": (
            genre_overlap_count / count if count else 0.0
        ),
        "mean_genre_jaccard": (
            float(np.mean(genre_jaccard_scores))
            if genre_jaccard_scores
            else 0.0
        ),
        "duplicates": duplicate_count,
    }


def recommendation_ids(recommendations):
    """Return track IDs for comparing recommendation lists."""
    return set(recommendations["track_id"].astype(str))


def main():
    recommender = SongRecommender()

    method_metrics = {method: [] for method in METHODS}
    method_results = {method: {} for method in METHODS}

    found = 0
    seed_count = len(SEEDS)

    for artist, title in SEEDS:
        index = find_seed(recommender, artist, title)

        if index is None:
            print(f"\nSKIPPED: {artist} — {title} (not found)")
            continue

        found += 1
        seed = recommender.get_song(index)

        print("\n" + "=" * 95)
        print(f"SEED: {seed['track_name']} — {seed['artists']}")
        print(f"Popularity: {seed['popularity']}")

        for method in METHODS:
            recommendations = recommender.recommend_songs(
                index,
                top_n=TOP_N,
                method=method,
                exclude_same_artist=False,
            )

            metrics = calculate_metrics(seed, recommendations)
            method_metrics[method].append(metrics)
            method_results[method][(artist, title)] = recommendations

            print(f"\n{method.upper()} TOP {TOP_N}")

            if recommendations.empty:
                print("No recommendations returned.")
                continue

            for rank, (_, row) in enumerate(
                recommendations.iterrows(), start=1
            ):
                print(
                    f"{rank}. {row['track_name']} — {row['artists']} "
                    f"| score={row['recommendation_score']:.3f} "
                    f"| popularity={row['popularity']:.0f}"
                )

            print(
                "Metrics: "
                f"same-artist={metrics['same_artist_rate']:.0%}, "
                f"shared-genre={metrics['shared_genre_rate']:.0%}, "
                f"mean-genre-Jaccard={metrics['mean_genre_jaccard']:.3f}, "
                f"duplicates={metrics['duplicates']}"
            )

        # Compare the recommendation lists for this seed.
        print("\nTOP-FIVE OVERLAP")

        for method_a, method_b in combinations(METHODS, 2):
            key = (artist, title)

            results_a = method_results[method_a][key]
            results_b = method_results[method_b][key]

            ids_a = recommendation_ids(results_a)
            ids_b = recommendation_ids(results_b)
            overlap = len(ids_a & ids_b)

            print(
                f"{method_a} vs {method_b}: "
                f"{overlap}/{TOP_N} shared track IDs"
            )

    print("\n" + "=" * 95)
    print("AGGREGATE SUMMARY")
    print(f"Seed tracks found: {found}/{seed_count}")

    for method in METHODS:
        metrics_list = method_metrics[method]

        if not metrics_list:
            continue

        print(f"\n{method.upper()}")

        print(
            "Average same-artist rate: "
            f"{np.mean([m['same_artist_rate'] for m in metrics_list]):.1%}"
        )
        print(
            "Average shared-genre rate: "
            f"{np.mean([m['shared_genre_rate'] for m in metrics_list]):.1%}"
        )
        print(
            "Average genre Jaccard: "
            f"{np.mean([m['mean_genre_jaccard'] for m in metrics_list]):.3f}"
        )
        print(
            "Total duplicate entries: "
            f"{sum(m['duplicates'] for m in metrics_list)}"
        )

    print("\nINTERPRETATION NOTES")
    print("- Same-artist rate measures artist-credit overlap, not relevance.")
    print("- Shared-genre rate measures dataset-label overlap, not relevance.")
    print("- Genre Jaccard measures genre-set overlap.")
    print("- List overlap measures agreement between methods.")
    print("- These metrics do not establish listener satisfaction.")
    print("- Manually review the actual song lists before choosing a model.")


if __name__ == "__main__":
    main()
