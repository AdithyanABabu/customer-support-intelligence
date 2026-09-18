import re
import ipaddress

URL_RE = re.compile(r"(?i)\b((?:https?://|www\.)[^\s<>\"']+)")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
IPV4_RE = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
ATTACHMENT_RE = re.compile(r"(?i)attach(?:ed|ment)?[^\S\r\n]{0,20}[\"'(]?([\w.\- ]+\.(?:exe|scr|bat|cmd|pif|js|ps1|vbs|wsf|jar|apk|msi|hta|iso|docm|xlsm|cpl|reg|lnk))[\"')]?")
FILENAME_RE = re.compile(r"(?i)([\w.\- ]+\.(?:exe|scr|bat|cmd|pif|js|ps1|vbs|wsf|jar|apk|msi|hta|iso|docm|xlsm|cpl|reg|lnk))")
ORDER_NUMBER_RE = re.compile(r"(?i)\b(?:order|invoice|ref(?:erence)?|ticket)\s*(?:no\.?|number|#|:)?\s*([a-z0-9]*\d[a-z0-9-]*)\b")
AMOUNT_RE = re.compile(r"(?i)(\$\s?\d+(?:[.,]\d{1,2})?|\d+\s*(?:usd|euro|dollars|pounds))")


def to_text(value):
    return "" if value is None else str(value).strip()


def dedupe_preserving_order(items):
    seen = set()
    result = []
    for item in items:
        key = item.lower().strip().rstrip(".,;")
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


def clean_url(raw):
    return raw.strip().rstrip(".,;:!?\"')]}>")


def extract_urls(text):
    if not text:
        return []
    urls = [clean_url(m.group(0)) for m in URL_RE.finditer(text)]
    return dedupe_preserving_order(urls)


def extract_emails(text):
    if not text:
        return []
    emails = [m.group(0) for m in EMAIL_RE.finditer(text)]
    return dedupe_preserving_order(emails)


def extract_attachment_hints(text):
    if not text:
        return []
    if "attach" in text.lower() or "attachment" in text.lower():
        found = [m.group(0) for m in FILENAME_RE.finditer(text)]
        return dedupe_preserving_order(found)
    return []


def extract_order_numbers(text):
    if not text:
        return []
    numbers = []
    for m in ORDER_NUMBER_RE.finditer(text):
        numbers.append(m.group(1))
    return dedupe_preserving_order(numbers)


def extract_amounts(text):
    if not text:
        return []
    return dedupe_preserving_order([m.group(0) for m in AMOUNT_RE.finditer(text)])


def is_ip_literal(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def parse_sender(from_header):
    header = to_text(from_header)
    email = None
    match = EMAIL_RE.search(header)
    if match:
        email = match.group(0)
    quoted = re.search(r"\"([^\"]+)\"", header)
    display = quoted.group(1).strip() if quoted else None
    if display is None and email and header:
        before = header.split("@")[0]
        cleaned = before.strip("<> ,")
        if cleaned and cleaned.lower() not in ("from", "re", "to"):
            display = cleaned
    domain = email.split("@")[1].lower() if email and "@" in email else None
    return {
        "raw": header,
        "display": display,
        "email": email,
        "domain": domain,
    }


def _split_headers(text):
    from_header = ""
    subject = ""
    body_lines = []
    in_headers = True
    for line in text.splitlines():
        if in_headers:
            lower = line.strip().lower()
            if lower.startswith("from:"):
                from_header = line.split(":", 1)[1].strip()
                continue
            if lower.startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                continue
            if lower in ("to:", "cc:", "date:") or lower.startswith(("to:", "cc:", "date:")):
                continue
            if line.strip() == "":
                in_headers = False
                continue
            in_headers = False
        body_lines.append(line)
    return from_header, subject, "\n".join(body_lines).strip()


def parse_message(text):
    text = to_text(text)
    from_header, subject, body = _split_headers(text)
    return {
        "from_header": from_header,
        "subject": subject,
        "body": body or text,
        "sender": parse_sender(from_header),
        "urls": extract_urls(text),
        "emails": extract_emails(text),
        "attachments": extract_attachment_hints(text),
        "order_numbers": extract_order_numbers(text),
        "amounts": extract_amounts(text),
    }


def normalize_text(text):
    text = to_text(text)
    text = text.lower()
    text = re.sub(r"[\s_]+", " ", text)
    return text