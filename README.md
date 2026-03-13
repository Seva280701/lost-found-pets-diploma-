# Lost & Found Pets — Latvian Animal Shelter Integration

Bachelor thesis project: a web platform for reporting lost/found pets with centralized Latvian animal shelter integration, maps, and CSV import.

## Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript (no React/Vue)
- **Database:** PostgreSQL (recommended) or SQLite (default for local run)
- **Maps:** Google Maps JavaScript API + Geocoding
- **Data import:** CSV for shelters (API structure can be added later)

## Project structure

```
config/          # Django settings, urls
accounts/        # User accounts, roles (user/shelter/admin)
core/            # Home page, common
reports/         # PetReport, PetImage, ContactRequest, search/filter
shelters/        # Shelter, ShelterPet, CSV import, directory
templates/       # Base and app templates
static/          # CSS, JS
```

## Setup

**Recommended:** Use **Python 3.12** for this project. Django 4.2 has compatibility issues with Python 3.14 (admin "Add"/"Change" and tests can fail with `AttributeError` in template context). Create the venv with 3.12: `py -3.12 -m venv venv` then `venv\Scripts\activate.bat`. Always run the server and admin from this venv.

1. **Clone and create venv**
   ```bash
   python -m venv venv
   # Activate (Windows):
   venv\Scripts\activate.bat     # Command Prompt (recommended if PowerShell blocks scripts)
   # OR in PowerShell (if activation is blocked by execution policy):
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   **Note:** If `venv\Scripts\activate` fails in PowerShell with "script not digitally signed", use **Command Prompt** and run `venv\Scripts\activate.bat`, or run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once in PowerShell (then activate works).

2. **Database**
   - **SQLite (default):** No config. Migrations create `db.sqlite3`.
   - **PostgreSQL:** Set env and run migrations:
     ```bash
     set USE_POSTGRES=1
     set DB_NAME=lostfound_pets
     set DB_USER=postgres
     set DB_PASSWORD=yourpassword
     python manage.py migrate
     ```

3. **Google Maps** (step 5 — see [docs/GOOGLE_MAPS_SETUP.md](docs/GOOGLE_MAPS_SETUP.md) for details)
   - Create an API key in [Google Cloud Console](https://console.cloud.google.com/) (enable **Maps JavaScript API** and **Geocoding API**).
   - Create a `.env` file in the project root and add: `GOOGLE_MAPS_API_KEY=your-key`
   - Restart the server; maps will work on report create/edit, report detail, and shelter directory.

4. **Run**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser   # optional, for admin
   python manage.py runserver
   ```
   If `python manage.py` says "django-admin not found", use: `python -m django migrate`, `python -m django runserver`, etc. (Or add your Python `Scripts` folder to PATH.)
   Open http://127.0.0.1:8000/

## Roles and permissions

- **Guest:** View/search reports, view details and map, contact form.
- **Registered user:** Create lost/found report, edit/delete only own reports.
- **Shelter account:** Manage shelter profile, CRUD shelter pets, CSV import. (Admin assigns a user to a shelter; that user’s role becomes “shelter”.)
- **Admin:** Full access via Django admin; can moderate reports and manage users/shelters.

Permissions are enforced on the backend (views return 403 when not allowed).

## Main flows

- **Reports:** List with filters (type, species, status, city, search) → detail (map + contact form) → create/edit (map picker + geocode).
- **Shelters:** Directory (list + map) → shelter detail → shelter dashboard (edit profile, add/edit pets, CSV import with preview).

## CSV import (shelters)

Required columns: `species`, `description`, `intake_date`.  
Also required: `address` OR both `lat` and `lng`.  
Optional: `external_id`, `name`, `breed`, `color`, `sex`, `intake_location_text`, `status`.  
Duplicate prevention: by `external_id` if present, otherwise by hash of species+description+intake_date+name.

## Shelter account (step 7)

To test Shelter Dashboard and CSV import, create a shelter user:

```bash
python manage.py create_default_shelter
```

Then log in at `/accounts/login/` with **shelter1** / **ShelterPass123!** and open **Shelter Dashboard**. See [docs/SHELTER_ACCOUNT_SETUP.md](docs/SHELTER_ACCOUNT_SETUP.md) for the manual admin way.

## Testing

```bash
python manage.py test accounts reports shelters
```

Manual test checklist (thesis):

- Registration / login
- Create report (logged-in user)
- Permissions: user cannot edit another user’s report
- Shelter CSV import (upload → preview → confirm)
- Map: coordinates saved on report create/edit

## Documentation for thesis

- **UML:** Use cases (guest, user, shelter, admin), ERD (User, Shelter, ShelterPet, PetReport, PetImage, ContactRequest), sequence diagrams as needed.
- **System testing:** Manual checklist above + automated tests in `accounts`, `reports`, `shelters` apps.

## License

Thesis project — use as required by your institution.
