import re
import math

from . import lexicon
from . import processing


def _tokenize(text):
    text = processing.normalize_text(text)
    tokens = re.findall(r"[a-z']+", text)
    stripped = [t.rstrip("'") for t in tokens]
    return [t for t in stripped if t]


def analyze_sentiment(text):
    tokens = _tokenize(text)
    if not tokens:
        return {"label": "Neutral", "score": 0.0, "notes": []}

    score = 0.0
    scores = [0.0] * len(tokens)
    for i, token in enumerate(tokens):
        weight = 1.0
        if token in lexicon.INTENSIFIERS:
            weight = 1.6
        if token in lexicon.POSITIVE_WORDS:
            scores[i] = 1.0 * weight
        elif token in lexicon.NEGATIVE_WORDS:
            scores[i] = -1.0 * weight

    for i, token in enumerate(tokens):
        negated = False
        for j in range(max(0, i - 3), i):
            if tokens[j] in lexicon.NEGATION_WORDS:
                negated = True
        if scores[i] != 0.0:
            scores[i] = -scores[i] if negated else scores[i]

    score = float(sum(scores))

    angry_terms = [t for t in tokens if t in lexicon.ANGER_WORDS]
    exclamations = text.count("!") if len(re.findall(r"[a-z]", text, re.I)) > 8 else 0
    uppercase_ratio = _uppercase_ratio(text)

    notes = []
    if angry_terms:
        notes.append("Strong anger indicators detected")
    if uppercase_ratio > 0.4 and uppercase_ratio < 1.0:
        notes.append("Message contains shouting / all-caps")
        score -= 1.0
    if exclamations >= 2:
        notes.append("Multiple exclamation marks")
        score -= 0.5

    if angry_terms and score <= 0:
        label = "Angry"
    elif score >= 2.0:
        label = "Happy"
    elif score > 0:
        label = "Neutral"
    elif score >= -2.5:
        label = "Frustrated"
    else:
        label = "Angry"

    return {
        "label": label,
        "score": round(score, 2),
        "notes": notes,
    }


def _uppercase_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    upper = sum(1 for c in letters if c.isupper())
    return upper / len(letters)


def classify_topic(text):
    normalized = processing.normalize_text(text)
    scores = {}
    match_notes = {}

    for topic, phrases in lexicon.TOPIC_KEYWORDS.items():
        count = 0
        matched = []
        for phrase in phrases:
            if phrase in normalized:
                count += 1
                matched.append(phrase)
        scores[topic] = count
        match_notes[topic] = matched

    best = max(scores, key=scores.get)
    total = sum(scores.values())
    if total == 0:
        return {
            "topic": "General",
            "confidence": 0.0,
            "scores": scores,
            "keywords": [],
        }

    confidence = round(scores[best] / total, 2)
    return {
        "topic": best.replace("_", " ").title(),
        "confidence": confidence,
        "scores": scores,
        "keywords": match_notes[best],
    }


def assess_urgency(text):
    normalized = processing.normalize_text(text)
    hits = [m for m in lexicon.URGENCY_MARKERS if m in normalized]
    uppercase_ratio = _uppercase_ratio(text)
    exclamations = text.count("!")

    score = 0.0
    for _ in hits:
        score += 1.0
    if uppercase_ratio > 0.5:
        score += 1.0
        hits.append("all-caps / shouting")
    if exclamations >= 2:
        score += 0.5
        if "exclamation marks" not in str(hits):
            hits.append("exclamation marks")

    level = "High" if score >= 1.5 else "Normal"
    return {
        "level": level,
        "score": round(score, 2),
        "reasons": sorted(dict.fromkeys(hits)),
    }


def _important_sentences(text, topic_keywords):
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    sentences = []
    for s in raw_sentences:
        s = s.strip()
        if 3 <= len(s) <= 260:
            sentences.append(s)

    if not sentences and len(text) > 0:
        return text

    scored = []
    for s in sentences:
        lower = processing.normalize_text(s)
        score = 0.0
        for kw in topic_keywords:
            if kw and kw in lower:
                score += 2.0
        if processing.AMOUNT_RE.search(s):
            score += 2.0
        if processing.ORDER_NUMBER_RE.search(s):
            score += 2.0
        if any(b in lower for b in lexicon.BRANDS):
            score += 1.0
        if any(p in lower for p in lexicon.POSITIVE_WORDS | lexicon.NEGATIVE_WORDS):
            score += 0.5
        scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    picked = [s for sc, s in scored if sc >= 2.0]
    if not picked:
        return " ".join(sentences[:2]) if len(sentences) >= 2 else (sentences[0] if sentences else text)
    return " ".join(picked[:3])


def generate_summary(text, topic, topic_keywords, sentiment, urgency):
    core = _important_sentences(text, topic_keywords)
    lead = f"Customer reports a {topic.lower()} concern."
    if urgency["level"] == "High":
        lead = f"Customer reports a {topic.lower()} concern and describes it as urgent."
    summary = lead + " " + core
    if len(summary) > 320:
        summary = summary[:317].rsplit(" ", 1)[0] + "..."
    return summary


def analyze_customer(text):
    processed = processing.parse_message(text)
    sentiment = analyze_sentiment(processed["body"])
    topic = classify_topic(processed["body"])
    urgency = assess_urgency(processed["body"])
    summary = generate_summary(
        processed["body"],
        topic["topic"],
        topic["keywords"],
        sentiment,
        urgency,
    )
    return {
        "topic": topic,
        "sentiment": sentiment,
        "urgency": urgency,
        "summary": summary,
        "processed": processed,
    }