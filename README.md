# Notely — Task Management Web Application

A Django-based productivity application developed for the WAD2 Group Project at the University of Glasgow.

---

## Team

| Name | Student Number |
|---|---|
| Mohamed ELhabib Ali | 3039352A|
| Xavier Witting | 3005670W|
| Liangyu Ji | 2960934J|
| Ethan Lamb | 2960504L|

**Lab Group:** LB10 10D

---

## Overview

Notely is a multi-user task management platform with project organisation, subtasks, rich-text notes, and real-time UI updates via AJAX. Users can only access their own projects and tasks, enforcing object-level data privacy across the application.

---

## Features

- Full CRUD for Projects and Tasks
- Subtask nesting with checkbox toggling
- Task status management (Todo / Doing / Done) via AJAX
- Quick Access pinning system via AJAX
- Notion-style block editor (Editor.js) for structured task notes — supports Headers, Checklists, Code Blocks and Tables
- User authentication with custom UserProfile (avatar, bio)
- Project cover images
- Responsive navigation with profile management
- Object-level privacy — users can only view or edit content they own

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Exxavia/notely_project.git
cd notely_project
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate       # Linux / Mac
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the population script

```bash
python populate_notely.py
```

This creates demo users, projects and tasks with pre-written Editor.js notes so the application is immediately usable without manual setup.

### 6. Start the development server

```bash
python manage.py runserver
```

---

## Demo Accounts

| Username | Password | 
|---|---|
| PedroLewis_t | Pedro123 |
| AliceLewis_t | Alice123 |
| DanielLewis_t | Daniel123 |

All accounts are created by the population script. Each user has their own isolated set of projects and tasks.

---

## Project Structure

```
notely_project/
┣ 📂accounts/              # User profiles & authentication
┣ 📂media/                 # User-uploaded files
┃ ┣ 📂avatars/             # Profile pictures
┃ ┗ 📂cover_images/        # Project cover images
┣ 📂notely_project/        # Django settings & root URLs
┣ 📂notes/                 # Core app — Task & Project models, views, AJAX endpoints
┣ 📂static/                # Frontend assets
┃ ┣ 📂css/
┃ ┃ ┗ style.css            # Site-wide styles
┃ ┗ 📂js/
┃   ┗ task_detail.js       # AJAX logic & Editor.js initialisation
┣ 📂templates/             # HTML templates (all inherit from base.html)
┣ 📜.env                   # Secret keys — keep out of Git
┣ 📜.gitignore             # Git ignore rules
┣ 📜manage.py              # Django entry point
┣ 📜populate_notely.py     # Demo data population script
┣ 📜README.md              # Documentation
┗ 📜requirements.txt       # Python dependencies
```

---

## Technical Notes

**Block-based notes (Editor.js)**
Task descriptions are saved as structured JSON rather than raw HTML. This keeps data clean, prevents XSS vulnerabilities, and makes partial updates straightforward.

**AJAX state management**
Task status, subtask toggling and quick-access pinning all use `fetch()` requests so the page does not reload on every interaction. Django views return JSON responses consumed directly by `task_detail.js`.

**Editor.js plugin stability**
Multiple CDN-loaded Editor.js plugins can conflict at runtime due to variable naming collisions. Initialisation is wrapped in `typeof` safety checks and mapped through the `window` object to prevent one failed plugin from blocking the rest of the page.

---

## External Sources

| Source | Usage |
|---|---|
| [Bootstrap 5](https://getbootstrap.com/) | Responsive CSS framework |
| [Editor.js](https://editorjs.io/) | Block-based rich text editor |
| [Bootstrap Icons](https://icons.getbootstrap.com/) | UI iconography |

---

## Deployment

The application is deployed on PythonAnywhere and is accessible at:

`https://notely.pythonanywhere.com` *(update with your actual URL)*
