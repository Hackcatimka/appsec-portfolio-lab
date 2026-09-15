from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

HeaderBag = dict[str, list[str]]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    title: str
    evidence: str
    remediation: str


def parse_raw_headers(raw: str) -> HeaderBag:
    headers: HeaderBag = {}
    current: str | None = None
    for line in raw.replace("\r\n", "\n").split("\n"):
        if not line.strip() or line.startswith("HTTP/"):
            continue
        if line[:1].isspace() and current:
            headers[current][-1] += " " + line.strip()
            continue
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        current = name.strip().lower()
        headers.setdefault(current, []).append(value.strip())
    return headers


def normalize_headers(items: Iterable[tuple[str, str]]) -> HeaderBag:
    result: HeaderBag = {}
    for name, value in items:
        result.setdefault(name.lower(), []).append(value.strip())
    return result


def _one(headers: HeaderBag, name: str) -> str:
    return ", ".join(headers.get(name, []))


def analyze(headers: HeaderBag, scheme: str = "https") -> list[Finding]:
    findings: list[Finding] = []
    csp = _one(headers, "content-security-policy")
    if not csp:
        findings.append(Finding("headers.missing-csp", "medium", "Content-Security-Policy is missing", "No CSP response header was observed.", "Deploy a restrictive, application-specific CSP and avoid unsafe-inline/unsafe-eval where possible."))
    if scheme == "https" and not _one(headers, "strict-transport-security"):
        findings.append(Finding("headers.missing-hsts", "medium", "HSTS is missing", "HTTPS response has no Strict-Transport-Security header.", "Add HSTS after confirming every subdomain is HTTPS-ready; increase max-age gradually."))
    if _one(headers, "x-content-type-options").lower() != "nosniff":
        findings.append(Finding("headers.missing-nosniff", "low", "MIME sniffing protection is missing", "X-Content-Type-Options is absent or not `nosniff`.", "Send `X-Content-Type-Options: nosniff`."))
    if "frame-ancestors" not in csp.lower() and not _one(headers, "x-frame-options"):
        findings.append(Finding("headers.missing-frame-control", "low", "Framing control is missing", "Neither CSP frame-ancestors nor X-Frame-Options was observed.", "Use CSP `frame-ancestors`; keep X-Frame-Options as legacy defense where needed."))
    if not _one(headers, "referrer-policy"):
        findings.append(Finding("headers.missing-referrer-policy", "low", "Referrer-Policy is missing", "No explicit referrer policy was observed.", "Use `strict-origin-when-cross-origin` or a stricter application-appropriate value."))
    if not _one(headers, "permissions-policy"):
        findings.append(Finding("headers.missing-permissions-policy", "info", "Permissions-Policy is missing", "No browser feature policy was observed.", "Disable unused browser capabilities with a minimal Permissions-Policy."))

    for cookie in headers.get("set-cookie", []):
        name = cookie.split("=", 1)[0].strip() or "<unnamed>"
        attrs = cookie.lower()
        if scheme == "https" and "; secure" not in attrs:
            findings.append(Finding("cookies.missing-secure", "medium", f"Cookie {name} lacks Secure", cookie, "Mark session and sensitive cookies Secure."))
        if "; httponly" not in attrs:
            findings.append(Finding("cookies.missing-httponly", "low", f"Cookie {name} lacks HttpOnly", cookie, "Mark cookies HttpOnly unless client-side JavaScript must read them."))
        if "samesite=" not in attrs:
            findings.append(Finding("cookies.missing-samesite", "low", f"Cookie {name} lacks SameSite", cookie, "Choose SameSite=Lax or Strict; use None only with Secure and a documented cross-site need."))

    server = _one(headers, "server")
    if server and any(char.isdigit() for char in server):
        findings.append(Finding("headers.server-version", "info", "Server header appears to disclose a version", server, "Remove unnecessary product version details at the edge."))
    return findings


def as_jsonable(findings: list[Finding]) -> list[dict[str, str]]:
    return [asdict(item) for item in findings]


def as_markdown(findings: list[Finding], target: str) -> str:
    lines = ["# SitePosture report", "", f"Target: `{target}`", "", f"Findings: **{len(findings)}**", ""]
    if not findings:
        lines.append("No header-posture issues were detected by this limited check.")
        return "\n".join(lines)
    for item in findings:
        lines.extend([f"## [{item.severity.upper()}] {item.title}", "", f"Rule: `{item.rule_id}`", "", f"Evidence: {item.evidence}", "", f"Recommendation: {item.remediation}", ""])
    return "\n".join(lines)
