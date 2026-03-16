## Recon

Found domain in HTML source:
html

support@mafialive.thm

Added to /etc/hosts:
bash

echo "10.114.156.157 mafialive.thm" | sudo tee -a /etc/hosts

Directory brute-force:
bash

gobuster dir -u http://mafialive.thm -w /usr/share/wordlists/dirb/common.txt -x php,html,txt

Interesting: /test.php, /robots.txt
