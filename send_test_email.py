#!/usr/bin/env python3
"""
Send a test email via Composio.
Usage:  python3 send_test_email.py
"""
import urllib.request, json, sys

API_KEY      = "ak_uO0QuhjOhKCm0Ghl4WM-"
TO_EMAIL     = "Mudhass22@gmail.com"
SUBJECT      = "test"
BODY         = "Test email from the HC Physio system via Composio."
BASE         = "https://backend.composio.dev/api/v1"

def api(method, path, payload=None):
    url  = BASE + path
    data = json.dumps(payload).encode() if payload else None
    req  = urllib.request.Request(url, data=data, method=method,
           headers={"X-API-Key": API_KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode() or "{}"), e.code

# 1. List connected accounts
print("Fetching connected accounts…")
data, status = api("GET", "/connectedAccounts")
if status != 200:
    print(f"Error {status}: {data}")
    sys.exit(1)

items = data.get("items") or data.get("connectedAccounts") or []
if not items:
    print("No connected accounts found. Please connect Gmail or Outlook at composio.dev first.")
    sys.exit(1)

# Pick Gmail first, fall back to first account
account = next((a for a in items if "gmail" in (a.get("appName") or "").lower()), items[0])
account_id = account["id"]
app_name   = account.get("appName", "?")
print(f"Using account: {account_id}  ({app_name})")

# 2. Send email
action = "GMAIL_SEND_EMAIL" if "gmail" in app_name.lower() else "MICROSOFT_OUTLOOK_SEND_EMAIL"
payload = {
    "connectedAccountId": account_id,
    "input": {
        "recipient_email": TO_EMAIL,
        "subject":         SUBJECT,
        "body":            BODY,
    }
}

print(f"Sending email to {TO_EMAIL} via {action}…")
result, status = api("POST", f"/actions/{action}/execute", payload)
if status == 200 and (result.get("successfull") or result.get("success") or result.get("data")):
    print(f"✓ Email sent successfully to {TO_EMAIL}")
else:
    print(f"✗ Failed ({status}): {json.dumps(result, indent=2)}")
