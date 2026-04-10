# Exam Bill Management System

A Django-based web application designed to streamline and automate the examination process for educational institutions. The system handles everything from exam scheduling and committee formation to instructor compensation calculation and PDF bill generation.

## Project Description

The **Exam Bill Management System (EBM)** is built for university exam controller offices to manage the end-to-end examination workflow. In a typical university exam cycle, the controller's office must:

1. **Form exam committees** for each semester — assigning a Chairman, two Tabulators, and an External member
2. **Assign roles** to faculty — Moderator (question paper moderation), Translator, and Typist (stencil-cutting)
3. **Manage courses** — assign Internal and External examiners for Theory, Lab, and Viva courses
4. **Track thesis work** — record how many papers each faculty evaluates and how many students they supervise
5. **Calculate compensation** — each role has a specific rate (e.g., Chairman gets 2,700 BDT, Paper Evaluation is 115 BDT/paper)
6. **Generate PDF bills** — produce official printable bills for each teacher showing all their roles and total compensation

This system automates all of the above, replacing manual spreadsheets and paper-based processes.

### Who Uses This System?

| User | What They Do |
|------|-------------|
| **Exam Controller / Admin** | Creates sessions, manages all committees, views all bills |
| **Committee Chairman** | Manages their semester — assigns courses, examiners, and roles |
| **Faculty / Instructor** | Views their own bill for a given semester |

### How the Billing Works

Each faculty member can hold multiple roles across a semester. The system calculates their total bill by summing up compensation for each role:

| Role | Rate |
|------|------|
| Chairman | 2,700 BDT (fixed) |
| Tabulation (1st-3rd semester) | 2,500 BDT (fixed) |
| Tabulation (4th+ semester) | 3,125 BDT (fixed) |
| Question Paper Formulation | 2,150 BDT per course |
| Paper Evaluation | 115 BDT per paper |
| Moderation | 2,150 BDT (fixed) |
| Translation | 400 BDT (fixed) |
| Stencil-Cutter (Typist) | 375 BDT (fixed) |
| Lab Evaluation | 15,000 BDT per course |
| Lab Viva | 200 BDT per hour |
| Lab Invigilator | 400 BDT per hour |
| Viva-Voce | 200 BDT per hour |
| Thesis Paper Evaluation | 1,250 BDT per paper |
| Thesis Supervision | 3,100 BDT per student |

The system generates an official bill document (PDF) with the university header, teacher details, role-wise breakdown, and total amount — ready for the exam controller's office.

## Features

### Exam Committee Management
- Create academic sessions (by year)
- Form semester committees with Chairman, Tabulator 1, Tabulator 2, and External member
- Validate that no faculty is assigned to duplicate roles
- Ensure one Chairman per session
- Update committee members (Chairman can modify their own committee)

### Course Management
- Add Theory, Lab, and Viva type courses to each semester
- Assign Internal and External examiners for Theory/Lab courses
- Assign third examiner for Theory courses
- Assign external viva examiner for Viva courses
- Add extra invigilators for Lab and Viva courses
- Track paper count and exam duration per course

### Thesis & Supervision
- Track thesis paper evaluations per faculty per course
- Track thesis supervision (number of students per faculty)
- Bulk assignment of all faculty to thesis tracking

### Billing & Compensation
- Individual teacher bill — view your own bill for any semester
- Semester bill (Chairman/Admin only) — view all teachers' bills for a semester
- Automatic calculation based on roles and rates
- PDF export of individual bills with university header format

### Role Assignment
- Assign Moderator, Translator, and Typist roles per semester
- Chairman-only access for role management
- Remove roles from faculty members

### Authentication
- Faculty login/logout
- Role-based access control (Chairman vs regular faculty)
- Admin panel for data management

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Django 4.1 | Web framework, ORM, admin panel |
| Language | Python 3.13 | Server-side logic |
| Database | SQLite | Development database (file-based) |
| Frontend | Bootstrap 3 | Responsive UI components |
| Templates | Django Templates | Server-side HTML rendering |
| PDF Engine | xhtml2pdf | Convert HTML templates to PDF |
| Version Control | Git + GitHub | Source code management |
| Project Management | Jira (Atlassian) | Issue tracking and sprint planning |
| AI Assistant | Claude Code | Development assistance |

## Prerequisites

Before you start, make sure you have:

