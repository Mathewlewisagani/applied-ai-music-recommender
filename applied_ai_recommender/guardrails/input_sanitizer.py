"""
Input Sanitizer & Boundary Guardrail.
Protects the recommender pipeline from malicious inputs, prompt injections,
out-of-bounds numeric parameters, and typographical variations.
"""

import re
from typing import Dict, Any, Tuple, List
from applied_ai_recommender.core.models import GuardrailAudit, GuardrailStatus


KNOWN_GENRES = {
    "pop", "rock", "lofi", "ambient", "jazz", "synthwave", "indie pop",
    "hip hop", "classical", "country", "metal", "r&b", "edm", "reggae",
    "folk", "blues", "latin"
}

GENRE_SYNONYMS = {
    "lo-fi": "lofi",
    "hiphop": "hip hop",
    "rap": "hip hop",
    "rnb": "r&b",
    "r and b": "r&b",
    "electronic": "edm",
    "techno": "edm",
    "dance": "edm",
    "chillhop": "lofi",
    "indie": "indie pop",
    "heavy metal": "metal",
    "salsa": "latin",
}

# Simple adversarial / prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"<script",
    r"drop table",
    r"delete from",
    r"curl\s+",
    r"exec\(",
    r"import\s+os",
    r"eval\(",
]


def sanitize_user_input(raw_input: Dict[str, Any]) -> Tuple[Dict[str, Any], GuardrailAudit]:
    """
    Sanitizes, validates, and normalizes user input parameters.
    Ensures safe types, clamped values, and canonical genre/mood strings.
    """
    audit = GuardrailAudit(
        status=GuardrailStatus.PASSED,
        original_input=dict(raw_input),
        sanitized_input={},
        warnings=[],
        modifications=[],
        hallucination_flags=[],
        passed=True,
    )

    sanitized = {}

    # 1. Check for prompt injection / adversarial strings in textual inputs
    combined_text = " ".join(str(v) for v in raw_input.values())
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            audit.status = GuardrailStatus.REJECTED
            audit.warnings.append(f"Security Alert: Disallowed pattern detected ('{pattern}').")
            audit.passed = False
            # Neutralize text and provide safe fallback
            sanitized["favorite_genre"] = "pop"
            sanitized["favorite_mood"] = "chill"
            sanitized["target_energy"] = 0.5
            sanitized["likes_acoustic"] = False
            audit.sanitized_input = sanitized
            return sanitized, audit

    # 2. Sanitize & Normalize Genre
    raw_genre = str(raw_input.get("favorite_genre", "pop")).strip().lower()
    canonical_genre = GENRE_SYNONYMS.get(raw_genre, raw_genre)
    if canonical_genre != raw_input.get("favorite_genre"):
        audit.modifications.append(
            f"Normalized genre from '{raw_input.get('favorite_genre')}' to canonical '{canonical_genre}'"
        )
    if canonical_genre not in KNOWN_GENRES:
        audit.warnings.append(
            f"Genre '{canonical_genre}' is not in catalog. Will rely on acoustic profile & semantic vector."
        )
    sanitized["favorite_genre"] = canonical_genre

    # 3. Sanitize & Normalize Mood
    raw_mood = str(raw_input.get("favorite_mood", "chill")).strip().lower()
    sanitized["favorite_mood"] = raw_mood

    # 4. Validate & Clamp Target Energy to [0.0, 1.0]
    raw_energy = raw_input.get("target_energy", 0.5)
    try:
        val_energy = float(raw_energy)
    except (ValueError, TypeError):
        val_energy = 0.5
        audit.warnings.append(f"Invalid energy type '{raw_energy}'. Reset to default 0.5.")

    if val_energy < 0.0:
        audit.warnings.append(f"Energy {val_energy} is below 0.0. Clamped to minimum 0.0.")
        val_energy = 0.0
        audit.status = GuardrailStatus.MODIFIED
    elif val_energy > 1.0:
        audit.warnings.append(f"Energy {val_energy} is above 1.0. Clamped to maximum 1.0.")
        val_energy = 1.0
        audit.status = GuardrailStatus.MODIFIED

    sanitized["target_energy"] = round(val_energy, 3)

    # 5. Sanitize likes_acoustic
    raw_acoustic = raw_input.get("likes_acoustic", False)
    if isinstance(raw_acoustic, str):
        sanitized["likes_acoustic"] = raw_acoustic.strip().lower() in ["true", "yes", "1", "y"]
    else:
        sanitized["likes_acoustic"] = bool(raw_acoustic)

    # Secondary preferences if provided
    sanitized["secondary_genres"] = [
        str(g).strip().lower() for g in raw_input.get("secondary_genres", [])
    ]
    sanitized["secondary_moods"] = [
        str(m).strip().lower() for m in raw_input.get("secondary_moods", [])
    ]

    audit.sanitized_input = sanitized
    return sanitized, audit
