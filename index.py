from flask import Flask, request, jsonify
from flask_cors import CORS
import ssl
import socket
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

TRUSTED_ISSUERS = [
    "DigiCert",
    "GlobalSign",
    "Let's Encrypt",
    "Sectigo",
    "GoDaddy",
    "Amazon",
    "Google Trust Services",
    "Cloudflare"
]

# ---------------- CLEAN DOMAIN ----------------
def clean_domain(domain: str) -> str:
    domain = domain.strip()
    domain = domain.replace("https://", "").replace("http://", "")
    return domain.rstrip("/")


# ---------------- TLS CHECK ----------------
def supports_tls(domain, version):
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = version
        context.maximum_version = version
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((domain, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=domain):
                return True
    except Exception:
        return False


def check_protocols(domain):
    protocol_versions = [
        ("TLS 1.0", ssl.TLSVersion.TLSv1),
        ("TLS 1.1", ssl.TLSVersion.TLSv1_1),
        ("TLS 1.2", ssl.TLSVersion.TLSv1_2),
        ("TLS 1.3", ssl.TLSVersion.TLSv1_3),
    ]

    results = []

    for name, version in protocol_versions:
        try:
            supported = supports_tls(domain, version)
        except Exception:
            supported = False

        if name in ["TLS 1.0", "TLS 1.1"]:
            is_secure = not supported
        else:
            is_secure = supported

        results.append({
            "name": name,
            "supported": supported,
            "is_secure": is_secure
        })

    return results


# ---------------- CERTIFICATE INFO ----------------
def get_cert_info(domain):
    context = ssl.create_default_context()

    with socket.create_connection((domain, 443), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert = ssock.getpeercert()

    expiry_date = datetime.strptime(
        cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
    ).replace(tzinfo=timezone.utc)

    issued_date = datetime.strptime(
        cert["notBefore"], "%b %d %H:%M:%S %Y %Z"
    ).replace(tzinfo=timezone.utc)

    issuer = "Unknown"
    for part in cert.get("issuer", []):
        for key, value in part:
            if key == "organizationName":
                issuer = value

    sans = [
        item[1].lower()
        for item in cert.get("subjectAltName", [])
        if item[0] == "DNS"
    ]

    cn = ""
    for part in cert.get("subject", []):
        for key, value in part:
            if key == "commonName":
                cn = value.lower()

    org = None
    country = None
    for part in cert.get("subject", []):
        for key, value in part:
            if key == "organizationName":
                org = value
            if key == "countryName":
                country = value

    if org and country:
        cert_type = "EV"
    elif org:
        cert_type = "OV"
    else:
        cert_type = "DV"

    return {
        "issuer": issuer,
        "issued_on": issued_date.strftime("%Y-%m-%d"),
        "expiry_date": expiry_date.strftime("%Y-%m-%d"),
        "valid_sans": sans,
        "common_name": cn,
        "cert_type": cert_type,
        "expiry_obj": expiry_date
    }


# ---------------- GRADE + SCORE CALCULATION ----------------
def calculate_grade_and_score(expiry_date, domain_match, trusted_issuer, cert_type, protocols):

    now = datetime.now(timezone.utc)
    days_left = (expiry_date - now).days
    score = 100
    breakdown = []

    # Expiry
    if days_left <= 0:
        breakdown.append("Certificate expired")
        return "F", 0, days_left, breakdown

    if days_left < 30:
        score -= 30
        breakdown.append("Less than 30 days remaining (-30)")
    elif days_left < 180:
        score -= 15
        breakdown.append("Less than 180 days remaining (-15)")
    else:
        breakdown.append("Sufficient validity period")

    # Domain match
    if not domain_match:
        breakdown.append("Domain mismatch (Critical)")
        score = 0
    else:
        breakdown.append("Domain matches certificate")

    # Issuer trust
    if not trusted_issuer:
        score -= 20
        breakdown.append("Untrusted issuer (-20)")
    else:
        breakdown.append("Trusted Certificate Authority")

    # Protocol security
    insecure_protocols = [p["name"] for p in protocols if not p["is_secure"]]

    if insecure_protocols:
        score -= 20
        breakdown.append(
            f"Insecure protocols enabled: {', '.join(insecure_protocols)} (-20)"
        )
    else:
        breakdown.append("Only secure TLS versions enabled")

    # Certificate type weight
    if cert_type == "DV":
        score -= 5
        breakdown.append("Domain Validation only (-5)")
    elif cert_type == "EV":
        score += 5
        breakdown.append("Extended Validation (+5)")

    score = max(0, min(score, 100))

    # Grade mapping
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 65:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "F"

    return grade, score, days_left, breakdown


# ---------------- ROUTE ----------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not data or "domain" not in data:
        return jsonify({"error": "No domain provided"}), 400

    domain = clean_domain(data["domain"])

    if not domain:
        return jsonify({"error": "Invalid domain"}), 400

    try:
        info = get_cert_info(domain)

        domain_match = (
            domain.lower() in info["valid_sans"]
            or domain.lower() == info["common_name"]
        )

        trusted_issuer = any(
            name.lower() in info["issuer"].lower()
            for name in TRUSTED_ISSUERS
        )

        protocols = check_protocols(domain)

        grade, score, days_left, breakdown = calculate_grade_and_score(
            info["expiry_obj"],
            domain_match,
            trusted_issuer,
            info["cert_type"],
            protocols
        )

        # Health logic
        if days_left <= 0:
            health = "Expired"
        elif not domain_match:
            health = "Invalid for domain"
        elif not trusted_issuer:
            health = "Untrusted Certificate"
        else:
            health = "Active"

        return jsonify({
            "domain": domain,
            "certificate_health": health,
            "certificate_grade": grade,
            "expiry_date": info["expiry_date"],
            "issuer": info["issuer"],
            "issued_on": info["issued_on"],
            "cert_type": info["cert_type"],
            "valid_sans": info["valid_sans"],
            "vulnerabilities": protocols,
            "days_remaining": days_left,
            "trusted_issuer": trusted_issuer,
            "domain_match": domain_match,
            "security_score": score,
            "score_breakdown": breakdown
        })

    except Exception:
        return jsonify({"error": "SSL analysis failed"}), 500


if __name__ == "__main__":
    app.run(debug=True)
