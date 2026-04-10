---
name: Confirm commit message before push
description: Always show the commit message and get approval before pushing to remote
type: feedback
---
Always show the full commit message to the user and wait for approval before running git push.

**Why:** User explicitly asked "always before each push confirm the commit message to me."

**How to apply:** Before any `git push`, show:
1. The commit message
2. Files changed
3. Branch name and target
Then wait for user to say "yes" / "approve" before pushing.