- **Python 3.10+** installed ([download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** installed ([download](https://git-scm.com/downloads))

To verify:

```bash
python --version    # Should show Python 3.10 or higher
pip --version       # Should show pip
git --version       # Should show git
```

## Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/Ertugrul2848/Exam-Bill-Management-System.git
cd Exam-Bill-Management-System
```

### 2. Create Virtual Environment

```bash
# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install django xhtml2pdf
```

### 4. Configure Environment Variables

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your values (Jira token, GitHub token, etc.). See [Environment Variables](#environment-variables) section below.

### 5. Run Database Migrations

```bash
cd Scripts/EBM
python manage.py migrate
```

### 6. Create Admin Account

```bash
python manage.py createsuperuser
```

Enter a username, email, and password when prompted.

### 7. Start the Server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

| Page | URL |
|------|-----|
| Login | http://127.0.0.1:8000/log/ |
| Home | http://127.0.0.1:8000/ |
| Admin Panel | http://127.0.0.1:8000/admin/ |
| Committee | http://127.0.0.1:8000/committee/ |
| Teacher Bill | http://127.0.0.1:8000/examBill/ |
| Semester Bill | http://127.0.0.1:8000/examBill2/ |

Press `Ctrl + C` to stop the server.

## Environment Variables

This project uses a `.env` file for sensitive and user-specific configuration.

```env
# ========== Jira Integration ==========
JIRA_HOST=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@gmail.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=SCRUM

# ========== GitHub Integration ==========
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat
GITHUB_ORG=your_github_org
GITHUB_REPO=Exam-Bill-Management-System
```

| Variable | Where to Get It |
|----------|----------------|
| `JIRA_API_TOKEN` | [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens) |

**Never commit `.env` to git.** It is already in `.gitignore`.

## Common Django Commands

Run all commands from the `Scripts/EBM/` directory:

```bash
cd Scripts/EBM
```

### Server

```bash
# Start development server
python manage.py runserver

# Start on a specific port
python manage.py runserver 8080

# Make accessible on network
python manage.py runserver 0.0.0.0:8000
```

### Database

```bash
# Create migration files after model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Reverse a migration (e.g., to migration 0003)
python manage.py migrate root 0003
```

### User Management

```bash
# Create admin/superuser
python manage.py createsuperuser

# Change a user's password
python manage.py changepassword <username>
```

### Django Shell & Debugging

```bash
# Open interactive Django shell
python manage.py shell

# Run system checks
python manage.py check
```

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic
```

### Testing

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test root
```

## Project Structure

```
Exam-Bill-Management-System/
├── Scripts/EBM/                  # Django project root
│   ├── manage.py                 # Django management script
│   ├── EBM/                      # Project config
│   │   ├── settings.py           # Django settings
│   │   ├── urls.py               # Root URL config
│   │   ├── wsgi.py               # WSGI entry point
│   │   └── asgi.py               # ASGI entry point
│   ├── root/                     # Main application
│   │   ├── models.py             # Database models (9 models)
│   │   ├── views.py              # View functions (22 views)
│   │   ├── urls.py               # URL patterns (active ROOT_URLCONF)
│   │   ├── admin.py              # Admin panel registration
│   │   ├── apps.py               # App config
│   │   ├── tests.py              # Tests
│   │   └── templates/            # HTML templates (22 files)
│   └── static/                   # Static files (images)
├── .claude/                      # Claude Code config
│   ├── CLAUDE.md                 # Project instructions for AI assistant
│   ├── commands/                 # Custom slash commands
│   └── plan/                     # Architecture migration plan
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── .mcp.json                     # MCP server config (Jira + GitHub)
└── README.md                     # This file
```

## Database Models

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `faculty` | Teacher/instructor profiles | name, email, title, username |
| `External` | External examiner profiles | name, email |
| `Session` | Academic year | year (primary key) |
| `Semester` | Semester with committee | session, semId, chairman, tabular1, tabular2, external |
| `SemesterBill` | Semester-level role flags | teacher, moderator, translator, typist |
| `Course` | Course details | courseName, courseCode, type, internal, external, paperNo, duration |
| `courseBill` | Extra invigilator for a course | course, extra (faculty) |
| `ThesisPaper` | Thesis paper evaluation | faculty, course, paperNo |
| `ThesisSupervisor` | Thesis supervision | faculty, course, studentNo |

### Entity Relationships

```
Session (year)
  └── Semester (semId, chairman, tabular1, tabular2, external)
       ├── SemesterBill (teacher, moderator, translator, typist)
       ├── Course (type: Theory/Lab/Viva, internal, external examiners)
       │    ├── courseBill (extra invigilators)
       │    ├── ThesisPaper (faculty, paperNo)
       │    └── ThesisSupervisor (faculty, studentNo)
       └── Bill Calculation → PDF Export
```

## Application Pages

| Page | Path | Access | Description |
|------|------|--------|-------------|
| Login | `/log/` | Public | Faculty login |
| Home | `/` | Authenticated | Welcome page |
| Committee Search | `/committee/` | Authenticated | Search sessions, create semesters |
| Create Committee | `/createCom/` | Chairman only | Form a new exam committee |
| View Session | `/viewCom/<year>/` | Authenticated | View all semesters in a session |
| View Semester | `/viewSem/<year>/<sem>/` | Authenticated | View committee details, manage roles |
| Create Course | `/createCourse/<year>/<sem>/` | Chairman only | Add a new course |
| View Courses | `/viewCourse/<year>/<sem>/` | Authenticated | List all courses in a semester |
| Update Course | `/updateCourse/<year>/<sem>/<code>/` | Chairman only | Edit course details and examiners |
| Thesis Papers | `/thesis/<year>/<sem>/<code>/` | Authenticated | Track paper evaluations |
| Supervision | `/supervising/<year>/<sem>/<code>/` | Authenticated | Track thesis supervision |
| Teacher Bill | `/examBill/` | Authenticated | View your own bill |
| Individual Bill | `/indBill/<year>/<sem>/<id>/` | Authenticated | Detailed bill breakdown |
| Semester Bill | `/examBill2/` | Chairman/Admin | View all teachers' bills |
| PDF Export | `/pdf_view/<year>/<sem>/<id>/` | Authenticated | Download bill as PDF |

## Contributing

### Branch Strategy

```
main (protected — PR only from dev)
 └── dev (working branch)
      └── feature/* (created from dev, merged into dev)
```

### Workflow

1. Create a Jira ticket for your task
2. Create a branch from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/EBMS-<ticket-number>-short-description
   ```
3. Make your changes and commit:
   ```bash
   git add <files>
   git commit -m "EBMS-<ticket-number>: Short description of changes"
   ```
4. Push and create a Pull Request into `dev`:
   ```bash
   git push -u origin feature/EBMS-<ticket-number>-short-description
   ```
5. After PR review and merge, delete the feature branch
6. `dev` is merged into `main` via PR when ready for release

### Commit Message Format

```
EBMS-<ticket>: Short description

- Detail 1
- Detail 2
```
