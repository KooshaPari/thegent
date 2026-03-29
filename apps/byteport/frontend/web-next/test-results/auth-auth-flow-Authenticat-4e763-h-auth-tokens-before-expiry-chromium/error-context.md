# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e4]:
    - heading "Sign in" [level=1] [ref=e6]
    - generic [ref=e9]:
      - generic [ref=e10]:
        - generic [ref=e11]:
          - generic [ref=e13]: Email
          - textbox "Email" [active] [ref=e15]:
            - /placeholder: Your email address
        - button "Continue" [ref=e16] [cursor=pointer]:
          - generic [ref=e17]: Continue
      - generic [ref=e18]: OR
      - link "Continue with GitHub" [ref=e21] [cursor=pointer]:
        - /url: api/login?provider=GitHubOAuth&state=eyJyZXR1cm5QYXRobmFtZSI6Ii9kYXNoYm9hcmQifQ%3D%3D&redirect_uri=https%3A%2F%2Fbyte.kooshapari.com%2Fauth%2Fcallback&client_id=client_01K4KYZR40RK7R9X3PPB5SEJ66&source=signin&authorization_session_id=01K788VMT42XF67XGZTV3FMABP
        - img [ref=e22]
        - generic [ref=e24]: Continue with GitHub
  - alert [ref=e25]
```