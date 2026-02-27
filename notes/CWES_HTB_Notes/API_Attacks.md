Application Programming Interfaces (APIs) are foundational to modern software development, with web APIs being the most prevalent form. They enable seamless communication and data exchange across diverse systems over the internet, serving as crucial bridges that facilitate integration and collaboration among different software applications.

At their essence, APIs consist of defined rules and protocols that dictate how disparate systems interact. They specify data formatting requirements, delineate access methods for resources, and define expected response structures. APIs are broadly categorized as either public, accessible to external parties, or private, restricted to specific organizations or groups of systems.
## API Building Styles
Web APIs can be built using various architectural styles, including REST, SOAP, GraphQL, and gRPC, each with its own strengths and use cases:

- Representational State Transfer (REST) is the most popular API style. It uses a client-server model where clients make requests to resources on a server using standard HTTP methods (GET, POST, PUT, DELETE). RESTful APIs are stateless, meaning each request contains all necessary information for the server to process it, and responses are typically serialized as JSON or XML.
- Simple Object Access Protocol (SOAP) uses XML for message exchange between systems. SOAP APIs are highly standardized and offer comprehensive features for security, transactions, and error handling, but they are generally more complex to implement and use than RESTful APIs.
- GraphQL is an alternative style that provides a more flexible and efficient way to fetch and update data. Instead of returning a fixed set of fields for each resource, GraphQL allows clients to specify exactly what data they need, reducing over-fetching and under-fetching of data. GraphQL APIs use a single endpoint and a strongly-typed query language to retrieve data.
- gRPC is a newer style that uses Protocol Buffers for message serialization, providing a high-performance, efficient way to communicate between systems. gRPC APIs can be developed in a variety of programming languages and are particularly useful for microservices and distributed systems.
## Broken Object Level Authorization
Web APIs allow users to request data or records by sending various parameters, including unique identifiers such as Universally Unique Identifiers (UUIDs), also known as Globally Unique Identifiers (GUIDs), and integer IDs. However, failing to properly and securely verify that a user has ownership and permission to view a specific resource through object-level authorization mechanisms can lead to data exposure and security vulnerabilities.

A web API endpoint is vulnerable to Broken Object Level Authorization (BOLA), also known as Insecure Direct Object Reference (IDOR), if its authorization checks (implemented at the source-code level) fail to correctly ensure that an authenticated user has sufficient permissions or privileges to request and view specific data or perform certain operations.
## LAB:  Exploit another Broken Authentication vulnerability to gain unauthorized access to the customer with the email 'MasonJenkins@ymail.com'. Retrieve their payment options data and submit the flag.
FLAG: HTB{115a6329120e-----c4ec6a63343ed1}

## Broken Object Property Level Authorization
Broken Object Property Level Authorization is a category of vulnerabilities that encompasses two subclasses: Excessive Data Exposure and Mass Assignment.
An API endpoint is vulnerable to Excessive Data Exposure if it reveals sensitive data to authorized users that they are not supposed to access.
On the other hand, an API endpoint is vulnerable to Mass Assignment if it permits authorized users to manipulate sensitive object properties beyond their authorized scope, including modifying, adding, or deleting values.

## Vulnerability Note: Unrestricted Resource Consumption (OTP Spam)

Date: 2026-02-26
Target: OTP SMS Endpoint

Summary:
The application endpoint responsible for sending OTP codes lacks rate limiting and anti-automation controls. This allows an attacker to spam the "Send OTP" button with repeated requests.

Impact:

- Service Disruption: SMS queue gets flooded, blocking legitimate users from receiving codes.

- Financial Cost: Each request triggers a paid SMS, potentially causing financial damage.

Fix:
Implement rate limiting (e.g., max 3 requests per minute) and CAPTCHA on the OTP request form.

## Server Side Request Forgery
A web API is vulnerable to Server-Side Request Forgery (SSRF) (also known as Cross-Site Port Attack (XPSA)) if it uses user-controlled input to fetch remote or local resources without validation. SSRF flaws occur when an API fetches a remote resource without validating the user-supplied URL. This allows an attacker to coerce the application to send a crafted request to an unexpected destination (especially local ones), bypassing firewalls or VPNs.

# Prevention 
To mitigate the SSRF vulnerability, the /api/v1/supplier-companies/certificates-of-incorporation POST and /api/v1/supplier-companies PATCH endpoints must strictly prohibit file URIs that point to local resources on the server other than the intended ones. Implementing validation checks to ensure that file URIs only point to permissible local resources is crucial, which in this case is within the wwwroot/SupplierCompaniesCertificatesOfIncorporations/ folder.

Furthermore, the /api/v1/supplier-companies/{ID}/certificates-of-incorporation GET endpoint must be configured to serve content exclusively from the designated folder wwwroot/SupplierCompaniesCertificatesOfIncorporations. This ensures that only certificates of incorporation are accessible and that local resources or files outside this directory are never exposed. Additionally, this acts as a safeguard, if in case the validations performed by the /api/v1/supplier-companies/certificates-of-incorporation POST and /api/v1/supplier-companies PATCH endpoints fail.

