import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return each row as a dict with numeric fields converted."""
    print(f"Loading songs from {csv_path}...")

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # CSV values are read as text, so convert the number columns
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })

    print(f"Loaded {len(songs)} songs.")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against a user's preferences and return (score, reasons)."""
    score = 0.0
    reasons = []

    # Genre match: +2.0 (strongest taste signal)
    if song["genre"] == user_prefs["favorite_genre"]:
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    # Mood match: +1.0
    if song["mood"] == user_prefs["favorite_mood"]:
        score += 1.0
        reasons.append(f"mood match: {song['mood']} (+1.0)")

    # Energy closeness: 0 to +2.0 (closer to the target scores higher)
    energy_points = 2.0 * (1 - abs(song["energy"] - user_prefs["target_energy"]))
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{energy_points:.2f})"
    )

    # Acoustic match: +1.0
    if user_prefs["likes_acoustic"] and song["acousticness"] > 0.6:
        score += 1.0
        reasons.append(f"acoustic sound: {song['acousticness']:.2f} (+1.0)")
    elif not user_prefs["likes_acoustic"] and song["acousticness"] < 0.4:
        score += 1.0
        reasons.append(f"non-acoustic sound: {song['acousticness']:.2f} (+1.0)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort high to low (ties by title), and return the top k."""
    # 1. Score every song
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))

    # 2. Rank: highest score first, ties broken alphabetically by title
    scored.sort(key=lambda item: (-item[1], item[0]["title"]))

    # 3. Return the top k
    return scored[:k]
