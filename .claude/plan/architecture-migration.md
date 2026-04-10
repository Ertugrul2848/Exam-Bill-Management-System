# EBM Architecture Migration Plan

## Overview

Convert the monolithic single-app Django project into a clean, layered MVT architecture with 5 separate apps — using **30 small, atomic steps**, each with its own git commit.

### Rules

1. **One step = one commit** — clear commit message explaining what changed
2. **Never break the project** — after every commit, the app must still run
3. **No mixing concerns** — a rename step doesn't also add features
4. **Commit before moving on** — no step depends on uncommitted work
5. **User approves each step** — show what's about to change, wait for go

### Git Branch Strategy

```
main (stable)
 └── refactor/cleanup          ← Steps 1-7
      └── refactor/config      ← Steps 8-11
           └── refactor/models ← Steps 12-17
                └── refactor/apps-skeleton ← Steps 18-20
                     └── refactor/move-logic ← Steps 21-26
                          └── refactor/templates ← Steps 27-28
                               └── refactor/tests ← Steps 29-30
```

Each phase gets its own branch. After each phase is confirmed working, merge back to `main`.

---

## Phase 1: Cleanup (Steps 1-7)

> Zero risk. No logic changes. Just removing noise.

### Step 1 — Create `.gitignore`

- [ ] Create `.gitignore` at project root
- [ ] Include: `*.pyc`, `__pycache__/`, `db.sqlite3`, `Lib/`, `pyvenv.cfg`, `.env`, `*.exe`
- **Risk:** None — just adds a file
- **Commit:** `chore: add .gitignore`

### Step 2 — Remove `Lib/` and `pyvenv.cfg` from git

- [ ] `git rm -r --cached Lib/`
- [ ] `git rm --cached pyvenv.cfg`
- **Risk:** None — only untracks, doesn't delete locally
- **Commit:** `chore: untrack virtual environment Lib/ and pyvenv.cfg`

### Step 3 — Remove venv binaries from git

- [ ] `git rm --cached Scripts/activate*`
- [ ] `git rm --cached Scripts/*.exe`
- [ ] `git rm --cached Scripts/deactivate.bat`
- [ ] Keep only `Scripts/EBM/` tracked
- **Risk:** None — untrack venv binaries
- **Commit:** `chore: untrack venv scripts and binaries`

### Step 4 — Create `requirements.txt`

- [ ] Run `pip freeze` inside the venv
- [ ] Create `requirements.txt` at project root with pinned versions
- **Risk:** None — just adds a file
- **Commit:** `chore: add requirements.txt with pinned dependencies`

### Step 5 — Remove junk imports in `models.py`

- [ ] Remove: `tkinter.CASCADE`, `turtle.title`, `unittest.util._MAX_LENGTH`, `urllib.parse.MAX_CACHE_SIZE`, `contextlib.nullcontext`, `email.policy.default`, `enum.unique`, `operator.mod`, `pyexpat.model`, `unicodedata.decimal`, `statistics.mode`
- [ ] Keep only: `django.db.models`, `django.contrib.auth.models`, `uuid`, `django.core.validators`
- **Risk:** None — all removed imports are unused
- **Commit:** `chore: remove unused junk imports from models.py`

### Step 6 — Remove junk import in `settings.py`

- [ ] Remove: `from telnetlib import AUTHENTICATION` (line 16)
- **Risk:** None — unused import
- **Commit:** `chore: remove unused telnetlib import from settings.py`

### Step 7 — Fix duplicate settings

- [ ] Remove duplicate `STATICFILES_DIRS` (lines 74-76, keep lines 122-124)
- [ ] Remove duplicate `DEFAULT_AUTO_FIELD` (line 130, keep line 134)
- **Risk:** None — removing exact duplicates
- **Commit:** `chore: remove duplicate STATICFILES_DIRS and DEFAULT_AUTO_FIELD`

---

