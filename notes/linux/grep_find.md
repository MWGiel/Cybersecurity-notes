# locate & grep - Raw Notes

## locate
- **Purpose:** Find files by name on the entire system.
- **Speed:** Extremely fast (uses a pre-built database, not real-time search).
- **Database:** `/var/lib/mlocate/mlocate.db` (updated via `updatedb` command).
- **Relevance:** Not installed by default on minimal/container systems (HTB often lacks it).

**Syntax:**
locate [OPTIONS] PATTERN

**Common Options:**
- `-i` : Case insensitive search.
- `-c` : Count matching entries instead of printing them.
- `-l N` : Limit output to N results (e.g., `-l 10`).
- `-r` : Use REGEX pattern instead of simple string.

**Examples:**
locate passwd
locate -i flag.txt
locate -c .php
locate -r '\.conf$'

**Maintenance:**
sudo updatedb   # Refresh the database (usually runs daily via cron)

**HTB Note:**
If `locate: command not found`, the box is minimal. Use `find` instead:
find / -name "*.txt" 2>/dev/null

---

## grep
- **Purpose:** Search INSIDE files for specific text patterns.
- **Usage:** Filter output of other commands OR search directly in files.

**Syntax:**
grep [OPTIONS] PATTERN [FILE...]

**Critical Options (HTB Enum):**
- `-r` : Recursive (search directories).
- `-i` : Case insensitive.
- `-v` : Invert match (show lines NOT containing pattern).
- `-l` : Show only filenames (not matching lines).
- `-n` : Show line numbers.
- `-A N` : Show N lines After match.
- `-B N` : Show N lines Before match.
- `-E` : Extended REGEX (same as `egrep`).
- `-o` : Show ONLY the matched part, not whole line.
- `--color=always` : Highlight matches (often alias by default).

**Examples (Enumeration):**

grep -r "password" /var/www/html 2>/dev/null
ps aux | grep root
cat /etc/passwd | grep -v nologin
grep -l "flag" *.txt
grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' file.txt  # Extract IPs
strings suspicious.bin | grep HTB
history | grep ssh
