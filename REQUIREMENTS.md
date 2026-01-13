# Requirements (Gentoo Linux)

## System Packages

```bash
# Python 3.x
emerge -av dev-lang/python

# IMAP filtering utility (optional, for Lua-based filtering)
emerge -av net-mail/imapfilter

# SSL/TLS support
emerge -av dev-libs/openssl
```

## Python Packages

```bash
pip install --user imapclient
pip install --user spambayes
```

## Configuration

1. Gmail requires an **App Password** (not your regular password) if 2FA is enabled
2. Enable IMAP access in Gmail settings: Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP
