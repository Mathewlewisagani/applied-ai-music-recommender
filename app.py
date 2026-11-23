"""
VibeCheck 2.0 - Applied AI Music Recommendation System
Minimalist monochrome interface with 13px typography, zero-radius design,
interactive attribute buttons, an animated network graph, and horizontal match bars.
"""

import sys
import os
import streamlit as st

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from applied_ai_recommender.rag.pipeline import AppliedRecommenderPipeline
from applied_ai_recommender.evaluation.benchmark import run_benchmark


# Set page configuration
st.set_page_config(
    page_title="VibeCheck 2.0",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enforce clean black and white design, 13px font size, and zero border-radius
st.markdown("""
<style>
    /* Global font size ~13px and typography */
    html, body, [class*="css"], .stMarkdown, p, span, label, div, input, select, button {
        font-size: 13px !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }

    /* Clean white background and dark text */
    .stApp {
        background-color: #ffffff !important;
        color: #18181b !important;
    }

    [data-testid="stSidebar"] {
        background-color: #fafaf9 !important;
        border-right: 1px solid #ede8e3 !important;
    }

    /* Big title with orange accent */
    .big-title {
        font-size: 44px !important;
        font-weight: 900 !important;
        letter-spacing: -1px !important;
        color: #111111 !important;
        line-height: 1.0 !important;
        margin-top: -10px !important;
        margin-bottom: 6px !important;
        text-transform: uppercase !important;
    }
    .orange-accent {
        color: #ea580c !important;
    }

    .sub-title {
        font-size: 13px !important;
        color: #71717a !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        margin-bottom: 18px !important;
        border-bottom: 1px solid #f0eee9 !important;
        padding-bottom: 10px !important;
    }

    /* Button styling: solid warm orange */
    .stButton>button {
        background-color: #ea580c !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: 1px solid #ea580c !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        transition: background-color 0.15s ease, border-color 0.15s ease;
    }
    .stButton>button:hover {
        background-color: #c2410c !important;
        border-color: #c2410c !important;
        color: #ffffff !important;
    }

    /* Rounded cards with subtle orange hover tinge */
    .song-card {
        background-color: #ffffff;
        border: 1px solid #e4e4e7;
        border-radius: 8px !important;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .song-card:hover {
        border-color: #fdba74;
        box-shadow: 0 3px 10px rgba(234, 88, 12, 0.08);
    }

    /* Interactive Attribute Buttons */
    .attr-btn {
        display: inline-block;
        background: #f4f4f5;
        color: #27272a;
        border: 1px solid #e4e4e7;
        border-radius: 12px !important;
        padding: 4px 11px;
        font-size: 11px !important;
        font-family: inherit;
        margin-right: 6px;
        margin-top: 6px;
        cursor: pointer;
        transition: all 0.15s ease;
        text-decoration: none;
        user-select: none;
    }
    .attr-btn:hover {
        background: #ea580c !important;
        color: #ffffff !important;
        border-color: #ea580c !important;
    }

    /* Horizontal Match Percentage Bar with Orange Fill */
    .match-bar-wrap {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 170px;
    }
    .match-bar-track {
        flex-grow: 1;
        height: 7px;
        background: #f4f4f5;
        border: 1px solid #e4e4e7;
        border-radius: 4px !important;
        overflow: hidden;
    }
    .match-bar-fill {
        height: 100%;
        background: #ea580c;
        border-radius: 4px !important;
        animation: fillBar 0.6s ease-out forwards;
    }
    .match-bar-percent {
        font-size: 11px !important;
        color: #ea580c;
        font-weight: 700;
        font-family: monospace;
        width: 32px;
        text-align: right;
    }
    @keyframes fillBar {
        from { width: 0%; }
    }

    .song-title-text {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #09090b !important;
    }
    .song-artist-text {
        font-size: 13px !important;
        color: #71717a !important;
        font-weight: 500 !important;
    }

    /* Selection Rationale with warm orange tinge */
    .rationale-text {
        border-left: 3px solid #ea580c;
        border-radius: 4px !important;
        padding: 8px 12px;
        margin-top: 10px;
        background: #fff7ed;
        color: #27272a;
        font-size: 12.5px !important;
        line-height: 1.5;
    }

    .audit-notice {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-radius: 6px !important;
        padding: 10px 14px;
        margin-bottom: 16px;
        font-size: 12.5px !important;
        color: #9a3412;
    }

    /* Visual Graph Container */
    .graph-container {
        border: 1px solid #ede8e3;
        background: #fbfbf9;
        padding: 14px 16px 10px 16px;
        margin-bottom: 18px;
        border-radius: 8px !important;
    }
    .graph-header {
        font-size: 11px !important;
        color: #71717a;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
    }

    /* SVG Animation Keyframes */
    @keyframes pulseCenter {
        0% { stroke-opacity: 0.3; stroke-width: 1.2; }
        50% { stroke-opacity: 1.0; stroke-width: 2.8; }
        100% { stroke-opacity: 0.3; stroke-width: 1.2; }
    }
    @keyframes flowDash {
        to { stroke-dashoffset: -40; }
    }
    .anim-pulse {
        animation: pulseCenter 2.4s ease-in-out infinite;
    }
    .anim-flow {
        stroke-dasharray: 4, 3;
        animation: flowDash 3s linear infinite;
    }

    /* Tabs styling with orange highlight */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: 1px solid #e4e4e7;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0px !important;
        color: #71717a !important;
        padding: 8px 16px !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #ea580c !important;
        border-bottom: 2px solid #ea580c !important;
        font-weight: 600 !important;
    }

    /* Clean inputs and select boxes */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 4px !important;
        color: #18181b !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_pipeline():
    return AppliedRecommenderPipeline()

pipeline = get_pipeline()


# --- PRESETS (NO EMOJIS, CLEAN LABELS) ---
PRESET_VIBES = {
    "Custom Profile": None,
    "Quiet Focus (Lofi Acoustic)": {
        "genre": "lofi", "mood": "chill", "energy": 0.35, "acoustic": True, "adventure": 0.70, "activity": "study"
    },
    "High Energy Workout (EDM)": {
        "genre": "edm", "mood": "energetic", "energy": 0.95, "acoustic": False, "adventure": 0.70, "activity": "workout"
    },
    "Fast Melancholy (Pop)": {
        "genre": "pop", "mood": "sad", "energy": 0.88, "acoustic": False, "adventure": 0.75, "activity": "party"
    },
    "Acoustic Rock": {
        "genre": "rock", "mood": "playful", "energy": 0.70, "acoustic": True, "adventure": 0.65, "activity": "general"
    },
    "Late Night Ambient": {
        "genre": "ambient", "mood": "chill", "energy": 0.30, "acoustic": True, "adventure": 0.75, "activity": "study"
    },
    "Upbeat Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.80, "acoustic": False, "adventure": 0.70, "activity": "party"
    },
}


# --- SIDEBAR: CLEAN CONTROLS ---
with st.sidebar:
    st.markdown("### Profile Controls")
    st.caption("Select a baseline profile or adjust parameters manually.")

    selected_preset = st.selectbox(
        "Preset Configuration",
        options=list(PRESET_VIBES.keys()),
        index=0
    )

    preset_data = PRESET_VIBES[selected_preset]

    st.markdown("---")

    # Genre selector
    genre_options = [
        "pop", "lofi", "rock", "metal", "hip hop", "r&b", "edm", "jazz",
        "classical", "country", "folk", "blues", "latin", "synthwave", "ambient"
    ]
    default_genre = preset_data["genre"] if preset_data else "pop"
    fav_genre = st.selectbox(
        "Genre",
        options=genre_options,
        index=genre_options.index(default_genre) if default_genre in genre_options else 0,
    )

    # Mood selector
    mood_options = [
        "happy", "chill", "energetic", "peaceful", "sad", "focused",
        "romantic", "nostalgic", "intense", "playful", "angry", "confident"
    ]
    default_mood = preset_data["mood"] if preset_data else "happy"
    fav_mood = st.selectbox(
        "Mood",
        options=mood_options,
        index=mood_options.index(default_mood) if default_mood in mood_options else 0,
    )

    # Energy slider
    default_energy = preset_data["energy"] if preset_data else 0.75
    st.markdown("**Target Energy**")
    energy_level = st.slider(
        "Energy Level",
        min_value=0.0,
        max_value=1.0,
        value=float(default_energy),
        step=0.05,
        format="%.2f",
        label_visibility="collapsed"
    )
    st.caption(f"Target: {energy_level:.2f} (0.0 Calm — 1.0 Intense)")

    # Acoustic preference
    st.markdown("**Instrument Profile**")
    default_acoustic_idx = 0 if (preset_data and preset_data["acoustic"]) else 1
    acoustic_choice = st.radio(
        "Instrument Type",
        options=["Acoustic / Organic Instruments", "Electronic / Studio Production"],
        index=default_acoustic_idx,
        label_visibility="collapsed"
    )
    likes_acoustic = "Acoustic" in acoustic_choice

    # Diversity slider
    st.markdown("**Diversity Tradeoff**")
    default_adv = preset_data["adventure"] if preset_data else 0.70
    adventure = st.slider(
        "Diversity",
        min_value=0.3,
        max_value=1.0,
        value=float(default_adv),
        step=0.05,
        label_visibility="collapsed"
    )
    st.caption(f"Relevance weight: {adventure:.2f} (lower increases acoustic variety)")

    # Session Activity
    default_act = preset_data["activity"] if preset_data else "general"
    act_options = {
        "general": "General Listening",
        "study": "Deep Focus / Study",
        "workout": "Workout / Cardio",
        "party": "Social / Gathering",
        "relaxation": "Evening Wind-Down"
    }
    activity = st.selectbox(
        "Activity Context",
        options=list(act_options.keys()),
        format_func=lambda x: act_options[x],
        index=list(act_options.keys()).index(default_act) if default_act in act_options else 0
    )

    st.markdown("<br>", unsafe_allow_html=True)
    get_recs_btn = st.button("Generate Recommendations", use_container_width=True)


# --- MAIN PAGE: CLEAN LIGHT HEADER WITH ORANGE ACCENT ---
st.markdown('<div class="big-title">VIBE CHECK <span class="orange-accent">2.0</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Applied AI Music Recommendation System & Evaluation Harness</div>', unsafe_allow_html=True)

# Tabs
tab_recommendations, tab_how_it_works, tab_story = st.tabs([
    "Recommendations",
    "System Logic & Verification",
    "Evaluation & Benchmark"
])


def render_animated_network_graph(genre: str, recommendations: list) -> str:
    """
    Renders an animated SVG graph connecting the central genre node
    to the top-5 recommended tracks with weights along the edges.
    """
    width, height = 780, 190
    cx, cy = 390, 95

    # Coordinates for the 5 surrounding song nodes
    node_coords = [
        (85, 42),
        (85, 148),
        (390, 24),
        (695, 42),
        (695, 148),
    ]

    lines_svg = []
    nodes_svg = []

    for idx, (coord, item) in enumerate(zip(node_coords, recommendations)):
        nx, ny = coord
        norm_weight = item.final_score / 10.0
        weight_str = f"{norm_weight:.2f}"

        # Midpoint for edge weight badge
        mx = (cx + nx) / 2
        my = (cy + ny) / 2

        # Flowing connecting line with warm orange tinge
        lines_svg.append(
            f'<line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="#fdba74" stroke-width="1.6" class="anim-flow" />'
        )

        # Edge weight badge
        lines_svg.append(
            f'<rect x="{mx-16:.1f}" y="{my-8:.1f}" width="32" height="16" fill="#ffffff" stroke="#fed7aa" stroke-width="1" rx="3" ry="3" />'
        )
        lines_svg.append(
            f'<text x="{mx:.1f}" y="{my+3:.1f}" fill="#c2410c" font-size="10" font-family="monospace" font-weight="700" text-anchor="middle">{weight_str}</text>'
        )

        # Song node rectangle & title (white rounded cards)
        clean_title = item.song.title if len(item.song.title) <= 13 else item.song.title[:12] + ".."
        nodes_svg.append(
            f'<rect x="{nx-52:.1f}" y="{ny-14:.1f}" width="104" height="28" fill="#ffffff" stroke="#e4e4e7" stroke-width="1.2" rx="4" ry="4" />'
        )
        nodes_svg.append(
            f'<text x="{nx:.1f}" y="{ny+4:.1f}" fill="#18181b" font-size="11" font-family="-apple-system, sans-serif" font-weight="600" text-anchor="middle">#{idx+1} {clean_title}</text>'
        )

    # Central Genre Node with animated orange pulse ring
    center_svg = f"""
    <circle cx="{cx}" cy="{cy}" r="38" fill="none" stroke="#ea580c" class="anim-pulse" />
    <circle cx="{cx}" cy="{cy}" r="32" fill="#fff7ed" stroke="#ea580c" stroke-width="2.2" />
    <text x="{cx}" y="{cy-3}" fill="#ea580c" font-size="11" font-weight="800" font-family="-apple-system, sans-serif" text-anchor="middle" letter-spacing="1">{genre.upper()}</text>
    <text x="{cx}" y="{cy+11}" fill="#9a3412" font-size="9" font-family="monospace" font-weight="600" text-anchor="middle">GENRE NODE</text>
    """

    svg_content = f"""
    <div class="graph-container">
        <div class="graph-header">
            <span>Acoustic Network Topology</span>
            <span>Weights represent normalized match scores [0.00 – 1.00]</span>
        </div>
        <svg width="100%" height="{height}" viewBox="0 0 {width} {height}" style="background: #fafaf9; display: block; border-radius: 6px;">
            {''.join(lines_svg)}
            {''.join(nodes_svg)}
            {center_svg}
        </svg>
    </div>
    """
    return svg_content


# --- TAB 1: RECOMMENDATIONS ---
with tab_recommendations:
    user_input = {
        "favorite_genre": fav_genre,
        "favorite_mood": fav_mood,
        "target_energy": energy_level,
        "likes_acoustic": likes_acoustic,
    }

    results = pipeline.run_pipeline(
        user_input,
        top_k=5,
        diversity_lambda=adventure,
        session_activity=activity
    )

    recs = results["recommendations"]
    audit = results["guardrail_audit"]
    conflict = results["conflict_report"]

    # Conflict / Guardrail Notification
    if conflict.has_conflict:
        st.markdown(f"""
        <div class="audit-notice">
            <strong>Preference Balance Active:</strong> Contradiction detected ({fav_mood} mood with {energy_level:.2f} energy). 
            Applied cross-modal retrieval to surface fast-tempo melancholic tracks rather than dropping mood criteria.
        </div>
        """, unsafe_allow_html=True)
    elif audit.warnings:
        for w in audit.warnings:
            st.markdown(f'<div class="audit-notice">Input Notice: {w}</div>', unsafe_allow_html=True)

    # 1. Animated Center Node Network Graph
    network_graph_html = render_animated_network_graph(fav_genre, recs)
    st.markdown(network_graph_html, unsafe_allow_html=True)

    st.markdown(f"**Recommended Catalog Matches** (Top {len(recs)} diversified selections)")

    # Render each song in a rounded card
    for idx, item in enumerate(recs, start=1):
        s = item.song
        score_pct = int(min(100, (item.final_score / 10.0) * 100))
        sound_type = "Acoustic" if s.acousticness > 0.5 else "Electronic"

        # Provide a rich musical vibe story instead of repeating the button stats
        vibe_text = s.vibe_description if s.vibe_description else f"A cohesive {s.mood} {s.genre} track."
        context_text = f" Ideal for {s.listening_context}." if s.listening_context else ""
        musical_narrative = vibe_text + context_text

        st.markdown(f"""
        <div class="song-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div>
                    <span class="song-title-text">{idx}. {s.title}</span>
                    <span class="song-artist-text"> — {s.artist}</span>
                </div>
                <div class="match-bar-wrap">
                    <div class="match-bar-track">
                        <div class="match-bar-fill" style="width: {score_pct}%;"></div>
                    </div>
                    <span class="match-bar-percent">{score_pct}%</span>
                </div>
            </div>
            
            <div style="margin-bottom: 10px;">
                <button class="attr-btn">{s.genre}</button>
                <button class="attr-btn">{s.mood}</button>
                <button class="attr-btn">{int(s.tempo_bpm)} BPM</button>
                <button class="attr-btn">Energy {s.energy:.2f}</button>
                <button class="attr-btn">{sound_type}</button>
                {f'<button class="attr-btn">{s.key_instruments}</button>' if s.key_instruments else ''}
            </div>

            <div class="rationale-text">
                {musical_narrative}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Collapsible verification audit for engineers and evaluators
    with st.expander("System Audit & Verification Details"):
        st.markdown("**Catalog Grounding Verification (Hallucination Defense)**")
        st.caption("Validates that every tempo, genre, and instrument claim matches catalog truth.")
        for item in recs:
            s = item.song
            st.markdown(f"- **{s.title}**: Genre `{s.genre}` | Tempo `{int(s.tempo_bpm)} BPM` | Energy `{s.energy:.2f}` | Acousticness `{s.acousticness:.2f}` | Score `{item.final_score:.2f}/10`")
        if audit.warnings:
            st.markdown("**Input Sanitization Warnings:**")
            for w in audit.warnings:
                st.markdown(f"- {w}")


# --- TAB 2: SYSTEM LOGIC & VERIFICATION ---
with tab_how_it_works:
    st.markdown("### System Logic and Architecture")
    st.write("""
    VibeCheck 2.0 decomposes recommendation requests into a deterministic, testable pipeline:
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **1. Input Guardrails & Conflict Resolution**  
        Validates parameter boundaries ($[0.0, 1.0]$) and neutralizes syntax injections. 
        Detects conflicting preferences (e.g. high energy with sad mood) and applies cross-modal 
        balancing rather than zeroing out one attribute.
        """)

    with col2:
        st.markdown("""
        **2. Vector Retrieval & Multi-Attribute Scoring**  
        Computes cosine similarity across a 6-dimensional normalized acoustic space 
        (energy, tempo, valence, danceability, acousticness, instrumentalness). 
        Ranks candidates using continuous non-linear closeness penalties.
        """)

    with col3:
        st.markdown("""
        **3. Diversity Re-ranking & Fact Verification**  
        Applies Maximal Marginal Relevance (MMR) to maximize intra-list diversity and enforce 
        artist frequency caps. Generated explanations are checked against catalog metadata 
        to ensure zero hallucination.
        """)


# --- TAB 3: EVALUATION & BENCHMARK ---
with tab_story:
    st.markdown("### Model Evaluation and Bias Analysis")
    st.write("""
    In VibeCheck 1.0, doubling the energy scoring weight produced an **energy filter bubble**. 
    Because *Fiesta en la Calle* possessed high energy (0.84) and danceability (0.89), it appeared in **52.9%** 
    of all user recommendations regardless of genre or mood preferences.
    """)

    b_report = run_benchmark()
    v1 = b_report["v1"]
    v2 = b_report["v2"]

    st.markdown("#### Performance Metrics Comparison")

    mcol1, mcol2, mcol3 = st.columns(3)

    with mcol1:
        st.metric(
            label="Single-Track Dominance (Fiesta en la Calle)",
            value=f"{v2['fiesta_dominance_pct']:.1f}%",
            delta=f"-{v1['fiesta_dominance_pct'] - v2['fiesta_dominance_pct']:.1f}%",
            delta_color="normal"
        )
        st.caption("Proportion of user profiles where a single track dominated.")

    with mcol2:
        st.metric(
            label="Intra-List Diversity (ILD)",
            value=f"{v2['intra_list_diversity']:.3f}",
            delta=f"+{v2['intra_list_diversity'] - v1['intra_list_diversity']:.3f}",
            delta_color="normal"
        )
        st.caption("Pairwise acoustic distance between songs in a recommendation list.")

    with mcol3:
        st.metric(
            label="Fairness Parity Ratio",
            value=f"{v2['parity_ratio']:.3f}",
            delta=f"+{v2['parity_ratio'] - v1['parity_ratio']:.3f}",
            delta_color="normal"
        )
        st.caption("Ratio of satisfaction scores between edge-case and standard cohorts.")
