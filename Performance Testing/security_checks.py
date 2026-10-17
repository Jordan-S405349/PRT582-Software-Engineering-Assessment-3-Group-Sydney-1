"""
security_checks.py - automated manual-security checks for Form E (SEC-02 to SEC-12).

Run ONLY against your own local copy of the app:
    1. Start the app (it must be running at BASE below).
    2. Make sure the test account exists (same one as locustfile.py).
    3. python security_checks.py

It prints one line per check with PASS / FAIL / INFO and saves the same text to
results/security_checks.txt. Copy each line's result into the matching row of the
"manual security test cases" table. Checks that need a human (SEC-06 other-user
access, SEC-13 payment tampering) are NOT done here - do those by hand.
"""
import os
import re
import sys

import requests

BASE = os.environ.get("BASE", "http://127.0.0.1:8000")
LOGIN = "/login/"
SEARCH = "/search/"
BOOKINGS = "/booking/"
USER = os.environ.get("TEST_USER", "loadtest@example.com")
PASS = os.environ.get("TEST_PASS", "TestPass123")
USER_FIELD, PASS_FIELD = "email", "password"   # from your login form

lines = []


def out(sec, status, detail):
    text = f"{sec} | {status} | {detail}"
    print(text)
    lines.append(text)


def token_from(session, html=""):
    m = re.search(r"""name=["']csrfmiddlewaretoken["'][^>]*value=["']([^"']+)""", html)
    return (m.group(1) if m else None) or session.cookies.get("csrftoken", "")


def login(session):
    page = session.get(BASE + LOGIN)
    tok = token_from(session, page.text)
    r = session.post(BASE + LOGIN, data={USER_FIELD: USER, PASS_FIELD: PASS, "csrfmiddlewaretoken": tok},
                     headers={"Referer": BASE + LOGIN})
    ok = session.get(BASE + BOOKINGS).status_code == 200
    return ok


