---
name: Delete branch after merge
description: After a PR is merged, ask user for permission to delete the feature branch
type: feedback
---
After a PR merge completes, always ask the user for permission to delete the feature branch (both local and remote).

**Why:** User wants branches cleaned up after merge, but still wants to confirm before deletion.

**How to apply:** After merge confirmation, ask: "Want me to delete the branch locally and on remote?" Wait for approval before running git branch -d and git push --delete.
