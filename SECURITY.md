# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| 0.x.x   | :warning:          |

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. Email: security@phenotype.dev (when available)
3. Or use GitHub's private vulnerability reporting

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)
- Version(s) affected

### Response Timeline

| Timeline | Action |
|----------|--------|
| 24 hours | Acknowledge receipt |
| 7 days | Initial assessment |
| 30 days | Resolution target |
| 90 days | Public disclosure |

## Security Best Practices

### For Contributors

#### Secure Coding

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user input
- Use parameterized queries
- Follow principle of least privilege

#### Secret Management

```bash
# Use .env files (never commit)
cp .env.example .env

# Add to .gitignore
.env
.env.local
*.pem
*.key
```

#### Dependency Security

```bash
# Audit dependencies regularly
npm audit
pip audit
cargo audit
```

### For Users

#### Installation

- Verify package integrity
- Use official sources only
- Check package signatures

#### Configuration

- Change default credentials
- Use strong passwords
- Enable 2FA where available
- Regularly update dependencies

## Security Features

### Authentication

- OAuth 2.0 / OIDC support
- API key authentication
- JWT tokens with expiration

### Authorization

- Role-based access control (RBAC)
- Permission-based policies
- Principle of least privilege

### Data Protection

- Encryption at rest
- Encryption in transit (TLS 1.3)
- Secure key management
- Data minimization

### Monitoring

- Audit logging
- Anomaly detection
- Security event alerts

## Vulnerability Disclosure Policy

### Private Disclosure

We follow a 90-day coordinated disclosure process:

1. Researcher reports vulnerability
2. We acknowledge within 24 hours
3. We work on fix (target: 30 days)
4. We notify affected users
5. We publish fix
6. We credit researcher (with permission)

### Public Disclosure

If a vulnerability is publicly disclosed before resolution:

1. We accelerate our timeline
2. We may issue emergency patches
3. We will communicate through official channels

## Security Updates

### Subscription

Subscribe to security advisories:
- GitHub Security Advisories
- Release notes
- Security mailing list

### Staying Updated

```bash
# Update dependencies regularly
npm update
pip install --upgrade
cargo update
```

## Security Resources

### External Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Guidelines](https://csrc.nist.gov/)

### Internal Documentation

- [Coding Standards](../governance/standards/)
- [Architecture Overview](ARCHITECTURE.md)
- [Incident Response Process](../governance/processes/incident-response.md)

## Contact

For security-related inquiries:
- Email: security@phenotype.dev
- GitHub: Private vulnerability reporting

## Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities. Contributors will be credited (with permission) in our security advisory.

---

*Last Updated: 2026-03-25*
