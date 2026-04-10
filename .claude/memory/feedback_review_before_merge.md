---
name: Review PR before merge
description: Always review the PR diff and provide analysis before merging
type: feedback
---

Always review the PR before merging. Never merge without reviewing first.

**Why:** User asked "before merge you don't review? you should must review."

**How to apply:** After user says "merge", first:
1. Run `gh pr diff` to get the changes
2. Provide a brief code review (what changed, any issues, approval/concerns)
3. Then merge after user confirms
