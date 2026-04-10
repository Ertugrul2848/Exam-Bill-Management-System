---
name: Confirm before remote git operations
description: Always ask user before any git command that changes the remote (push, merge PR, delete branch, create PR, etc.)
type: feedback
---
Always ask for explicit approval before running any git command that affects the remote repository.

**Why:** User wants to check and verify all remote changes before they happen. They want full control over what gets pushed/merged/deleted on GitHub.

**How to apply:** Before running git push, gh pr merge, gh pr create, git push --delete, gh repo create, or any remote-modifying command:
1. Show the exact command
2. Explain what it will do
3. Wait for user to say "go" / "yes" / "do it" before executing

Local-only commands (commit, branch, checkout, diff, log) are fine without asking.
