# Product Catalog — EPAM Interview Challenge

A secure Flask web application built as part of the EPAM / White Hat penetration testing role challenge.
Every architectural and code decision maps to a specific parameter in the internal **פרמטרים לפיתוח מאובטח** (Secure Development Parameters) document.

Live demo: https://epam-product-catalog.onrender.com

---

## Features

- Login page (shared guest account)
- Add a product (name + price)
- Search products by name
- Full security stack: input validation, parameterized queries, CSRF, rate limiting, reCAPTCHA v3, HSTS, CSP, bcrypt, structured logging

---

## Security Architecture

Each layer maps to one or more parameters from the secure development document.

| Layer | Implementation | Parameter |
|---|---|---|
| **Input validation** | Server-side whitelist regex on all fields; no blacklist | INP-1 (רשימה לבנה) |
| **Range validation** | Price: positive, ≤ 999,999.99; name: 1–100 chars | INP-3 (בדיקות לוגיות/טווחים) |
| **Database** | Parameterized queries only via psycopg2; no string concatenation | DB-3 (שאילתות מול בסיס נתונים) |
| **DB privileges** | `app_user` role: SELECT + INSERT on `products` only; no UPDATE/DELETE/DROP | DB-1 (הרשאות מינימליות) |
| **Secrets** | All secrets in environment variables; `.env` gitignored; `.env.example` committed | CONF-1 (ניהול תצורה) |
| **Transport** | HTTPS enforced via Render SSL + Flask-Talisman HSTS (1 year) | INT-1, ENC-2 |
| **Security headers** | X-Frame-Options: DENY, X-Content-Type-Options: nosniff, strict CSP, Referrer-Policy | PROTO-1, ERR-1 |
| **Session cookies** | Secure + HttpOnly + SameSite=Strict flags | Session layer, INT-1 |
| **CSRF protection** | Flask-WTF tokens on all POST forms | CSRF layer |
| **Password hashing** | bcrypt (cost 12) — one-way, never reversible | AUTH-1 (ערבול סיסמאות) |
| **Timing attack prevention** | bcrypt always runs even when username not found | ERR-2 |
| **Error messages** | Generic only; no stack traces, DB names, or server details exposed | ERR-1, ERR-2 (הודעות שגיאה) |
| **Rate limiting / DoS** | Flask-Limiter: login 5/min, add 10/min, search 30/min; timed auto-release | DOS-1 (חסימת DOS) |
| **Bot prevention** | reCAPTCHA v3 on login and add-product forms; server-side score verification | BOT-1 (מניעת בוטים) |
| **Logging** | All requests + failures logged server-side; sensitive fields scrubbed | LOG-2, LOG-3 (לוגים) |
| **No security questions** | Password recovery via OTP is out of scope; documented gap | REC-1 |
| **Version control** | Git + GitHub; rollback via git revert | VER-1 (ניהול גרסאות) |
| **Dependencies** | All packages pinned to exact versions; no unused packages | Dependency layer |

### Known Gaps (documented honestly)

| Gap | Parameter | Remediation for production |
|---|---|---|
| No WAF | PROTO-1 | Add custom domain + Cloudflare Free WAF |
| No SIEM | LOG-1 | Forward Render logs to a SIEM (Datadog, etc.) |
| No password expiry | PASS-2 | Add expiry column to users table; enforce in middleware |
| No OTP password recovery | REC-2 | Integrate email/SMS OTP service |

---

## Folder Structure

```
product-catalog/
├── .env.example          # Secret template — CONF-1
├── .gitignore            # Blocks .env from repo — CONF-1
├── requirements.txt      # Pinned exact versions — Dependency layer
├── wsgi.py               # Gunicorn entry point
├── create_user.py        # Local utility to bcrypt-hash a password
│
├── app/
│   ├── __init__.py       # App factory: Talisman, CSRF, Limiter, blueprints
│   ├── config.py         # Reads secrets from env; fails fast if missing — CONF-1
│   ├── db.py             # Sole DB access point; parameterized queries only — DB-3
│   ├── validators.py     # Whitelist regex + range checks — INP-1, INP-3
│   ├── recaptcha.py      # Server-side reCAPTCHA v3 verification — BOT-1
│   ├── logger.py         # Structured logging; scrubs sensitive fields — LOG-2, LOG-3
│   ├── error_handlers.py # Generic HTTP error responses — ERR-1
│   │
│   ├── routes/
│   │   ├── auth.py       # Login (bcrypt, timing-safe, rate-limited) — AUTH-1, DOS-1, ERR-2
│   │   └── products.py   # Add + Search (validated, rate-limited, CAPTCHA-gated)
│   │
│   ├── templates/
│   │   ├── base.html     # CSP, CSRF meta, nav
│   │   ├── login.html    # reCAPTCHA v3
│   │   ├── add_product.html  # reCAPTCHA v3
│   │   ├── search.html   # Read-only; output escaped
│   │   └── error.html    # Generic error page
│   │
│   └── static/css/
│       └── main.css
```

