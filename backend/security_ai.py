import re
from urllib.parse import urlparse

from . import lexicon
from . import processing


def _registrable_domain(host):
    host = host.lower().strip()
    labels = [l for l in host.split(".") if l]
    if len(labels) <= 1:
        return host
    if len(labels) >= 3 and labels[-1] in ("com", "net", "org", "info") and len(labels[-2]) <= 3:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def _normalize_lookalike(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9]", "", value)
    for k, v in lexicon.BRAND_HOMOGLYPHS.items():
        value = value.replace(k, v)
    return value


def _levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _lookalike_brand(host):
    normalized = _normalize_lookalike(host)
    for brand in lexicon.BRANDS:
        brand_norm = _normalize_lookalike(brand)
        if brand_norm and brand_norm in normalized:
            return brand.title()
        name_like = "paypal"
        if brand_norm and name_like and brand_norm in normalized.replace(name_like, name_like):
            return brand.title()
    return None


def _tld(host):
    labels = host.lower().strip(".").split(".")
    return labels[-1] if labels else ""


def inspect_url(url):
    if not url:
        return None
    scheme, netloc, path, params, query, fragment = urlparse(url if "://" in url else "//" + url)
    host = (netloc or "").split(":")[0].lower()
    port = netloc.split(":")[1] if ":" in netloc else None
    reasons = []

    if processing.is_ip_literal(host):
        reasons.append(f"URL uses a raw IP address ({host})")
    if "@" in netloc:
        reasons.append("URL contains an @ sign (classic URL-obfuscation trick)")
    if "xn--" in host:
        reasons.append(f"URL uses punycode/IDN obfuscation ({host})")
    if port and port not in ("80", "443", ""):
        reasons.append(f"URL uses a non-standard port ({port})")

    registrable = _registrable_domain(host)
    tld = _tld(host)
    if tld in lexicon.SUSPICIOUS_TLDS:
        reasons.append(f"Domain uses a high-risk TLD (.{tld})")

    if registrable in lexicon.URL_SHORTENERS or host in lexicon.URL_SHORTENERS:
        reasons.append(f"Domain is a URL shortener ({registrable})")

    if registrable and not any(registrable == d for d in lexicon.BRANDS.values()):
        lookalike = _lookalike_brand(host)
        if lookalike:
            reasons.append(f"URL looks like it spoofs '{lookalike}' ({host})")
        elif any(kw in host for kw in ("verify", "secure", "login", "signin", "account", "alert", "update", "billing", "unlock")):
            reasons.append(f"Domain contains security-keywords and is not an official {registrable} domain")

    if "-" in registrable:
        count = registrable.count("-")
        if count >= 2 or _registrable_domain(host) != host:
            reasons.append(f"Domain uses hyphens ({registrable}), a common phishing pattern")

    if not reasons:
        return None
    return {
        "url": url,
        "host": host,
        "registrable": registrable,
        "reasons": reasons,
    }


def inspect_domain(domain):
    if not domain:
        return None
    domain = domain.lower().strip()
    reasons = []
    registrable = _registrable_domain(domain)
    tld = _tld(domain)

    if processing.is_ip_literal(domain):
        reasons.append("Email domain is a raw IP address")
    if "xn--" in domain:
        reasons.append("Email domain uses punycode")
    if tld in lexicon.SUSPICIOUS_TLDS:
        reasons.append(f"Email domain uses a high-risk TLD (.{tld})")
    if registrable in lexicon.URL_SHORTENERS:
        reasons.append("Email domain is a URL shortener")

    lookalike = _lookalike_brand(domain)
    if lookalike:
        official = lexicon.BRANDS.get(lookalike.lower())
        if registrable != official:
            reasons.append(f"Email domain looks like an impersonation of {lookalike} ({domain})")
    elif any(kw in domain for kw in ("verify", "secure", "customerservice", "help", "support", "account")):
        reasons.append(f"Email domain contains suspicious keywords ({domain})")

    if not reasons:
        return None
    return {"domain": domain, "registrable": registrable, "reasons": reasons}


def _has_any(haystack, needles):
    return [n for n in needles if n in haystack]


