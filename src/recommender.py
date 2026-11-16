import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# ---------------------------------------------------------------------------
# Scoring weights
#
# EXPERIMENT (Step 3 "Weight Shift"): energy importance doubled, genre halved.
#   Baseline weights were: genre 2.0, mood 1.0, energy 2.0, acoustic 1.0 (max 6.0)
#   Experiment weights:    genre 1.0, mood 1.0, energy 4.0, acoustic 1.0 (max 7.0)
# To go back to the baseline, set GENRE_WEIGHT = 2.0 and ENERGY_WEIGHT = 2.0.
# ---------------------------------------------------------------------------
GENRE_WEIGHT = 1.0     # was 2.0 (halved)
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 4.0    # was 2.0 (doubled)
ACOUSTIC_WEIGHT = 1.0

# Highest score a song can get: every check matched and energy is exact.
MAX_SCORE = GENRE_WEIGHT + MOOD_WEIGHT + ENERGY_WEIGHT + ACOUSTIC_WEIGHT

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
        """Return the top k Song objects for this user, using score_song."""
        prefs = asdict(user)
        ranked = sorted(
            self.songs,
            key=lambda song: (-score_song(prefs, asdict(song))[0], song.title),
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return the scoring reasons for one song as a single string."""
        score, reasons = score_song(asdict(user), asdict(song))
        return f"Score {score:.2f} / {MAX_SCORE:.2f}: " + ", ".join(reasons)

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

    # Genre match: +GENRE_WEIGHT
    if song["genre"] == user_prefs["favorite_genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.1f})")

    # Mood match: +MOOD_WEIGHT
    if song["mood"] == user_prefs["favorite_mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.1f})")

    # Energy closeness: 0 to +ENERGY_WEIGHT (closer to the target scores higher).
    # closeness is clamped to [0, 1] so an out-of-range target (e.g. -1.0)
    # can never produce negative points or push the score outside 0..MAX_SCORE.
    gap = abs(song["energy"] - user_prefs["target_energy"])
    closeness = max(0.0, 1.0 - gap)
    energy_points = ENERGY_WEIGHT * closeness
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{energy_points:.2f})"
    )

    # Acoustic match: +ACOUSTIC_WEIGHT
    if user_prefs["likes_acoustic"] and song["acousticness"] > 0.6:
        score += ACOUSTIC_WEIGHT
        reasons.append(f"acoustic sound: {song['acousticness']:.2f} (+{ACOUSTIC_WEIGHT:.1f})")
    elif not user_prefs["likes_acoustic"] and song["acousticness"] < 0.4:
        score += ACOUSTIC_WEIGHT
        reasons.append(f"non-acoustic sound: {song['acousticness']:.2f} (+{ACOUSTIC_WEIGHT:.1f})")

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
