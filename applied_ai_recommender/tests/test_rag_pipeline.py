"""
Unit Tests for RAG Explanations and Factual Grounding.
"""

import unittest
from applied_ai_recommender.core.models import Song, UserProfile
from applied_ai_recommender.rag.generator import GroundedRAGGenerator
from applied_ai_recommender.guardrails.hallucination_verifier import HallucinationVerifier


class TestRAGPipeline(unittest.TestCase):
    def setUp(self):
        self.song = Song(
            id=1,
            title="Sunrise City",
            artist="Neon Echo",
            genre="pop",
            mood="happy",
            energy=0.82,
            tempo_bpm=118.0,
            valence=0.84,
            danceability=0.79,
            acousticness=0.18,
            key_instruments="bright synthesizers and punchy kick",
            listening_context="morning commute",
            vibe_description="Gleaming synth pop"
        )
        self.user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False
        )
        self.generator = GroundedRAGGenerator()

    def test_grounded_explanation_generation(self):
        score_breakdown = {"genre": 2.5, "mood": 2.0, "energy": 2.45, "acoustic": 1.4, "vector_sim": 1.3}
        explanation = self.generator.generate_explanation(self.user, self.song, 9.65, score_breakdown)
        
        self.assertIn("pop", explanation.lower())
        self.assertIn("118", explanation)  # Verified BPM
        self.assertIn("Verified Catalog Grounding", explanation)

    def test_hallucination_verifier_detects_false_claim(self):
        # Claiming this pop song is jazz and strictly acoustic
        false_claim = "This jazz track features all acoustic instruments at a slow tempo."
        is_valid, flags, _ = HallucinationVerifier.verify_explanation(self.song, false_claim)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(flags), 0)
        # Should flag genre contradiction
        self.assertTrue(any("contradicts actual genre" in f for f in flags))


if __name__ == "__main__":
    unittest.main()
