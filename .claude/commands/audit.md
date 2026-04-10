---
description: Audit the codebase for security issues and code quality
---

Perform a code audit on the EBM project.

1. Check for security vulnerabilities:
   - Plain-text passwords
   - Missing @login_required decorators
   - Unvalidated user input
   - Hardcoded secrets or credentials
   - SQL injection risks

2. Check for code quality issues:
   - Unused imports
   - Code duplication
   - Missing error handling
   - Naming convention violations

3. Report findings grouped by severity (Critical, High, Medium, Low)
