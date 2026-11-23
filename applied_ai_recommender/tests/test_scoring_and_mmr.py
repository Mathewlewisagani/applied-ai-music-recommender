"""
Unit Tests for Scoring Math and Maximal Marginal Relevance (MMR).
"""

import unittest
from applied_ai_recommender.core.models import Song, UserProfile
from applied_ai_recommender.core.vector_engine import cosine_similarity, VectorEngine
from applied_ai_recommender.core.scoring import score_song_v2, MAX_V2_SCORE
from applied_ai_recommender.core.diversity_reranker import mmr_rerank, compute_intra_song_similarity


class TestScoringAndMMR(unittest.TestCase):
    def setUp(self):
        self.user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False
        )
        self.pop_song = Song(
            id=1, title="Pop One", artist="Artist A", genre="pop", mood="happy",
            energy=0.8, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.1
        )
        self.metal_song = Song(
            id=2, title="Metal Two", artist="Artist B", genre="metal", mood="angry",
            energy=0.95, tempo_bpm=160, valence=0.2, danceability=0.3, acousticness=0.05
        )

    def test_cosine_similarity_bounds(self):
        v1 = [1.0, 0.5, 0.2]
        v2 = [0.8, 0.4, 0.1]
        sim = cosine_similarity(v1, v2)
        self.assertGreaterEqual(sim, -1.0)
        self.assertLessEqual(sim, 1.0)
        self.assertAlmostEqual(cosine_similarity(v1, v1), 1.0)

    def test_score_song_v2_bounds(self):
        score, breakdown, reasons = score_song_v2(self.user, self.pop_song)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, MAX_V2_SCORE)
        self.assertGreater(score, 8.0)  # Near perfect match

        m_score, _, _ = score_song_v2(self.user, self.metal_song)
        self.assertLess(m_score, score)  # Pop matches much better than metal

    def test_mmr_prevents_artist_monopoly(self):
        candidates = [
            (Song(id=1, title="S1", artist="SoloStar", genre="pop", mood="happy", energy=0.8, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.1), 9.0, []),
            (Song(id=2, title="S2", artist="SoloStar", genre="pop", mood="happy", energy=0.8, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.1), 8.8, []),
            (Song(id=3, title="S3", artist="SoloStar", genre="pop", mood="happy", energy=0.8, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.1), 8.5, []),
            (Song(id=4, title="S4", artist="OtherBand", genre="pop", mood="happy", energy=0.79, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.1), 8.2, []),
        ]
        # max_per_artist=2 should cap SoloStar to 2 tracks and include OtherBand
        results = mmr_rerank(candidates, lambda_param=0.5, top_k=3, max_per_artist=2)
        artists = [item[0].artist for item in results]
        self.assertEqual(artists.count("SoloStar"), 2)
        self.assertIn("OtherBand", artists)


if __name__ == "__main__":
    unittest.main()
