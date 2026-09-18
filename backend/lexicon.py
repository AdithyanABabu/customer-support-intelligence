POSITIVE_WORDS = {
    "happy", "great", "excellent", "amazing", "wonderful", "fantastic", "awesome",
    "delighted", "pleased", "satisfied", "good", "best", "love", "perfect",
    "helpful", "quick", "fast", "smooth", "resolved", "fixed", "works", "thank",
    "thanks", "appreciate", "grateful", "glad", "reliable", "convenient", "easy",
    "friendly", "polite", "professional", "superb", "brilliant", "outstanding",
    "impressive", "excellent", "solid", "strong", "greatful", "like", "enjoy",
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "disappointed", "disappointing",
    "frustrated", "frustrating", "annoyed", "annoying", "upset", "unhappy",
    "angry", "furious", "mad", "livid", "pissed", "hate", "waste", "useless",
    "broken", "defective", "damaged", "faulty", "failed", "failure", "error",
    "problem", "issue", "wrong", "unacceptable", "ridiculous", "incompetent",
    "unhelpful", "unreliable", "slow", "late", "delay", "delayed", "missing",
    "lost", "stuck", "scam", "fraud", "stolen", "hacked", "refund", "cancel",
    "cancelled", "charge", "charged", "billing", "overcharged", "poor", "cheap",
    "useless", "worst", "awful", "horrible", "exasperated", "outraged", "irritated",
}

ANGER_WORDS = {
    "angry", "furious", "mad", "livid", "pissed", "outraged", "irritated",
    "rage", "fuming", "enraged",
}

NEGATION_WORDS = {
    "not", "no", "never", "nothing", "none", "cannot", "cant", "dont", "doesnt",
    "didnt", "isnt", "arent", "wasnt", "werent", "wont", "shouldnt", "wouldnt",
    "without",
}

INTENSIFIERS = {
    "very", "extremely", "really", "totally", "absolutely", "completely",
    "horribly", "incredibly", "so", "super", "utterly",
}

TOPIC_KEYWORDS = {
    "refund": [
        "refund", "reimburse", "money back", "chargeback", "return my money",
        "cash back", "refund request", "get my money",
    ],
    "payment": [
        "payment", "billing", "invoice", "transaction", "debit", "credit",
        "charged twice", "double charge", "payment failed", "card declined",
        "money taken", "subscription charge", "billing error", "overcharge",
    ],
    "delivery": [
        "order", "shipping", "shipment", "package", "parcel", "tracking",
        "dispatch", "delivered", "arrived", "hasn't arrived", "not arrived",
        "out for delivery", "delivery date", "delay", "late", "missing package",
        "lost in transit", "delivery status", "order status", "track my order",
        "where is my order",
    ],
    "login_account": [
        "login", "log in", "sign in", "password", "cannot access", "locked out",
        "verify", "verification code", "two-step", "two factor", "2fa", "otp",
        "authenticate", "access my account", "reset password", "forgot password",
        "account access",
    ],
    "product_problem": [
        "broken", "defective", "damaged", "not working", "doesn't work",
        "doest work", "faulty", "error", "bug", "malfunction", "glitch",
        "crashed", "freezes", "won't turn on", "dead on arrival", "cracked screen",
        "not responding", "defect", "firmware", "software issue",
    ],
    "account_security": [
        "suspicious activity", "hacked", "compromised", "unauthorized",
        "fraud", "stolen", "identity", "account closed", "account suspended",
        "account locked", "security", "unusual activity", "unauthorized charge",
    ],
    "cancellation": [
        "cancel", "cancellation", "unsubscribe", "cancel my subscription",
        "stop", "terminate", "close my account", "end my plan",
    ],
}

URGENCY_MARKERS = [
    "urgent", "asap", "immediately", "as soon as possible", "right away",
    "right now", "today", "tonight", "within 24", "within 48", "this week",
    "deadline", "expires", "limited time", "will be closed", "will be suspended",
    "will be deleted", "last day", "hurry", "act now", "respond fast",
    "time sensitive", "immediate", "high priority", "before it's too late",
]

