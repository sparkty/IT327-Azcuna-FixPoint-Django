# FixPoint (Django Edition)
 
FixPoint is a secure, web-based Issue and Service Management System that allows users to report problems, attach files, and track their resolution. This repository contains the Django port of the original Spring Boot implementation, using PostgreSQL via Supabase as the database.
 
## Tech Stack
 
- **Backend Framework:** Django 5.x
- **Database:** PostgreSQL via Supabase
- **Language:** Python 3.11+
- **Auth:** Django's built-in authentication system (`django.contrib.auth`)
- **IDE:** PyCharm
- **Version Control:** GitHub
## Features Implemented So Far
 
- User Registration (with validation and duplicate-email prevention)
- User Login / Logout
- Supabase PostgreSQL integration
- Custom-styled Login/Register screen (tab-based UI)
## Prerequisites
 
Before setting up this project, make sure you have installed:
 
- [Python 3.11 or later](https://www.python.org/downloads/)
- [PyCharm](https://www.jetbrains.com/pycharm/) (Community or Professional)
- [Git](https://git-scm.com/)
- A [Supabase](https://supabase.com/) account and project
## Setup Instructions
 
### 1. Clone the repository
 
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```
 
### 2. Create and activate a virtual environment
 
**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```
 
**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```
 
### 3. Install dependencies
 
```bash
pip install -r requirements.txt
```
 
### 4. Set up environment variables
 
Create a `.env` file in the project root (this file is git-ignored and should never be committed):
 
```
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgresql://postgres.<project-ref>:<your-db-password>@aws-0-<region>.pooler.supabase.com:6543/postgres
```
 
To generate a `SECRET_KEY`, run:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
 
Your `DATABASE_URL` connection string can be found in your Supabase project under **Project Settings → Database → Connection string**.
 
### 5. Run migrations
 
```bash
python manage.py migrate
```
 
This creates Django's default tables (including `auth_user`) inside your connected Supabase database.
 
### 6. Run the development server
 
```bash
python manage.py runserver
```
 
Visit **http://127.0.0.1:8000/** in your browser.
 
## Project Structure
 
```
IT327-Azcuna-FixPoint-Django/
├── fixpoint_backend/       # Django project settings and root URL config
│   ├── settings.py
│   └── urls.py
├── pages/                  # Main app (login, register, dashboard views)
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/pages/
│   └── static/pages/
├── manage.py
├── requirements.txt
├── .env                    # Not committed — holds secrets
└── .gitignore
```
 
## Notes
 
- The default Django Admin interface is **not** used as the system's main admin interface, per project requirements. A custom admin dashboard is planned for a future milestone.
- Passwords are hashed automatically by Django (PBKDF2) and never stored in plaintext.
## Author
 
Azcuna, Christian Joel D.
IT327 - Information Management 2
