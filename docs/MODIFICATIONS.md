# Lost & Found Pets — List of Possible Modifications

A checklist of features and improvements you can add to the project (for thesis or future use).

---

## 1. Shelter contact form

**Status:** Model supports it (`ContactRequest.to_shelter`), but no UI.

**Add:**
- Contact form on shelter detail page (“Contact this shelter”).
- View that creates `ContactRequest(to_shelter=shelter, ...)`.
- URL e.g. `shelters/<pk>/contact/`.
- Optional: show contact form only when shelter has email, or always and store in DB for admin.

**Complexity:** Low

---

## 2. Geocode CSV address to coordinates

**Status:** CSV accepts `address` or `lat`/`lng`. Rows with only `address` get no lat/lng.

**Add:**
- During CSV import (or as optional “Geocode” step): for each row with `address` and no lat/lng, call Google Geocoding API and set `ShelterPet.lat`/`lng`.
- Consider rate limits and batch size (e.g. geocode in background or limit to N rows per import).

**Complexity:** Medium

---

## 3. Localization (Latvian)

**Status:** `LANGUAGE_CODE` is `en-us`; no translations.

**Add:**
- Enable Django i18n: `USE_I18N = True` (already set), add `LOCALE_PATHS`, `LANGUAGES`.
- Extract strings: `manage.py makemessages -l lv`.
- Translate `.po` files (or use machine translation as base).
- Optional: language switcher in header; set `LANGUAGE_CODE = 'lv'` for Latvia-first.

**Complexity:** Medium

---

## 4. Link reports to shelters (use `linked_shelter`)

**Status:** `PetReport.linked_shelter` exists but is not used in UI.

**Add:**
- In report create/edit form: optional “Link to shelter” dropdown (for shelter staff or admin).
- On report detail: show linked shelter name and link to shelter page.
- In shelter dashboard: list or filter “Reports linked to this shelter”.

**Complexity:** Low–Medium

---

## 5. Shelter pet detail page

**Status:** Shelter detail shows pets as cards only; no dedicated pet page.

**Add:**
- View `shelters/pet/<pk>/` with full pet info (photo, description, status, map if lat/lng).
- Optional: “Contact shelter about this pet” (reuse contact form with pet name in message or add `to_shelter_pet` later).

**Complexity:** Low

---

## 6. Pagination on reports list

**Status:** List is limited to 100 items with no pagination.

**Add:**
- Django `Paginator`: e.g. 12–24 reports per page.
- “Next / Previous” or page numbers in template.

**Complexity:** Low

---

## 7. Clear “no map” message

**Status:** When API key or coordinates are missing, map area can be empty.

**Add:**
- In report detail and shelter detail: if no map (no key or no lat/lng), show a short message: “Map not available” or “Add address and use Geocode to show map.”

**Complexity:** Low

---

## 8. Shared map/geocode JavaScript

**Status:** Map and geocode logic is duplicated in report form, report detail, shelter form, shelter detail, directory.

**Add:**
- Single `static/js/maps.js` (or similar) with init functions for: report picker, report marker, shelter marker, directory markers, geocode button.
- Templates include this file and call one function with config (e.g. element id, lat/lng, options).

**Complexity:** Medium

---

## 9. More automated tests

**Status:** Tests cover registration, login, report permissions, list filter, CSV import.

**Add:**
- Test: submit report contact form (guest and logged-in).
- Test: non-shelter user gets 403 or redirect on shelter dashboard.
- Test: report create and delete flow.
- When shelter contact exists: test shelter contact form.
- Optional: test that map/geocode scripts load when key is present (e.g. with mock or skip in CI).

**Complexity:** Low–Medium

---

## 10. Admin improvements

**Status:** Admin is functional; ContactRequest and filters could be clearer.

**Add:**
- ContactRequest: in `list_display` show “To report” / “To shelter” (or link to object); add `list_filter` by `to_report` / `to_shelter` (or by target type).
- Optional: custom method to show “Contact re: Report #X” vs “Contact re: Shelter Y”.

**Complexity:** Low

---

## 11. Password reset by email

**Status:** Only login/register; no “Forgot password”.

