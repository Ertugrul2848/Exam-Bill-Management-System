# Exam Bill Management System (EBM)

## Project Overview

A Django-based web application for managing university examination processes — including exam scheduling, committee formation, instructor compensation/billing, and PDF report generation.

**Tech Stack:** Django 4.1, Python 3.10, SQLite (dev), Bootstrap 3, xhtml2pdf

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
# Activate virtual environment (Windows)
Scripts\activate

# Run development server
cd Scripts/EBM && python manage.py runserver

# Run migrations
cd Scripts/EBM && python manage.py makemigrations && python manage.py migrate

# Create superuser
cd Scripts/EBM && python manage.py createsuperuser
```

## Architecture Notes

- Currently a single-app monolith (`root/`) — planned refactor to 5 apps: accounts, committee, courses, thesis, billing
- See `architecture-plan.html` for the full redesign document
- ROOT_URLCONF is set to `root.urls` (not `EBM.urls`)
- Bill calculation logic exists in `views.py` (lines 537-969) — needs extraction to a service layer
- Rate constants (chairman: 2700, tabulation: 2500/3125, paper eval: 115/paper, etc.) are hardcoded in views

## Models (root/models.py)

| Model | Purpose |
|-------|---------|
| `faculty` | Teacher/instructor profiles |
| `External` | External examiner profiles |
| `Session` | Academic year (primary key = year) |
| `Semester` | Semester with committee roles (chairman, tabulators, external) |
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

## Known Issues

- Plain-text password storage in `faculty.password` field
- No `forms.py` — all input handled via raw `request.POST`
- Bill calculation duplicated 4 times in views.py
- Junk imports in models.py (tkinter, turtle, pyexpat)
- No test coverage (tests.py is empty)
- Virtual environment (Lib/, Scripts/) committed to git
- Inline CSS duplicated across all 22 templates
