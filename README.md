# Background 
The goal of this repository is to demonstrate useful permutations of pingid id python implementations.

Pingid integration is Shell's standard method of securing applications which will have endpoints exposed to the open internet. 
While many librarys exist for doing this in C# and javascript, there is not a pyton analogue for the functionality required for how Shell has implemented ping. 

# **PKCE - 'Proof Key for Code Exchange' explained**

To be specific, Shell uses the PKCE security standard. It is a more secure form of Oauth2. 
An example of basic Oauth2 would be a two factor verification for login to something like a social media site.
To facilitate a basic Oauth2 implementation, a post reqest is made to a token endpoint, using an assigned client id and client secret, and a token is returned. Then that token is used to make a second post request to an authorization endpoint, which then redirects the user to the landing page of the application if all is well. 
The issue with 'stock' Oauth2 is that this client id has a degree of exposure, and could theoretcially be collected from a request and then used maliciously.

PKCE bridges this gap by placing the burden on the application side to make and verify the client secret itself, and to do so for each and every authentication. This on-the-fly generated analogue to the client secret is officially called the 'code challenge', and the way to verify it in the PKCE flow is called the 'code verifier', which is a base 64 hash of the code challenge. What is accomplished here is that effectively, a brand new client secret is used every time and will only work once, and therefore intercepting it has no value for future accesses. 

The flow changes from 

**Oauth2 stock**

1. post request with id and secret
2. obtain token 
3. post request with token to auth server 
4. get redirected to app fully logged in 
5. app continues to check for valid token in cookies with each request to

**Oauth2 PKCE**

1. app generates code verifier and code challenge, stores them locally
2. post request to auth server with code challenge
3. auth server makes its own base64 hash of the code challenge and stores it, then returns an authorization code to the app
4. app makes second post request containing the returned autorization code, and the code verifier to the token end point
5. auth server compares its own base64 hash of the code challenge with the code verifier, then issues a token if they match and redirects to the apps landing page authenticated 6. app continues to check for valid token in cookies with each request

For more details on everything needed for each post request in PKCE flow, please see below links or the code. They will also cover token validation which is not discussed above. 

https://developer.okta.com/blog/2019/08/22/okta-authjs-pkce

https://www.stefaanlippens.net/oauth-code-flow-pkce.html

# **Examples explained**

**simple_flask_app** - stripped down pure python flask example

**flask_templates_databaseforuser** - uses flask templates and an option to toggle matching the users email versus a database table on top of PKCE. Heavily commented code. uses no ping specific libraries.

**pingid_plotly_dash** - the very radical departure implementation of pingid for plotly dash. Most of the magic happens under the hood, so numerous break points and stepping will be needed to understand why it works. Also has an option of checking user emails against a database table. Also has an option for using oauth0 to generate an artifical ping endpoint for testing. 

**django_ping_app** - django pingid example. adjusts the callbacks seen in the vanilla python examples into django views. 
