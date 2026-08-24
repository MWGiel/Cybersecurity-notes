
# Linux Services & Internals Enumeration
This section focuses on deep enumeration of the target system to intentify services, processes, network configuration, history files, cron jobs, and configuration files. This enumeration is crucial before attempting privilege escalation.



##### Network and Communication

## Network Interfaces
```bash
ip a
```
- Check for additional interfaces that could be used for pivoting to other subnets.

## /etc/hosts
```bash
cat /etc/hosts
```
- May contain custom DNS entries that could indicate internal servers.



##### Users and Sessions

## Users' Last Login
```bash
lastlog
```
- Shows when each user last logged in. Useful for identifying active users.

## Currently Logged In Users
```bash
w
```
- Check who else is currently on the system (may have interesting processes or history).



##### History Files

## Bash History
```bash
history
cat ~/.bash_history
```
- Often contains passwords, git commits, and other sensitive data.

## Find History Files
```bash
find / -type f \( -name "_hist" -o -name "_history" \) 2/dev/null
```


##### Cron Jobs (Scheduled Tasks)

```bash
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/
cs /etc/crontab
```
- If a cron job runs a script as root and you can modify it, this is handy for privilege escalation.



##### Process Information (Procf)

## View Process Command Lines
```bash
find /proc -name cmdline -exec cat \;\ 2 /dev/null | tr " " "\n"
```
- Can reveal passwords or sensitive arguments passed to processes.


##### Installed Packages and Binaries

## List Installed Packages
```bash
apt list --installed
```

## Check Sudo Version
```bash
sudo -V
```
- ‣ Unsecure versions may have known exploits.

## List Installed Binaries
```bash
ls -l /bin /usr/bin/ /usr/sbin/
```

### GTFOBins - Find Potentially Dangerous Binaries
```bash
for i in $(curl -s https://gtfobins.org/api.json | jq -r '.executables | keys[]'); do 
  if grep -q "$i" installed_pkgs.list; then 
    echo "Check GTFO: $i"
  fi
done
```
- Compares installed packages with the GTFOBins database to find binaries that can be exploited for privilege escalation.



##### System Call Tracing (Strace)

```bash
strace ping -c1 10.129.112.20
```
- Monitors system calls in real-time; can reveal passwords, file paths, and other sensitive data.



##### Configuration Files and Scripts

## Find Configuration Files
```bash
find / -type f \( -name "*.conf" -o -name "*.config" \) 2/dev/null
```
- May contain passwords, API keys, or internal paths.

## Find Scripts (.sh)
```bash
find / -type f -name "*.sh" 2/dev/null | grep -v "src|\snap|\share"
```
- Scripts often contain sensitive variables or configuration details.



##### Processes Running as Root

```bash
ps aux | grep root
```
- Any process or script running as root that can be overwritten or exploited is a prime escalation path.


##### Summary of Key Points

| What to Check              | Why It Matters                       |
|-------------------------|--------------------------------------------|
| Cron Jobs                   | Often run as root - easy privesc if modifiable |
| Bash History               | Passwords, paths, git, sensitive commands |
| Root Processes               | Potential exploits or overwritable scripts |
| Config Files                | API keys, passwords, internal paths           |
| GTFOBins                    | Find binaries that can be exploited for root  |
| Network & /etc/hosts       | Pivoting, internal DNS, unexpected subnets  |
| Strace                      | Real-time system calls with sensitive data       |
