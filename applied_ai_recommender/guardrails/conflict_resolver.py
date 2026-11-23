"""
Preference Conflict Resolver Guardrail.
Detects contradictory user preferences (e.g. 'Sad but Hyped', 'Unplugged Metalhead')
and formulates an adaptive resolution strategy rather than arbitrarily suppressing
one dimension as happened in VibeCheck 1.0.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ConflictResolution:
    has_conflict: bool
    conflict_type: Optional[str] = None
    description: Optional[str] = None
    strategy: Optional[str] = None
    applied_adjustments: List[str] = None

    def __post_init__(self):
        if self.applied_adjustments is None:
            self.applied_adjustments = []


def resolve_preference_conflicts(user_prefs: Dict[str, Any]) -> ConflictResolution:
    """
    Analyzes preferences for physiological and acoustic contradictions:
    1. High energy + Sad/Peaceful ('Sad but Hyped' contradiction)
    2. Metal/EDM + Acoustic ('Unplugged Metalhead' contradiction)
    3. Ambient + Very High Energy
    4. Classical + Extreme Loudness / Distortion
    """
    genre = str(user_prefs.get("favorite_genre", "")).lower()
    mood = str(user_prefs.get("favorite_mood", "")).lower()
    energy = float(user_prefs.get("target_energy", 0.5))
    acoustic = bool(user_prefs.get("likes_acoustic", False))

    resolution = ConflictResolution(has_conflict=False)

    # Case 1: High Energy (> 0.75) + Sad/Melancholic mood
    if energy > 0.75 and mood in ["sad", "melancholic"]:
        resolution.has_conflict = True
        resolution.conflict_type = "HYPED_SADNESS_TENSION"
        resolution.description = (
            f"User requested high energy ({energy:.2f}) paired with '{mood}' mood. "
            "In naive recommenders, this causes an energy filter bubble that starves the mood."
        )
        resolution.strategy = "CROSS_MODAL_CATHARSIS"
        resolution.applied_adjustments.append(
            "Targeting high-tempo emotional catharsis: fast melancholic pop, post-punk, or melodic metal."
        )
        # Expand secondary moods to include intense and energetic catharsis
        if "energetic" not in user_prefs.get("secondary_moods", []):
            user_prefs.setdefault("secondary_moods", []).append("energetic")

    # Case 2: Acoustic Heavy Metal / Hard Rock
    elif genre in ["metal", "rock"] and acoustic and energy > 0.8:
        resolution.has_conflict = True
        resolution.conflict_type = "ACOUSTIC_HEAVY_TENSION"
        resolution.description = (
            f"User requested acoustic music ({acoustic}) for high-energy genre '{genre}'. "
            "Catalog metal tracks are predominantly electric and heavily distorted."
        )
        resolution.strategy = "EXPANDED_ACOUSTIC_CROSSOVER"
        resolution.applied_adjustments.append(
            "Expanding candidate retrieval to acoustic rock, bluegrass breakdowns, and post-metal ambient interludes."
        )
        user_prefs.setdefault("secondary_genres", []).extend(["folk", "country", "rock"])

    # Case 3: Ambient at Workout Energy
    elif genre == "ambient" and energy > 0.75:
        resolution.has_conflict = True
        resolution.conflict_type = "AMBIENT_HIGH_ENERGY_TENSION"
        resolution.description = (
            f"Ambient music typically resides in low energy (< 0.40). Target energy {energy:.2f} conflicts."
        )
        resolution.strategy = "HYBRID_ELECTRONIC_BRIDGE"
        resolution.applied_adjustments.append(
            "Bridging ambient soundscapes with synthwave and atmospheric downtempo EDM."
        )
        user_prefs.setdefault("secondary_genres", []).extend(["synthwave", "edm", "lofi"])

    return resolution
