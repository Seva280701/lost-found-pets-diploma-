# Production deployment checklist

Use this checklist when deploying Lost & Found Pets to a production environment.

## Security

- [ ] **SECRET_KEY**: Set `DJANGO_SECRET_KEY` in environment; do **not** use the default dev key.
- [ ] **DEBUG**: Set `DJANGO_DEBUG=False` (or `0` / `no`).
- [ ] **ALLOWED_HOSTS**: Set `DJANGO_ALLOWED_HOSTS` to your domain(s), e.g. `lostfound.example.com,www.lostfound.example.com`.
- [ ] **HTTPS**: Serve the site over HTTPS; set `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True` in production.
- [ ] **CSRF_TRUSTED_ORIGINS**: If using a custom domain, add `https://yourdomain.com` to this list.

## Database

- [ ] Use **PostgreSQL** in production: set `USE_POSTGRES=1` and `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- [ ] Run migrations: `python manage.py migrate`.
- [ ] Set up regular backups of the database.

## Static and media files

- [ ] Run `python manage.py collectstatic` and configure the web server (e.g. Nginx) to serve `STATIC_ROOT` at `/static/` and `MEDIA_ROOT` at `/media/`.
- [ ] Or use a storage backend (e.g. S3) for media files and set `DEFAULT_FILE_STORAGE` and related settings.

## Email

- [ ] Configure real email: set `EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend` and provide `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (or use a provider like SendGrid/Mailgun).
- [ ] Set `DEFAULT_FROM_EMAIL` and `SERVER_EMAIL` to a valid address for your domain.

## Google Maps

- [ ] Set `GOOGLE_MAPS_API_KEY` in environment (from Google Cloud Console; restrict the key by HTTP referrer in production).
- [ ] Enable **Maps JavaScript API** and **Geocoding API** for the key.

## Application server

- [ ] Use a production WSGI server (e.g. **Gunicorn** or **uWSGI**) instead of `runserver`.
- [ ] Example: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`.
- [ ] Put the app behind a reverse proxy (e.g. **Nginx**) for static files and SSL termination.

## Optional

- [ ] Create a superuser: `python manage.py createsuperuser`.
- [ ] Set up monitoring and error reporting (e.g. Sentry).
- [ ] Use a process manager (e.g. systemd, Supervisor) to keep Gunicorn running.

## Example .env (production, values to be replaced)

```env
DJANGO_SECRET_KEY=your-long-random-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
USE_POSTGRES=1
DB_NAME=lostfound_pets
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
GOOGLE_MAPS_API_KEY=your-google-maps-key
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```