def run():
    try:
        requests.get(BASE, timeout=5)
    except Exception as e:
        print("Cannot reach the app at", BASE, "-", e)
        sys.exit(1)

    # SEC-02 logged-out access to a protected page
    r = requests.get(BASE + BOOKINGS)
    if r.status_code in (301, 302, 303, 307, 308) or (r.status_code == 200 and "login" in r.url.lower()):
        out("SEC-02", "PASS", f"logged-out visit to {BOOKINGS} handled (status {r.status_code})")
    else:
        out("SEC-02", "FAIL", f"logged-out visit to {BOOKINGS} returned HTTP {r.status_code} instead of redirecting to login")

    # SEC-03 SQL injection in search
    bad = ("sql", "syntax error", "operationalerror", "programmingerror", "traceback", "database error")
    problems = []
    for p in ["'", "' OR '1'='1", "' UNION SELECT 1--", "\" OR \"1\"=\"1"]:
        r = requests.get(BASE + SEARCH, params={"q": p})
        if r.status_code >= 500 or any(w in r.text.lower() for w in bad):
            problems.append(f"payload {p!r} -> HTTP {r.status_code}")
    out("SEC-03", "FAIL" if problems else "PASS",
        "; ".join(problems) if problems else "4 injection payloads in search: no server error or database error shown")

    # SEC-04 reflected XSS
    payload = "<script>alert(1)</script>"
    r = requests.get(BASE + SEARCH, params={"q": payload})
    if payload in r.text:
        out("SEC-04", "FAIL", "search text is reflected unescaped in the page (script tag present)")
    elif "&lt;script&gt;" in r.text:
        out("SEC-04", "PASS", "search text is reflected but HTML-escaped (shown as text, not run)")
    else:
        out("SEC-04", "PASS", "script payload is not reflected in the page")

    # SEC-05 CSRF
    s = requests.Session()
    page = s.get(BASE + LOGIN)
    has_input = bool(re.search(r"""name=["']csrfmiddlewaretoken["']""", page.text))
    has_cookie = "csrftoken" in s.cookies
    r = s.post(BASE + LOGIN, data={USER_FIELD: USER, PASS_FIELD: PASS})   # no token sent
    logged_in = s.get(BASE + BOOKINGS).status_code == 200
    if r.status_code == 403:
        out("SEC-05", "PASS", f"POST without CSRF token rejected with 403 (token in form: {has_input}, cookie: {has_cookie})")
    elif logged_in:
        out("SEC-05", "FAIL", f"login POST accepted WITHOUT a CSRF token (token in form: {has_input}, cookie: {has_cookie}) - CSRF not enforced")
    else:
        out("SEC-05", "INFO", f"POST without token got HTTP {r.status_code} and no login (token in form: {has_input}, cookie: {has_cookie}) - check by hand")

    # SEC-07 brute force
    s = requests.Session()
    s.get(BASE + LOGIN)
    locked = False
    codes = set()
    for i in range(15):
        tok = s.cookies.get("csrftoken", "")
        r = s.post(BASE + LOGIN, data={USER_FIELD: USER, PASS_FIELD: "wrong-password-%d" % i, "csrfmiddlewaretoken": tok},
                   headers={"Referer": BASE + LOGIN})
        codes.add(r.status_code)
        if r.status_code in (403, 429) or "locked" in r.text.lower() or "too many" in r.text.lower():
            locked = True
            break
    out("SEC-07", "PASS" if locked else "FAIL",
        ("lockout or rate limit triggered after %d attempts" % (i + 1)) if locked
        else f"15 wrong passwords in a row, no lockout or rate limit (HTTP codes seen: {sorted(codes)})")

    # SEC-08 session cookies
    s = requests.Session()
    if login(s):
        for c in s.cookies:
            if c.name.lower() in ("sessionid", "csrftoken"):
                rest = {k.lower(): v for k, v in c._rest.items()}
                out("SEC-08", "INFO", f"cookie {c.name}: HttpOnly={'httponly' in rest}, Secure={bool(c.secure)}, SameSite={rest.get('samesite', 'not set')}")
        s.get(BASE + "/logout/")
        after = s.get(BASE + BOOKINGS).status_code
        out("SEC-08", "INFO", f"after visiting /logout/, My Bookings returns HTTP {after} (200 = still logged in, check the real logout address)")
    else:
        out("SEC-08", "INFO", "could not log in with TEST_USER / TEST_PASS - register the account first")

    # SEC-09 debug information disclosure
    r = requests.get(BASE + "/this-page-does-not-exist-xyz/")
    markers = ("You're seeing this error because you have", "Using the URLconf", "DEBUG = True")
    if any(m in r.text for m in markers):
        out("SEC-09", "FAIL", "unknown URL shows the Django debug page (DEBUG = True), exposing settings and URL patterns")
    else:
        out("SEC-09", "PASS", f"unknown URL returns a normal error page (HTTP {r.status_code}), no debug details")
    r2 = requests.get(BASE + BOOKINGS)
    if r2.status_code >= 500:
        leaked = "Traceback" in r2.text or "Exception Value" in r2.text
        out("SEC-09", "FAIL" if leaked else "INFO",
            "the 500 error page shows a stack trace" if leaked else "the 500 error page does not show a stack trace")

    # SEC-10 security headers
    h = requests.get(BASE).headers
    for name in ["X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy",
                 "Strict-Transport-Security", "Referrer-Policy"]:
        out("SEC-10", "PASS" if name in h else "FAIL", f"{name}: {h.get(name, 'MISSING')}")

    # SEC-11 Django version
    try:
        import django
        out("SEC-11", "INFO", f"Django version in this environment: {django.get_version()}")
    except ImportError:
        out("SEC-11", "INFO", "Django not installed here - run: pip show django   (in the app's environment)")

    # SEC-12 admin panel exposure
    r = requests.get(BASE + "/admin/login/")
    out("SEC-12", "FAIL" if r.status_code == 200 else "PASS",
        f"/admin/login/ returned HTTP {r.status_code}" + (" - admin login is reachable on the default path" if r.status_code == 200 else ""))


if __name__ == "__main__":
    run()
    os.makedirs("results", exist_ok=True)
    with open(os.path.join("results", "security_checks.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\nSaved to results/security_checks.txt")