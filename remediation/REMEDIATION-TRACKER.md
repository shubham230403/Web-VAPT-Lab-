# VAPT Remediation Tracker

| ID | Vulnerability | Remediation | Status |
|---|---|---|---|
| WEB-001 | SQL Injection | Parameterized SQL queries | Pending |
| WEB-002 | IDOR/BOLA | Server-side object authorization | Pending |
| WEB-003 | Broken Access Control | Authentication + role-based authorization | Pending |
| WEB-004 | Stored XSS | Output encoding / HTML escaping | Pending |
| WEB-005 | Path Traversal | Canonical path validation | Pending |
| WEB-006 | Command Injection | Input validation + safe subprocess execution | Pending |
| WEB-007 | Unrestricted File Upload | Extension/MIME validation + safe storage | Pending |
| WEB-008 | Information Disclosure | Remove debug endpoint / sensitive output | Pending |

## Retesting Requirement

Each vulnerability must be retested after remediation using the same or equivalent proof-of-concept used during the vulnerable assessment.

Expected result:

- Malicious request rejected
- Legitimate functionality continues to work
- Appropriate HTTP status returned
- Sensitive information is no longer exposed
