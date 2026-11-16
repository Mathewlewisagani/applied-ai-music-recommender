"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


# Test users. Each profile uses the same fields as the UserProfile class:
# favorite_genre, favorite_mood, target_energy (0 to 1), likes_acoustic.
USER_PROFILES = {
    "Happy Pop Fan": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    },
    "Chill Studier": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
    "Gym Goer": {
        "favorite_genre": "edm",
        "favorite_mood": "energetic",
        "target_energy": 0.95,
        "likes_acoustic": False,
    },
    "Headbanger": {
        "favorite_genre": "metal",
        "favorite_mood": "angry",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "Classical Listener": {
        "favorite_genre": "classical",
        "favorite_mood": "peaceful",
        "target_energy": 0.2,
        "likes_acoustic": True,
    },
    "Sad Folk Fan": {
        "favorite_genre": "folk",
        "favorite_mood": "sad",
        "target_energy": 0.25,
        "likes_acoustic": True,
    },
    "Late Night R&B": {
        "favorite_genre": "r&b",
        "favorite_mood": "romantic",
        "target_energy": 0.5,
        "likes_acoustic": False,
    },
    "Hip Hop Head": {
        "favorite_genre": "hip hop",
        "favorite_mood": "confident",
        "target_energy": 0.75,
        "likes_acoustic": False,
    },
    "Country Roads": {
        "favorite_genre": "country",
        "favorite_mood": "nostalgic",
        "target_energy": 0.5,
        "likes_acoustic": True,
    },
    "Party Starter": {
        "favorite_genre": "latin",
        "favorite_mood": "playful",
        "target_energy": 0.85,
        "likes_acoustic": False,
    },
    # Edge case: preferences that conflict (metal is loud, but wants peaceful and low energy)
    "Conflicted Listener": {
        "favorite_genre": "metal",
        "favorite_mood": "peaceful",
        "target_energy": 0.2,
        "likes_acoustic": True,
    },
}


def main() -> None:
    songs = load_songs("../data/songs.csv")

    for name, user_prefs in USER_PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Print one user's profile and their top songs with scores and reasons."""
    acoustic = "yes" if user_prefs["likes_acoustic"] else "no"

    print()
    print("=" * 60)
    print(f" {name}")
    print(
        f" genre: {user_prefs['favorite_genre']} | mood: {user_prefs['favorite_mood']}"
        f" | energy: {user_prefs['target_energy']:.2f} | acoustic: {acoustic}"
    )
    print("=" * 60)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n {rank}. {song['title']} ({song['artist']})")
        print(f"    Score: {score:.2f} / 6.00")
        print("    Reasons:")
        # explanation is the reasons from score_song joined by ", "
        for reason in explanation.split(", "):
            print(f"      - {reason}")


if __name__ == "__main__":
    main()
