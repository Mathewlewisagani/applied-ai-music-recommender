# 🎵 VibeCheck 2.0: Applied AI Music Recommendation System

> **VibeCheck 2.0** extends the initial prototype into a production-grade, trustworthy, and auditable applied AI recommendation system. It combines **hybrid vector retrieval**, **calibrated multi-objective scoring**, **Maximal Marginal Relevance (MMR) diversity optimization**, **verifiable RAG explanations**, and **two-tier guardrails**.

---

## 🚀 Quick Start & Demo Instructions

The system now features a **user-friendly, non-technical Streamlit interface** designed for everyone!

### Option 1: Friendly Streamlit Web App (Recommended)
Launch the accessible, interactive visual interface:
```bash
python3 demo.py
# or directly:
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser!
- **Zero Technical Jargon**: Uses relatable music concepts (e.g. *"Discovery Dial"*, *"How Energetic Should It Feel"*, *"Acoustic vs Electronic Instruments"*).
- **One-Click Mood Presets**: Quick picks for *"Sunday Morning Coffee"*, *"Workout Power Hour"*, *"Late Night Focus"*, *"Crying in the Club"*, etc.
- **Why You'll Love This**: Plain-English explanations behind why each song was chosen.
- **The Story & Glitch Fix**: An illustrated look at how we fixed Version 1.0's "same salsa song for everyone" glitch.

### Option 2: Run Verification Test Suite
Execute the comprehensive test suite (unit tests for models, scoring, MMR, guardrails, and RAG):
```bash
python3 demo.py --test
```

### Option 3: Quantitative Benchmark
Compare VibeCheck 1.0 vs VibeCheck 2.0 metrics:
```bash
python3 demo.py --benchmark
```

### Option 4: Terminal CLI Mode (Optional)
If you prefer terminal text mode:
```bash
python3 demo.py --cli
```

---

## 📂 Project Organization & Fork Separation

To preserve the starter prototype in its pristine original state, all extensions reside in the standalone `applied_ai_recommender/` package and unified `demo.py` launcher:

```
.
├── src/                               # [ORIGINAL STARTER] Unmodified prototype files
│   ├── main.py                        # Original CLI runner
│   └── recommender.py                 # Original VibeCheck 1.0 scoring
├── tests/                             # [ORIGINAL STARTER] Unmodified prototype tests
│   ├── test_recommender.py
│   └── test_scoring.py
├── data/                              # [ORIGINAL STARTER] 20-song starter catalog
│   └── songs.csv
├── demo.py                            # [V2.0 EXTENSION] Unified launcher (CLI, Web, Benchmark, Test)
└── applied_ai_recommender/            # [V2.0 EXTENSION] Full Applied AI System
    ├── data/
    │   ├── enriched_songs.csv         # 50-song balanced catalog with 15 acoustic attributes
    │   └── songs_loader.py            # Universal schema loader & vectorizer
    ├── core/
    │   ├── models.py                  # Dataclasses: Song, UserProfile, SessionContext
    │   ├── vector_engine.py           # 6D acoustic cosine similarity engine
    │   ├── scoring.py                 # Calibrated multi-objective continuous scoring
    │   └── diversity_reranker.py      # Maximal Marginal Relevance (MMR) re-ranker
    ├── guardrails/
    │   ├── input_sanitizer.py         # Prompt injection & parameter bounds guard
    │   ├── conflict_resolver.py       # Contradiction detection ('Sad but Hyped')
    │   └── hallucination_verifier.py  # Fact-checking against catalog metadata
    ├── rag/
    │   ├── context_builder.py         # Factual prompt context assembler
    │   ├── generator.py               # Grounded RAG explanation generator
    │   └── pipeline.py                # End-to-end workflow orchestrator
    ├── evaluation/
    │   ├── metrics.py                 # ILD, Coverage, Parity, Fiesta Dominance
    │   └── benchmark.py               # Quantitative comparative harness
    ├── ui/
    │   ├── cli.py                     # Rich terminal UI
    │   └── web_server.py              # Zero-dependency HTTP server & web app
    ├── tests/
    │   ├── test_models.py
    │   ├── test_scoring_and_mmr.py
    │   ├── test_guardrails.py
    │   ├── test_rag_pipeline.py
    │   └── run_all_tests.py           # Unified test runner
    ├── ARCHITECTURE_SPEC.md           # Systems & algorithms spec with UML diagrams
    └── MODEL_CARD_V2.md               # Comprehensive Model Card 2.0
```

---

## 🛠️ Instructions to Fork and Extend on GitHub

To publish this extended system to your own GitHub repository:
1. Initialize or check your remote:
   ```bash
   git remote -v
   ```
2. Create and switch to an extended feature branch:
   ```bash
   git checkout -b extended-applied-ai-system
   ```
3. Add and commit all new files:
   ```bash
   git add applied_ai_recommender/ demo.py
   git commit -m "feat: implement VibeCheck 2.0 applied AI recommendation system with RAG, MMR, and guardrails"
   ```
4. Push to your GitHub fork:
   ```bash
   git push -u origin extended-applied-ai-system
   ```
5. Open a Pull Request on GitHub to merge into `main`!

---

## 🔬 What Was Solved, Limitations, and Extensions

### 1. The Problems We Solved:
- **The Energy Filter Bubble**: In VibeCheck 1.0, doubling energy weight caused *Fiesta en la Calle* to show up in 52.9% of user recommendations regardless of genre or mood. VibeCheck 2.0 restored calibrated weights and MMR diversity, dropping dominance to **5.9%**.
- **Acoustic Contradiction Failure**: V1.0 failed on edge cases like "Sad but Hyped" by completely ignoring mood. V2.0 detects contradictions and redirects to cathartic cross-modal tracks (e.g. fast melancholic pop or melodic metal).
- **Vulnerability to Malformed / Adversarial Inputs**: V1.0 allowed out-of-bounds energies (-1.0) and unhandled strings. V2.0 enforces a strict input sanitization tier that clamps bounds and neutralizes injections.
- **Hallucinated Explanations**: V2.0 grounds all generated rationale in catalog facts, verifying BPM, genre, and instruments.

### 2. Limitations:
- **Catalog Breadth**: While expanded from 20 to 50 songs, real-world catalogs span tens of millions of tracks.
- **Collaborative Signals**: Content-based filtering does not model global community listening patterns (e.g., "listeners who liked X also liked Y").
- **Cold-Start Genres**: Unknown out-of-catalog genres (e.g., K-pop) must be approximated via acoustic feature vectors.

### 3. How This System Could Be Extended:
1. **Hybrid Collaborative-Filtering**: Integrate implicit feedback (skips, replays, dwell time) with matrix factorization or graph neural networks (LightGCN).
2. **Real-Time Audio DSP**: Extract spectral centroid, zero-crossing rate, and MFCCs directly from audio files using `librosa`.
3. **Conversational Multi-Turn Agent**: Connect an LLM orchestrator using function-calling tools to refine recommendations dynamically across conversation turns.
