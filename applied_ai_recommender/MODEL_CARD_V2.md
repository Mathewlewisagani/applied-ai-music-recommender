# 🎧 Model Card: VibeCheck 2.0 (Applied AI Music Recommender)

## 1. Model Name & Version
**VibeCheck 2.0 (Production-Grade Applied AI Edition)**  
A hybrid content-vector music recommendation system featuring Maximal Marginal Relevance (MMR) diversity optimization, multi-tier guardrails, and grounded Retrieval-Augmented Generation (RAG) explanations.

---

## 2. Intended Use & Target Audience
- **Primary Task**: Deliver personalized, acoustic-aware music recommendations from an enriched audio catalog, accompanied by verifiable, transparent explanations.
- **Intended Users**: Music listeners seeking mood-based listening sessions, workout playlists, study focus audio, and serendipitous discovery across genres.
- **Out of Scope**:
  - Guessing clinical emotional states or psychological diagnoses from listening habits.
  - Commercial licensing arbitration or artist royalty management.
  - Fully uncurated open-web music scraping without metadata verification.

---

## 3. Data Literacy & Structural Patterns

### 3.1 Catalog Composition & Feature Distribution
The VibeCheck 2.0 catalog (`enriched_songs.csv`) contains **50 curated tracks** across 17 genres and 16 moods, representing a 2.5x expansion over VibeCheck 1.0 (20 tracks).

| Feature Dimension | VibeCheck 1.0 (Starter Prototype) | VibeCheck 2.0 (Applied AI System) | Impact on Model Behavior |
|---|---|---|---|
| **Catalog Size** | 20 songs | 50 songs | Reduces sparsity; provides multiple candidate tracks per genre. |
| **Genre Distribution** | 15 of 17 genres had only **1 song** | Every major genre has 3–5 representative tracks | Eliminates single-song bottleneck; allows multi-song diversity. |
| **Energy Distribution** | Severe bimodal split: 9 high (>0.7), 8 low (<0.45), only 3 mid-range | Continuous uniform distribution: 16 low (<0.4), 18 mid (0.4–0.7), 16 high (>0.7) | Mid-energy listeners no longer get forced into extreme loud or extreme quiet tracks. |
| **Mood-Energy Coupling** | Stereotyped: all sad songs quiet (<0.3); all high-energy songs happy/angry | De-coupled: includes high-energy melancholia (*Crying in the Strobe*, *Battle Cry of the Fallen*) and calm intense ambience (*Subterranean Echo*) | Enables cross-modal recommendations for complex affective states. |
| **Acoustic Features** | 4 utilized (genre, mood, energy, acousticness) | 10 utilized (energy, tempo_bpm, valence, danceability, acousticness, instrumentalness, speechiness, key_instruments, listening_context, vibe_description) | Enables high-fidelity 6D acoustic vector similarity and grounded RAG narratives. |

### 3.2 Systemic Bias Identified in V1.0: The *Fiesta en la Calle* Phenomenon
In VibeCheck 1.0, doubling the energy weight to 4.0 out of 7.0 created an **energy filter bubble**. Because *Fiesta en la Calle* possessed high energy (0.84), high valence (0.92), and high danceability (0.89), it was recommended to **52.9% of all test listeners** (9 out of 17 profiles), including listeners who had zero interest in Latin music!

**How VibeCheck 2.0 Solves This**:
1. **Calibrated Multi-Attribute Weights**: Restored genre (2.5) and mood (2.0) authority alongside energy (2.5).
2. **MMR Diversity Optimization**: Downweights songs acoustically redundant with already-selected items ($\lambda = 0.70$).
3. **Result**: *Fiesta en la Calle* recommendation frequency dropped from **52.9% to 5.9%**, restoring diverse catalog discovery.

---

## 4. Evaluation Beyond Accuracy

Standard accuracy or top-1 hit rates are insufficient for recommender systems. VibeCheck 2.0 is evaluated across five multi-dimensional criteria:

