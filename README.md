# EventHub

A Django-based smart event discovery and management platform.

## Features implemented
- Custom user roles: attendee, organizer, admin
- Event creation, listing, detail, edit, and delete
- Registration flow with validation and capacity checks
- Organizer participant visibility per event
- Ticketing with General/VIP/Premium types
- Auto-generated ticket numbers on registration
- Ticket detail page
- Organizer sales summary page

## Setup instructions

### 1. Prerequisites
- Python 3.11+
- pip
- virtualenv

### 2. Create and activate a virtual environment
Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install django==5.1.15 django-environ django-crispy-forms crispy-bootstrap5 pillow djangorestframework
```

### 4. Configure environment variables
```powershell
copy .env.example .env
```
Then edit .env and set:
```text
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Run migrations
```powershell
python manage.py migrate
```

### 6. Create a superuser (optional)
```powershell
python manage.py createsuperuser
```

### 7. Run the server
```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Testing
```powershell
python manage.py test tickets registrations
```

## Notes
- The SQLite database is stored in db.sqlite3.
- Media uploads are stored in the media/ directory.
- If you move this project to another machine or another model workflow, keep the full folder intact, including db.sqlite3 and media/ if you want your local demo data preserved.
