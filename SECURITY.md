# Security Policy

## Supported Versions

| Version | Supported |
| ------- | ------------------ |
| < 3.0   | :white_check_mark: |
| ≥ 3.0   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

Please send an email to the security team at:

**Email**: jello@jelloeater.me

### What to Include

Please provide the following information in your report:

- **Description**: Clear explanation of the vulnerability
- **Impact**: What could an attacker potentially do
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions are affected
- **Environment**: Operating system, Python version, etc.
- **Proof of Concept**: Code or commands that demonstrate the issue (if applicable)

### Responsible Disclosure

We follow responsible disclosure practices:

1. You report the vulnerability privately via email
2. We acknowledge receipt within 48 hours
3. We investigate and validate the report
4. If confirmed, we develop and test a fix
5. We notify you when the fix is ready
6. We publish the fix and credit you (if you wish)
7. We publish a security advisory with full details

### Timeline

- **Initial Response**: Within 48 hours
- **Fix Development**: Within 7 days (depending on severity)
- **Public Disclosure**: Within 30 days of fix release

### Rewards

Currently, we do not offer monetary rewards for security vulnerabilities. However, we deeply appreciate responsible disclosure and will credit reporters in our security advisories and release notes.

## Security Best Practices

### For Users

- Keep your ActivityWatch MCP Server updated to the latest version
- Use environment variables for configuration instead of hardcoded values
- Regularly review your ActivityWatch API access logs
- Use strong, unique passwords for your ActivityWatch instance
- Consider using a firewall to restrict API access

### For Developers

- Use `whispers` and `bandit` for security scanning
- Never commit secrets, API keys, or passwords
- Use environment variables for sensitive configuration
- Validate all user inputs and API responses
- Follow the principle of least privilege
- Keep dependencies updated and monitor for vulnerabilities

### Security Tools Used

This project uses the following security tools:

- **whispers**: Secret detection in code
- **bandit**: Security linting for Python code
- **tartufo**: Entropy scanning for potential secrets
- **CodeQL**: Advanced static analysis for security vulnerabilities

## Security Advisories

Security advisories will be published for confirmed vulnerabilities. You can subscribe to security advisories for this repository by:

1. Watching the repository
2. Enabling security advisory notifications
3. Following the releases

## Current Security Status

As of the latest release, this project maintains the following security posture:

- **Code Scanning**: Enabled via GitHub CodeQL
- **Dependency Scanning**: Enabled via GitHub Dependabot
- **Secret Scanning**: Enabled via GitHub secret scanning
- **Security Testing**: Automated via GitHub Actions

## Contact

For general security questions or concerns that don't involve reporting vulnerabilities:

- **Email**: jello@jelloeater.me
- **GitHub Issues**: Create an issue with the "security" label

We take security seriously and appreciate your help in keeping this project secure.
