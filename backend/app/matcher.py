import difflib
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Incident

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate TF-IDF Cosine Similarity between two text strings."""
    if not text1 or not text2:
        return 0.0
    t1 = text1.strip()
    t2 = text2.strip()
    if t1 == t2:
        return 1.0
    try:
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit([t1, t2])
        tfidf_matrix = vectorizer.transform([t1, t2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim)
    except Exception:
        # Fallback to SequenceMatcher if TF-IDF fails (e.g. single word / syntax mismatch)
        return difflib.SequenceMatcher(None, t1, t2).ratio()

def find_similar_incidents(target: Incident, historical_incidents: List[Incident]) -> List[Dict[str, Any]]:
    """
    Compares target incident against a list of historical/resolved incidents.
    Returns ranked list of matches with similarity scores (0 to 100%) and evidence breakdowns.
    """
    results = []

    for hist in historical_incidents:
        if hist.id == target.id:
            continue

        # 1. Endpoint match score (0.0 or 1.0)
        endpoint_score = 1.0 if target.endpoint.strip() == hist.endpoint.strip() else 0.0
        if endpoint_score == 0.0 and (target.endpoint in hist.endpoint or hist.endpoint in target.endpoint):
            endpoint_score = 0.6

        # 2. Error Type match score (0.0 to 1.0)
        if target.error_type.strip() == hist.error_type.strip():
            error_type_score = 1.0
        else:
            error_type_score = difflib.SequenceMatcher(None, target.error_type.strip(), hist.error_type.strip()).ratio()

        # 3. Error Message TF-IDF score
        message_score = calculate_text_similarity(target.error_message, hist.error_message)

        # 4. Stack Trace TF-IDF score
        stack_score = calculate_text_similarity(target.stack_trace or "", hist.stack_trace or "")

        # Weighted combination
        # Endpoint: 25%, Error Type: 25%, Error Message: 30%, Stack Trace: 20%
        raw_weighted = (
            (0.25 * endpoint_score) +
            (0.25 * error_type_score) +
            (0.30 * message_score) +
            (0.20 * stack_score)
        )

        similarity_pct = round(raw_weighted * 100, 1)

        results.append({
            "incident": hist,
            "similarity_score": similarity_pct,
            "evidence": {
                "endpoint_score": round(endpoint_score * 100, 1),
                "error_type_score": round(error_type_score * 100, 1),
                "message_tfidf_score": round(message_score * 100, 1),
                "stack_tfidf_score": round(stack_score * 100, 1),
            }
        })

    # Sort descending by similarity score
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results
