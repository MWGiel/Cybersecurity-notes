
# OWASP API Top 10 - Broken Authentication (API2:2023)

## What is Broken Authentication?

Broken Authentication is the second most critical API security risk according to the OWASP API Top 10 for 2023. It occurs when an application's authentication mechanisms are poorly implemented, making it possible for attackers to compromise user credentials or session tokens and assume other users' identities.

Authentication relates to all endpoints and data flows that handle the identity of users or entities accessing an API. This includes credentials, keys, tokens, and even password reset functionality.

## Common Attack Vectors

### 1. Credential Stuffing & Brute Force Attacks
Attackers use automated tools to try leaked username/password pairs or common passwords across many accounts. Even attackers with limited technical skills can leverage readily available tools to exploit authentication issues.

Tools commonly used: Hydra, Medusa, Burp Suite Intruder, ffuf with POST requests.

### 2. Weak JWT (JSON Web Token) Secrets
JWTs with weak secrets can be cracked using tools like hashcat:

hashcat -a 0 -m 16500 <JWT_TOKEN> /usr/share/wordlists/rockyou.txt

Once cracked, attackers can forge their own valid tokens and impersonate any user.

### 3. Token Manipulation Vulnerabilities
- Weak or unsigned keys
- Expired tokens that remain valid beyond their intended lifetime
- Predictable session IDs (e.g., sequential integers)
- Tokens without integrity checks
- Leaked tokens exposed in URLs, logs, or client-side code

### 4. Lack of Rate Limiting
Without proper rate limits, attackers can perform unlimited login attempts, enumerate valid usernames, and bypass account lockout mechanisms.

## Real-World Impact - RBI International Incident (September 2025)

Restaurant Brands International (owner of Burger King, Tim Hortons, and Popeyes) exposed multiple API security flaws related to their drive-thru operations:

- Attackers could generate authentication tokens without proper checks
- Privilege escalation from customer to admin was possible
- An open GraphQL endpoint allowed signup without email validation

## Best Practices for Prevention

### 1. Implement Strong Authentication
- Use standardized authentication mechanisms (JWT, OAuth 2.0, OpenID Connect)
- Enforce strong password policies
- Implement Multi-Factor Authentication (MFA)

### 2. Protect Tokens and Credentials
- Never expose tokens in URL parameters
- Use short token expiration times (TTL)
- Implement token refresh mechanisms securely
- Use strong secrets (minimum 32 characters, random)

### 3. Add Rate Limiting
Implement progressive delays after repeated failed attempts. Block IP addresses after excessive failures. Use captcha for suspicious activity.

### 4. Regular Security Testing
- Perform automated DAST/SAST scans
- Conduct regular penetration testing
- Review authentication flows for logical flaws
- Test for brute-force vulnerabilities with realistic tools

## Key Takeaways from the Video

- Broken authentication is not just about passwords - it includes session management, token handling, and recovery mechanisms.
- The API itself must enforce authentication on both ends - frontend authentication is insufficient.
- Rate limiting should be implemented at both the application and infrastructure levels (WAF, API gateway).
- Even large organizations like RBI can misconfigure APIs, leading to critical breaches.
- Testing tools like Medusa are essential for identifying weak authentication implementations before attackers do.

## Tools Mentioned for Testing

| Tool | Purpose |
|------|---------|
| Medusa | Brute-force authentication testing |
| Hydra | Network login cracking |
| Hashcat | JWT secret cracking |
| Burp Suite | Token manipulation and replay attacks |
| ffuf | Fuzzing login endpoints |

## OWASP API Top 10 Classification

Broken Authentication appears as API2:2023 in the OWASP API Security Top 10. It is considered a critical risk due to the potential for complete account takeover and unauthorized access to sensitive data.

Prevention requires defense in depth: strong credential policies, secure session management, proper token validation, and continuous monitoring for suspicious authentication patterns.
