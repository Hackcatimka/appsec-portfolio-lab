import unittest

from siteposture.analyzer import analyze, parse_raw_headers


class AnalyzerTests(unittest.TestCase):
    def test_secure_example_has_no_findings(self):
        raw = """HTTP/2 200
Content-Security-Policy: default-src 'self'; frame-ancestors 'none'
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Permissions-Policy: camera=()
Set-Cookie: session=x; Secure; HttpOnly; SameSite=Lax
"""
        self.assertEqual(analyze(parse_raw_headers(raw), "https"), [])

    def test_missing_headers_and_cookie_flags_are_reported(self):
        findings = analyze(parse_raw_headers("Set-Cookie: session=x\n"), "https")
        rules = {item.rule_id for item in findings}
        self.assertIn("headers.missing-csp", rules)
        self.assertIn("headers.missing-hsts", rules)
        self.assertIn("cookies.missing-secure", rules)
        self.assertIn("cookies.missing-httponly", rules)
        self.assertIn("cookies.missing-samesite", rules)

    def test_duplicate_set_cookie_headers_are_preserved(self):
        headers = parse_raw_headers("Set-Cookie: a=1; Secure\nSet-Cookie: b=2; Secure\n")
        self.assertEqual(len(headers["set-cookie"]), 2)


if __name__ == "__main__":
    unittest.main()


