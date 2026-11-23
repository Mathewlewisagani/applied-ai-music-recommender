"""
Core Data Models for VibeCheck 2.0 Applied AI Recommender System.
Maintains backward compatibility with VibeCheck 1.0 whilst introducing
rich feature vectors, session context, and guardrail audit entities.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import math


class ActivityContext(str, Enum):
    WORKOUT = "workout"
    STUDY = "study"
    RELAXATION = "relaxation"
    PARTY = "party"
    COMMUTE = "commute"
    FOCUS = "focus"
    GENERAL = "general"


class GuardrailStatus(str, Enum):
    PASSED = "passed"
    MODIFIED = "modified"
    REJECTED = "rejected"


@dataclass
class Song:
    """
    Rich song representation containing audio features, qualitative descriptors,
    and a normalized numeric vector for semantic/acoustic retrieval.
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
    instrumentalness: float = 0.0
    speechiness: float = 0.0
    key_instruments: str = ""
    listening_context: str = ""
    vibe_description: str = ""

    def to_feature_vector(self) -> List[float]:
        """
        Returns normalized 6-dimensional acoustic vector:
        [energy, tempo/200, valence, danceability, acousticness, instrumentalness]
        """
        norm_tempo = min(1.0, max(0.0, self.tempo_bpm / 200.0))
        return [
            self.energy,
            norm_tempo,
            self.valence,
            self.danceability,
            self.acousticness,
            self.instrumentalness,
        ]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SessionContext:
    """
    Dynamic real-time context describing the user's current situation,
    which dynamically informs ranking and guardrail logic.
    """
    activity: ActivityContext = ActivityContext.GENERAL
    time_of_day: str = "afternoon"  # morning, afternoon, evening, late_night
    diversity_preference: float = 0.3  # 0.0 (strictly similar) to 1.0 (highly adventurous)
    allow_cross_genre_serendipity: bool = True
    session_history_ids: List[int] = field(default_factory=list)


@dataclass
class UserProfile:
    """
    Comprehensive user profile supporting single or multi-genre preferences,
    acoustic tolerance, explicit target energy, and session state.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    secondary_genres: List[str] = field(default_factory=list)
    secondary_moods: List[str] = field(default_factory=list)
    session_context: SessionContext = field(default_factory=SessionContext)
    user_id: str = "anonymous_listener"

    def to_target_vector(self) -> List[float]:
        """
        Constructs expected acoustic profile for vector similarity.
        """
        acoustic_target = 0.85 if self.likes_acoustic else 0.15
        # Default valence derived from mood or neutral 0.5
        valence_target = 0.7 if self.favorite_mood in ["happy", "playful", "uplifting"] else (
            0.25 if self.favorite_mood in ["sad", "melancholic", "angry"] else 0.5
        )
        norm_tempo = min(1.0, max(0.2, self.target_energy * 0.8 + 0.2))
        danceability = 0.8 if self.target_energy > 0.7 else 0.45
        return [
            min(1.0, max(0.0, self.target_energy)),
            norm_tempo,
            valence_target,
            danceability,
            acoustic_target,
            0.2,  # Default neutral instrumentalness
        ]


@dataclass
class RecommendationItem:
    """
    A single recommendation outcome with score breakdown and grounded explanation.
    """
    song: Song
    final_score: float
    retrieval_similarity: float
    score_breakdown: Dict[str, float]
    reasons: List[str]
    grounded_explanation: str
    guardrail_notes: List[str] = field(default_factory=list)

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "id": self.song.id,
            "title": self.song.title,
            "artist": self.song.artist,
            "genre": self.song.genre,
            "mood": self.song.mood,
            "energy": self.song.energy,
            "acousticness": self.song.acousticness,
            "final_score": round(self.final_score, 2),
            "retrieval_similarity": round(self.retrieval_similarity, 3),
            "grounded_explanation": self.grounded_explanation,
            "reasons": self.reasons,
        }


@dataclass
class GuardrailAudit:
    """
    Audit log capturing pre-processing checks, transformations, and verifications.
    """
    status: GuardrailStatus
    original_input: Dict[str, Any]
    sanitized_input: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    modifications: List[str] = field(default_factory=list)
    hallucination_flags: List[str] = field(default_factory=list)
    passed: bool = True
