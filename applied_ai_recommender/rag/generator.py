"""
Grounded RAG Explanation Generator.
Produces human-readable, trustworthy explanations synthesizing retrieved facts
with the user's active context, without hallucinating details.
"""

from typing import Dict, Any, List
from applied_ai_recommender.core.models import Song, UserProfile
from applied_ai_recommender.guardrails.hallucination_verifier import HallucinationVerifier


class GroundedRAGGenerator:
    """
    Generates grounded musical explanations using retrieved catalog facts.
    Guarantees transparent, personalized, and hallucination-free rationale.
    """

    def generate_explanation(
        self,
        user: UserProfile,
        song: Song,
        score: float,
        score_breakdown: Dict[str, float]
    ) -> str:
        """
        Synthesizes a personalized rationale combining:
        1. Contextual match (why this fits the user's target energy & mood)
        2. Acoustic sonic details (instruments, tempo, production style)
        3. Factual verification badge
        """
        # Feature comparison narratives
        tempo_desc = "uptempo" if song.tempo_bpm > 120 else ("moderate tempo" if song.tempo_bpm >= 85 else "downtempo")
        
        # Energy narrative
        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff <= 0.1:
            energy_desc = f"hits your exact energy target ({song.energy:.2f} vs {user.target_energy:.2f})"
        elif song.energy > user.target_energy:
            energy_desc = f"gives a slightly elevated energy boost ({song.energy:.2f} vs {user.target_energy:.2f})"
        else:
            energy_desc = f"delivers a slightly more laid-back pace ({song.energy:.2f} vs {user.target_energy:.2f})"

        # Mood & Genre connection
        if song.genre == user.favorite_genre and song.mood == user.favorite_mood:
            connection = f"Matches both your favorite genre ({song.genre}) and desired mood ({song.mood})."
        elif song.genre == user.favorite_genre:
            connection = f"Anchored in your favorite genre ({song.genre}) with a complementary {song.mood} atmosphere."
        elif song.mood == user.favorite_mood:
            connection = f"Crosses into {song.genre} to bring you your favorite {song.mood} vibe."
        else:
            connection = f"A serendipitous {song.genre} discovery chosen for its strong acoustic harmony."

        # Instrumentation fact
        instrument_phrase = ""
        if song.key_instruments:
            instrument_phrase = f" Features {song.key_instruments}."

        act = user.session_context.activity
        activity_str = act.value if hasattr(act, "value") else str(act)
        context_phrase = f" Tailored for your {activity_str} session." if activity_str not in ["general", "ActivityContext.GENERAL"] else ""

        draft_text = (
            f"{connection} This {tempo_desc} track ({song.tempo_bpm:.0f} BPM) {energy_desc}.{instrument_phrase}{context_phrase}"
        )

        # Pass through Hallucination Verifier
        is_valid, flags, verified_text = HallucinationVerifier.verify_explanation(song, draft_text)
        return verified_text
