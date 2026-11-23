"""
RAG Context Builder.
Constructs factual context representations for candidate songs,
formatting them into structured knowledge blocks for grounded generation.
"""

from typing import List, Dict, Any
from applied_ai_recommender.core.models import Song, UserProfile


class RAGContextBuilder:
    """
    Assembles retrieved factual context from catalog records
    and user session constraints.
    """

    @staticmethod
    def build_song_factsheet(song: Song) -> Dict[str, Any]:
        """Extracts immutable facts about a song."""
        return {
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "tempo_bpm": song.tempo_bpm,
            "energy": song.energy,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "key_instruments": song.key_instruments or "standard production instruments",
            "listening_context": song.listening_context or "general listening",
            "vibe_description": song.vibe_description or f"A {song.mood} {song.genre} track",
        }

    @staticmethod
    def assemble_prompt_context(user: UserProfile, candidates: List[Song]) -> str:
        """
        Creates a structured prompt string that binds candidate facts
        for generation or audit logging.
        """
        lines = [
            "### USER PROFILE CONTEXT ###",
            f"- Favorite Genre: {user.favorite_genre}",
            f"- Favorite Mood: {user.favorite_mood}",
            f"- Target Energy: {user.target_energy:.2f}",
            f"- Likes Acoustic: {user.likes_acoustic}",
            f"- Current Activity: {user.session_context.activity.value}",
            "",
            "### RETRIEVED CATALOG FACTS (GROUND TRUTH) ###",
        ]

        for i, s in enumerate(candidates, start=1):
            lines.append(
                f"Track {i}: '{s.title}' by {s.artist} | Genre: {s.genre} | Mood: {s.mood} | "
                f"Energy: {s.energy:.2f} | BPM: {s.tempo_bpm:.0f} | Acousticness: {s.acousticness:.2f} | "
                f"Instruments: {s.key_instruments} | Context: {s.listening_context}"
            )

        return "\n".join(lines)