## Phase 2: Settings & Config (Steps 8-11)

> Reorganize project configuration. Same behavior, better structure.

### Step 8 — Create `config/` directory

- [ ] Create `Scripts/EBM/config/__init__.py`
- [ ] Create `Scripts/EBM/config/wsgi.py` (copy from `EBM/wsgi.py`, update path)
- [ ] Create `Scripts/EBM/config/asgi.py` (copy from `EBM/asgi.py`, update path)
- **Risk:** Low — new files, nothing references them yet
- **Commit:** `refactor: create config/ directory with wsgi and asgi`

### Step 9 — Split settings into base/dev/prod

- [ ] Create `Scripts/EBM/config/settings/__init__.py`
- [ ] Create `Scripts/EBM/config/settings/base.py` (shared settings from current `settings.py`)
- [ ] Create `Scripts/EBM/config/settings/development.py` (DEBUG=True, SQLite)
- [ ] Create `Scripts/EBM/config/settings/production.py` (DEBUG=False, PostgreSQL placeholder)
- [ ] Update `manage.py` to point to `config.settings.development`
- **Risk:** Medium — must test that server still starts
- **Commit:** `refactor: split settings into base/development/production`

### Step 10 — Move SECRET_KEY to environment variable

- [ ] Create `.env.example` with placeholder
- [ ] Update `base.py`: `SECRET_KEY = os.environ.get('SECRET_KEY', '<dev-fallback>')`
- **Risk:** Low — fallback ensures dev still works without .env
- **Commit:** `security: move SECRET_KEY to environment variable with dev fallback`

### Step 11 — Fix ROOT_URLCONF and create config/urls.py

- [ ] Create `Scripts/EBM/config/urls.py` that includes `root.urls`
- [ ] Update `ROOT_URLCONF` in `base.py` to `config.urls`
- **Risk:** Medium — URL routing changes, must test all pages
- **Commit:** `refactor: create config/urls.py as root URL dispatcher`

---

## Phase 3: Model Fixes (Steps 12-17)

> One model change per step. Database migrations at each step.

### Step 12 — Add SEMESTER_CHOICES + display method

- [ ] Add `SEMESTER_CHOICES` list to `Semester` model
- [ ] Add `choices=SEMESTER_CHOICES` to `semId` field
- [ ] Add `get_display_name()` method that returns `self.get_semId_display()`
- [ ] Run `makemigrations` + `migrate`
- **Risk:** Low — additive only, no data change
- **Commit:** `feat: add SEMESTER_CHOICES and get_display_name() to Semester model`

### Step 13 — Add CourseType choices

- [ ] Create `CourseType` IntegerChoices: THEORY=1, LAB=2, VIVA=3
- [ ] Add `choices=CourseType.choices` to `Course.type` field
- [ ] Run `makemigrations` + `migrate`
- **Risk:** Low — same integer values, just adding labels
- **Commit:** `feat: add CourseType choices enum to Course model`

### Step 14 — Rename `faculty` to `Faculty`

- [ ] Rename class `faculty` to `Faculty`
- [ ] Add `class Meta: db_table = 'root_faculty'` to keep same table
- [ ] Update ALL references in: `models.py`, `views.py`, `admin.py`, templates
- [ ] Run `makemigrations` + `migrate`
- **Risk:** Medium — many references to update, must search thoroughly
- **Commit:** `refactor: rename faculty model to Faculty (PascalCase)`

### Step 15 — Rename `courseBill` to `CourseInvigilator`

- [ ] Rename class `courseBill` to `CourseInvigilator`
- [ ] Add `class Meta: db_table = 'root_coursebill'` to keep same table
- [ ] Update ALL references in: `models.py`, `views.py`, `admin.py`
- [ ] Run `makemigrations` + `migrate`
- **Risk:** Medium — fewer references than faculty, but still must search
- **Commit:** `refactor: rename courseBill to CourseInvigilator`

