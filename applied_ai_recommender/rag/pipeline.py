"""
End-to-End Applied AI Recommendation & RAG Pipeline.
Orchestrates:
1. Input Sanitization & Boundary Guardrails
2. Preference Conflict Resolution
3. Candidate Retrieval via Vector Engine & Acoustic Features
4. Multi-Objective Scoring
5. Maximal Marginal Relevance (MMR) Diversity Re-Ranking
6. Grounded RAG Explanation Generation with Fact Verification
"""

from typing import List, Dict, Any, Optional
from applied_ai_recommender.core.models import (
    Song, UserProfile, RecommendationItem, GuardrailAudit, SessionContext
)
from applied_ai_recommender.core.vector_engine import VectorEngine
from applied_ai_recommender.core.scoring import score_song_v2
from applied_ai_recommender.core.diversity_reranker import mmr_rerank
from applied_ai_recommender.guardrails.input_sanitizer import sanitize_user_input
from applied_ai_recommender.guardrails.conflict_resolver import resolve_preference_conflicts
from applied_ai_recommender.rag.generator import GroundedRAGGenerator
from applied_ai_recommender.data.songs_loader import load_catalog


class AppliedRecommenderPipeline:
    """
    Production-grade applied AI recommender combining retrieval,
    ranking, diversity re-ranking, guardrails, and RAG explanations.
    """
    def __init__(self, catalog: Optional[List[Song]] = None):
        if catalog is None:
            self.catalog = load_catalog()
        else:
            self.catalog = catalog

        self.vector_engine = VectorEngine(self.catalog)
        self.rag_generator = GroundedRAGGenerator()

    def run_pipeline(
        self,
        raw_user_input: Dict[str, Any],
        top_k: int = 5,
        diversity_lambda: float = 0.7,
        session_activity: str = "general"
    ) -> Dict[str, Any]:
        """
        Executes the full applied AI workflow.
        Returns a dictionary containing:
        - recommendations: List of RecommendationItem
        - guardrail_audit: GuardrailAudit details
        - conflict_resolution: ConflictResolution report
        - catalog_size: int
        """
        # Step 1: Input Guardrail & Sanitization
        sanitized_input, guardrail_audit = sanitize_user_input(raw_user_input)

        # Step 2: Preference Conflict Resolution
        conflict_report = resolve_preference_conflicts(sanitized_input)

        # Step 3: Instantiate UserProfile with session context
        user = UserProfile(
            favorite_genre=sanitized_input["favorite_genre"],
            favorite_mood=sanitized_input["favorite_mood"],
            target_energy=sanitized_input["target_energy"],
            likes_acoustic=sanitized_input["likes_acoustic"],
            secondary_genres=sanitized_input.get("secondary_genres", []),
            secondary_moods=sanitized_input.get("secondary_moods", []),
        )
        try:
            from applied_ai_recommender.core.models import ActivityContext
            user.session_context.activity = ActivityContext(session_activity)
        except (ValueError, TypeError):
            user.session_context.activity = ActivityContext.GENERAL

        # Step 4: Hybrid Retrieval & Scoring
        # Score candidates across catalog
        scored_candidates = []
        for song in self.catalog:
            score, breakdown, reasons = score_song_v2(user, song)
            scored_candidates.append((song, score, reasons, breakdown))

        # Sort by initial multi-objective score descending
        scored_candidates.sort(key=lambda x: (-x[1], x[0].title))

        # Step 5: Maximal Marginal Relevance (MMR) Diversity Re-Ranking
        # Takes top 20 candidates and applies MMR to pick top_k diverse, high-relevance songs
        top_pool = [(cand[0], cand[1], cand[2]) for cand in scored_candidates[:20]]
        mmr_results = mmr_rerank(top_pool, lambda_param=diversity_lambda, top_k=top_k)

        # Step 6: RAG Explanation Generation with Fact Verification
        recommendations: List[RecommendationItem] = []
        for song, final_score, reasons, diversity_penalty in mmr_results:
            # Re-obtain breakdown
            _, breakdown, _ = score_song_v2(user, song)
            sim = self.vector_engine._index.get(song.id)
            vector_sim = 0.8
            if sim:
                from applied_ai_recommender.core.vector_engine import cosine_similarity
                vector_sim = cosine_similarity(user.to_target_vector(), song.to_feature_vector())

            explanation = self.rag_generator.generate_explanation(user, song, final_score, breakdown)
            
            rec_item = RecommendationItem(
                song=song,
                final_score=final_score,
                retrieval_similarity=vector_sim,
                score_breakdown=breakdown,
                reasons=reasons,
                grounded_explanation=explanation,
                guardrail_notes=guardrail_audit.warnings + (
                    [f"Conflict mitigation applied: {conflict_report.strategy}"] if conflict_report.has_conflict else []
                ),
            )
            recommendations.append(rec_item)

        return {
            "recommendations": recommendations,
            "guardrail_audit": guardrail_audit,
            "conflict_report": conflict_report,
            "user_profile": user,
            "catalog_size": len(self.catalog),
        }
