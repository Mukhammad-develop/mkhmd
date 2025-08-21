# Email Setup Guide for MKHMD Authentication

## Quick Setup for Gmail

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"

3. **Update Django Settings**:
   ```python
   # In mkhmd/settings.py
   EMAIL_HOST_USER = 'your-email@mkhmd.uk'  # Your actual email
   EMAIL_HOST_PASSWORD = 'your-16-char-app-password'  # App password from step 2
   ```

## Alternative Email Providers

### For Custom Domain (mkhmd.uk)
```python
EMAIL_HOST = 'mail.mkhmd.uk'  # Your hosting provider's SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@mkhmd.uk'
EMAIL_HOST_PASSWORD = 'your-email-password'
```

### For Development/Testing
```python
# Console backend (prints emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## Email Template Customization

The verification email is sent from `accounts/views.py` in the `send_verification_email()` function.

You can customize:
- Subject line
- Email content
- Sender name
- HTML templates (optional)

## Security Notes

- Never commit real email passwords to Git
- Use environment variables for production:
  ```python
  import os
  EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
  ```
- Consider using services like SendGrid or Mailgun for production

## Testing

1. Start the development server: `python manage.py runserver`
2. Go to `/accounts/signup/`
3. Register with your email
4. Check console/email for verification code
5. Complete verification process 