---

## Threat Model

| Attack | Mitigated by |
|---|---|
| SQL Injection | Parameterized queries (DB-3) + whitelist validation (INP-1) |
| XSS | Jinja2 auto-escaping + strict CSP (no inline scripts) |
| CSRF | Flask-WTF tokens on all POST forms; SameSite=Strict cookies |
| Brute force (login) | Rate limit 5/min + bcrypt cost 12 (DOS-1, AUTH-1) |
| Bot attacks | reCAPTCHA v3 server-side score check (BOT-1) |
| User enumeration | Generic error + timing-safe bcrypt comparison (ERR-2) |
| Session hijacking | Secure + HttpOnly + SameSite=Strict cookies; HTTPS-only |
| Man-in-the-Middle | HTTPS + HSTS 1-year (INT-1, ENC-2) |
| Clickjacking | X-Frame-Options: DENY (PROTO-1) |
| Information disclosure | Generic errors; debug=False in production (ERR-1) |
| Secret leakage | Env vars only; .env gitignored (CONF-1) |
| DB privilege escalation | app_user: SELECT + INSERT only (DB-1) |
| Dependency CVEs | All packages pinned; no unused packages |

---

## Local Development

```bash
# 1. Clone and enter the project
git clone https://github.com/gilgil3331/spam-product-catalog.git
cd spam-product-catalog

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your real values

# 5. Run
FLASK_ENV=development flask --app wsgi:app run
```

> With `FLASK_ENV=development`: DEBUG mode on, HTTPS not enforced, session cookie Secure flag off (so HTTP works locally).

---

## Database Setup (Supabase)

```sql
CREATE TABLE products (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    price      NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Minimal privileges for the app user (DB-1)
CREATE ROLE app_user WITH LOGIN PASSWORD 'STRONG_PASSWORD';
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT ON TABLE products TO app_user;
GRANT SELECT ON TABLE users TO app_user;
GRANT USAGE, SELECT ON SEQUENCE products_id_seq TO app_user;
```

To create the guest user, run locally:
```bash
python3 create_user.py
```
Paste the printed INSERT statement into Supabase SQL Editor.

---

## Security Self-Audit Checklist

- [ ] **INP-1** — All inputs validated server-side with whitelist regex before any DB call
- [ ] **INP-3** — Price has positive + upper-bound range check
- [ ] **DB-3** — Zero dynamic SQL; all queries use `%s` parameterization
- [ ] **DB-1** — `app_user` role has no UPDATE, DELETE, DROP, or schema-level rights
- [ ] **CONF-1** — `.env` is gitignored; no secret appears in any committed file
- [ ] **INT-1** — HTTPS enforced; HSTS header present in production responses
- [ ] **AUTH-1** — Password stored as bcrypt hash (starts with `$2b$12$`); plaintext never stored
- [ ] **ERR-2** — Login returns "Invalid credentials" for both wrong password and unknown username
- [ ] **ERR-1** — 500 errors show generic message; no stack trace in response body
- [ ] **DOS-1** — Rate limits active: login 5/min, add 10/min, search 30/min
- [ ] **BOT-1** — reCAPTCHA v3 verified server-side on login and add-product
- [ ] **LOG-2** — Failed logins, reCAPTCHA blocks, and 5xx errors all appear in server logs
- [ ] **LOG-3** — No password, token, or secret appears in any log line
- [ ] **PROTO-1** — X-Frame-Options: DENY present; CSP restricts script sources
- [ ] **VER-1** — All changes tracked in Git with meaningful commit messages
