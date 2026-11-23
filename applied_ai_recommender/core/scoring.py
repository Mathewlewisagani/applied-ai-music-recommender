"""
Multi-Objective Scoring Engine for VibeCheck 2.0.
Addresses the severe "energy filter bubble" flaw identified in VibeCheck 1.0
by restoring balanced feature weights, continuous acoustic scaling,
and multi-dimensional similarity blending.
"""

from typing import Dict, List, Tuple
from applied_ai_recommender.core.models import Song, UserProfile
from applied_ai_recommender.core.vector_engine import cosine_similarity


# Calibrated VibeCheck 2.0 Scoring Weights (Total Max = 10.0)
WEIGHT_GENRE = 2.5
WEIGHT_MOOD = 2.0
WEIGHT_ENERGY = 2.5
WEIGHT_ACOUSTIC = 1.5
WEIGHT_VECTOR_SIM = 1.5

MAX_V2_SCORE = WEIGHT_GENRE + WEIGHT_MOOD + WEIGHT_ENERGY + WEIGHT_ACOUSTIC + WEIGHT_VECTOR_SIM


def score_song_v2(user: UserProfile, song: Song) -> Tuple[float, Dict[str, float], List[str]]:
    """
    Computes a balanced, continuous score for a song against a user profile.
    Returns:
        final_score: float in [0.0, 10.0]
        breakdown: dict mapping feature name to awarded points
        reasons: list of auditable explanation strings
    """
    score = 0.0
    breakdown: Dict[str, float] = {}
    reasons: List[str] = []

    # 1. Genre Affinity (Primary match or Secondary match)
    user_genre = user.favorite_genre.lower().strip()
    song_genre = song.genre.lower().strip()
    if song_genre == user_genre:
        pts = WEIGHT_GENRE
        breakdown["genre"] = pts
        reasons.append(f"Direct genre match: '{song.genre}' (+{pts:.2f})")
    elif song_genre in [g.lower().strip() for g in user.secondary_genres]:
        pts = WEIGHT_GENRE * 0.6  # Partial credit for secondary taste
        breakdown["genre"] = pts
        reasons.append(f"Secondary genre match: '{song.genre}' (+{pts:.2f})")
    else:
        breakdown["genre"] = 0.0

    # 2. Mood Alignment (Primary or Secondary mood)
    user_mood = user.favorite_mood.lower().strip()
    song_mood = song.mood.lower().strip()
    if song_mood == user_mood:
        pts = WEIGHT_MOOD
        breakdown["mood"] = pts
        reasons.append(f"Direct mood match: '{song.mood}' (+{pts:.2f})")
    elif song_mood in [m.lower().strip() for m in user.secondary_moods]:
        pts = WEIGHT_MOOD * 0.5
        breakdown["mood"] = pts
        reasons.append(f"Secondary mood match: '{song.mood}' (+{pts:.2f})")
    else:
        breakdown["mood"] = 0.0

    # 3. Energy Closeness (Smooth continuous decay: 1 - |gap|)
    # Clamped to [0.0, 1.0] so no negative scores occur
    target_energy = min(1.0, max(0.0, user.target_energy))
    energy_gap = abs(song.energy - target_energy)
    closeness = max(0.0, 1.0 - energy_gap)
    pts = WEIGHT_ENERGY * closeness
    breakdown["energy"] = pts
    reasons.append(
        f"Energy alignment: song {song.energy:.2f} vs target {target_energy:.2f} (gap {energy_gap:.2f}) (+{pts:.2f})"
    )

    # 4. Continuous Acousticness Alignment
    # Instead of brittle step-function (>0.6 vs <0.4), evaluate distance to acoustic preference
    target_acoustic = 0.85 if user.likes_acoustic else 0.15
    acoustic_gap = abs(song.acousticness - target_acoustic)
    acoustic_match = max(0.0, 1.0 - acoustic_gap)
    pts = WEIGHT_ACOUSTIC * acoustic_match
    breakdown["acoustic"] = pts
    acoustic_desc = "acoustic" if user.likes_acoustic else "electronic/produced"
    reasons.append(
        f"Acoustic fit for {acoustic_desc} preference: song is {song.acousticness:.2f} (+{pts:.2f})"
    )

    # 5. Multi-dimensional Vector Cosine Similarity
    user_vec = user.to_target_vector()
    song_vec = song.to_feature_vector()
    sim = cosine_similarity(user_vec, song_vec)
    # Map [-1, 1] cosine similarity to non-negative [0, 1] scale
    normalized_sim = max(0.0, (sim + 1.0) / 2.0)
    pts = WEIGHT_VECTOR_SIM * normalized_sim
    breakdown["vector_sim"] = pts
    reasons.append(f"Acoustic vector similarity: {sim:.3f} (+{pts:.2f})")

    total_score = sum(breakdown.values())
    return round(total_score, 3), breakdown, reasons
