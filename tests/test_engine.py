import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.insights import combine_analysis
from backend import security_ai, customer_ai, processing

PHISHING_SAMPLE = """From: support@paypa1-security.com

Dear customer,

Your PayPal account has been suspended due to unusual activity. Verify your account within 24 hours or it will be permanently closed.

Click here to confirm: http://paypa1-verify-example.com

Enter your password and OTP code to restore access. Attached: Invoice_2024_final.exe

Act immediately. Final notice."""

ANGRY_REFUND = """From: angry_customer_77@example.com
Subject: WHERE IS MY REFUND?

I asked for a refund 3 weeks ago and you have completely ignored me! This is absolutely unacceptable. I was charged twice for my order #ORD-884213 and nobody is responding. I want my money back TODAY or I will cancel my account. You people are useless and unprofessional!"""

DELIVERY_QUERY = """From: jane.doe@gmail.com
Subject: Order lookup

Hi, I just wanted to check on the status of my order #8874321. It said it was shipped last week but I have not received any tracking update. Could you let me know when it should arrive? Thanks for your help."""


def test_phishing_detection():
    result = combine_analysis(PHISHING_SAMPLE)
    sec = result["security_intelligence"]
    assert sec["phishing_detected"] is True, "phishing must be detected"
    assert sec["risk_level"] == "HIGH"
    assert sec["social_engineering"] is True
    assert sec["flags"]["suspicious_url"] is True
    assert sec["flags"]["impersonation"] is True
    assert sec["flags"]["credential_request"] is True
    assert sec["flags"]["attachment_risk"] is True
    assert "paypa1-verify-example.com" in sec["suspicious_urls"][0]
    assert any("do not click" in a.lower() for a in result["recommended_actions"])


def test_sentiment_detection():
    r1 = combine_analysis(ANGRY_REFUND)
    assert r1["customer_intelligence"]["sentiment"] in ("Angry", "Frustrated")
    r2 = combine_analysis(DELIVERY_QUERY)
    assert r2["customer_intelligence"]["sentiment"] == "Neutral"


def test_topic_classification():
    r1 = combine_analysis(ANGRY_REFUND)
    assert r1["customer_intelligence"]["topic"] == "Refund"
    r2 = combine_analysis(DELIVERY_QUERY)
    assert r2["customer_intelligence"]["topic"] == "Delivery"
    assert r2["customer_intelligence"]["order_numbers"] == ["8874321"]


def test_urgency_detection():
    r1 = combine_analysis(ANGRY_REFUND)
    assert r1["customer_intelligence"]["urgency"] == "High"
    r2 = combine_analysis(DELIVERY_QUERY)
    assert r2["customer_intelligence"]["urgency"] == "Normal"


def test_url_extraction():
    parsed = processing.parse_message(PHISHING_SAMPLE)
    assert parsed["urls"] == ["http://paypa1-verify-example.com"]
    assert parsed["sender"]["email"] == "support@paypa1-security.com"


def test_lookalike_domain():
    result = security_ai.inspect_domain("paypa1-security.com")
    assert result is not None
    assert any("impersonation" in r or "looks like" in r for r in result["reasons"])
    assert security_ai.inspect_domain("paypal.com") is None


def test_clean_message_no_false_positive():
    clean = "From: jane.doe@gmail.com\nSubject: Thanks\n\nThank you so much! My order arrived and it works perfectly. Great service."
    result = combine_analysis(clean)
    assert result["security_intelligence"]["phishing_detected"] is False
    assert result["security_intelligence"]["risk_level"] == "LOW"
    assert result["customer_intelligence"]["sentiment"] == "Happy"


def run_all():
    functions = [
        test_phishing_detection,
        test_sentiment_detection,
        test_topic_classification,
        test_urgency_detection,
        test_url_extraction,
        test_lookalike_domain,
        test_clean_message_no_false_positive,
    ]
    failed = 0
    for fn in functions:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {fn.__name__}: {exc}")
        except Exception as exc:
            failed += 1
            print(f"ERROR {fn.__name__}: {exc!r}")
    print(f"\n{len(functions) - failed}/{len(functions)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run_all())