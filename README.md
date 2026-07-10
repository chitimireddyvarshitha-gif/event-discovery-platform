# EventHub 🎟️

A Django-based **smart event discovery and management platform** supporting attendees, organizers, and admins with a full-featured REST API.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [Populating Sample Data](#populating-sample-data)
- [REST API](#rest-api)
- [Running Tests](#running-tests)
- [Notes](#notes)

---

## Features

| Area | Details |
|------|---------|
| **Authentication** | Custom user model with roles: `attendee`, `organizer`, `admin` |
| **Events** | Create, list, detail, edit, and delete events with categories (Music, Cultural, Business, Education, Sports, Food) |
| **Registrations** | Registration flow with capacity validation and conflict checks |
| **Tickets** | General / VIP / Premium ticket types; auto-generated ticket numbers |
| **Favorites** | Save and manage favourite events |
| **Notifications** | In-app notification system with console email backend |
| **Analytics** | Per-event and platform-wide analytics dashboard |
| **Reports** | Organizer sales & participant reports |
| **REST API** | Token + Session authenticated API for events, registrations, tickets, and notifications |
| **Admin Panel** | Full Django admin for all models |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.0.8 |
| API | Django REST Framework 3.17.1 |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Images | Pillow 12.3.0 |
| Config | django-environ 0.14.0 |
| Database | SQLite (default) |
| Python | 3.11+ |

---

## Project Structure

```
EventDiscoveryPlatform/
├── EventDiscoveryPlatform/   # Django project settings & root URLs
│   ├── settings.py
│   ├── urls.py
│   ├── views.py              # Home view
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                 # Custom user model, auth views (login/register/profile)
├── events/                   # Event CRUD, categories, banner uploads
├── registrations/            # Event registration with capacity checks
├── tickets/                  # Ticket generation (General/VIP/Premium)
├── favorites/                # Save favourite events
├── notifications/            # In-app notification system
├── analytics/                # Event & platform analytics
├── reports/                  # Organizer sales reports
├── api/                      # REST API (DRF ViewSets + auth endpoints)
├── templates/                # Shared HTML templates
├── static/                   # CSS, JS, and static assets
├── media/                    # User-uploaded files (banners, profile pics)
├── populate_events.py        # Script to seed sample event data
├── manage.py
├── requirements.txt          # Pinned Python dependencies
├── .env.example              # Environment variable template
└── db.sqlite3                # SQLite database (development)
```

---

## Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **pip** (bundled with Python)
- **Git** (optional, for cloning)

---

## Installation & Setup

### 1. Clone the repository

```powershell
git clone <your-repo-url>
cd EventDiscoveryPlatform
```

### 2. Create a virtual environment

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

> **Tip:** Your terminal prompt will show `(venv)` when the environment is active.

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

This installs all pinned packages:
- `Django 5.0.8`
- `djangorestframework 3.17.1`
- `django-crispy-forms` + `crispy-bootstrap5`
- `django-environ`
- `Pillow`

### 4. Configure environment variables

```powershell
copy .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

Then open `.env` and fill in the required values (see [Environment Variables](#environment-variables) below).

### 5. Apply database migrations

```powershell
python manage.py migrate
```

### 6. Create a superuser (admin account)

```powershell
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

### 7. Collect static files (optional, for production)

```powershell
python manage.py collectstatic
```

---

## Environment Variables

Copy `.env.example` to `.env` and set the following:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ Yes | — | Django secret key (generate a secure random string) |
| `DEBUG` | No | `False` | Set to `True` for local development |
| `DATABASE_URL` | No | SQLite | Optional: PostgreSQL/MySQL URL (e.g., `postgres://user:pass@host/db`) |

**Generating a secure `SECRET_KEY`:**

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example `.env` for local development:**

```env
SECRET_KEY=your-generated-secret-key-here
DEBUG=True
DATABASE_URL=
```

---

## Running the Server

```powershell
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000/**

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Home page |
| `http://127.0.0.1:8000/events/` | Browse all events |
| `http://127.0.0.1:8000/accounts/login/` | Login |
| `http://127.0.0.1:8000/accounts/register/` | Register |
| `http://127.0.0.1:8000/admin/` | Django admin panel |
| `http://127.0.0.1:8000/api/` | REST API root |

---

## Populating Sample Data

A seed script is included to create realistic sample events:

```powershell
python populate_events.py
```

This will generate sample events across all categories (Music, Cultural, Business, Education, Sports, Food).

---

## REST API

The API is available at `/api/` and uses **Token Authentication**.

### Authentication

**Register a new user:**
```http
POST /api/register/
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "attendee"
}
```

**Login and get a token:**
```http
POST /api/login/
Content-Type: application/json

{
  "username": "john",
  "password": "securepassword"
}
```

Use the returned token in subsequent requests:
```http
Authorization: Token <your-token-here>
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/events/` | List all events |
| `POST` | `/api/events/` | Create a new event (organizer) |
| `GET` | `/api/events/{id}/` | Get event details |
| `PUT/PATCH` | `/api/events/{id}/` | Update an event |
| `DELETE` | `/api/events/{id}/` | Delete an event |
| `GET` | `/api/registrations/` | List user's registrations |
| `POST` | `/api/registrations/` | Register for an event |
| `GET` | `/api/tickets/` | List user's tickets |
| `GET` | `/api/notifications/` | List user's notifications |
| `GET` | `/api/profile/` | Get/update current user profile |

---

## Running Tests

```powershell
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test events
python manage.py test tickets
python manage.py test registrations
python manage.py test api
```

---

## Notes

- **Database**: SQLite (`db.sqlite3`) is used by default — suitable for development. For production, switch to PostgreSQL via `DATABASE_URL` in `.env`.
- **Media files**: User-uploaded files (event banners, profile pictures) are stored in the `media/` directory.
- **Email**: The console email backend is configured — emails are printed to the terminal, not sent. Change `EMAIL_BACKEND` in `settings.py` for production.
- **Organizer approval**: New organizer accounts require admin approval before they can create events (`is_approved = False` by default).
- **Moving the project**: Keep `db.sqlite3` and `media/` intact to preserve local demo data when switching machines.
