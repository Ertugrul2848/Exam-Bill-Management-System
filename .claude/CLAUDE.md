# Exam Bill Management System (EBM)

## Project Overview

A Django-based web application for managing university examination processes — including exam scheduling, committee formation, instructor compensation/billing, and PDF report generation.

**Tech Stack:** Django 4.1, Python 3.13, SQLite (dev), Bootstrap 3, xhtml2pdf

## Project Structure

```
Scripts/EBM/              <- Django project root
  EBM/                    <- Project config (settings.py, urls.py, wsgi.py)
  root/                   <- Main app (models, views, templates, admin)
  static/                 <- Static files
  db.sqlite3              <- SQLite database
  manage.py               <- Django management script
```

## Key Commands

```bash
# Run development server
cd Scripts/EBM && python manage.py runserver

# Run migrations
cd Scripts/EBM && python manage.py makemigrations && python manage.py migrate

# Create superuser
cd Scripts/EBM && python manage.py createsuperuser

# System check
cd Scripts/EBM && python manage.py check
```

## Git & Workflow

- **Remote:** https://github.com/Ertugrul2848/Exam-Bill-Management-System.git
- **Jira:** https://ertugrul28.atlassian.net (project key: EBMS)
- **Branch strategy:** `main` (protected) ← `dev` (working) ← `feature/*` branches
- **Commit format:** `EBMS-<ticket>: Short description`

### Workflow per task:
1. Update CLAUDE.md + progress.md with task context → **commit and push to dev first**
2. Create Jira ticket → transition to **In Progress**
3. Create `feature/EBMS-<ticket>-short-desc` branch from `dev`
4. Make changes + commit locally
5. Show commit message to user → wait for approval → push
6. Create PR into `dev`
7. Review PR with Sonnet
8. Wait for user to say "merge"
9. Merge → ask to delete branch → update Jira to **Done**
10. Update progress.md → commit and push to dev

### User Preferences (MUST FOLLOW):
- Never add `Co-Authored-By: Claude` to commit messages
- Never auto-merge PRs — only merge when user explicitly says "merge"
- Always ask before any remote git operation (push, PR, delete branch)
- Always show commit message and get approval before pushing
- After PR merge, ask user before deleting feature branch
- Always review PR before merging
- Always update Jira ticket status after transitions
- Always commit and push context files (CLAUDE.md, progress.md) to dev BEFORE starting work — so context is never lost

## Architecture Migration — Current State

### Completed
| Ticket | What |
|--------|------|
| SCRUM-5 | .gitignore, remove junk imports, .mcp.json, .claude/ config |
| EBMS-6 | README.md full rewrite |
| EBMS-7 | Add memory files to git |
| EBMS-8 | Add SEMESTER_CHOICES to Semester model |

### Active Backlog (in order)
| Ticket | What | Phase |
|--------|------|-------|
| EBMS-9 | Fix duplicate STATICFILES_DIRS and DEFAULT_AUTO_FIELD | Cleanup |
| EBMS-10 | Create requirements.txt | Cleanup |
| EBMS-11 | Remove Lib/, pyvenv.cfg, venv binaries from git | Cleanup |
| EBMS-12 | Add CourseType choices to Course model | Model |
| EBMS-13 | Move SECRET_KEY to env variable | Security |
| EBMS-14 | Add @login_required to all views | Security |
| EBMS-15 | Create forms.py (LoginForm, CommitteeCreateForm) | Forms |
| EBMS-16 | Create billing rates.py | Service |
| EBMS-17 | Create BillCalculator service class | Service |
| EBMS-18 | Replace bill duplication with BillCalculator | Refactor |
| EBMS-19 | Replace string URLs with reverse() | Refactor |
| EBMS-20 | Create base.html template | Templates |
| EBMS-21 | Extract inline CSS to styles.css | Templates |
| EBMS-22 | Write tests for BillCalculator | Tests |

### Status Tracking
See `.claude/plan/progress.md` for detailed progress with commit hashes and PR numbers.

## Architecture Notes

- Currently a single-app monolith (`root/`) — planned refactor to 5 apps
- See `.claude/plan/architecture-plan.html` for the visual redesign document
- See `.claude/plan/architecture-migration.md` for the 30-step migration plan
- ROOT_URLCONF is set to `root.urls` (not `EBM.urls`)
- Bill calculation logic in `views.py` (lines 537-969) — duplicated 4 times
- Rate constants hardcoded in views — needs extraction to rates.py

## Models (root/models.py)

| Model | Purpose |
|-------|---------|
| `faculty` | Teacher/instructor profiles |
| `External` | External examiner profiles |
| `Session` | Academic year (primary key = year) |
| `Semester` | Semester with committee roles + SEMESTER_CHOICES |
| `SemesterBill` | Semester-level roles (moderator, translator, typist) |
| `Course` | Course with type (1=Theory, 2=Lab, 3=Viva) |
| `courseBill` | Extra invigilator assignment for a course |
| `ThesisPaper` | Thesis paper evaluation tracking |
| `ThesisSupervisor` | Thesis supervision tracking |

## Coding Conventions

- Follow Django's MVT pattern: keep views thin, logic in services/models
- Use PascalCase for model class names
- Use snake_case for field names and function names
- Use Django Forms/ModelForms for all user input
- Use `reverse()` for URL building, never string concatenation
- Use `get_object_or_404()` instead of bare `.objects.get()`
- Always add `@login_required` to protected views
- Use Django's built-in `User` model for authentication

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
