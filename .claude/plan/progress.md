# Architecture Migration — Progress Tracker

## Last Updated: 2026-04-11
## Current Task: EBMS-9 (PR #5 created, pending user merge decision)
## Current Branch: feature/EBMS-9-fix-duplicate-settings (pushed)

## Completed Tasks
| # | Ticket | Description | PR | Commit | Status |
|---|--------|-------------|-----|--------|--------|
| 1 | SCRUM-5 | .gitignore, remove junk imports, .mcp.json, .claude/ | PR #1 | 897e755, 6bb1ee2 | DONE |
| 2 | EBMS-6 | README.md full rewrite | PR #2 | 5c55936 | DONE |
| 3 | EBMS-7 | Add memory files to git | PR #3 | adcb987 | DONE |
| 4 | EBMS-8 | Add SEMESTER_CHOICES to Semester model | PR #4 | 55ba604 | DONE |

## In Progress
| # | Ticket | Description | Branch | PR | Status |
|---|--------|-------------|--------|-----|--------|
| 5 | EBMS-9 | Fix duplicate STATICFILES_DIRS and DEFAULT_AUTO_FIELD | feature/EBMS-9-fix-duplicate-settings | PR #5 | Sonnet reviewed, PR created, pending merge |

## Backlog (To Do)
| # | Ticket | Description | Phase | Depends On |
|---|--------|-------------|-------|------------|
| 6 | EBMS-10 | Create requirements.txt | Cleanup | — |
| 7 | EBMS-11 | Remove Lib/, pyvenv.cfg, venv binaries from git | Cleanup | — |
| 8 | EBMS-12 | Add CourseType choices to Course model | Model | — |
| 9 | EBMS-13 | Move SECRET_KEY to env variable | Security | — |
| 10 | EBMS-14 | Add @login_required to all views | Security | — |
| 11 | EBMS-15 | Create forms.py (LoginForm, CommitteeCreateForm) | Forms | — |
| 12 | EBMS-16 | Create billing rates.py | Service | — |
| 13 | EBMS-17 | Create BillCalculator service class | Service | EBMS-16 |
| 14 | EBMS-18 | Replace bill duplication with BillCalculator | Refactor | EBMS-17 |
| 15 | EBMS-19 | Replace string URLs with reverse() | Refactor | — |
| 16 | EBMS-20 | Create base.html template | Templates | — |
| 17 | EBMS-21 | Extract inline CSS to styles.css | Templates | EBMS-20 |
| 18 | EBMS-22 | Write tests for BillCalculator | Tests | EBMS-17 |

## Jira Transition IDs
- To Do: 11
- In Progress: 21
- In Review: 31
- Review Ready: 41
- Done: 51

## Resume Context
- Working directory: D:\personal project\Exam-Bill-Management-System
- Django project: Scripts/EBM/
- Remote: origin → https://github.com/Ertugrul2848/Exam-Bill-Management-System.git
- Jira: https://ertugrul28.atlassian.net (project key: EBMS)
- Python: 3.13 (global install)
- GitHub CLI: logged in as artugal28373
- Admin user: ertugrul28 / admin1234