def analyze_security(parsed, body):
    flagged = {
        "suspicious_url": False,
        "malicious_domain": False,
        "impersonation": False,
        "credential_request": False,
        "payment_request": False,
        "urgency_tactics": False,
        "threat_tactics": False,
        "attachment_risk": False,
    }
    suspicious_urls = []
    malicious_domains = []
    impersonated_brands = []
    social_engineering = False
    findings = []
    score = 0

    normalized = processing.normalize_text(body)
    urls = processing.extract_urls(body)
    for url in urls:
        info = inspect_url(url)
        if info:
            flagged["suspicious_url"] = True
            score += 3
            suspicious_urls.append(info)
            findings.extend(info["reasons"])
            if info["registrable"] not in (m["domain"] for m in malicious_domains):
                malicious_domains.append(inspect_domain(info["registrable"]) or {"domain": info["registrable"], "reasons": info["reasons"]})

    sender_domain = parsed["domain"]
    if sender_domain:
        domain_info = inspect_domain(sender_domain)
        if domain_info:
            flagged["malicious_domain"] = True
            score += 2
            malicious_domains.append(domain_info)
            findings.extend(domain_info["reasons"])
            if any("impersonation" in r or "looks like" in r for r in domain_info["reasons"]):
                flagged["impersonation"] = True

    brand_hits = [b for b in lexicon.BRANDS if b in (parsed["display"] or "").lower() or b in normalized]
    if brand_hits:
        for brand in brand_hits:
            official = lexicon.BRANDS[brand]
            domain = sender_domain
            if domain and _registrable_domain(domain) == official:
                continue
            if domain and _registrable_domain(domain) == _normalize_lookalike(brand):
                continue
            impersonated_brands.append(brand.title())
        if impersonated_brands:
            flagged["impersonation"] = True
            score += 3
            findings.append(f"Message impersonates {', '.join(dict.fromkeys(impersonated_brands))} while claiming to be official")

    credential_hits = _has_any(normalized, lexicon.CREDENTIAL_REQUEST_MARKERS)
    if credential_hits:
        flagged["credential_request"] = True
        score += 3
        findings.append("Asks for passwords, OTPs, or personal credentials")
        if impersonated_brands:
            flagged["impersonation"] = True

    payment_hits = _has_any(normalized, lexicon.PAYMENT_REQUEST_MARKERS)
    if payment_hits:
        flagged["payment_request"] = True
        score += 2
        findings.append("Requests a money transfer or unusual payment")

    urgency_hits = _has_any(normalized, lexicon.URGENCY_TACTICS_SECURITY)
    threat_hits = _has_any(normalized, lexicon.THREAT_MARKERS)
    if urgency_hits:
        flagged["urgency_tactics"] = True
        score += 2
        findings.append("Uses urgency or limited-time pressure")
    if threat_hits:
        flagged["threat_tactics"] = True
        score += 2
        findings.append("Uses threats or legal scare tactics")

    attachment_hits = processing.extract_attachment_hints(body)
    if attachment_hits:
        flagged["attachment_risk"] = True
        score += 3
        findings.append(f"Dangerous attachment(s) mentioned: {', '.join(attachment_hits)}")

    if flagged["impersonation"] or flagged["credential_request"] or flagged["payment_request"] or flagged["urgency_tactics"] or flagged["threat_tactics"]:
        if not any("social" in f.lower() for f in findings):
            findings.append("Social engineering: uses impersonation/pressure to manipulate the recipient")
        social_engineering = True

    phishing = any([
        flagged["suspicious_url"],
        flagged["malicious_domain"],
        flagged["impersonation"],
        flagged["credential_request"],
        flagged["attachment_risk"],
        flagged["payment_request"] and (flagged["urgency_tactics"] or flagged["threat_tactics"]),
    ])

    if flagged["suspicious_url"] and flagged["credential_request"]:
        score += 2
        findings.append("Suspicious link combined with credential request: high-leverage phishing chain")

    if score >= 8:
        risk_level = "HIGH"
    elif score >= 4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if risk_level == "HIGH":
        findings = list(dict.fromkeys(["Security risk is HIGH"] + findings))
    elif risk_level == "MEDIUM":
        findings = list(dict.fromkeys(["Security risk is MEDIUM"] + findings))

    recommended_actions = []
    if flagged["suspicious_url"] or flagged["malicious_domain"]:
        recommended_actions.append("Do not click any link in the message")
    if flagged["impersonation"]:
        recommended_actions.append("Do not trust the claimed sender identity")
    if flagged["credential_request"]:
        recommended_actions.append("Never share passwords, OTPs, or personal details")
    if flagged["attachment_risk"]:
        recommended_actions.append("Do not open the attached file")
    if flagged["payment_request"]:
        recommended_actions.append("Verify the payment request through official channels only")
    if phishing:
        recommended_actions.append("Escalate to the security team")

    return {
        "phishing_detected": phishing,
        "risk_level": risk_level,
        "risk_score": score,
        "flags": flagged,
        "suspicious_urls": [u for u in suspicious_urls],
        "malicious_domains": malicious_domains,
        "impersonated_brands": list(dict.fromkeys(impersonated_brands)),
        "social_engineering": social_engineering,
        "credential_requests_found": credential_hits,
        "findings": list(dict.fromkeys(findings)),
        "recommended_actions": recommended_actions,
    }