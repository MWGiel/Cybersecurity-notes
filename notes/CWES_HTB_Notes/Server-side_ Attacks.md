## Introduction to Server-side Attacks
Server-side attacks target the application or service provided by a server, whereas client-side attacks occur at the client's machine, not the server itself. Understanding and identifying the differences is essential for penetration testing and bug bounty hunting.

For instance, vulnerabilities like Cross-Site Scripting (XSS) target the web browser, i.e., the client. On the other hand, server-side attacks target the web server.

- Server-Side Request Forgery (SSRF)
- Server-Side Template Injection (SSTI)
- Server-Side Includes (SSI) Injection
- eXtensible Stylesheet Language Transformations (XSLT) Server-Side Injection

# Server-Side Request Forgery (SSRF)
Server-Side Request Forgery (SSRF) is a vulnerability that allows an attacker to manipulate a web application into sending unauthorized requests from the server. This vulnerability often occurs when an application makes HTTP requests to other servers based on user input. Successful exploitation of SSRF can enable an attacker to access internal systems, bypass firewalls, and retrieve sensitive information.

# Server-Side Template Injection (SSTI)
Web applications can utilize templating engines and server-side templates to generate responses, such as HTML content dynamically. This generation is often based on user input, enabling the web application to respond to user input dynamically. When an attacker can inject template code, a Server-Side Template Injection vulnerability can occur. SSTI can lead to various security risks, including data leakage and even full server compromise via remote code execution.

# Server-Side Includes (SSI) Injection
Similar to server-side templates, server-side includes (SSI) can be used to generate HTML responses dynamically. SSI directives instruct the web server to include additional content dynamically. These directives are embedded in HTML files. For instance, SSI can be used to include content that is present in all HTML pages, such as headers or footers. When an attacker can inject commands into the SSI directives, Server-Side Includes (SSI) Injection can occur. SSI injection can lead to data leakage or even remote code execution.

---
## Local File Inclusion (LFI)
Since the URL scheme is part of the URL supplied to the web application, let us attempt to read local files from the file system using the file:// URL scheme. We can achieve this by supplying the URL file:///etc/passwd.
## The gopher Protocol
As we have seen previously, we can use SSRF to access restricted internal endpoints. However, we are restricted to GET requests as there is no way to send a POST request with the http:// URL scheme. For instance, let us consider a different version of the previous web application. Assuming we identified the internal endpoint /admin.php just like before
> POST /admin.php HTTP/1.1 Host: dateserver.htb Content-Length: 13 Content-Type: application/x-www-form-urlencoded  adminpw=admin

# Exploiting Blind SSRF
Exploiting blind SSRF vulnerabilities is generally severely limited compared to non-blind SSRF vulnerabilities. However, depending on the web application's behavior, we might still be able to conduct a (restricted) local port scan of the system, provided the response differs for open and closed ports.