### Step 16 — Rename camelCase fields to snake_case

- [ ] `semId` → `sem_id`
- [ ] `courseCode` → `course_code`
- [ ] `courseName` → `course_name`
- [ ] `paperNo` → `paper_no`
- [ ] `tPaperNo` → `third_paper_no`
- [ ] `vivaExternal` → `viva_external`
- [ ] `thirdExaminer` → `third_examiner`
- [ ] `studentNo` → `student_no`
- [ ] Update ALL references in views.py + templates
- [ ] Run `makemigrations` (use `RenameField`) + `migrate`
- **Risk:** High — many references across views and templates. Must test thoroughly
- **Commit:** `refactor: rename camelCase fields to snake_case across all models`

### Step 17 — Migrate authentication to Django User model

- [ ] Modify `Faculty` to have `user = OneToOneField(User)` instead of username/email/password
- [ ] Remove `password` CharField from Faculty
- [ ] Create data migration:
  - For each faculty row, create a Django `User` with hashed password
  - Link `Faculty.user` to the new `User`
- [ ] Update `views.py` login logic to use Django's `authenticate()`
- [ ] Run `makemigrations` + `migrate`
- **Risk:** HIGH — changes authentication. Must test login flow carefully
- **Commit:** `security: migrate faculty auth to Django User model with hashed passwords`

---

## Phase 4: Create App Skeleton (Steps 18-20)

> Empty apps first. Wire them in later.

### Step 18 — Create empty app directories

- [ ] `python manage.py startapp accounts` → move to `apps/accounts/`
- [ ] `python manage.py startapp committee` → move to `apps/committee/`
- [ ] `python manage.py startapp courses` → move to `apps/courses/`
- [ ] `python manage.py startapp thesis` → move to `apps/thesis/`
- [ ] `python manage.py startapp billing` → move to `apps/billing/`
- [ ] Create `apps/__init__.py`
- [ ] Register all apps in `INSTALLED_APPS`
- **Risk:** Low — empty apps, no logic yet
- **Commit:** `refactor: create 5 empty app skeletons under apps/`

### Step 19 — Create forms.py in each app

- [ ] `apps/accounts/forms.py` → `LoginForm`
- [ ] `apps/committee/forms.py` → `CommitteeCreateForm`, `RoleAssignmentForm`
- [ ] `apps/courses/forms.py` → `CourseCreateForm`, `CourseUpdateForm`
- [ ] `apps/thesis/forms.py` → `ThesisPaperForm`, `SupervisorForm`
- [ ] `apps/billing/forms.py` → `BillSearchForm`
- **Risk:** None — new files, not wired in yet
- **Commit:** `feat: add Django Forms for all apps (not yet wired to views)`

### Step 20 — Create billing rates.py + services.py

- [ ] Create `apps/billing/rates.py` — all 14 rate constants
- [ ] Create `apps/billing/services.py` — `BillLineItem` dataclass + `BillCalculator` class
- [ ] Create `apps/committee/services.py` — `validate_committee()` function
- **Risk:** None — new files, not wired in yet
- **Commit:** `feat: add BillCalculator service and rate constants (not yet wired)`

---

## Phase 5: Move Logic to New Apps (Steps 21-26)

> One view group at a time. Old root/ views replaced.

### Step 21 — Move auth views to accounts app

- [ ] Move `log()` → `apps/accounts/views.py` as `login_view()`, use `LoginForm`
- [ ] Move `logOut()` → `apps/accounts/views.py` as `logout_view()`
- [ ] Create `apps/accounts/urls.py` with routes
- [ ] Update `config/urls.py` to include accounts URLs
- [ ] Remove old auth views from `root/views.py`
- [ ] Move `log.html` → `apps/accounts/templates/accounts/login.html`
- **Risk:** Medium — must test login/logout flow
- **Commit:** `refactor: move auth views to accounts app with LoginForm`

### Step 22 — Move committee views to committee app

