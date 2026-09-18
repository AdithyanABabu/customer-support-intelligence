import re

from . import customer_ai
from . import security_ai
from . import processing


def combine_analysis(text):
    text = processing.to_text(text)
    if not text:
        return {
            "error": "Empty message",
            "customer_intelligence": {},
            "security_intelligence": {},
            "risk": {},
            "recommended_actions": [],
            "history_id": None,
        }

    parsed = processing.parse_message(text)
    customer = customer_ai.analyze_customer(text)
    security = security_ai.analyze_security(parsed["sender"], customer["processed"]["body"])

    risk_score = security["risk_score"]
    customer_urgency = 2 if customer["urgency"]["level"] == "High" else 0
    combined_score = risk_score + customer_urgency

    if combined_score >= 10:
        overall_risk = "HIGH"
    elif combined_score >= 6:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    recommended_actions = list(security["recommended_actions"])
    routing_advice = _routing_advice(customer["topic"]["topic"])
    if routing_advice:
        recommended_actions.append(routing_advice)

    summary = customer["summary"]

    return {
        "error": None,
        "raw": text,
        "from_header": parsed["from_header"],
        "sender": parsed["sender"],
        "customer_intelligence": {
            "topic": customer["topic"]["topic"],
            "topic_confidence": customer["topic"]["confidence"],
            "topic_keywords": customer["topic"]["keywords"],
            "sentiment": customer["sentiment"]["label"],
            "sentiment_score": customer["sentiment"]["score"],
            "sentiment_notes": customer["sentiment"]["notes"],
            "urgency": customer["urgency"]["level"],
            "urgency_reasons": customer["urgency"]["reasons"],
            "summary": summary,
            "order_numbers": parsed["order_numbers"],
            "amounts": parsed["amounts"],
        },
        "security_intelligence": {
            "phishing_detected": security["phishing_detected"],
            "risk_level": security["risk_level"],
            "risk_score": security["risk_score"],
            "social_engineering": security["social_engineering"],
            "suspicious_urls": [u["url"] for u in security["suspicious_urls"]],
            "malicious_domains": [d["domain"] for d in security["malicious_domains"]],
            "impersonated_brands": security["impersonated_brands"],
            "flags": security["flags"],
            "findings": security["findings"],
        },
        "risk": {
            "level": overall_risk,
            "score": combined_score,
            "security_score": security["risk_score"],
            "urgency_score": customer_urgency,
        },
        "recommended_actions": list(dict.fromkeys(recommended_actions)),
        "urls_found": parsed["urls"],
        "emails_found": parsed["emails"],
        "attachments_found": parsed["attachments"],
    }


def _routing_advice(topic):
    routing = {
        "Refund": "Route to the billing/refund team",
        "Payment": "Route to the billing/payments team",
        "Delivery": "Route to the shipping/fulfillment team",
        "Login Account": "Route to the account-access support team",
        "Product Problem": "Route to the technical/product support team",
        "Account Security": "Route to the security/fraud team",
        "Cancellation": "Route to the account management team",
        "General": "Route to the general support queue",
    }
    return routing.get(topic)


def analyze_messages_bulk(messages):
    insights = {
        "total": len(messages),
        "by_topic": {},
        "by_sentiment": {},
        "by_urgency": {},
        "phishing_count": 0,
        "repeated_problems": [],
        "sentiment_score_avg": 0.0,
        "messages": messages,
    }
    if not messages:
        return insights

    topic_map = {}
    sentiment_map = {}
    urgency_map = {}
    phishing = 0
    total_sentiment = 0.0

    for m in messages:
        topic = m.get("topic", "General")
        sentiment = m.get("sentiment", "Neutral")
        urgency = m.get("urgency", "Normal")
        total_sentiment += m.get("sentiment_score", 0.0)
        if m.get("phishing_detected"):
            phishing += 1

        topic_map[topic] = topic_map.get(topic, 0) + 1
        sentiment_map[sentiment] = sentiment_map.get(sentiment, 0) + 1
        urgency_map[urgency] = urgency_map.get(urgency, 0) + 1

    insights["by_topic"] = topic_map
    insights["by_sentiment"] = sentiment_map
    insights["by_urgency"] = urgency_map
    insights["phishing_count"] = phishing
    insights["sentiment_score_avg"] = round(total_sentiment / len(messages), 2)

    repeated = []
    for topic, count in topic_map.items():
        if count >= 2:
            repeated.append({
                "topic": topic,
                "count": count,
                "share": round(count / len(messages) * 100),
                "insight": f"{count} of the last {len(messages)} messages concern {topic.lower()} issues"
                            if count > 1 else f"A recent message concerns {topic.lower()}",
            })
    repeated.sort(key=lambda x: x["count"], reverse=True)
    insights["repeated_problems"] = repeated[:5]
    return insights