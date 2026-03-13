# Step 7 — Shelter account setup

You can do step 7 in either of two ways.

---

## Option A: One command (quick test)

In CMD (with venv active) run:

```bat
python manage.py create_default_shelter
```

This creates:

- **User:** `shelter1`  
- **Password:** `ShelterPass123!`  
- **Shelter:** "Test Animal Shelter (Latvia)" in Riga, linked to `shelter1`

Then:

1. Open http://127.0.0.1:8000/accounts/login/
2. Log in with **shelter1** / **ShelterPass123!**
3. In the menu you should see **Shelter Dashboard**
4. There you can: **Edit profile**, **Add pet**, **Import CSV**

If `shelter1` already exists and you want to reset the password:

```bat
python manage.py create_default_shelter --force
```

---

## Option B: Manual setup in Django admin

1. Open http://127.0.0.1:8000/admin/ and log in as admin.
2. **Create a user** (or use an existing one):
   - **Authentication and Authorization** → **Users** → **Add user**
   - Set username and password, save.
3. **Create the shelter**:
   - **Shelters** → **Shelters** → **Add Shelter**
   - Fill **Name**, **Address**, **City** (and optionally description, phone, email).
   - Set **Owner user** to the user from step 2.
   - Save.
4. The chosen user’s role is set to “Shelter” automatically. That user can log in and use **Shelter Dashboard**, edit profile, add pets, and use **Import CSV**.