```
===========================================================================
 📊 VIBECHECK 1.0 vs VIBECHECK 2.0 QUANTITATIVE BENCHMARK
===========================================================================
Evaluation Metric                | VibeCheck 1.0      | VibeCheck 2.0     
---------------------------------------------------------------------------
Intra-List Diversity (ILD)       | 0.371             | 0.525 (+0.154)
Fiesta en la Calle Dominance     | 52.9% (Severe)    | 5.9% (Diversified)
Fairness Parity Ratio            | 0.800             | 0.924 (+0.124)
Edge-Case Cohort Satisfaction    | 59.1%             | 68.7% (+9.6%)
Normal Cohort Satisfaction       | 73.9%             | 74.4% (+0.5%)
Catalog Exploration (Coverage)   | 95.0% (19/20)     | 86.0% (43/50)
===========================================================================
```

### Metric Definitions:
1. **Intra-List Diversity (ILD)**: Pairwise Euclidean acoustic distance between recommended tracks. V2.0 increases ILD by **41.5%**, ensuring playlists do not feel repetitive.
2. **Fairness Parity Ratio**: $\frac{\text{MeanScore}_{\text{EdgeCases}}}{\text{MeanScore}_{\text{Normal}}}$. V2.0 reaches **0.924**, closing the satisfaction gap for users with non-traditional tastes.
3. **Fiesta Dominance**: Measures the degree to which a single popular item cannibalizes catalog exposure. Reduced by **88.8%**.

---

## 5. Who the Model Works Best For vs. Where It Fails

### 🟢 Works Best For:
- **Mainstream Single-Genre Listeners**: (e.g. *Happy Pop Fan*, *Chill Studier*, *Gym Goer*). High acoustic resonance, exact genre hits, and 90%+ satisfaction scores.
- **Activity-Specific Sessions**: (e.g. *Study / Coding Flow*, *High-Cadence Cardio*). Leverages BPM and instrumentalness filters to protect focus.
- **Cross-Genre Explorers**: Listeners with high diversity tolerance ($\lambda \le 0.65$) who enjoy serendipitous acoustic matches.

### 🟡 Handled Gracefully with Conflict Guardrails:
- **Contradictory Preferences**: (e.g. *Sad but Hyped*). Detected by the Conflict Resolver, which redirects to high-tempo melancholia (*Crying in the Strobe*) rather than ignoring mood.
- **Acoustic Hard Rock / Metal**: (e.g. *Unplugged Metalhead*). Detected and expanded to acoustic blues, bluegrass, and post-metal ambient interludes.

### 🔴 Failure Modes & Limitations:
- **Completely Unknown Out-of-Catalog Genres**: (e.g. *Ghost Genre: K-Pop or Mongolian Throat Singing*). The model gracefully falls back to 6D acoustic similarity, but cannot fabricate missing cultural genres.
- **Micro-Linguistic Nuances**: Currently relies on English metadata and genre tags; does not analyze multi-lingual lyrical content.
- **Zero Real-Time Audio DSP**: Does not process raw PCM WAV/MP3 waveforms directly; relies on pre-computed feature vectors.

---

## 6. Trust, Safety & Guardrails Architecture

VibeCheck 2.0 enforces a **Two-Tier Guardrail Pipeline**:
1. **Tier 1: Pre-Execution Input Sanitization**:
   - Defeats prompt injections (`DROP TABLE`, `ignore previous instructions`, `<script>`).
   - Normalizes casing and fuzzily maps genre synonyms (`lo-fi` $\rightarrow$ `lofi`, `rnb` $\rightarrow$ `r&b`).
   - Clamps out-of-range energies (e.g. -2.5 $\rightarrow$ 0.0) with explicit audit warnings.
2. **Tier 2: Post-Generation Hallucination Verifier**:
   - Cross-checks all assertions in generated explanations against immutable catalog facts.
   - Detects and rejects hallucinated tempos, false genre labels, or phantom instruments.
   - Appends verifiable catalog grounding citations to every recommendation.
