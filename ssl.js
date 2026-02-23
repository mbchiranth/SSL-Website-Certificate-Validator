// ---------- CLEAN DOMAIN ----------
function cleanDomain(input) {
    return input
        .replace(/^https?:\/\//, "")
        .replace(/\/.*$/, "")
        .trim();
}

// ---------- SET UI STATE ----------
function setState(id, text, state) {
    const el = document.getElementById(id);
    if (el) {
        el.innerText = text;
        if (state) el.className = state;
    }
}

// ---------- HOME PAGE ----------
const analyzeBtn = document.getElementById("analyzeBtn");

if (analyzeBtn) {
    analyzeBtn.addEventListener("click", function () {
        let domain = document.getElementById("domain").value.trim();

        if (!domain) {
            alert("Enter a valid domain");
            return;
        }

        domain = cleanDomain(domain);

        window.location.href =
            "process.html?domain=" + encodeURIComponent(domain);
    });
}

// ---------- PROCESS PAGE ----------
if (window.location.pathname.includes("process.html")) {

    const params = new URLSearchParams(window.location.search);
    let domain = params.get("domain");

    if (!domain) {
        alert("No domain provided");
        window.location.href = "ssl.html";
    } else {
        domain = cleanDomain(domain);

        const display = document.getElementById("domainDisplay");
        if (display) {
            display.innerText = "Analyzing: " + domain;
        }

        analyzeDomain(domain);
    }
}

// ---------- BACK BUTTON ----------
const backBtn = document.getElementById("backBtn");

if (backBtn) {
    backBtn.addEventListener("click", function () {
        window.location.href = "ssl.html";
    });
}

// ---------- ANALYZE DOMAIN ----------
function analyzeDomain(domain) {

    setState("health", "Checking...", "waiting");
    setState("grade", "Analyzing...", "waiting");
    setState("expiry", "Fetching...", "waiting");
    setState("issuer", "Fetching...", "waiting");
    setState("issued_on", "Fetching...", "waiting");
    setState("cert_type", "Fetching...", "waiting");
    setState("valid_sans", "Fetching...", "waiting");

    fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ domain: domain })
    })
    .then(res => res.json())
    .then(data => {

        if (data.error) {
            setState("health", "Error", "error");
            setState("grade", "-", "error");
            setState("expiry", data.error, "error");
            return;
        }

        setState("health", data.certificate_health, "success");
        setState("grade", data.certificate_grade, "success");
        setState("expiry", data.expiry_date, "success");
        setState("issuer", data.issuer, "success");
        setState("issued_on", data.issued_on, "success");
        setState("cert_type", data.cert_type, "success");

        if (data.valid_sans && data.valid_sans.length > 0) {
            setState("valid_sans", data.valid_sans.join(", "), "success");
        } else {
            setState("valid_sans", "No SANs found", "error");
        }

    })
    .catch(() => {
        setState("health", "Backend not running", "error");
        setState("grade", "-", "error");
        setState("expiry", "Start Flask server", "error");
    });
}