**Add:**
- Django built-in: `PasswordResetView`, `PasswordResetDoneView`, `PasswordResetConfirmView`, `PasswordResetCompleteView`; email backend (console for dev, SMTP for production).
- Configure `EMAIL_*` in settings and add URLs/templates.

**Complexity:** Low–Medium

---

## 12. Email verification (optional)

**Status:** Registration does not verify email.

**Add:**
- After signup: send email with confirmation link; set `user.is_active = False` until verified (or use a “verified” flag on profile).
- View that handles token/link and activates account.

**Complexity:** Medium

---

## 13. Production deployment checklist (docs)

**Status:** README has setup; no explicit production checklist.

**Add:**
- `docs/PRODUCTION.md`: set `SECRET_KEY` from env (no default); `DEBUG=False`; `ALLOWED_HOSTS`; HTTPS; `STATIC_ROOT` + `collectstatic`; DB backups; optional: Gunicorn/uWSGI, Nginx, env example.

**Complexity:** Low (documentation only)

---

## 14. Django / Python version upgrade

**Status:** Django 4.2; README recommends Python 3.12.

**Add:**
- When ready: upgrade to Django 5.x LTS; test on Python 3.12 (and 3.13 if needed).
- Update `requirements.txt` and README; run tests and manual checks.

**Complexity:** Low–Medium

---

## 15. Image optimization

**Status:** Images uploaded as-is (Pillow already in requirements).

**Add:**
- Resize/compress on upload: e.g. max width 1200px, JPEG quality 85%; or use `django-imagekit` / custom `save()` override.
- Optional: thumbnails for list views (e.g. report cards, shelter pets).

**Complexity:** Low–Medium

---

## 16. Search improvements

**Status:** Reports search is `icontains` on description, breed, location_text.

**Add:**
- Optional: search in report title if you add a `title` field.
- Optional: full-text search (PostgreSQL `SearchVector`/`SearchQuery`) for better relevance.
- Optional: filters in URL and “Clear filters” link.

**Complexity:** Low (title + clear filters); Medium (full-text).

---

## 17. Notifications (optional)

**Status:** No in-app or email notifications.

**Add:**
- When someone sends a contact request for a report: email to report owner (or list in dashboard “Messages”).
- When someone contacts a shelter: email to shelter or list in shelter dashboard.
- Optional: “My reports” dashboard section “Contact requests” with count/link.

**Complexity:** Medium

---

## 18. API (optional)

**Status:** All interaction is server-rendered; no REST/API.

**Add:**
- Django REST framework: read-only endpoints for reports list/detail and shelters list/detail (for future mobile app or external integration).
- Optional: API key or token auth for shelters to push pets (alternative to CSV).

**Complexity:** Medium–High

---

## Summary table

| #  | Modification              | Complexity | Impact / use case              |
|----|---------------------------|------------|---------------------------------|
| 1  | Shelter contact form      | Low        | Completes contact flow          |
| 2  | CSV geocode address       | Medium     | Better shelter pet maps        |
| 3  | Localization (Latvian)    | Medium     | Thesis / real use in Latvia    |
| 4  | Link reports to shelters  | Low–Med    | Clearer shelter integration    |
| 5  | Shelter pet detail page   | Low        | Better adoption flow           |
| 6  | Reports pagination        | Low        | UX for many reports            |
| 7  | “No map” message          | Low        | Clearer UX                     |
| 8  | Shared map JS             | Medium     | Maintainability                |
| 9  | More tests                | Low–Med    | Reliability                    |
| 10 | Admin improvements        | Low        | Easier moderation              |
| 11 | Password reset            | Low–Med    | Standard auth                  |
| 12 | Email verification        | Medium     | Safer signups                  |
| 13 | Production docs           | Low        | Deployment                     |
| 14 | Django/Python upgrade     | Low–Med    | Security / support             |
| 15 | Image optimization        | Low–Med    | Performance                    |
| 16 | Search improvements       | Low–Med    | Findability                    |
| 17 | Notifications             | Medium     | Engagement                     |
| 18 | REST API                  | Med–High   | Mobile / integrations          |

---

*Pick items by priority (e.g. 1, 4, 5, 6, 7 for quick wins, then 2, 3, 9 for thesis depth).*
