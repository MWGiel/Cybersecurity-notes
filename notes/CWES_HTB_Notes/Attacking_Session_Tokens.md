Session tokens are unique identifiers that a web application uses to identify a user. More specifically, the session token is tied to the user's session. If an attacker can obtain a valid session token of another user, they can impersonate the user to the web application, thereby taking over their session.
## Brute-Force Attack
Suppose a session token does not provide sufficient randomness and is cryptographically weak. In that case, we can brute-force valid session tokens similarly to how we were able to brute-force valid password-reset tokens. This can occur if a session token is too short or contains static data that does not provide randomness to the token, i.e., the token provides insufficient entropy.
## Attacking Predictable Session Tokens
The simplest form of predictable session tokens contains encoded data we can tamper with.

> Cookie: session=757365723d6874622d7374646e743b726f6c653d75736572 = user=htb-stdnt;role=user
>  757365723D6874622D7374646E743B726F6C653D61646D696E = user=htb-stdnt;role-admin
and got a flag :)
