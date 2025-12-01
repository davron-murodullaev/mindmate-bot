# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

We take the security of MindMate seriously. If you discover a security vulnerability, please follow these steps:

### 🔒 Private Disclosure

**DO NOT** open a public issue for security vulnerabilities.

Instead, please report it privately:

1. **Email**: Send details to [your.email@example.com]
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### ⏱️ Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix Release**: Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: Next regular release

### 🎖️ Recognition

We appreciate responsible disclosure. With your permission, we will:
- Credit you in the CHANGELOG
- Mention you in release notes
- List you in our security acknowledgments

---

## Security Measures

### 🔐 Data Protection

- **Encryption**: All database connections use SSL
- **Environment Variables**: API keys stored securely
- **No Logging**: Sensitive data is not logged
- **Access Control**: Database access restricted

### 🛡️ Input Validation

- Message length limits (4000 characters)
- Journal entry limits (10000 characters)
- SQL injection prevention (parameterized queries)
- XSS prevention through proper escaping

### 🔑 API Security

- **OpenAI API**: Secured with API key
- **Telegram Bot**: Token validation
- **Database**: Connection string encryption
- **No Key Exposure**: Keys never in code or git

### 👥 User Privacy

- **Data Ownership**: Users own their data
- **No Sharing**: Data never shared with third parties
- **Deletion**: Users can delete their data
- **Encryption at Rest**: Database supports encryption

---

## Security Best Practices for Deployment

### 🌐 Environment Setup

```bash
# Use strong, unique passwords
DATABASE_URL=postgresql://user:STRONG_PASSWORD@host/db

# Rotate API keys regularly
OPENAI_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here

# Set proper file permissions
chmod 600 .env
```

### 🔥 Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 🗄️ Database Security

```sql
-- Create dedicated user
CREATE USER mindmate_user WITH PASSWORD 'strong_password';

-- Grant minimal permissions
GRANT CONNECT ON DATABASE mindmate TO mindmate_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO mindmate_user;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
```

### 🐳 Docker Security

```bash
# Use non-root user in Docker
USER appuser

# Scan for vulnerabilities
docker scan mindmate-bot

# Keep images updated
docker-compose pull
docker-compose up -d
```

### 🔄 Regular Maintenance

- Update dependencies monthly
- Review security logs weekly
- Backup database daily
- Rotate API keys quarterly
- Monitor for suspicious activity

---

## Known Security Considerations

### ⚠️ Current Limitations

1. **Rate Limiting**: Not implemented yet (planned for v1.1)
2. **2FA**: Not available for bot access
3. **Audit Logging**: Basic logging only
4. **Data Encryption**: Not encrypted at rest by default

### 🎯 Planned Security Enhancements

- [ ] Implement rate limiting per user
- [ ] Add request throttling
- [ ] Enhance audit logging
- [ ] Add data encryption at rest
- [ ] Implement automatic key rotation
- [ ] Add security monitoring and alerts
- [ ] Implement GDPR compliance tools

---

## Security Checklist for Self-Hosting

Before deploying MindMate:

- [ ] Strong, unique passwords for all services
- [ ] Environment variables properly set
- [ ] `.env` file not committed to git
- [ ] Database SSL enabled
- [ ] Firewall configured
- [ ] Regular backups scheduled
- [ ] Server security updates enabled
- [ ] Monitoring system in place
- [ ] Incident response plan created

---

## Compliance

### 📋 GDPR Considerations

- Users can request data deletion
- Data minimization practiced
- Purpose limitation enforced
- Data portability supported

### 🏥 HIPAA Notice

**MindMate is NOT HIPAA compliant.** Do not use for:
- Medical diagnosis
- Treatment recommendations
- Protected health information (PHI)
- Clinical mental health services

MindMate is for wellness and self-care only.

---

## Contact

For security concerns:
- **Email**: your.email@example.com
- **PGP Key**: [Link to PGP key if available]
- **Response Time**: 48 hours maximum

For general issues:
- **GitHub Issues**: https://github.com/yourusername/mindmate-bot/issues

---

**Last Updated**: 2025-12-01

Thank you for helping keep MindMate secure! 🔒
