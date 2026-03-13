# Localization (Latvian, English, Russian)

The site supports three languages: **English** (default), **Latvian** (Latviešu), and **Russian** (Русский).

## For users

- Use the **language dropdown** in the top navigation (next to Login/Register) to switch language.
- The choice is saved in your session, so it persists while you browse.

## For developers

### Compiling translations (required after editing .po files)

Django needs compiled `.mo` files to use translations. You need **GNU gettext** installed:

1. **Windows:** Install gettext (e.g. from [gettext for Windows](https://mlocati.github.io/articles/gettext-iconv-windows.html)) and add the `bin` folder to your PATH.
2. **macOS:** `brew install gettext` and ensure `msgfmt` is on PATH.
3. **Linux:** `sudo apt install gettext` (Debian/Ubuntu) or equivalent.

Then run:

```bash
python manage.py compilemessages
```

This compiles `locale/*/LC_MESSAGES/django.po` into `django.mo`.

### Adding or updating translated strings

1. Edit the templates or Python code and use `{% trans "..." %}` in templates or `gettext_lazy()` in Python.
2. Install gettext (see above) and run:
   ```bash
   python manage.py makemessages -l en -l lv -l ru --ignore=venv
   ```
   This updates `locale/*/LC_MESSAGES/django.po` with new msgids.
3. Fill in the `msgstr` for each language in the `.po` files.
4. Run `python manage.py compilemessages`.

### Locale files layout

```
locale/
  en/LC_MESSAGES/django.po   # English (source)
  lv/LC_MESSAGES/django.po   # Latvian
  ru/LC_MESSAGES/django.po   # Russian
```

After compiling, each has a `django.mo` next to `django.po`.

### Default language

Default is set in `config/settings.py`: `LANGUAGE_CODE = 'en'`. To default to Latvian, set `LANGUAGE_CODE = 'lv'`.
