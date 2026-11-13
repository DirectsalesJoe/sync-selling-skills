"""Look someone up on the Sync Selling Lead Magic account, using your own access code.

Sync Selling members get Lead Magic credits on Revitk's account. Your access code says who you are and
how many credits you have left. It never shows Revitk's Lead Magic key, and nobody else can spend your
credits without your code.

    python3 lookup.py setup ssl_yourcode              save your code once (kept in ~/.sync-selling/access-code)
    python3 lookup.py balance                         how many credits you have left (free)
    python3 lookup.py email --first Jane --last Smith --domain example.co.uk
    python3 lookup.py check-email someone@example.co.uk
    python3 lookup.py role --title "Managing Director" --domain example.co.uk
    python3 lookup.py company --domain example.co.uk
    python3 lookup.py people --domain example.co.uk
    python3 lookup.py mobile --profile-url https://www.linkedin.com/in/someone

Add --json to any lookup to get the full answer. Needs only Python 3.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

GATE = "https://revitk.app.n8n.cloud/webhook/sync-leadmagic"
CODE_FILE = Path.home() / ".sync-selling" / "access-code"


def saved_code():
    code = os.environ.get("SYNC_SELLING_ACCESS_CODE", "").strip()
    if not code and CODE_FILE.exists():
        code = CODE_FILE.read_text().strip()
    if not code:
        sys.exit("No access code yet. Run: python3 lookup.py setup <your code>. "
                 "Sync Selling members get theirs from Revitk.")
    return code


def call(endpoint, payload, code=None):
    body = json.dumps({"endpoint": endpoint, "payload": payload}).encode()
    req = urllib.request.Request(GATE, data=body, method="POST", headers={
        "content-type": "application/json", "X-Access-Code": code or saved_code()})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"error": raw.decode()[:200] or f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        sys.exit(f"Couldn't reach the lookup service: {e.reason}. Check your internet connection and try again.")


def opt(args, flag):
    if flag in args and args.index(flag) + 1 < len(args):
        return args[args.index(flag) + 1]
    return None


def need(args, *flags):
    vals = [opt(args, f) for f in flags]
    missing = [f for f, v in zip(flags, vals) if not v]
    if missing:
        sys.exit("This lookup needs " + ", ".join(missing) + ".")
    return vals


def show(status, out, full):
    if status != 200:
        sys.exit(out.get("error") or f"The lookup failed ({status}).")
    if full:
        print(json.dumps(out, indent=2))
    else:
        r = out.get("result", {})
        keep = {k: v for k, v in r.items() if k in (
            "email", "status", "email_status", "message", "first_name", "last_name", "full_name", "job_title", "title",
            "company_name", "company_domain", "domain", "profile_url", "mobile_number", "employees",
            "data", "total", "industry", "employee_count", "website", "linkedin_url")}
        print(json.dumps(keep or r, indent=2)[:4000])
    left = out.get("credits_left")
    if left is not None:
        print(f"Credits used: {out.get('credits_used', 0):g}. Credits left: {left:g}.")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, full = a[0], "--json" in a
    if cmd == "setup":
        if len(a) < 2:
            sys.exit("Run: python3 lookup.py setup <your code>")
        code = a[1].strip()
        status, out = call("balance", {}, code=code)
        if status != 200:
            sys.exit(out.get("error") or f"That code didn't work ({status}).")
        CODE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CODE_FILE.write_text(code)
        os.chmod(CODE_FILE, 0o600)
        print(f"Saved. Hello {out['name']}: you have {out['credits_left']:g} credits.")
        return
    if cmd == "balance":
        status, out = call("balance", {})
        if status != 200:
            sys.exit(out.get("error") or f"The check failed ({status}).")
        print(f"{out['credits_left']:g} credits left of {out['limit']:g}.")
        return
    if cmd == "email":
        first, last, domain = need(a, "--first", "--last", "--domain")
        show(*call("email-finder", {"first_name": first, "last_name": last, "domain": domain}), full)
    elif cmd == "check-email":
        if len(a) < 2:
            sys.exit("Run: python3 lookup.py check-email someone@example.co.uk")
        show(*call("email-validate", {"email": a[1]}), full)
    elif cmd == "role":
        title, domain = need(a, "--title", "--domain")
        show(*call("role-finder", {"company_domain": domain, "job_title": title}), full)
    elif cmd == "company":
        (domain,) = need(a, "--domain")
        show(*call("company-search", {"company_domain": domain}), full)
    elif cmd == "people":
        (domain,) = need(a, "--domain")
        show(*call("employee-finder", {"company_domain": domain, "limit": int(opt(a, "--limit") or 50)}), full)
    elif cmd == "mobile":
        (url,) = need(a, "--profile-url")
        show(*call("mobile-finder", {"profile_url": url}), full)
    else:
        sys.exit(f"Unknown lookup '{cmd}'. Run python3 lookup.py --help to see them.")


if __name__ == "__main__":
    main()
