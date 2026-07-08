# FixPoint – Issue and Service Management System (Django)

FixPoint is a web-based Issue and Service Management System where users can register, report problems, track issue resolution, attach files, post comments, and receive notifications. Built with Django and PostgreSQL (Supabase).

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Framework | Django 6.x |
| Database | PostgreSQL via Supabase |
| Auth | Django AbstractUser (custom model) |
| Frontend | HTML5, CSS3 (vanilla), JavaScript |
| File Storage | Supabase Storage (S3-compatible) |
| Version Control | Git / GitHub |

---

## Models / Entities

| Model | App | Description |
|-------|-----|-------------|
| `Role` | `fixpoint_backend.users` | Permission roles (e.g., Employee, IT Staff) |
| `CustomUser` | `fixpoint_backend.users` | Custom user model extending AbstractUser; uses email as login |
| `Issue` | `fixpoint_backend.issues` | Core entity — reported problems or service requests |
| `Attachment` | `fixpoint_backend.attachments` | Files attached to an issue |
| `Comment` | `fixpoint_backend.comments` | Text replies on an issue thread |
| `Notification` | `fixpoint_backend.notifications` | System messages triggered by issue activity |

---

## Pages / Interfaces

| URL | View | Description |
|-----|------|-------------|
| `/` | `login_register` | Tab-based login and registration page |
| `/dashboard/` | `dashboard` | Issue dashboard (user sees own issues; staff sees all) |
| `/logout/` | `logout_view` | Logs out the user and redirects to `/` |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Create and activate a virtual environment

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate
```

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root (never commit this file):

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Project Structure

```
FixPointDjango/
├── fixpoint_backend/           # Django project package
│   ├── settings.py
│   ├── urls.py
│   ├── users/                  # CustomUser and Role models
│   ├── issues/                 # Issue model
│   ├── attachments/            # Attachment model
│   ├── comments/               # Comment model
│   └── notifications/          # Notification model
├── pages/                      # UI app (login, register, dashboard)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── templates/pages/
│   └── static/pages/
├── manage.py
├── requirements.txt
└── .env                        # Not committed — holds secrets
```

---

## Notes

- The Django Admin panel is **not** used as the system interface. All data management is done through custom-built views and templates.
- Passwords are hashed by Django (PBKDF2) and never stored in plaintext.
- File uploads are configured to use Supabase Storage (S3-compatible). If no Supabase Storage credentials are set, uploads fall back to local `media/`.

---

## Author

**Azcuna, Christian Joel D.**  
IT327 – Information Management 2