- [ ] Move `committee()`, `createCom()`, `viewCom()`, `viewSem()`, `addRole()`, `createSem()` → `apps/committee/views.py`
- [ ] Wire forms: use `CommitteeCreateForm` instead of raw POST
- [ ] Use `validate_committee()` from services.py
- [ ] Create `apps/committee/urls.py` with named routes
- [ ] Move related templates → `apps/committee/templates/committee/`
- [ ] Remove old views from `root/views.py`
- **Risk:** Medium — 6 views, must test each page
- **Commit:** `refactor: move committee views to committee app with forms and services`

### Step 23 — Move course views to courses app

- [ ] Move `createCourse()`, `viewCourse()`, `updateCourse()`, `deleteCourse()`, `addInvigilator()`, `indCourse()` → `apps/courses/views.py`
- [ ] Wire `CourseCreateForm` and `CourseUpdateForm`
- [ ] Create `apps/courses/urls.py`
- [ ] Move related templates → `apps/courses/templates/courses/`
- [ ] Remove old views from `root/views.py`
- **Risk:** Medium — 6 views, must test CRUD flow
- **Commit:** `refactor: move course views to courses app with forms`

### Step 24 — Move thesis views to thesis app

- [ ] Move `thesis()`, `supervising()` → `apps/thesis/views.py`
- [ ] Create `apps/thesis/urls.py`
- [ ] Move related templates → `apps/thesis/templates/thesis/`
- [ ] Remove old views from `root/views.py`
- **Risk:** Low — only 2 views
- **Commit:** `refactor: move thesis views to thesis app`

### Step 25 — Move billing views + replace with BillCalculator

- [ ] Move `examBill()`, `examBill2()`, `indBill()`, `indBill2()`, `semBill()`, `pdf_view()` → `apps/billing/views.py`
- [ ] **Replace all 4 duplicated bill calculation blocks** with `BillCalculator` calls
- [ ] Remove inline `class bill:` definitions
- [ ] Remove standalone `cal()` helper function
- [ ] Wire `BillSearchForm`
- [ ] Create `apps/billing/urls.py`
- [ ] Move related templates → `apps/billing/templates/billing/`
- **Risk:** HIGH — the biggest refactor step. Must verify bill amounts match
- **Commit:** `refactor: move billing views, replace 4x duplicated logic with BillCalculator`

### Step 26 — Add @login_required + @chairman_required

- [ ] Add `@login_required` to ALL views except `login_view`
- [ ] Create `apps/committee/decorators.py` with `@chairman_required`
- [ ] Apply `@chairman_required` to `committee_create`, `semester_bill` views
- [ ] Remove hardcoded `chairman@gmail.com` check
- **Risk:** Medium — changes access control, must test with different users
- **Commit:** `security: add @login_required to all views and @chairman_required decorator`

---

## Phase 6: Templates & Static (Steps 27-28)

> Visual cleanup. Same pages, better code.

### Step 27 — Create base.html + extract CSS

- [ ] Create `templates/base.html` — HTML5 skeleton, Bootstrap CDN, nav block, content block, messages block
- [ ] Create `templates/components/navbar.html` (from `nevigation.html`)
- [ ] Create `templates/components/alert_error.html` (reusable error modal)
- [ ] Create `templates/components/alert_success.html` (reusable success modal)
- [ ] Extract all inline CSS from templates → `static/css/styles.css`
- [ ] Update ALL templates to `{% extends "base.html" %}` and use components
- **Risk:** Medium — every template changes, but visually should be identical
- **Commit:** `refactor: create base.html template, extract inline CSS to stylesheet`

### Step 28 — Replace string URLs with reverse()

- [ ] Replace all `'/viewSem/'+str(id)+'/'+str(id2)` patterns with `reverse()`
- [ ] Replace all hardcoded `href="/committee"` in templates with `{% url 'committee:search' %}`
- [ ] Verify all named URLs resolve correctly
- **Risk:** Medium — must test every link on every page
- **Commit:** `refactor: replace string URL concatenation with reverse() and {% url %} tags`

