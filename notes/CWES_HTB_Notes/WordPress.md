## WPScan
WPScan is an automated WordPress scanner and enumeration tool. It determines if the various themes and plugins used by a blog are outdated or vulnerable. It’s installed by default on Parrot OS but can also be installed manually with gem.
````bash
wpscan -h
sudo wpscan --url http://blog.inlanefreight.local --enumerate --api-token dEOFB<SNIP>
````
WPScan uses various passive and active methods to determine versions and vulnerabilities, as shown in the report above. The default number of threads used is 5. However, this value can be changed using the -t flag.

This scan helped us confirm some of the things we uncovered from manual enumeration (WordPress core version 5.8 and directory listing enabled), showed us that the theme that we identified was not exactly correct (Transport Gravity is in use which is a child theme of Business Gravity), uncovered another username (john), and showed that automated enumeration on its own is often not enough (missed the wpDiscuz and Contact Form 7 plugins). WPScan provides information about known vulnerabilities. The report output also contains URLs to PoCs, which would allow us to exploit these vulnerabilities.
````bash
http://blog.inlanefreight.local/wp-content/plugins/wp-sitemap-page/readme.txt
````
