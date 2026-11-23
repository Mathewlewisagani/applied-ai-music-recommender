"""
Unit Tests for VibeCheck 2.0 Core Models.
"""

import unittest
from applied_ai_recommender.core.models import Song, UserProfile, SessionContext, ActivityContext


class TestCoreModels(unittest.TestCase):
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
            instrumentalness=0.02,
            speechiness=0.06,
        )

    def test_feature_vector_dimensions_and_bounds(self):
        vec = self.song.to_feature_vector()
        self.assertEqual(len(vec), 6)
        for val in vec:
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)

    def test_user_target_vector_generation(self):
        user = UserProfile(
            favorite_genre="lofi",
            favorite_mood="chill",
            target_energy=0.35,
            likes_acoustic=True
        )
        target_vec = user.to_target_vector()
        self.assertEqual(len(target_vec), 6)
        self.assertAlmostEqual(target_vec[0], 0.35)
        # Acoustic target should be high since user likes acoustic
        self.assertGreater(target_vec[4], 0.7)


if __name__ == "__main__":
    unittest.main()
