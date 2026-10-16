# HTB Kobold - Writeup

- **Difficulty:** Medium
- **OS:** Linux (Ubuntu 24.04)
- **Attack path:** MCPJam Inspector RCE → PrivateBin LFI → Credential Reuse → Arcane Docker Escape

## 1. Reconnaissance

### Port Scanning

```bash
nmap -p- --min-rate 5000 -T4 kobold.htb -oN nmap_all.txt
nmap -sV -sC -p 22,80,443,3552 kobold.htb -oN nmap_services.txt
```

**Results:**

```text
PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 9.6p1 Ubuntu 3ubuntu13.15
80/tcp   open  http     nginx 1.24.0 (Ubuntu) [redirects to 443]
443/tcp  open  ssl/http nginx 1.24.0 (Ubuntu)
|_http-title: Kobold Operations Suite
| ssl-cert: Subject: commonName=kobold.htb
| Subject Alternative Name: DNS:kobold.htb, DNS:*.kobold.htb
3552/tcp open  http     Golang net/http server
```

### Add the Host to `/etc/hosts`

```bash
echo "<IP> kobold.htb" | sudo tee -a /etc/hosts
```

### Virtual Host Enumeration

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -u https://kobold.htb/ \
  -H "Host: FUZZ.kobold.htb" \
  -fs 0 -t 100 -k
```

**Discovered virtual hosts:**

- `bin.kobold.htb` - PrivateBin 2.0.2
- `mcp.kobold.htb` - MCPJam Inspector

Add them to `/etc/hosts`:

```bash
echo "<IP> bin.kobold.htb mcp.kobold.htb" | sudo tee -a /etc/hosts
```

## 2. Foothold - MCPJam Inspector RCE (CVE-2026-23744)

### Identification

`mcp.kobold.htb` hosts an MCPJam Inspector instance (versions ≤ 1.4.2). The service exposes an unauthenticated `/api/mcp/connect` endpoint that accepts a user-supplied `serverConfig` object. Its `command` and `args` fields are passed to `child_process.spawn()` without sanitisation.

### Exploit

The proof of concept sends a reverse-shell payload using the vulnerable endpoint.

### Shell Access

The exploit provides a shell as `ben` on the host:

```bash
id
```

```text
uid=1000(ben) gid=1000(ben) groups=1000(ben),1001(operator)
```

### User Flag

```bash
cat /home/ben/user.txt
```


## 3. Write Primitive - PrivateBin Data Directory

During enumeration, we discover that the `operator` group has write access to `/privatebin-data/data/`.

This directory is bind-mounted into the PrivateBin container as `/srv/data`, allowing a PHP file written on the host to be accessed from inside the container.

## 4. PrivateBin LFI → RCE (CVE-2025-64714)

PrivateBin versions 1.7.7–2.0.2 are vulnerable to Local File Inclusion through the template cookie. By using a path traversal payload in the `template` cookie, the application can include the writable PHP file.

The result is remote command execution inside the PrivateBin container as `nobody`.

## 5. Credential Harvesting - PrivateBin Configuration

The PrivateBin configuration file at `/srv/cfg/conf.php` contains database credentials that were accidentally left uncommented.

The recovered password is reused to authenticate to the Arcane web interface.

## 6. Privilege Escalation - Arcane (Port 3552)

Arcane is a self-hosted Docker management platform running as root. Its systemd service configuration confirms the root execution context, and the service has access to the host Docker socket.

### Credential Reuse

- **URL:** `http://kobold.htb:3552/`
- **Username:** `arcane`
- **Password:** `ComplexP@sswordAdmin1928`

### Docker Escape

Using Arcane's container management interface, a container is configured with the host filesystem mounted at `/host` with read/write access.

The host's root flag is then accessible from within the container at `/host/root/root.txt`.



## 7. Summary

| Stage | Technique | Result |
|---|---|---|
| Recon | Nmap and virtual host enumeration | Discovered `bin.kobold.htb`, `mcp.kobold.htb` and Arcane on port 3552 |
| Foothold | MCPJam Inspector RCE | Shell as `ben` |
| Write primitive | Writable PrivateBin data directory | PHP file placed in shared directory |
| RCE | PrivateBin LFI via template cookie | Shell as `nobody` |
| Credential theft | Credentials exposed in `conf.php` | Password recovered |
| Credential reuse | Arcane web interface | Authenticated as `arcane` |
| Privilege escalation | Arcane and Docker bind mount | Root filesystem access |

