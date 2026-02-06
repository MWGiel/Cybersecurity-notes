Session tokens are unique identifiers that a web application uses to identify a user. More specifically, the session token is tied to the user's session. If an attacker can obtain a valid session token of another user, they can impersonate the user to the web application, thereby taking over their session.
## Brute-Force Attack
Suppose a session token does not provide sufficient randomness and is cryptographically weak. In that case, we can brute-force valid session tokens similarly to how we were able to brute-force valid password-reset tokens. This can occur if a session token is too short or contains static data that does not provide randomness to the token, i.e., the token provides insufficient entropy.
## Attacking Predictable Session Tokens
The simplest form of predictable session tokens contains encoded data we can tamper with.

> Cookie: session=757365723d6874622d7374646e743b726f6c653d75736572 = user=htb-stdnt;role=user
---
> 757365723D6874622D7374646E743B726F6C653D61646D696E = user=htb-stdnt;role-admin
- and got a flag :)
## Further Session Attacks
Session Fixation is an attack that enables an attacker to obtain a victim's valid session. A web application vulnerable to session fixation does not assign a new session token after a successful authentication. If an attacker can coerce the victim into using a session token chosen by the attacker, session fixation enables an attacker to steal the victim's session and access their account.

For instance, assume a web application vulnerable to session fixation uses a session token in the HTTP cookie session. Furthermore, the web application sets the user's session cookie to a value provided in the sid GET parameter. Under these circumstances, a session fixation attack could look like this:
- An attacker obtains a valid session token by authenticating to the web application. For instance, let us assume the session token is a1b2c3d4e5f6. Afterward, the attacker invalidates their session by logging out.
- The attacker tricks the victim into using the known session token by sending the following link: http://vulnerable.htb/?sid=a1b2c3d4e5f6. When the victim clicks this link, the web application sets the session cookie to the provided value
- The victim authenticates to the vulnerable web application. The victim's browser already stores the attacker-provided session cookie, so it is sent along with the login request. The victim uses the attacker-provided session token since the web application does not assign a new one.
- Since the attacker knows the victim's session token a1b2c3d4e5f6, they can hijack the victim's session.
