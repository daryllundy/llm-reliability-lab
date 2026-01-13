# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainer directly with details of the vulnerability
3. Include steps to reproduce the issue
4. Allow up to 48 hours for an initial response

## Security Best Practices

This project follows these security practices:

- No secrets stored in code (use `.env` files)
- Input validation via Pydantic models
- Non-root container execution
- Regular dependency updates

## Disclosure Policy

Once a vulnerability is confirmed and fixed:
1. A patch will be released
2. The vulnerability will be disclosed in release notes
3. Credit will be given to the reporter (if desired)