CREDENTIAL_REQUEST_MARKERS = [
    "password", "otp", "one-time passcode", "one time passcode", "pin code",
    "login details", "sign in to verify", "verify your account", "verify your identity",
    "confirm your details", "card number", "cvv", "ssn", "social security",
    "bank account", "routing number", "confirm your password", "click and sign in",
    "enter your password", "send me the code", "security code", "credit card details",
    "date of birth", "mother's maiden name", "secret question",
]

URGENCY_TACTICS_SECURITY = [
    "within 24", "within the next 24", "immediately", "act now", "limited time",
    "before your account is deleted", "before your account is closed",
    "will be permanently disabled", "final notice", "act fast", "hurry",
    "don't delay", "at once", "right away", "urgent action required",
    "immediate response required", "last chance",
]

PAYMENT_REQUEST_MARKERS = [
    "wire transfer", "bitcoin", "crypto", "gift card", "western union",
    "moneygram", "processing fee", "activation fee", "send money", "cash app",
    "zelle", "paycheck", "refund requires", "claim your refund", "inheritance",
]

THREAT_MARKERS = [
    "account will be suspended", "account will be closed", "will be deleted",
    "legal action", "lawsuit", "reported to the police", "you will be fined",
    "penalty", "arrest", "court", "federal", "authorities", "audit",
    "freeze your account", "confiscate", "criminal",
]

BRANDS = {
    "paypal": "paypal.com",
    "amazon": "amazon.com",
    "apple": "apple.com",
    "microsoft": "microsoft.com",
    "google": "google.com",
    "facebook": "facebook.com",
    "instagram": "instagram.com",
    "whatsapp": "whatsapp.com",
    "netflix": "netflix.com",
    "chase": "chase.com",
    "wellsfargo": "wellsfargo.com",
    "bank of america": "bankofamerica.com",
    "hsbc": "hsbc.com",
    "citibank": "citibank.com",
    "amex": "americanexpress.com",
    "visa": "visa.com",
    "mastercard": "mastercard.com",
    "stripe": "stripe.com",
    "square": "squareup.com",
    "binance": "binance.com",
    "coinbase": "coinbase.com",
    "ebay": "ebay.com",
    "walmart": "walmart.com",
    "bestbuy": "bestbuy.com",
    "target": "target.com",
    "fedex": "fedex.com",
    "ups": "ups.com",
    "dhl": "dhl.com",
    "usps": "usps.com",
    "steam": "steampowered.com",
    "spotify": "spotify.com",
    "payoneer": "payoneer.com",
    "stripe": "stripe.com",
    "revolut": "revolut.com",
    "wise": "wise.com",
}

URL_SHORTENERS = {
    "bit.ly", "goo.gl", "tinyurl.com", "t.co", "ow.ly", "is.gd", "buff.ly",
    "cutt.ly", "rebrand.ly", "bitly.com", "shorturl.at", "rb.gy", "tiny.cc",
    "qr.ae", "s.id",
}

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "click", "link", "club",
    "online", "site", "buzz", "icu", "info", "icu", "stream", "review",
    "country", "work", "vip", "party", "kim", "gdn",
}

SUSPICIOUS_DOMAIN_KEYWORDS = [
    "verify", "paypa1", "secure-", "-secure", "login", "signin", "account",
    "alert", "update", "billing-", "-billing", "unlock", "prize", "winner",
    "bonus", "help", "support-", "-service", "customerservice", "hotmail1",
    "gmail-", "-gmail", "0", "1", "2", "9",
]

BRAND_HOMOGLYPHS = {
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "6": "g", "7": "t",
    "8": "b", "9": "g", "l": "l",
}

DANGEROUS_ATTACHMENT_EXTENSIONS = [
    ".exe", ".scr", ".bat", ".cmd", ".pif", ".js", ".ps1", ".vbs",
    ".wsf", ".jar", ".apk", ".msi", ".hta", ".iso", ".docm", ".xlsm",
    ".cpl", ".reg", ".lnk",
]