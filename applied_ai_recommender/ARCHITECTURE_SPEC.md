# 📐 Systems & Algorithms Specification: VibeCheck 2.0

## 1. Architectural Philosophy: Decomposing Vague Feature Requests

In music recommendation products, stakeholder requests are typically phrased in conversational, ambiguous language:
> *"Recommend good music that fits my vibe, adapt whether I'm studying or at the gym, explain why you picked it, don't repeat the same artist, don't make stuff up, and make sure it doesn't break when users do weird things."*

In VibeCheck 2.0, this vague request is rigorously decomposed into six testable, auditable system components:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       USER REQUEST & INTERFACES                             │
│   (Terminal Interactive CLI / Zero-Dependency HTML5 Web UI / Python API)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Raw Query & Session Context
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMPONENT 1: INPUT GUARDRAILS                          │
│   - Injection Pattern Detection & Neutralization                            │
│   - Parameter Bounds Clamping (Target Energy [0.0, 1.0])                    │
│   - Orthographic & Typo Normalization (Fuzzy Genre Synonyms)                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Sanitized User Profile
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  COMPONENT 2: CONFLICT RESOLUTION ENGINE                    │
│   - Contradiction Detection ('Sad but Hyped', 'Unplugged Metalhead')         │
│   - Acoustic Compromise Strategies & Secondary Taste Expansion              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Resolved Taste Profile & Vector Query
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              COMPONENT 3: HYBRID VECTOR & ATTRIBUTE RETRIEVAL               │
│   - 6D Acoustic Embedding Space (Energy, Tempo, Valence, Dance, Acoustic)   │
│   - Cosine Similarity Nearest Neighbor Filtering                            │
│   - Fast In-Memory Candidate Retrieval                                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Top-20 High-Similarity Candidates
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  COMPONENT 4: MULTI-OBJECTIVE SCORING                       │
│   - Calibrated Weights: Genre (2.5), Mood (2.0), Energy (2.5), Acoustic(1.5)│
│   - Acoustic Vector Harmony (1.5) -> Max 10.0 Points                        │
│   - Continuous Non-Linear Decay (Combats 1.0's Energy Filter Bubble)        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Scored Candidates
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│            COMPONENT 5: MAXIMAL MARGINAL RELEVANCE (MMR) RE-RANKING         │
│   - Diversity vs. Relevance Balancing (Lambda = 0.70)                       │
│   - Intra-List Acoustic Distance Maximization (Increases ILD)               │
│   - Artist Frequency Constraint (Prevents Monopolies)                       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Top-K Diversified Recommendations
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               COMPONENT 6: GROUNDED RAG EXPLANATION PIPELINE                │
│   - Context Assembler: Binds verified catalog metadata to prompt facts      │
│   - Grounded RAG Generator: Synthesizes personalized listening rationale    │
│   - Hallucination Verifier: Cross-checks tempo, genre, acoustic claims      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Verified Recommendations & Explanations
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION & AUDIT LOGGING                         │
│       (Transparent Scores, Grounding Badges, Security Audit Trail)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. System Structure Visualizations (UML)

### 2.1 Component Architecture Diagram

```mermaid
graph TD
    UI["Client Interface<br/>(CLI / Web UI)"] -->|Raw Profile| IS["Input Sanitizer & Boundary Guard"]
    IS -->|Audit Log| AUDIT["Guardrail Audit Trail"]
    IS -->|Sanitized Profile| CR["Conflict Resolver"]
    CR -->|Resolved Constraints| PIPE["Recommender Pipeline"]
    
    subgraph Data & Storage
        CAT["Enriched Song Catalog<br/>(50 Tracks, 15 Attributes)"]
        VEC_IDX["Vector Index<br/>(6D Acoustic Space)"]
    end
    
    CAT --> VEC_IDX
    CAT --> PIPE
    VEC_IDX -->|Cosine Similarity| RET["Vector Retrieval Engine"]
    
    PIPE --> RET
    RET -->|Candidates| SCORER["Multi-Objective Scorer"]
    SCORER -->|Scored Pool| MMR["MMR Diversity Re-Ranker"]
    MMR -->|Top-K Selections| RAG["Grounded RAG Engine"]
    
    CAT -->|Immutable Facts| RAG
    RAG --> HV["Hallucination Verifier"]
    HV -->|Grounding Audit| AUDIT
    HV -->|Final Verified Output| UI
```

### 2.2 Sequence Diagram: End-to-End Recommendation Request

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Client Interface
    participant Guard as Guardrails Engine
    participant Pipe as Recommender Pipeline
    participant Vec as Vector Engine
    participant MMR as Diversity Re-Ranker
    participant RAG as Grounded RAG
    participant Catalog as Song Catalog

    User->>UI: Submit Profile (e.g. Pop, Sad, Energy: 0.90)
    UI->>Guard: Validate & Sanitize Input
    Guard->>Guard: Detect Contradiction ('Sad but Hyped')
    Guard-->>Pipe: Sanitized Profile + Mitigation Strategy
    
    Pipe->>Vec: Query Nearest Acoustic Vectors
    Vec-->>Pipe: Top 20 Candidates
    
    Pipe->>Pipe: Calculate Multi-Objective Score (Max 10.0)
    
    Pipe->>MMR: Re-rank Candidates (Lambda = 0.70)
    MMR->>MMR: Maximize Marginal Relevance & Apply Artist Cap
    MMR-->>Pipe: Top-K Diversified Songs
    
    Pipe->>Catalog: Fetch Immutable Audio Facts (BPM, Instruments, Context)
    Catalog-->>RAG: Ground Truth Factsheet
    Pipe->>RAG: Generate Rationale
    RAG->>RAG: Verify Assertions (No Hallucinations)
    RAG-->>Pipe: Grounded Narrative + Verification Badge
    
    Pipe-->>UI: Output Top-K Recommendations + Audit Log
    UI-->>User: Display Recommendations, Scores, & Transparent Reasons
```

### 2.3 Class Diagram: Domain & Pipeline Models

```mermaid
classDiagram
    class Song {
        +int id
        +str title
        +str artist
        +str genre
        +str mood
        +float energy
        +float tempo_bpm
        +float valence
        +float danceability
        +float acousticness
        +str key_instruments
        +str listening_context
        +to_feature_vector() List~float~
    }

    class UserProfile {
        +str favorite_genre
        +str favorite_mood
        +float target_energy
        +bool likes_acoustic
        +List~str~ secondary_genres
        +SessionContext session_context
        +to_target_vector() List~float~
    }

    class SessionContext {
        +ActivityContext activity
        +str time_of_day
        +float diversity_preference
    }

    class RecommendationItem {
        +Song song
        +float final_score
        +float retrieval_similarity
        +Dict score_breakdown
        +List~str~ reasons
        +str grounded_explanation
    }

    class GuardrailAudit {
        +GuardrailStatus status
        +Dict original_input
        +Dict sanitized_input
        +List~str~ warnings
        +bool passed
    }

    class AppliedRecommenderPipeline {
        +List~Song~ catalog
        +VectorEngine vector_engine
        +GroundedRAGGenerator rag_generator
        +run_pipeline(raw_input, top_k) Dict
    }

    UserProfile "1" *-- "1" SessionContext
    AppliedRecommenderPipeline "1" o-- "*" Song
    AppliedRecommenderPipeline ..> RecommendationItem : produces
    AppliedRecommenderPipeline ..> GuardrailAudit : produces
    RecommendationItem "1" o-- "1" Song
```

### 2.4 State Diagram: Listener Session State Machine

```mermaid
stateDiagram-v2
    [*] --> AnonymousColdStart : First Request
    AnonymousColdStart --> InputValidation : Submit Taste Preferences
    
    state InputValidation {
        [*] --> CheckSecurity
        CheckSecurity --> CheckBounds : Safe
        CheckSecurity --> NeutralizeInput : Malicious / Injection
        CheckBounds --> CheckContradictions : Clamped
        CheckContradictions --> [*]
    }
    
    InputValidation --> CandidateRetrieval : Validated Profile
    CandidateRetrieval --> ScoringAndMMR : Vector Cosine & Constraints
    ScoringAndMMR --> RAGExplanation : Diversified Top-K
    RAGExplanation --> ActiveSession : Presentation & Grounding Badge
    
    ActiveSession --> SessionRefinement : User Provides Feedback / Activity Change
    SessionRefinement --> CandidateRetrieval : Updated Session Context
    ActiveSession --> [*] : Terminate Session
```

---

## 3. Planned Algorithms (Formal Specifications)

### Algorithm 1: Multi-Dimensional Acoustic Vector Cosine Similarity
$$\vec{v}_{\text{song}} = \left[ \text{energy}, \frac{\text{tempo}}{200}, \text{valence}, \text{danceability}, \text{acousticness}, \text{instrumentalness} \right]$$
$$\text{Sim}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2} = \frac{\sum_{i=1}^{d} u_i v_i}{\sqrt{\sum_{i=1}^{d} u_i^2} \sqrt{\sum_{i=1}^{d} v_i^2}}$$

### Algorithm 2: Continuous Multi-Objective Scoring
To prevent the catastrophic energy filter bubble where energy dominated 57% of all points in VibeCheck 1.0, VibeCheck 2.0 uses calibrated multi-criteria weighting:

$$S(u, s) = w_g \cdot \mathbb{I}_{\text{genre}}(u, s) + w_m \cdot \mathbb{I}_{\text{mood}}(u, s) + w_e \cdot (1 - |\text{energy}_s - \text{energy}_u|) + w_a \cdot (1 - |\text{acoust}_s - \text{acoust}_u|) + w_v \cdot \frac{\text{Sim}(\vec{u}, \vec{s}) + 1}{2}$$

Where:
- $w_g = 2.5$ (Genre affinity)
- $w_m = 2.0$ (Mood alignment)
- $w_e = 2.5$ (Energy closeness)
- $w_a = 1.5$ (Acoustic distance)
- $w_v = 1.5$ (6D Vector cosine similarity)
- Total Maximum Score = $10.0$.

### Algorithm 3: Maximal Marginal Relevance (MMR)
Given candidate pool $R$ and selected set $S$, iteratively select song $d^*$:
$$d^* = \arg\max_{d \in R \setminus S} \left[ \lambda \cdot \text{Rel}(d, u) - (1 - \lambda) \cdot \max_{d_s \in S} \text{Sim}(d, d_s) \right]$$
Subject to:
$$\text{Count}(\text{artist}(d), S) < \text{MaxPerArtist} \quad (\text{Default: } 2)$$

Where $\lambda = 0.70$ balances personalized relevance with acoustic variety, preventing single-artist and single-tempo clustering.

### Algorithm 4: Factual Grounding & Hallucination Guardrail
Let $E$ be the generated rationale text, and let $F(s)$ be the ground-truth attribute tuple:
$$F(s) = (\text{genre}_s, \text{BPM}_s, \text{energy}_s, \text{acousticness}_s, \text{instruments}_s)$$
The verification function $\mathcal{V}(E, F(s))$ applies deterministic NLP assertion checking:
1. Genre consistency: $\forall g \in \mathcal{G}, \text{mention}(g, E) \implies g = \text{genre}_s$.
2. Tempo consistency: $\text{mention}("fast", E) \implies \text{BPM}_s \ge 90$; $\text{mention}("slow", E) \implies \text{BPM}_s \le 130$.
3. Acoustic consistency: $\text{mention}("all acoustic", E) \implies \text{acousticness}_s \ge 0.5$.
4. Metadata citation badge: $E \leftarrow E \oplus \text{Badge}(F(s))$.