---

## Phase 7: Tests & Final (Steps 29-30)

> Add safety nets. Clean up.

### Step 29 — Write tests

- [ ] `tests/test_billing.py` — test BillCalculator for all 12 rate rules:
  - Chairman rate = 2700
  - Tabulation junior (sem 1-3) = 2500, senior (sem 4+) = 3125
  - Paper evaluation = 115/paper
  - Question paper = 2150
  - Thesis paper = 1250/paper
  - Thesis supervisor = 3100/student
  - Moderation = 2150, Translation = 400, Stencil-cutter = 375
  - Lab evaluation = 15000, Lab viva = 200/hr, Lab invigilator = 400/hr
  - Viva voce = 200/hr
- [ ] `tests/test_committee.py` — test validation rules
- [ ] `tests/test_accounts.py` — test login/logout flow
- [ ] Run `python manage.py test` and verify all pass
- **Risk:** None — only adds tests
- **Commit:** `test: add test suites for billing, committee, and accounts`

### Step 30 — Final cleanup

- [ ] Remove empty `root/` app if fully migrated
- [ ] Delete `root/views.py`, `root/models.py`, `root/urls.py` (now empty)
- [ ] Update `INSTALLED_APPS` to remove `root.apps.RootConfig`
- [ ] Update `README.md` with new project structure and setup instructions
- [ ] Remove old `nevigation.html`
- **Risk:** Low — just removing dead code
- **Commit:** `chore: remove legacy root/ app and update README`

---

## Progress Tracker

| Step | Description | Status | Commit Hash |
|------|-------------|--------|-------------|
| 1 | Create .gitignore | ⬜ Not started | — |
| 2 | Untrack Lib/ and pyvenv.cfg | ⬜ Not started | — |
| 3 | Untrack venv binaries | ⬜ Not started | — |
| 4 | Create requirements.txt | ⬜ Not started | — |
| 5 | Remove junk imports in models.py | ⬜ Not started | — |
| 6 | Remove junk import in settings.py | ⬜ Not started | — |
| 7 | Fix duplicate settings | ⬜ Not started | — |
| 8 | Create config/ directory | ⬜ Not started | — |
| 9 | Split settings base/dev/prod | ⬜ Not started | — |
| 10 | SECRET_KEY to env variable | ⬜ Not started | — |
| 11 | Fix ROOT_URLCONF + config/urls.py | ⬜ Not started | — |
| 12 | Add SEMESTER_CHOICES | ⬜ Not started | — |
| 13 | Add CourseType choices | ⬜ Not started | — |
| 14 | Rename faculty → Faculty | ⬜ Not started | — |
| 15 | Rename courseBill → CourseInvigilator | ⬜ Not started | — |
| 16 | Rename camelCase → snake_case fields | ⬜ Not started | — |
| 17 | Migrate auth to Django User model | ⬜ Not started | — |
| 18 | Create empty app directories | ⬜ Not started | — |
| 19 | Create forms.py in each app | ⬜ Not started | — |
| 20 | Create billing rates.py + services.py | ⬜ Not started | — |
| 21 | Move auth → accounts app | ⬜ Not started | — |
| 22 | Move committee views → committee app | ⬜ Not started | — |
| 23 | Move course views → courses app | ⬜ Not started | — |
| 24 | Move thesis views → thesis app | ⬜ Not started | — |
| 25 | Move billing views + BillCalculator | ⬜ Not started | — |
| 26 | Add @login_required + @chairman_required | ⬜ Not started | — |
| 27 | Create base.html + extract CSS | ⬜ Not started | — |
| 28 | Replace string URLs with reverse() | ⬜ Not started | — |
| 29 | Write tests | ⬜ Not started | — |
| 30 | Final cleanup | ⬜ Not started | — |
